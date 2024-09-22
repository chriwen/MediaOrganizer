"""
Media File Organizer

This script automatically renames and organizes media files (images and videos)
based on their creation date. It's particularly useful for managing media
uploaded from various devices to a central storage system like a Synology NAS.

Copyright © 2024 Christian Wenzel. All rights reserved.

This script is licensed under the MIT License. 
See the LICENSE file for details.

Author: Christian Wenzel
Date: 2024
"""

import os
import shutil
import subprocess
from datetime import datetime
import sys

# Liste der gängigen Video- und Bildformate
video_extensions = ('.mov', '.mp4', '.avi', '.mkv', '.flv', '.wmv', '.m4v')
image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic')

# Mögliche Metadatenfelder für das Erstellungsdatum
date_fields = ['CreateDate', 'DateTimeOriginal', 'MediaCreateDate', 'TrackCreateDate']

def print_help():
    """
    Zeigt die Hilfeoptionen an, wenn -help als Parameter übergeben wird.
    """
    help_text = """
    Nutzungsweise des Skripts:

    python script.py <Quellverzeichnis> [Optionen]

    Optionen:
    -move <Zielverzeichnis>  : Benennt Dateien im Quellverzeichnis um und verschiebt sie anschließend in die entsprechende Jahres-/Monatsstruktur im Zielverzeichnis.
    -rename                  : Benennt nur die Dateien im Quellverzeichnis um, ohne sie zu verschieben.
    -r                       : Verarbeitet die Dateien im Quellverzeichnis rekursiv (durchläuft auch Unterverzeichnisse).
    -help                    : Zeigt diese Hilfsnachricht an.

    Beispiele:
    1. Nur Umbenennen von Dateien im Quellverzeichnis:
       python script.py /path/to/source_directory -rename
    
    2. Rekursives Umbenennen und Verschieben der Dateien ins Zielverzeichnis:
       python script.py /path/to/source_directory -move /path/to/target_directory -r
    """
    print(help_text)

def log_info(message, log_file_path):
    """ Schreibe Informationen ins Logfile. """
    with open(log_file_path, 'a') as log_file:
        log_file.write(message + "\n")

def get_creation_date(file_path):
    """ Versuche, das Erstellungsdatum einer Datei (Bild oder Video) zu extrahieren. """
    try:
        result = subprocess.run(['exiftool', '-j'] + [f'-{field}' for field in date_fields] + [file_path],
                                capture_output=True, text=True)
        metadata = result.stdout
        
        for field in date_fields:
            if f'"{field}"' in metadata:
                date_str = metadata.split(f'"{field}": "')[1].split('"')[0]
                creation_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                return creation_date, field
        return None, None
    except Exception as e:
        print(f"Fehler beim Abrufen des Erstellungsdatums für {file_path}: {e}")
        return None, None

def rename_file_based_on_date(file_path, log_file_path):
    """ Benenne die Datei basierend auf ihrem Erstellungsdatum um. """
    creation_date, field_used = get_creation_date(file_path)
    if creation_date:
        formatted_date = creation_date.strftime('%Y-%m-%d_%H-%M-%S')
        file_dir, file_extension = os.path.splitext(file_path)
        new_name = f"{formatted_date}{file_extension}"
        new_file_path = os.path.join(os.path.dirname(file_path), new_name)
        
        try:
            shutil.move(file_path, new_file_path)
            print(f"Datei umbenannt: {file_path} -> {new_file_path}")
            log_info(f"Datei umbenannt: {file_path} -> {new_file_path} (basierend auf {field_used})", log_file_path)
            return new_file_path  # Rückgabe des neuen Dateipfads
        except Exception as e:
            print(f"Fehler beim Umbenennen der Datei: {e}")
            log_info(f"Fehler beim Umbenennen der Datei {file_path}: {e}", log_file_path)
    else:
        print(f"Kein Erstellungsdatum gefunden für {file_path}. Datei bleibt unverändert.")
        log_info(f"Kein Erstellungsdatum gefunden: {file_path} bleibt unverändert.", log_file_path)
    return None  # Wenn kein Datum gefunden wurde

def move_file_based_on_date(file_path, target_base_folder, log_file_path):
    """ Verschiebe die Datei basierend auf ihrem Erstellungsdatum in die Zielverzeichnisstruktur. """
    creation_date, _ = get_creation_date(file_path)
    if creation_date:
        year = creation_date.strftime('%Y')
        year_month = creation_date.strftime('%Y-%m')
        
        target_folder = os.path.join(target_base_folder, year, year_month)
        os.makedirs(target_folder, exist_ok=True)
        
        file_name = os.path.basename(file_path)
        target_file_path = os.path.join(target_folder, file_name)
        
        # Prüfe, ob die Datei bereits im Zielverzeichnis existiert
        if os.path.exists(target_file_path):
            log_info(f"Datei existiert bereits: {target_file_path}. Datei wurde nicht verschoben.", log_file_path)
            print(f"Datei existiert bereits: {target_file_path}. Datei wurde nicht verschoben.")
            return
        
        try:
            shutil.move(file_path, target_file_path)
            print(f"Datei verschoben: {file_path} -> {target_file_path}")
            log_info(f"Datei verschoben: {file_path} -> {target_file_path}", log_file_path)
        except Exception as e:
            print(f"Fehler beim Verschieben der Datei: {e}")
            log_info(f"Fehler beim Verschieben der Datei {file_path}: {e}", log_file_path)
    else:
        print(f"Kein Erstellungsdatum gefunden für {file_path}. Datei wird nicht verschoben.")
        log_info(f"Kein Erstellungsdatum gefunden: {file_path}. Datei wird nicht verschoben.", log_file_path)

def process_media_in_folder(folder, recursive, target_folder=None, rename_only=False):
    """ 
    Durchlaufe den angegebenen Ordner und benenne Bild- und Videodateien um oder verschiebe sie je nach Parametern.
    """
    if recursive:
        for root, dirs, files in os.walk(folder):
            print(f"Verarbeite Verzeichnis: {root}")
            log_file_path = os.path.join(root, "RenameScript_log.txt")
            if os.path.exists(log_file_path):
                os.remove(log_file_path)

            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(video_extensions) or file.lower().endswith(image_extensions):
                    print(f"Verarbeite Datei: {file_path}")
                    new_file_path = rename_file_based_on_date(file_path, log_file_path)
                    if new_file_path and not rename_only and target_folder:
                        move_file_based_on_date(new_file_path, target_folder, log_file_path)  # Verschiebe die Datei mit dem neuen Namen
    else:
        print(f"Verarbeite Verzeichnis: {folder}")
        log_file_path = os.path.join(folder, "RenameScript_log.txt")
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                if file.lower().endswith(video_extensions) or file.lower().endswith(image_extensions):
                    print(f"Verarbeite Datei: {file_path}")
                    new_file_path = rename_file_based_on_date(file_path, log_file_path)
                    if new_file_path and not rename_only and target_folder:
                        move_file_based_on_date(new_file_path, target_folder, log_file_path)  # Verschiebe die Datei mit dem neuen Namen

if __name__ == "__main__":
    # Wenn -help als Parameter übergeben wird, Hilfe anzeigen
    if '-help' in sys.argv:
        print_help()
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Fehler: Es muss mindestens ein Quellverzeichnis angegeben werden. Verwende -help für weitere Informationen.")
        sys.exit(1)

    source_folder = sys.argv[1]
    target_folder = None
    rename_only = False
    recursive = False

    # Parameter auswerten
    if '-move' in sys.argv:
        move_index = sys.argv.index('-move') + 1
        if move_index >= len(sys.argv):
            print("Fehler: Es muss ein Zielverzeichnis angegeben werden, wenn '-move' verwendet wird.")
            sys.exit(1)
        target_folder = sys.argv[move_index]

    if '-rename' in sys.argv:
        rename_only = True

    if '-r' in sys.argv:
        recursive = True

    # Fehlerüberprüfung für Ordner
    if not os.path.isdir(source_folder):
        print(f"Fehler: {source_folder} ist kein gültiges Quellverzeichnis.")
        sys.exit(1)

    if target_folder and not os.path.isdir(target_folder):
        print(f"Fehler: {target_folder} ist kein gültiges Zielverzeichnis.")
        sys.exit(1)

    # Wenn sowohl -move als auch -rename angegeben wurden
    if target_folder and rename_only:
        print("Fehler: Die Optionen '-move' und '-rename' dürfen nicht gleichzeitig verwendet werden.")
        sys.exit(1)

    # Medienverarbeitung starten
    process_media_in_folder(source_folder, recursive, target_folder, rename_only)

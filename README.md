# MediaOrganizer
Media Organizer is a Python script designed to automatically rename and organize media files (images and videos) based on their creation date. It's particularly useful for managing media uploaded from various devices to a central storage system like a Synology NAS.

## Features

- Renames media files based on their creation date
- Moves renamed files into a year/month folder structure
- Supports recursive processing of directories
- Logs all actions for easy tracking
- Handles common image and video formats

## Requirements

- Python 3.x
- exiftool (must be available in the system path)

## Installation

1. Ensure Python 3.x is installed on your system.
2. Install exiftool on your system.
3. Clone this repository or download the script:

```bash
git clone https://github.com/yourusername/media-file-organizer.git
cd media-file-organizer
```

## Usage

Run the script from the command line with various options:

```bash
python media_file_organizer.py <source_directory> [options]
```

### Options:

- `-move <target_directory>`: Renames files and moves them to the year/month structure in the target directory.
- `-rename`: Only renames the files in the source directory without moving them.
- `-r`: Processes the source directory recursively (including subdirectories).
- `-help`: Displays the help message.

### Examples:

1. Only rename files in the source directory:
   ```bash
   python media_file_organizer.py /path/to/source_directory -rename
   ```

2. Recursively rename and move files to the target directory:
   ```bash
   python media_file_organizer.py /path/to/source_directory -move /path/to/target_directory -r
   ```

## How It Works

1. The script searches for image and video files in the specified source directory.
2. For each file found, it extracts the creation date from the metadata.
3. The file is renamed based on the creation date (format: YYYY-MM-DD_HH-MM-SS).
4. If the `-move` option is used, the renamed file is moved to the corresponding year/month structure in the target directory.
5. All actions are logged in a log file in the source directory.

## Use Case: Synology NAS and Smartphone Backup

A typical use case for this script is organizing media backed up from a smartphone to a Synology NAS using the Synology Photos app:

1. Users regularly back up their smartphone photos and videos to a specific backup directory on the NAS using the Synology Photos app.
2. The Media File Organizer is set up on the NAS to process the backup directory regularly (e.g., via a cron job).
3. The script renames the files in the backup directory and moves them to the general photo album, structured by year and month.
4. This enables uniform organization of all media, regardless of their source, and facilitates easy file discovery and management.

## Special Features

- Uses exiftool for metadata extraction, ensuring reliable date detection across various camera and smartphone models.
- Checks multiple metadata fields to determine the creation date, increasing compatibility with different file formats.
- Detects duplicate files and avoids overwriting to prevent data loss.

## Troubleshooting

- Ensure exiftool is correctly installed and available in the system path.
- Check access permissions for source and target directories.
- Consult the `RenameScript_log.txt` file in the source directory for detailed information about the processing of each file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

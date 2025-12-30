# Apple iCloud Photos Downloader Script

A Python wrapper for [icloud-photos-downloader](https://github.com/icloud-photos-downloader/icloud_photos_downloader) for downloading photos from Apple iCloud with flexible options for albums, date ranges, or complete library downloads.

## Features

- **Download by Albums**: Select specific albums to download
- **Download by Date Range**: Download photos from a specific time period
- **Download All**: Download your entire Apple iCloud photo library
- **Reload Credentials**: Refresh authentication and handle 2FA
- Interactive and non-interactive modes
- Configurable via environment variables
- Docker-based (no Python dependencies to install)

## Prerequisites

- Docker installed and running
- [icloud-photos-downloader](https://github.com/icloud-photos-downloader/icloud_photos_downloader) Docker image downloaded (the script will download one automatically if none exists on the host)
- Apple iCloud account with photos
- Apple iCloud account configured for icloudpd:
  - **Access Apple iCloud Data on the Web** enabled (`Settings > Apple ID > Apple iCloud > Access Apple iCloud Data on the Web`)
  - **Advanced Data Protection** disabled (`Settings > Apple ID > Apple iCloud > Advanced Data Protection`)

## Setup

1. Clone or download this repository

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your credentials:
   ```bash
   Apple iCloud_USERNAME=your_email@example.com
   Apple iCloud_PASSWORD=your_password_here
   ```

4. Make the script executable:
   ```bash
   chmod +x Apple iCloudpd-interactive-albums.py
   ```

5. (Optional) Authenticate for the first time:
   ```bash
   ./Apple iCloudpd-interactive-albums.py --mode reload
   ```

## Usage

### Interactive Mode

Run the script without arguments to see all options:

```bash
./Apple iCloudpd-interactive-albums.py
```

You'll be prompted to choose:
1. Download by albums
2. Download by date range
3. Reload Apple iCloud credentials
4. Download all photos

### Non-Interactive Mode

**Download specific albums:**
```bash
./Apple iCloudpd-interactive-albums.py --mode albums
```
Then select albums by number or name (comma-separated):
- `1,3,5` - Select albums by number
- `album1, album2` - Select albums by name
- `all` - Download all albums
- `none` or empty - Abort

**Download by date range:**
```bash
./Apple iCloudpd-interactive-albums.py --mode date --start-date 2019-01-01 --end-date 2019-12-31
```

**Download everything:**
```bash
./Apple iCloudpd-interactive-albums.py --mode all
```

**Reload credentials (for 2FA):**
```bash
./Apple iCloudpd-interactive-albums.py --mode reload
```

## Environment Variables

Configure these in your `.env` file:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `Apple iCloud_USERNAME` | Yes | - | Your Apple iCloud email address |
| `Apple iCloud_PASSWORD` | Yes | - | Your Apple iCloud password |
| `TIMEZONE` | No | `Europe/London` | Timezone for timestamps |
| `DOWNLOAD_SIZE` | No | `original` | Photo size: `original`, `medium`, `thumb` |
| `DATA_DIR` | No | `./Apple iCloud-photos` | Local directory for downloaded photos |
| `COOKIES_DIR` | No | `./Apple iCloudpd-cookies` | Directory for authentication cookies |

## File Structure

```
.
├── Apple iCloudpd-interactive-albums.py  # Main script
├── .env                            # Your credentials (not in git)
├── .env.example                    # Template for credentials
├── .gitignore                      # Excludes sensitive files
├── Apple iCloud-photos/                  # Downloaded photos (not in git)
└── Apple iCloudpd-cookies/               # Session cookies (not in git)
```

## Examples

**Download photos from 2019:**
```bash
./Apple iCloudpd-interactive-albums.py --mode date --start-date 2019-01-01 --end-date 2019-12-31
```

**Download specific albums interactively:**
```bash
./Apple iCloudpd-interactive-albums.py --mode albums
# Then enter: 1,5,album1
```

**Download everything:**
```bash
./Apple iCloudpd-interactive-albums.py --mode all
```

## Troubleshooting

**Authentication errors:**
- Run `./Apple iCloudpd-interactive-albums.py --mode reload` to refresh credentials
- Complete 2FA when prompted

**Container name errors with special characters:**
- The script automatically sanitizes album names for Docker compatibility

**No albums found:**
- Verify your credentials in `.env`
- Check that Apple iCloud web access is enabled
- Try reloading credentials

## Credits

This script is a wrapper around [Apple iCloudpd](https://github.com/iCloud-photos-downloader/Apple iCloud_photos_downloader), the excellent command-line tool for downloading photos from Apple iCloud.

## License

MIT License - see LICENSE file for details

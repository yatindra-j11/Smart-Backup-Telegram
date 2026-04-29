# SmartBackup - Django + Telegram Backup Application

A modern backup solution that automatically splits large files and uploads them to Telegram via bot API, with a beautiful web interface for management.

## Features

- 🤖 **Telegram Integration**: Upload backup parts to Telegram using bot API
- 📁 **File Splitting**: Automatically splits files larger than 19MB to respect Telegram's download limits
- 🌐 **Modern Web UI**: Clean, dark-themed interface built with Tailwind CSS
- 👁️ **Watch Folder**: Automatic backups when files are dropped into watch folder
- 💾 **SQLite Database**: Tracks backup history without external database requirements
- 🔄 **Restore Functionality**: Download and restore backups from Telegram
- ⚙️ **Easy Setup**: Step-by-step configuration for Telegram bot

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

```bash
python manage.py migrate
```

### 3. Run the Application

```bash
python manage.py runserver
```

### 4. Access the Web Interface

Open your browser and navigate to: http://localhost:8000

### 5. Setup Telegram Bot

Follow the on-screen setup instructions:
1. Create a bot via @BotFather on Telegram
2. Get your Chat ID from the Telegram Bot API
3. Configure the bot in the web interface

### 6. Start the Watcher (Optional)

For automatic backups, run the watcher in a separate terminal:

```bash
python manage.py start_watcher
```

By default, it watches `~/Desktop/SmartBackupWatch` folder. You can customize this with:

```bash
python manage.py start_watcher --watch-folder /path/to/your/folder
```

## API Endpoints

The application provides REST API endpoints:

- `POST /api/backup/` - Create a new backup
- `GET /api/backups/` - List all backups
- `POST /api/restore/<id>/` - Restore a backup
- `DELETE /api/backups/<id>/` - Delete backup record
- `GET /api/config/` - Get configuration status
- `POST /api/config/save/` - Save configuration
- `POST /api/config/test/` - Test Telegram connection

## Project Structure

```
smart-bakcup/
├── core/                 # Django project
│   ├── settings.py       # Django configuration
│   └── urls.py          # URL routing
├── backup_app/          # Django app
│   ├── models.py        # BackupRecord model
│   ├── views.py         # API views
│   ├── urls.py          # App URLs
│   └── management/
│       └── commands/
│           └── start_watcher.py  # Watcher command
├── templates/           # HTML templates
│   └── index.html      # Main web interface
├── config.py           # Configuration (MAX_SIZE fixed at 19MB)
├── zipper.py           # ZIP creation
├── splitter.py         # File splitting
├── merger.py           # File merging
├── telegram_uploader.py # Telegram upload
├── telegram_downloader.py # Telegram download
├── metadata.py         # Legacy metadata (replaced by Django model)
└── requirements.txt    # Python dependencies
```

## Important Notes

### File Size Limits

- **MAX_SIZE is set to 19MB** (not 45MB) to ensure compatibility with Telegram's download limits
- Telegram bots can upload up to 50MB, but `getFile` API only supports files up to 20MB
- Files larger than 19MB are automatically split into chunks

### Security

- Store your `.env` file securely and never commit it to version control
- The application runs locally by default - configure `ALLOWED_HOSTS` for production use

### Watch Folder

- The watcher uses a 3-second debounce to avoid triggering backups during file copying
- Only newly added items are backed up, not the entire watch folder
- Watcher activity is logged to the console

## Troubleshooting

### Common Issues

1. **Bot Token Invalid**: Double-check your bot token from @BotFather
2. **Chat ID Not Found**: Ensure you've started a chat with your bot and get the correct Chat ID
3. **Upload Fails**: Check that your bot has permission to send documents
4. **Watcher Not Working**: Ensure the watch folder exists and is writable

### Logs

- Django logs are displayed in the console
- Watcher logs are shown when running the watcher command
- Backup progress is logged during operations

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Superuser

```bash
python manage.py createsuperuser
```

Access admin interface at: http://localhost:8000/admin/

## License

This project is for personal use. Please ensure you comply with Telegram's terms of service when using their API.

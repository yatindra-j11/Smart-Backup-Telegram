import os
import time
import threading
import uuid
from django.core.management.base import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
from backup_app.models import BackupRecord
from backup_app.views import background_backup_task
from datetime import datetime


# Global dictionary to track background tasks (shared with views.py)
background_tasks = {}


class BackupEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.debounce_timer = None
        self.pending_item = None
        
    def on_created(self, event):
        if event.is_directory:
            self.handle_new_item(event.src_path, is_directory=True)
        else:
            self.handle_new_item(event.src_path, is_directory=False)
    
    def handle_new_item(self, path, is_directory):
        # Cancel previous timer if exists
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        # Set new timer for 3 seconds
        self.pending_item = (path, is_directory)
        self.debounce_timer = threading.Timer(3.0, self.process_backup, args=[path, is_directory])
        self.debounce_timer.start()
    
    def process_backup(self, path, is_directory):
        try:
            print(f"[WATCHER] Processing new item: {path}")
            
            # Create display name
            name = os.path.basename(path.rstrip('/\\'))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            display_name = f"Auto: {name} - {timestamp}"
            
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Create backup record with pending status
            record = BackupRecord.objects.create(
                display_name=display_name,
                task_id=task_id,
                status='pending'
            )
            
            # Start background task using the same function as manual flow
            thread = threading.Thread(
                target=background_backup_task,
                args=(task_id, path, display_name)
            )
            thread.daemon = True
            thread.start()
            
            # Add to global tasks
            background_tasks[task_id] = thread
            
            print(f"[WATCHER] Started background backup: {display_name} (task_id: {task_id})")
            
        except Exception as e:
            print(f"[WATCHER] Failed to start backup: {str(e)}")


class Command(BaseCommand):
    help = 'Start file system watcher for automatic backups'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--watch-folder',
            type=str,
            default=os.path.expanduser("~/Desktop/SmartBackupWatch"),
            help='Folder to watch for new files/directories'
        )
    
    def handle(self, *args, **options):
        watch_folder = options['watch_folder']
        
        # Create watch folder if it doesn't exist
        os.makedirs(watch_folder, exist_ok=True)
        
        self.stdout.write(f"📁 Watching folder: {watch_folder}")
        self.stdout.write("🔍 Waiting for new files/folders...")
        self.stdout.write("Press Ctrl+C to stop")
        
        event_handler = BackupEventHandler()
        observer = Observer()
        observer.schedule(event_handler, watch_folder, recursive=False)
        
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.stdout.write("\n🛑 Watcher stopped")
        
        observer.join()

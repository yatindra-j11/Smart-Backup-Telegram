import os
import threading
from django.apps import AppConfig


class BackupAppConfig(AppConfig):
    name = 'backup_app'
    verbose_name = 'SmartBackup'
    
    def ready(self):
        """Auto-start the file system watcher when Django starts"""
        # Only start watcher in production mode, not during migrations
        if os.environ.get('RUN_MAIN') == 'true':
            self.start_watcher()
    
    def start_watcher(self):
        """Start the file system watcher in a background thread"""
        try:
            from watchdog.observers import Observer
            from .management.commands.start_watcher import BackupEventHandler
            
            # Get the watch folder path
            watch_folder = os.path.expanduser("~/Desktop/SmartBackupWatch")
            watch_folder = os.path.abspath(watch_folder)
            
            # Create watch folder if it doesn't exist
            os.makedirs(watch_folder, exist_ok=True)
            
            # Start the observer
            event_handler = BackupEventHandler()
            observer = Observer()
            observer.schedule(event_handler, watch_folder, recursive=False)
            
            # Start in a daemon thread so it doesn't block Django shutdown
            def start_observer():
                observer.start()
                try:
                    while True:
                        import time
                        time.sleep(1)
                except:
                    observer.stop()
            
            thread = threading.Thread(target=start_observer, daemon=True)
            thread.start()
            
            print(f"SmartBackup watcher started for: {watch_folder}")
            
        except Exception as e:
            print(f"Failed to start SmartBackup watcher: {e}")

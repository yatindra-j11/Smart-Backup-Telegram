import os

def create_watch_folder():
    """Create the watch folder on startup with proper Windows path resolution"""
    try:
        # Get the proper Desktop path
        import os
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        watch_folder = os.path.join(desktop_path, "SmartBackupWatch")
        
        # Convert to absolute path
        watch_folder = os.path.abspath(watch_folder)
        
        # Create folder if it doesn't exist
        os.makedirs(watch_folder, exist_ok=True)
        
        print(f"Watch folder created/verified: {watch_folder}")
        return watch_folder
        
    except Exception as e:
        print(f"Error creating watch folder: {e}")
        return None

# Create watch folder when Django starts
watch_folder_path = create_watch_folder()
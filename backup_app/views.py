import json
import os
import uuid
import threading
import time
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import BackupRecord
from zipper import create_zip
from splitter import split_file
from telegram_uploader import upload_multiple
from telegram_downloader import download_multiple
from merger import merge_files
import zipfile
import tempfile
import shutil
from config import BOT_TOKEN, CHAT_ID

# Global dictionary to track background tasks
background_tasks = {}

def background_backup_task(task_id, folder_path, display_name):
    """Background thread function for backup operations"""
    try:
        # Get the backup record
        backup = BackupRecord.objects.get(task_id=task_id)
        
        # Update status to running
        backup.status = 'running'
        backup.save()
        
        print(f"[{task_id}] [1] Creating ZIP...")
        zip_path = create_zip(folder_path)
        
        size = os.path.getsize(zip_path)
        
        print(f"[{task_id}] [2] Splitting if needed...")
        parts = split_file(zip_path)
        
        # Update progress total
        backup.progress_total = len(parts)
        backup.progress_current = 0
        backup.save()
        
        print(f"[{task_id}] [3] Uploading {len(parts)} part(s)...")
        
        # Custom upload with progress tracking
        file_ids = []
        for i, part in enumerate(parts):
            try:
                from telegram_uploader import upload_single
                file_id = upload_single(part)
                file_ids.append(file_id)
                
                # Update progress
                backup.progress_current = i + 1
                backup.save()
                
                print(f"[{task_id}] Uploaded part {i + 1}/{len(parts)}")
                
            except Exception as e:
                print(f"[{task_id}] Failed to upload part {i + 1}: {str(e)}")
                raise
        
        # Clean up parts
        for part in parts:
            if part != zip_path:  # Don't delete the original zip
                os.remove(part)
        
        # Update backup record with success
        backup.file_ids = file_ids
        backup.file_name = os.path.basename(zip_path)
        backup.size_bytes = size
        backup.parts_count = len(file_ids)
        backup.status = 'completed'
        backup.save()
        
        # Clean up the task from global dict
        if task_id in background_tasks:
            del background_tasks[task_id]
            
        print(f"[{task_id}] Backup completed successfully!")
        
    except Exception as e:
        print(f"[{task_id}] Backup failed: {str(e)}")
        
        # Update backup record with error
        try:
            backup = BackupRecord.objects.get(task_id=task_id)
            backup.status = 'failed'
            backup.error_message = str(e)
            backup.save()
        except:
            pass
        
        # Clean up the task from global dict
        if task_id in background_tasks:
            del background_tasks[task_id]


@csrf_exempt
@require_http_methods(["POST"])
def create_backup(request):
    try:
        data = json.loads(request.body)
        folder_path = data.get('folder_path')
        custom_name = data.get('custom_name')
        
        if not folder_path or not os.path.exists(folder_path):
            return JsonResponse({'error': 'Invalid folder path'}, status=400)
        
        # Create display name
        folder_name = os.path.basename(folder_path.rstrip('/\\'))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        display_name = custom_name or f"{folder_name} - {timestamp}"
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create backup record with pending status
        record = BackupRecord.objects.create(
            display_name=display_name,
            task_id=task_id,
            status='pending'
        )
        
        # Start background task
        thread = threading.Thread(
            target=background_backup_task,
            args=(task_id, folder_path, display_name)
        )
        thread.daemon = True
        thread.start()
        
        # Add to global tasks
        background_tasks[task_id] = thread
        
        return JsonResponse({
            'task_id': task_id,
            'id': record.id,
            'display_name': record.display_name,
            'status': 'pending'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def backup_status(request, task_id):
    try:
        backup = BackupRecord.objects.get(task_id=task_id)
        
        response_data = {
            'status': backup.status,
            'progress': f"{backup.progress_current} of {backup.progress_total} parts uploaded"
        }
        
        if backup.status == 'failed':
            response_data['error'] = backup.error_message
        
        return JsonResponse(response_data)
        
    except BackupRecord.DoesNotExist:
        return JsonResponse({'error': 'Backup not found'}, status=404)


@require_http_methods(["GET"])
def list_backups(request):
    backups = BackupRecord.objects.all()
    data = []
    for backup in backups:
        data.append({
            'id': backup.id,
            'display_name': backup.display_name,
            'file_name': backup.file_name,
            'backup_date': backup.backup_date.isoformat(),
            'size_bytes': backup.size_bytes,
            'parts_count': backup.parts_count,
            'status': backup.status,
            'progress_current': backup.progress_current,
            'progress_total': backup.progress_total,
            'task_id': backup.task_id,
            'error_message': backup.error_message
        })
    return JsonResponse({'backups': data})


@csrf_exempt
@require_http_methods(["POST"])
def restore_backup(request, backup_id):
    try:
        backup = BackupRecord.objects.get(id=backup_id)
        
        # Check if backup is completed
        if backup.status != 'completed':
            return JsonResponse({'error': 'Cannot restore incomplete backup'}, status=400)
        
        print(f"[1] Downloading {backup.parts_count} part(s)...")
        parts = download_multiple(backup.file_ids)
        
        print("[2] Merging parts...")
        merged_path = merge_files(parts, backup.file_name)
        
        print("[3] Extracting...")
        extract_path = f"restored_files_{backup.id}"
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(merged_path, 'r') as zipf:
            zipf.extractall(extract_path)
        
        # Clean up
        os.remove(merged_path)
        for part in parts:
            os.remove(part)
        
        return JsonResponse({
            'message': 'Backup restored successfully',
            'extract_path': extract_path
        })
        
    except BackupRecord.DoesNotExist:
        return JsonResponse({'error': 'Backup not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
def delete_backup(request, backup_id):
    try:
        backup = BackupRecord.objects.get(id=backup_id)
        backup.delete()
        return JsonResponse({'message': 'Backup record deleted'})
    except BackupRecord.DoesNotExist:
        return JsonResponse({'error': 'Backup not found'}, status=404)


@require_http_methods(["GET"])
def get_config(request):
    return JsonResponse({
        'configured': bool(BOT_TOKEN and CHAT_ID),
        'bot_token': bool(BOT_TOKEN),
        'chat_id': bool(CHAT_ID)
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_config(request):
    try:
        data = json.loads(request.body)
        bot_token = data.get('bot_token')
        chat_id = data.get('chat_id')
        
        # Update .env file
        env_path = '.env'
        env_lines = []
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add tokens
        updated_lines = []
        token_found = False
        chat_found = False
        
        for line in env_lines:
            if line.startswith('BOT_TOKEN='):
                updated_lines.append(f'BOT_TOKEN={bot_token}\n')
                token_found = True
            elif line.startswith('CHAT_ID='):
                updated_lines.append(f'CHAT_ID={chat_id}\n')
                chat_found = True
            else:
                updated_lines.append(line)
        
        if not token_found:
            updated_lines.append(f'BOT_TOKEN={bot_token}\n')
        if not chat_found:
            updated_lines.append(f'CHAT_ID={chat_id}\n')
        
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        return JsonResponse({'message': 'Configuration saved successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_connection(request):
    try:
        import requests
        data = json.loads(request.body)
        bot_token = data.get('bot_token')
        chat_id = data.get('chat_id')
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': 'SmartBackup connection test successful!'
        })
        
        if response.status_code == 200:
            return JsonResponse({'message': 'Connection test successful'})
        else:
            return JsonResponse({'error': 'Connection test failed'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def open_watch_folder(request):
    try:
        import os
        # Get the watch folder path
        watch_folder = os.path.expanduser("~/Desktop/SmartBackupWatch")
        watch_folder = os.path.abspath(watch_folder)
        
        # Create folder if it doesn't exist
        os.makedirs(watch_folder, exist_ok=True)
        
        # Open folder in Windows Explorer
        os.startfile(watch_folder)
        
        return JsonResponse({'message': f'Opened folder: {watch_folder}'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

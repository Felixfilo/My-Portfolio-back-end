import os
from supabase import create_client, Client
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'portfolio-media')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_to_supabase(file, folder):
    """Upload file to Supabase storage and return public URL"""
    try:
        if not file or not file.filename:
            print("No file provided")
            return None
            
        # Secure the filename and add UUID to prevent conflicts
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{folder}/{unique_filename}"
        
        print(f"Uploading file: {file_path}")
        
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Upload to Supabase
        response = supabase.storage.from_(BUCKET_NAME).upload(
            file_path,
            file_content,
            file_options={
                "content-type": file.content_type or "application/octet-stream",
                "upsert": "true"
            }
        )
        
        print(f"Upload response: {response}")
        
        # Check for errors in response
        if hasattr(response, 'error') and response.error:
            print(f"Upload error: {response.error}")
            return None
            
        # Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        
        if public_url:
            # Clean up any trailing characters
            public_url = public_url.rstrip('?')
            print(f"File uploaded successfully: {public_url}")
            return public_url
        else:
            print("Failed to get public URL")
            return None
            
    except Exception as e:
        print(f"Error uploading file to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return None

def delete_file_from_supabase(file_url):
    """Delete file from Supabase storage"""
    try:
        if not file_url:
            return False
            
        # Check if it's a Supabase URL
        if 'supabase.co' not in file_url:
            print(f"Not a Supabase URL: {file_url}")
            return False
            
        # Clean URL of any trailing characters
        clean_url = file_url.rstrip('?')
        
        # Extract file path from URL
        # URL format: https://project.supabase.co/storage/v1/object/public/bucket/folder/file.ext
        try:
            url_parts = clean_url.split(f'/storage/v1/object/public/{BUCKET_NAME}/')
            if len(url_parts) < 2:
                print(f"Invalid URL format: {clean_url}")
                return False
                
            file_path = url_parts[1]
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return False
        
        print(f"Deleting file: {file_path}")
        
        # Delete from Supabase
        response = supabase.storage.from_(BUCKET_NAME).remove([file_path])
        
        print(f"Delete response: {response}")
        
        if hasattr(response, 'error') and response.error:
            print(f"Delete error: {response.error}")
            return False
            
        print(f"File deleted successfully: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error deleting file from Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supabase_connection():
    """Test Supabase connection"""
    try:
        # Test storage connection
        buckets = supabase.storage.list_buckets()
        print(f"Available buckets: {buckets}")
        
        # Check if our bucket exists
        bucket_exists = any(bucket.name == BUCKET_NAME for bucket in buckets)
        print(f"Bucket '{BUCKET_NAME}' exists: {bucket_exists}")
        
        return bucket_exists
        
    except Exception as e:
        print(f"Error testing Supabase connection: {e}")
        return False
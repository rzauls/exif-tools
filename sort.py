import os
import shutil
import datetime
from PIL import Image, UnidentifiedImageError
import piexif
import hachoir.parser
import hachoir.metadata

def get_image_date_taken(file_path):
    """Extract date taken from image EXIF data."""
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None
            
        # EXIF tag for DateTimeOriginal is 36867
        date_taken = exif_data.get(36867)
        
        if not date_taken:
            # Try alternate tags
            date_taken = exif_data.get(306)  # DateTime
            if not date_taken:
                return None
                
        # Convert the date string to datetime object
        try:
            # Format: "YYYY:MM:DD HH:MM:SS"
            dt = datetime.datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            return dt
        except (ValueError, TypeError):
            return None
            
    except (UnidentifiedImageError, AttributeError, KeyError, OSError):
        # Try using piexif for non-standard image formats
        try:
            exif_dict = piexif.load(file_path)
            exif = exif_dict.get('Exif', {})
            
            # Check for DateTimeOriginal (36867) or DateTime (306)
            date_taken = None
            if 36867 in exif:
                date_taken = exif[36867].decode('utf-8')
            elif 306 in exif_dict.get('0th', {}):
                date_taken = exif_dict['0th'][306].decode('utf-8')
                
            if date_taken:
                return datetime.datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            return None
            
        except Exception:
            return None

def get_video_date_taken(file_path):
    """Extract date taken from video metadata."""
    try:
        parser = hachoir.parser.createParser(file_path)
        if not parser:
            return None
            
        metadata = hachoir.metadata.extractMetadata(parser)
        if not metadata:
            return None
            
        # Try different metadata fields for creation date
        for date_field in ['creation_date', 'date_time_original', 'datetime_original']:
            if hasattr(metadata, date_field):
                date_value = getattr(metadata, date_field)
                if isinstance(date_value, datetime.datetime):
                    return date_value
                    
        return None
        
    except Exception:
        return None

def get_media_date_taken(file_path):
    """Determine if file is image or video and extract date taken."""
    lower_path = file_path.lower()
    
    # Image file extensions
    if any(lower_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']):
        return get_image_date_taken(file_path)
        
    # Video file extensions
    elif any(lower_path.endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm']):
        return get_video_date_taken(file_path)
        
    return None

def format_filename(dt):
    """Format datetime to a filename-friendly string."""
    return dt.strftime("%Y%m%d_%H%M%S")

def process_directory(source_dir, target_subdir="dated_media"):
    """Process all media files in source directory."""
    # Create target subdirectory if it doesn't exist
    target_dir = os.path.join(source_dir, target_subdir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    # Statistics
    files_processed = 0
    files_moved = 0
    files_without_date = 0
    
    # Process each file in the directory
    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        
        # Skip directories and the target subdirectory
        if os.path.isdir(source_path) or filename == target_subdir:
            continue
            
        files_processed += 1
        print(f"Processing {filename}...")
        
        # Extract date taken
        date_taken = get_media_date_taken(source_path)
        
        if date_taken:
            # Get file extension
            _, ext = os.path.splitext(filename)
            
            # Create new filename based on date taken
            new_filename = format_filename(date_taken) + ext.lower()
            target_path = os.path.join(target_dir, new_filename)
            
            # Handle filename conflicts
            counter = 1
            while os.path.exists(target_path):
                new_filename = f"{format_filename(date_taken)}_{counter}{ext.lower()}"
                target_path = os.path.join(target_dir, new_filename)
                counter += 1
                
            # Move and rename the file
            shutil.move(source_path, target_path)
            print(f"Moved {filename} to {new_filename}")
            files_moved += 1
        else:
            print(f"No date taken found for {filename}, leaving in place")
            files_without_date += 1
    
    # Print summary
    print("\nSummary:")
    print(f"Total files processed: {files_processed}")
    print(f"Files moved and renamed: {files_moved}")
    print(f"Files without date metadata: {files_without_date}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        source_directory = sys.argv[1]
        target_subdirectory = sys.argv[2] if len(sys.argv) > 2 else "dated_media"
        process_directory(source_directory, target_subdirectory)
    else:
        print("Usage: python script.py <source_directory> [target_subdirectory]")
        print("Example: python script.py ./my_photos dated_photos")

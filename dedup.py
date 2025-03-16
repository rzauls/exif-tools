import os
import sys

def remove_duplicate_mov_files(directory):
    """
    Remove .MOV files if an image with the same base name exists in the directory.
    
    Args:
        directory (str): Path to the directory to process
    
    Returns:
        tuple: (removed_count, skipped_count)
    """
    # Define common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic']
    
    # Get all files in the directory
    all_files = os.listdir(directory)
    
    # Create a dictionary to store base names of image files
    image_base_names = set()
    
    # First pass: collect all image base names
    for filename in all_files:
        file_path = os.path.join(directory, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Get file extension in lowercase
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # If it's an image file, add its base name to the set
        if ext in image_extensions:
            base_name = os.path.splitext(filename)[0]
            image_base_names.add(base_name)
    
    # Second pass: remove .MOV files with matching base names
    removed_count = 0
    skipped_count = 0
    
    for filename in all_files:
        file_path = os.path.join(directory, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Get file extension in lowercase
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # If it's a .MOV file, check if there's a matching image
        if ext == '.mov':
            base_name = os.path.splitext(filename)[0]
            
            if base_name in image_base_names:
                try:
                    # Remove the .MOV file
                    os.remove(file_path)
                    print(f"Removed: {filename}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {filename}: {str(e)}")
                    skipped_count += 1
            else:
                print(f"Kept: {filename} (no matching image found)")
                skipped_count += 1
    
    return removed_count, skipped_count

def main():
    if len(sys.argv) != 2:
        print("Usage: python remove_duplicate_mov.py <directory>")
        print("Example: python remove_duplicate_mov.py ./my_photos")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Processing directory: {directory}")
    print("This script will remove .MOV files if an image with the same base name exists.")
    confirmation = input("Continue? (y/n): ")
    
    if confirmation.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    removed, skipped = remove_duplicate_mov_files(directory)
    
    print("\nSummary:")
    print(f"Total .MOV files removed: {removed}")
    print(f"Total .MOV files kept: {skipped}")

if __name__ == "__main__":
    main()

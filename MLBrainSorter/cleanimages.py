import os
from PIL import Image

# Define directories to scan
directories = [
    "./MLBrainSorter/brain_mri_data/train/good",
    "./MLBrainSorter/brain_mri_data/train/bad",
    "./MLBrainSorter/brain_mri_data/test/good",
    "./MLBrainSorter/brain_mri_data/test/bad"
]

def verify_and_fix_images():
    for dir_path in directories:
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            
            # Rename .JPG to .jpg for consistency
            if filename.endswith('.JPG'):
                new_file_path = os.path.join(dir_path, filename.lower())
                os.rename(file_path, new_file_path)
                file_path = new_file_path
            
            # Verify if the file is a valid image
            try:
                with Image.open(file_path) as img:
                    img.verify()  # Verify that it is an image
            except (IOError, SyntaxError) as e:
                print(f"Removing corrupted or invalid image file: {file_path}")
                os.remove(file_path)  # Remove invalid files

verify_and_fix_images()
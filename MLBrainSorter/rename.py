import os

# Define the paths to the train and test directories
base_dir = "./MLBrainSorter/brain_mri_data"
folders = ["train/good", "train/bad", "test/good", "test/bad"]

def remove_spaces_in_filenames(base_path, folders):
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        for filename in os.listdir(folder_path):
            # Skip if already renamed
            if " " not in filename:
                continue

            # Define old and new file paths
            old_file_path = os.path.join(folder_path, filename)
            new_filename = filename.replace(" ", "")
            new_file_path = os.path.join(folder_path, new_filename)

            # Rename file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed '{filename}' to '{new_filename}'")

# Execute the function
remove_spaces_in_filenames(base_dir, folders)
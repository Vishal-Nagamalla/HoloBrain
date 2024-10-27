import os
import shutil
import torch
from torchvision import transforms
from PIL import Image
from model import BrainScanCNN

# Load model and set to eval mode
model = BrainScanCNN()
model.load_state_dict(torch.load("brain_model.pth", weights_only=True))
model.eval()

# Define transformation for input images
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

def classify_and_sort(input_folder, output_folder_good, output_folder_bad):
    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        
        # Skip non-image files like .DS_Store
        if not img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            print(f"Skipping non-image file: {img_file}")
            continue

        img = Image.open(img_path).convert("RGB")
        img = transform(img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(img)
            _, predicted = torch.max(outputs, 1)
            label = "bad" if predicted.item() == 0 else "good"

        target_folder = output_folder_good if label == "good" else output_folder_bad
        shutil.move(img_path, os.path.join(target_folder, img_file))

# Run the classification and sorting
classify_and_sort("./MLBrainSorter/new_mri_scans", "./MLBrainSorter/sorted_mri/good", "./MLBrainSorter/sorted_mri/bad")
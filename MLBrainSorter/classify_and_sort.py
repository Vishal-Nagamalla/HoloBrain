import shutil
import torch
from torchvision import transforms
from PIL import Image
from model import BrainScanCNN

# Load model and set to eval mode
model = BrainScanCNN()
model.load_state_dict(torch.load("brain_model.pth"))
model.eval()

# Define transformation for input images
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

def classify_and_sort(input_folder, output_folder_good, output_folder_bad):
    for img_file in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_file)
        img = Image.open(img_path)
        img = transform(img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(img)
            _, predicted = torch.max(outputs, 1)
            label = "good" if predicted.item() == 0 else "bad"

        target_folder = output_folder_good if label == "good" else output_folder_bad
        shutil.move(img_path, os.path.join(target_folder, img_file))
import os
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Define transformation pipeline for training and testing
data_transforms = {
    "train": transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.RandomRotation(15),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ]),
    "test": transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ]),
}

def load_data(data_dir, batch_size=32):
    image_datasets = {
        x: datasets.ImageFolder(
            os.path.join(data_dir, x), data_transforms[x]
        )
        for x in ["train", "test"]
    }
    dataloaders = {
        x: DataLoader(image_datasets[x], batch_size=batch_size, shuffle=True)
        for x in ["train", "test"]
    }
    return dataloaders
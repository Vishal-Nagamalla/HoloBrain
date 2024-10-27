import os
import torch
import torch.optim as optim
import torch.nn as nn
from tqdm import tqdm
from model import BrainScanCNN
from data_loader import load_data

# Set directory paths
data_dir = "./MLBrainSorter/brain_mri_data"
save_model_path = "brain_model.pth"  # Path to save the trained model

# Load data with augmentations
dataloaders = load_data(data_dir, batch_size=32)

# Initialize model, loss function, and optimizer
model = BrainScanCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)  # Lower learning rate for stability

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Training function
def train_model(model, dataloaders, criterion, optimizer, num_epochs=200):  # Set to 100 epochs
    best_accuracy = 0.0  # Track the best accuracy to save the best model

    for epoch in range(num_epochs):
        print(f"Epoch {epoch+1}/{num_epochs}")
        
        # Track training and test metrics separately
        for phase in ["train", "test"]:
            if phase == "train":
                model.train()
            else:
                model.eval()
            
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in tqdm(dataloaders[phase]):
                inputs, labels = inputs.to(device), labels.to(device)

                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # Only backpropagate if in training phase
                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                # Track loss and accuracy
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)
            print(f"{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

            # Save model if this epoch's test accuracy is the best
            if phase == "test" and epoch_acc > best_accuracy:
                best_accuracy = epoch_acc
                torch.save(model.state_dict(), save_model_path)
                print("Best model saved with accuracy: {:.4f}".format(best_accuracy))

    print("Training complete. Best test accuracy: {:.4f}".format(best_accuracy))

# Option to load a previously trained model for evaluation
def evaluate_model(model, dataloaders):
    model.load_state_dict(torch.load(save_model_path))
    model.eval()
    running_corrects = 0

    with torch.no_grad():
        for inputs, labels in tqdm(dataloaders["test"]):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            running_corrects += torch.sum(preds == labels.data)

    accuracy = running_corrects.double() / len(dataloaders["test"].dataset)
    print(f"Test Accuracy: {accuracy:.4f}")

# Choose to either train or evaluate
if __name__ == "__main__":
    train = True  # Set to False if you only want to evaluate a saved model

    if train:
        train_model(model, dataloaders, criterion, optimizer, num_epochs=200)
    else:
        evaluate_model(model, dataloaders)
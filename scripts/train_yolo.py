import os
from ultralytics import YOLO

def train():
    # Load a pre-trained YOLOv8 model
    model = YOLO("yolov8n.pt")
    
    # Dataset config
    dataset_yaml = os.path.abspath("data/logo_dataset/data.yaml")
    
    # Train the model
    # We use epochs=1 for demonstration purposes due to CPU constraints.
    # In production, increase this to 50-100 epochs.
    print(f"Training YOLOv8 on {dataset_yaml}...")
    results = model.train(
        data=dataset_yaml,
        epochs=1,
        imgsz=640,
        batch=8,
        device="cpu",
        project="ml/models",
        name="logo_detection"
    )
    print("Training complete! Weights saved in ml/models/logo_detection/weights/best.pt")

if __name__ == "__main__":
    train()

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.config import settings
from server.extractors.image_extractor import ImageExtractor

def verify():
    print(f"Using YOLO model at: {settings.YOLO_MODEL_PATH}")
    
    # Initialize the extractor
    extractor = ImageExtractor(
        enable_logo_redaction=True,
        enable_ocr=False,  # We just want to test logo redaction
        yolo_model_path=settings.YOLO_MODEL_PATH
    )
    
    # Pick a test image
    test_image_path = "data/logo_dataset/test/images/03042025-zurich-switzerland-skoda-car-600nw-2608640939_jpg.rf.42ee747d2a76e15ec9bb23f9f51f4c79.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Error: test image {test_image_path} not found.")
        return
        
    print(f"Processing image: {test_image_path}")
    
    # Extract
    result = extractor.extract(test_image_path)
    
    # Check logo detections
    detections = result.get("logo_detections", [])
    print(f"Found {len(detections)} logos!")
    for d in detections:
        print(f" - {d.get('template')} (confidence: {d.get('score'):.2f}, bbox: {d.get('bbox')})")
        
    # Check if redacted image was generated
    if result.get("redacted_image_base64"):
        print("Redacted image was successfully generated in base64!")
        
    print("Verification complete.")

if __name__ == "__main__":
    verify()

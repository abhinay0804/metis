---
license: apache-2.0
task_categories:
- object-detection
language:
- en
tags:
- computer-vision
- object-detection
- yolo
- brand-detection
- logo-detection
- car-brands
size_categories:
- 1K<n<10K
---
# 🚗 Brand Eye Dataset - Automotive Brand Detection

A comprehensive dataset for automotive brand/logo detection and recognition, formatted for YOLO training. This dataset contains high-quality images with precise annotations for 33 different automotive brands.

## 📊 Dataset Overview

This dataset is specifically designed for object detection tasks focusing on automotive brand recognition in various contexts including vehicles, logos, and brand emblems.

### 📈 Dataset Statistics

- **Total Images**: 1,404
- **Total Annotations**: 1,452
- **Number of Classes**: 33 automotive brands
- **Image Format**: JPG
- **Annotation Format**: YOLO v8 (.txt files)
- **Split Ratio**: Train 75.4% | Valid 15.2% | Test 9.3%

### 📂 Directory Structure

```
brand-eye-dataset/
├── train/
│   ├── images/          # 1,059 training images
│   └── labels/          # 1,059 training annotations (.txt)
├── valid/
│   ├── images/          # 214 validation images  
│   └── labels/          # 214 validation annotations (.txt)
├── test/
│   ├── images/          # 131 test images
│   └── labels/          # 131 test annotations (.txt)
├── data.yaml           # Dataset configuration
└── README.md           # This file
```

## 🚗 Automotive Brands (Classes)

The dataset includes the following 33 automotive brands:

```yaml
0: audi          1: bmw           2: byd           3: cherry
4: chevrolet     5: citroen       6: cupra         7: dacia
8: fiat          9: ford          10: honda        11: hyundai
12: kia          13: landrover    14: mazda        15: mercedes
16: mg           17: mini         18: mitsubishi   19: nissan
20: opel         21: pegout       22: porsche      23: rangerover
24: renault      25: seat         26: skoda        27: suzuki
28: tesla        29: togg         30: toyota       31: volvo
32: wolksvogen
```

## 📋 YOLO Annotation Format

Each image has a corresponding `.txt` file with the same name containing bounding box annotations:

```
class_id center_x center_y width height
```

Where:
- `class_id`: Integer class identifier (0-32)
- `center_x`, `center_y`: Normalized center coordinates (0.0-1.0)  
- `width`, `height`: Normalized width and height (0.0-1.0)

**Example annotation:**
```
15 0.5 0.3 0.2 0.4    # Mercedes logo at center-left
26 0.7 0.8 0.15 0.25  # Skoda emblem at bottom-right
```

## 🚀 Quick Start

### Loading with Ultralytics

```python
from ultralytics import YOLO

# Train a model
model = YOLO('yolov8n.pt')
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```

### Loading with Custom Code

```python
import os
import cv2
import yaml

def load_dataset_info(data_yaml_path):
    with open(data_yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data

def load_image_and_labels(img_path, label_path):
    # Load image
    image = cv2.imread(img_path)

    # Load labels
    labels = []
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                labels.append(list(map(float, line.strip().split())))

    return image, labels

# Example usage
data_info = load_dataset_info('data.yaml')
print(f"Classes: {data_info['names']}")
```

### Visualization Example

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2

def visualize_annotations(img_path, label_path, class_names):
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w = image.shape[:2]

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(image)

    # Read annotations
    with open(label_path, 'r') as f:
        for line in f:
            class_id, cx, cy, width, height = map(float, line.strip().split())

            # Convert to pixel coordinates
            x = (cx - width/2) * w
            y = (cy - height/2) * h
            w_box = width * w
            h_box = height * h

            # Create rectangle
            rect = patches.Rectangle((x, y), w_box, h_box, 
                                   linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect)

            # Add label
            brand_name = class_names[int(class_id)]
            ax.text(x, y-10, brand_name, 
                   color='red', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

    plt.axis('off')
    plt.tight_layout()
    plt.show()

# Example usage
class_names = ['audi', 'bmw', 'byd', 'cherry', 'chevrolet', 'citroen', 'cupra', 'dacia',
               'fiat', 'ford', 'honda', 'hyundai', 'kia', 'landrover', 'mazda', 'mercedes',
               'mg', 'mini', 'mitsubishi', 'nissan', 'opel', 'pegout', 'porsche', 'rangerover',
               'renault', 'seat', 'skoda', 'suzuki', 'tesla', 'togg', 'toyota', 'volvo', 'wolksvogen']

# visualize_annotations('train/images/sample.jpg', 'train/labels/sample.txt', class_names)
```

## 📊 Dataset Quality & Statistics

### Split Distribution
- **Training Set**: 1,059 images (75.4%)
- **Validation Set**: 214 images (15.2%) 
- **Test Set**: 131 images (9.3%)

### Class Distribution
Balanced representation across all 33 automotive brands with varying annotation density based on brand prevalence in real-world scenarios.

## 🎯 Use Cases

- **Automotive Brand Recognition**: Identify car brands from images
- **Dealership Management**: Automated inventory cataloging
- **Market Research**: Brand presence analysis in automotive industry
- **Traffic Analysis**: Vehicle brand distribution studies
- **Insurance Applications**: Automated vehicle brand identification
- **Parking Management**: Brand-specific parking solutions

## 🏆 Model Training Results

This dataset was used to train the [Brand Eye YOLO model](https://huggingface.co/haydarkadioglu/brand-eye) with excellent results:

- **mAP@0.5**: 0.808 (Final epoch)
- **mAP@0.5:0.95**: 0.473 (Final epoch)
- **Training Epochs**: 50
- **Best Performance**: Available in model repository
- **Model Size**: ~14MB (optimized for deployment)

## 🔧 Data Preparation & Validation

### Quality Assurance

```python
def validate_dataset(images_dir, labels_dir):
    issues = []

    for img_file in os.listdir(images_dir):
        if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            label_file = img_file.rsplit('.', 1)[0] + '.txt'
            label_path = os.path.join(labels_dir, label_file)

            if not os.path.exists(label_path):
                issues.append(f"Missing label: {label_file}")
            else:
                # Check label format
                with open(label_path, 'r') as f:
                    for i, line in enumerate(f):
                        parts = line.strip().split()
                        if len(parts) != 5:
                            issues.append(f"Invalid format in {label_file}:{i+1}")
                        else:
                            try:
                                cls_id, cx, cy, w, h = map(float, parts)
                                if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                                    issues.append(f"Invalid coordinates in {label_file}:{i+1}")
                                if not (0 <= cls_id <= 32):
                                    issues.append(f"Invalid class_id in {label_file}:{i+1}")
                            except ValueError:
                                issues.append(f"Non-numeric values in {label_file}:{i+1}")

    return issues

# Validate dataset
train_issues = validate_dataset('train/images/', 'train/labels/')
print(f"Training set validation: {len(train_issues)} issues found")
```

## 📄 License

This dataset is released under **Apache 2.0 License**.

## 🤝 Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{brand_eye_dataset_2024,
  title={Brand Eye Dataset: Automotive Brand Detection Dataset},
  author={Haydar Kadioğlu},
  year={2024},
  publisher={Hugging Face},
  url={https://huggingface.co/datasets/haydarkadioglu/brand-eye-dataset}
}
```

## 🔗 Related Resources

- **🤖 Trained Model**: [haydarkadioglu/brand-eye-yolo](https://huggingface.co/haydarkadioglu/brand-eye-yolo)
- **📊 Training Analysis**: See `visualize.ipynb` in model repository
- **💻 Code Examples**: Available in model repository
- **🐛 Issues**: Report issues in model repository

## 📞 Contact

- **GitHub**: [haydarkadioglu](https://github.com/haydarkadioglu)
- **Hugging Face**: [haydarkadioglu](https://huggingface.co/haydarkadioglu)
- **Model Repository**: [brand-eye-yolo](https://huggingface.co/haydarkadioglu/brand-eye-yolo)

---

**🎯 Perfect for automotive industry applications, research, and brand recognition tasks!**

*This dataset represents months of careful curation and annotation work, providing high-quality training data for automotive brand detection systems.*
# Dengue Breeding Site Detection System - YOLOv11

This project uses YOLOv11 with Ultralytics to detect breeding sites of Aedes aegypti mosquito, vector of dengue, chikungunya and zika.

## Objective

Automatically detect sites that can serve as breeding grounds for dengue vector mosquitoes:
- Holes or cavities that accumulate water
- Puddles and stagnant water accumulations
- Broken or poorly constructed streets that retain water
- Garbage and waste dumps where water accumulates

## Project Structure

```
Yolov11/
├── main.py                    # Main detection system
├── requirements.txt           # Project dependencies
├── configs/
│   └── dataset.yaml           # Dataset configuration
├── data/
│   ├── images/                # Images organized by dataset split
│   │   ├── train/             # Training images
│   │   ├── val/               # Validation images
│   │   └── test/              # Test images
│   └── labels/                # YOLO format annotations
│       ├── train/
│       ├── val/
│       └── test/
├── models/                    # Trained models (created during training)
├── results/                   # Detection outputs and reports (created during inference)
│   └── reports/               # JSON reports with risk assessment
└── scripts/                   # Utility tools
    ├── prepare_dataset.py     # Dataset preparation and validation
    ├── batch_detection.py     # Batch processing
    └── train_dengue_model.py  # Model training
```

## Installation

```bash
pip install -r requirements.txt
```

## Detection Classes

| ID | Class | Risk Level | Description |
|----|-------|------------|-------------|
| 0 | huecos | High | Holes and cavities that accumulate water |
| 1 | charcos_cumulos_agua | High | Stagnant water and accumulations |
| 2 | calles_rotas_mal_hechas | High | Deteriorated roads that retain water |
| 3 | basura_basurales | Medium | Waste accumulations |

## Usage

### Single Image Detection
```python
from main import detect_breeding_sites

# Detect breeding sites in an image
results, detections = detect_breeding_sites(
    model_path='models/dengue_detection/weights/best.pt',
    source='path/to/image.jpg',
    conf_threshold=0.5
)

# The system automatically generates:
# - Risk assessment (HIGH/MEDIUM/LOW/MINIMAL)
# - Specific recommendations
# - JSON report with details
```

### Model Training
```bash
# Train nano model (fast)
python scripts/train_dengue_model.py --model n --epochs 100

# Train medium model (more accurate)
python scripts/train_dengue_model.py --model m --epochs 150 --batch 8
```

### Batch Processing
```bash
# Process multiple images
python scripts/batch_detection.py --model models/dengue_detection/weights/best.pt --images data/images/test/
```

## Risk Assessment

The system automatically classifies risk level:

- **HIGH**: ≥2 high-risk sites → Immediate intervention
- **MEDIUM**: ≥1 high-risk or ≥2 medium-risk sites → Regular monitoring  
- **LOW**: ≥1 medium-risk site → Preventive maintenance
- **MINIMAL**: No significant sites → Routine surveillance

## Dataset Preparation

```bash
# Organize images and labels
python scripts/prepare_dataset.py --source /path/to/raw/data --target data

# Validate annotations
python scripts/prepare_dataset.py --validate
```

## Annotation Format

Labels follow YOLO format (one .txt file per image):
```
class_id center_x center_y width height
```

Example:
```
0 0.5 0.3 0.2 0.1  # hole in center-top
1 0.8 0.7 0.15 0.1 # puddle in bottom-right corner
```

## Generated Reports

The system generates JSON reports with:
- Detected objects with coordinates and confidence scores
- Automatic risk assessment
- Specific recommendations by risk level
- Timestamps and metadata

## Applications

- **Public Health**: Epidemiological surveillance
- **Municipalities**: Automated urban inspection
- **NGOs**: Community monitoring
- **Research**: Environmental pattern analysis

## Docker Setup

### Build and Run
```bash
# Build and start services
docker-compose up -d

# Access the container
docker-compose exec dengue-detection bash

# Stop services
docker-compose down
```

### Available Services
- **Port 8888**: Jupyter Notebook (if configured)
- **Port 8080**: Main container
- **Port 8081**: LabelStudio for annotations

### Mounted Volumes
- `./data` → `/app/data` (dataset)
- `./models` → `/app/models` (trained models)
- `./results` → `/app/results` (detection outputs)
- `./configs` → `/app/configs` (configurations)
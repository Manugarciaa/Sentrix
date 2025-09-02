# Dataset Structure

## Directory Organization
```
data/
├── images/
│   ├── train/         # Training images (.jpg, .png)
│   ├── val/           # Validation images
│   └── test/          # Test images
├── labels/
│   ├── train/         # Training labels (.txt)
│   ├── val/           # Validation labels
│   └── test/          # Test labels
└── videos/
    ├── raw/           # Original video files (.mp4, .avi)
    ├── processed/     # Processed video outputs
    └── frames/        # Extracted frames for training
```

## Supported Formats
- **Images**: .jpg, .jpeg, .png, .bmp
- **Videos**: .mp4, .avi, .mov, .mkv
- **Labels**: .txt (YOLO format)

## Quick Setup
```bash
# Place your images in appropriate folders
cp your_images/* data/images/train/
cp your_labels/* data/labels/train/

# For videos
cp your_videos/* data/videos/raw/
```
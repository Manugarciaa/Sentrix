"""
Quick test of newly trained model
"""
from ultralytics import YOLO
import glob

# Load the newly trained model
model = YOLO('runs/segment/dengue_test_run/weights/best.pt')

# Find test images
test_imgs = glob.glob('test_images/imagen_test*.jpg')[:2]

if not test_imgs:
    print("No test images found!")
    exit(1)

print(f"Testing model on {len(test_imgs)} images...")
print("-" * 60)

for img_path in test_imgs:
    results = model(img_path, conf=0.5, verbose=False)

    print(f"\nImage: {img_path}")
    print(f"Detections: {len(results[0].boxes)}")

    for i, (box, mask) in enumerate(zip(results[0].boxes, results[0].masks.data if results[0].masks else [])):
        cls_id = int(box.cls)
        cls_name = model.names[cls_id]
        conf = float(box.conf)
        print(f"  {i+1}. {cls_name}: {conf:.3f}")

print("\n" + "=" * 60)
print("Model test SUCCESSFUL!")
print(f"Best model path: runs/segment/dengue_test_run/weights/best.pt")

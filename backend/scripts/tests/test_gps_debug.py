"""
Script to debug GPS coordinate extraction
"""
import sys
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.sentrix_shared.gps_utils import extract_gps_from_exif

def test_gps_extraction(image_path: str):
    """Test GPS extraction from an image"""
    print(f"\n{'='*60}")
    print(f"Testing GPS extraction from: {image_path}")
    print(f"{'='*60}\n")

    result = extract_gps_from_exif(image_path)

    print("GPS Extraction Result:")
    print(f"  Has GPS: {result.get('has_gps')}")
    print(f"  Latitude: {result.get('latitude')}")
    print(f"  Longitude: {result.get('longitude')}")
    print(f"  Altitude: {result.get('altitude')}")
    print(f"  Location Source: {result.get('location_source')}")
    print(f"  Error: {result.get('error')}")

    if result.get('has_gps'):
        lat = result.get('latitude')
        lon = result.get('longitude')
        print(f"\nGoogle Maps URL: https://www.google.com/maps?q={lat},{lon}")

        # Check if coordinates should be in Argentina (Tucumán area)
        if lat is not None and lon is not None:
            if 20 < lat < 30 and 60 < lon < 70:
                print("\n⚠️  WARNING: Coordinates are POSITIVE")
                print(f"    This would place the location in: India/Pakistan")
                print(f"    For Tucumán, Argentina, coordinates should be NEGATIVE:")
                print(f"    Corrected: {-lat}, {-lon}")
                print(f"    Google Maps URL (corrected): https://www.google.com/maps?q={-lat},{-lon}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_gps_extraction(image_path)
    else:
        print("Usage: python test_gps_debug.py <image_path>")
        print("\nSearching for recent images in Supabase storage...")

        # Try to find images in the temp directory
        storage_paths = [
            Path(__file__).parent / "storage" / "sentrix-images",
            Path(__file__).parent / "temp"
        ]

        for storage_path in storage_paths:
            if storage_path.exists():
                images = list(storage_path.glob("*.jpg")) + list(storage_path.glob("*.jpeg")) + list(storage_path.glob("*.png"))
                if images:
                    print(f"\nFound {len(images)} images in {storage_path}")
                    for img in images[:3]:  # Test first 3
                        test_gps_extraction(str(img))

"""
Download and compare YOLO models for traffic control system.
This script helps you download different YOLO models and shows their specs.
"""

from ultralytics import YOLO
import os


def download_model(model_name):
    """
    Download a YOLO model. Ultralytics will automatically download it
    if it doesn't exist locally.

    Args:
        model_name: Name of the model (e.g., 'yolov8s.pt')
    """
    print(f"\n{'='*60}")
    print(f"Downloading/Loading: {model_name}")
    print(f"{'='*60}")

    try:
        model = YOLO(model_name)

        # Get file size if it exists
        if os.path.exists(model_name):
            size_mb = os.path.getsize(model_name) / (1024 * 1024)
            print(f"✓ Model downloaded successfully!")
            print(f"  File: {model_name}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"  Location: {os.path.abspath(model_name)}")
        else:
            print(f"✓ Model loaded from cache")

        return True

    except Exception as e:
        print(f"✗ Failed to download {model_name}")
        print(f"  Error: {e}")
        return False


def show_model_comparison():
    """Display comparison of different YOLO models."""
    print("\n" + "="*80)
    print("YOLO MODEL COMPARISON")
    print("="*80)
    print()
    print("Model      | Size    | Speed    | Accuracy | Recommended For")
    print("-----------+---------+----------+----------+--------------------------------")
    print("yolov8n.pt | 6 MB    | Fastest  | Good     | Fast detection, limited accuracy")
    print("yolov8s.pt | 22 MB   | Fast     | Better   | RECOMMENDED - Best balance")
    print("yolov8m.pt | 52 MB   | Medium   | Great    | Higher accuracy, slower")
    print("yolov8l.pt | 87 MB   | Slow     | Excellent| Maximum accuracy")
    print("yolov8x.pt | 136 MB  | Slowest  | Best     | Professional use")
    print("="*80)
    print()
    print("For toy car detection, we recommend: yolov8s.pt or yolov8m.pt")
    print("These provide much better accuracy than yolov8n.pt without being too slow.")
    print()


def main():
    """Main function to download models."""
    show_model_comparison()

    print("\nWhich models would you like to download?")
    print("1. yolov8s.pt (Small - RECOMMENDED)")
    print("2. yolov8m.pt (Medium - More accurate)")
    print("3. Both")
    print("4. All models (n, s, m, l, x)")
    print("5. Exit")

    choice = input("\nEnter your choice (1-5): ").strip()

    models_to_download = []

    if choice == '1':
        models_to_download = ['yolov8s.pt']
    elif choice == '2':
        models_to_download = ['yolov8m.pt']
    elif choice == '3':
        models_to_download = ['yolov8s.pt', 'yolov8m.pt']
    elif choice == '4':
        models_to_download = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
    elif choice == '5':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Downloading yolov8s.pt by default...")
        models_to_download = ['yolov8s.pt']

    print(f"\nDownloading {len(models_to_download)} model(s)...")

    success_count = 0
    for model_name in models_to_download:
        if download_model(model_name):
            success_count += 1

    print("\n" + "="*60)
    print(f"DOWNLOAD COMPLETE: {success_count}/{len(models_to_download)} successful")
    print("="*60)

    if success_count > 0:
        print("\nTo use a model, run:")
        print(f"  python smart_traffic_control.py --model {models_to_download[0]}")
        print("\nOr for a different model:")
        print("  python smart_traffic_control.py --model yolov8s.pt")
        print("  python smart_traffic_control.py --model yolov8m.pt")
        print("\nFor real car detection:")
        print("  python smart_traffic_control.py --model yolov8s.pt --real-cars")


if __name__ == "__main__":
    main()

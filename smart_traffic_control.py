"""
Smart Traffic Control System
Uses YOLO object detection to count cars on left and right sides
of camera view and controls traffic lights accordingly.
"""

import cv2
import time
import numpy as np
from collections import deque
from ultralytics import YOLO
from arduino_controller import ArduinoController
import sys


class SmartTrafficControl:
    def __init__(self, model_path="yolov8s.pt", camera_index=0, toy_car_mode=True):
        """
        Initialize the smart traffic control system.

        Args:
            model_path: Path to YOLO model file (yolov8n.pt, yolov8s.pt, yolov8m.pt, etc.)
            camera_index: Camera device index (0 for default camera)
            toy_car_mode: Enable detection settings optimized for toy cars
        """
        print("Initializing Smart Traffic Control System...")
        print(f"Mode: {'TOY CAR' if toy_car_mode else 'REAL CAR'} detection")
        print(f"Model: {model_path}")

        # Detection settings
        self.toy_car_mode = toy_car_mode
        if toy_car_mode:
            # Lower threshold for toy cars, detect all objects
            self.confidence_threshold = 0.15
            self.detect_all_objects = True
            self.inference_size = 640  # Larger size for better detection
            print("Using low confidence threshold (0.15) for toy car detection")
            print("Detecting all objects (not just cars)")
        else:
            # Higher threshold for real cars
            self.confidence_threshold = 0.5
            self.detect_all_objects = False
            self.inference_size = 640

        # Image preprocessing settings
        self.brightness_adjust = 30  # Brightness boost
        self.contrast_adjust = 1.3   # Contrast multiplier
        self.enable_preprocessing = True

        # Detection smoothing - use history to reduce flickering
        self.detection_history_size = 5  # Average over last 5 frames
        self.left_count_history = deque(maxlen=self.detection_history_size)
        self.right_count_history = deque(maxlen=self.detection_history_size)

        # Load YOLO model
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)

        # Initialize camera with better settings
        print(f"Opening camera {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")

        # Set camera properties for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Higher resolution
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Enable auto exposure

        # Get actual camera resolution
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {self.frame_width}x{self.frame_height}")

        # Initialize Arduino controller
        print("Connecting to Arduino...")
        self.arduino = ArduinoController()
        if not self.arduino.is_connected():
            raise RuntimeError("Could not connect to Arduino")

        # Set to manual mode initially
        self.arduino.set_manual_mode()
        time.sleep(0.5)

        # Traffic light state tracking
        self.current_green_side = None  # 'left' or 'right'
        self.last_switch_time = time.time()
        self.min_switch_interval = 5.0  # Minimum 5 seconds between switches
        # For toy cars, use lower threshold since there are fewer cars
        # 0 means switch as soon as one side has ANY more cars
        self.car_count_threshold = 0 if toy_car_mode else 1

        # Statistics
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()

        print("Initialization complete!")
        print("\nControls:")
        print("  'q' - Quit")
        print("  'r' - Reset (both lights red)")
        print("  '+' - Increase confidence threshold (less detections)")
        print("  '-' - Decrease confidence threshold (more detections)")
        print("  'p' - Toggle preprocessing (brightness/contrast)")
        print("  'b' - Increase brightness")
        print("  'd' - Decrease brightness")
        print(f"\nCurrent confidence threshold: {self.confidence_threshold:.2f}")
        print("\nStarting detection...\n")

    def preprocess_frame(self, frame):
        """
        Preprocess frame to improve detection quality.
        Adjusts brightness, contrast, and sharpness.

        Args:
            frame: Input frame

        Returns:
            Preprocessed frame
        """
        if not self.enable_preprocessing:
            return frame

        # Convert to float for processing
        frame_float = frame.astype(np.float32)

        # Adjust brightness
        frame_float = frame_float + self.brightness_adjust

        # Adjust contrast
        frame_float = (frame_float - 128) * self.contrast_adjust + 128

        # Clip values to valid range
        frame_float = np.clip(frame_float, 0, 255)

        # Convert back to uint8
        preprocessed = frame_float.astype(np.uint8)

        # Apply sharpening filter
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(preprocessed, -1, kernel)

        # Blend original and sharpened (70% sharpened, 30% original)
        result = cv2.addWeighted(sharpened, 0.7, preprocessed, 0.3, 0)

        return result

    def detect_cars(self, frame):
        """
        Detect cars in the frame using YOLO.
        In toy car mode, detects all objects with low confidence threshold.
        In real car mode, only detects vehicles with higher confidence.

        Args:
            frame: Input frame from camera

        Returns:
            list: List of car bounding boxes [(x1, y1, x2, y2, confidence, class_name), ...]
        """
        # Preprocess frame for better detection
        processed_frame = self.preprocess_frame(frame)

        # Run YOLO detection with improved settings
        if self.detect_all_objects:
            # Detect all objects for toy cars
            results = self.model(
                processed_frame,
                imgsz=self.inference_size,
                conf=self.confidence_threshold,
                iou=0.4,  # Lower IOU threshold for better overlapping detection
                verbose=False,
                agnostic_nms=True  # Class-agnostic NMS
            )
        else:
            # COCO dataset vehicle classes: 2=car, 3=motorcycle, 5=bus, 7=truck
            results = self.model(
                processed_frame,
                imgsz=self.inference_size,
                conf=self.confidence_threshold,
                iou=0.45,
                classes=[2, 3, 5, 7],
                verbose=False
            )

        cars = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id] if hasattr(self.model, 'names') else str(class_id)

                # Already filtered by confidence in model call
                cars.append((int(x1), int(y1), int(x2), int(y2), confidence, class_name))

        return cars

    def count_cars_by_side(self, cars):
        """
        Count cars on left and right sides of the frame.
        Uses detection history to smooth counts and reduce flickering.

        Args:
            cars: List of car bounding boxes

        Returns:
            tuple: (left_count, right_count, smoothed_left, smoothed_right)
        """
        mid_x = self.frame_width // 2
        left_count = 0
        right_count = 0

        for x1, y1, x2, y2, conf, class_name in cars:
            # Use center of bounding box to determine side
            center_x = (x1 + x2) // 2

            if center_x < mid_x:
                left_count += 1
            else:
                right_count += 1

        # Add to history
        self.left_count_history.append(left_count)
        self.right_count_history.append(right_count)

        # Calculate smoothed average (reduces flickering)
        smoothed_left = int(round(sum(self.left_count_history) / len(self.left_count_history)))
        smoothed_right = int(round(sum(self.right_count_history) / len(self.right_count_history)))

        return left_count, right_count, smoothed_left, smoothed_right

    def update_traffic_lights(self, left_count, right_count):
        """
        Update traffic lights based on car counts.

        Args:
            left_count: Number of cars on left side
            right_count: Number of cars on right side
        """
        current_time = time.time()
        time_since_last_switch = current_time - self.last_switch_time

        # Determine which side needs green light
        # Use >= so that if threshold is 0, even 1 more car will trigger switch
        if left_count >= right_count + self.car_count_threshold and left_count > right_count:
            preferred_side = 'left'
        elif right_count >= left_count + self.car_count_threshold and right_count > left_count:
            preferred_side = 'right'
        else:
            preferred_side = self.current_green_side  # Keep current state

        # Check if we should switch lights
        should_switch = False

        if self.current_green_side is None:
            # Initial state - set based on car counts
            should_switch = True
        elif preferred_side != self.current_green_side:
            # Want to switch - check if enough time has passed
            if time_since_last_switch >= self.min_switch_interval:
                should_switch = True

        if should_switch and preferred_side is not None:
            print(f"\n{'='*60}")
            print(f"SWITCHING LIGHTS: {preferred_side.upper()} side GREEN")
            print(f"Car counts - Left: {left_count}, Right: {right_count}")
            print(f"Threshold: {self.car_count_threshold}")
            print(f"{'='*60}\n")

            if preferred_side == 'left':
                # Left side green (Light 1), right side red (Light 2)
                print("→ Light 1 (LEFT): GREEN")
                print("→ Light 2 (RIGHT): RED")
                self.arduino.set_green_1()
                time.sleep(0.1)  # Small delay between commands
                self.arduino.set_red_2()
            else:
                # Right side green (Light 2), left side red (Light 1)
                print("→ Light 1 (LEFT): RED")
                print("→ Light 2 (RIGHT): GREEN")
                self.arduino.set_red_1()
                time.sleep(0.1)  # Small delay between commands
                self.arduino.set_green_2()

            self.current_green_side = preferred_side
            self.last_switch_time = current_time

    def draw_visualization(self, frame, cars, left_count, right_count, smoothed_left, smoothed_right):
        """
        Draw visualization on frame including bounding boxes and statistics.

        Args:
            frame: Input frame
            cars: List of car bounding boxes
            left_count: Current number of cars on left
            right_count: Current number of cars on right
            smoothed_left: Smoothed average for left side
            smoothed_right: Smoothed average for right side

        Returns:
            frame: Annotated frame
        """
        # Draw center dividing line
        mid_x = self.frame_width // 2
        cv2.line(frame, (mid_x, 0), (mid_x, self.frame_height), (255, 255, 255), 2)

        # Draw bounding boxes for detected objects
        for x1, y1, x2, y2, conf, class_name in cars:
            center_x = (x1 + x2) // 2

            # Color based on side: blue for left, green for right
            color = (255, 0, 0) if center_x < mid_x else (0, 255, 0)

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw class name and confidence score
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw car counts with light status indicators
        left_indicator = " [GREEN]" if self.current_green_side == 'left' else " [RED]"
        right_indicator = " [GREEN]" if self.current_green_side == 'right' else " [RED]"
        left_color = (0, 255, 0) if self.current_green_side == 'left' else (0, 0, 255)
        right_color = (0, 255, 0) if self.current_green_side == 'right' else (0, 0, 255)

        cv2.putText(frame, f"LEFT: {smoothed_left} ({left_count}){left_indicator}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, left_color, 2)
        cv2.putText(frame, f"RIGHT: {smoothed_right} ({right_count}){right_indicator}", (mid_x + 10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, right_color, 2)

        # Draw current light state with larger text
        if self.current_green_side:
            light_text = f"Light {1 if self.current_green_side == 'left' else 2} ({self.current_green_side.upper()}) is GREEN"
        else:
            light_text = "Waiting for cars..."
        cv2.putText(frame, light_text, (10, self.frame_height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (self.frame_width - 120, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Draw side labels
        cv2.putText(frame, "Light 1", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, "Light 2", (mid_x + 10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw detection settings
        settings_y = self.frame_height - 50
        cv2.putText(frame, f"Conf: {self.confidence_threshold:.2f}",
                   (10, settings_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Preprocess: {'ON' if self.enable_preprocessing else 'OFF'}",
                   (120, settings_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Brightness: {self.brightness_adjust}",
                   (300, settings_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Threshold: {self.car_count_threshold}",
                   (480, settings_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw detection mode
        mode_text = f"Mode: {'TOY CARS' if self.toy_car_mode else 'REAL CARS'}"
        cv2.putText(frame, mode_text, (self.frame_width // 2 - 80, self.frame_height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        return frame

    def run(self):
        """
        Main loop for the smart traffic control system.
        """
        try:
            while True:
                # Read frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break

                # Detect cars
                cars = self.detect_cars(frame)

                # Count cars by side (returns current and smoothed counts)
                left_count, right_count, smoothed_left, smoothed_right = self.count_cars_by_side(cars)

                # Update traffic lights using smoothed counts (more stable)
                self.update_traffic_lights(smoothed_left, smoothed_right)

                # Draw visualization
                frame = self.draw_visualization(frame, cars, left_count, right_count, smoothed_left, smoothed_right)

                # Calculate FPS
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.fps = self.frame_count / (current_time - self.last_fps_time)
                    self.frame_count = 0
                    self.last_fps_time = current_time

                # Display frame
                cv2.imshow('Smart Traffic Control', frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord('r'):
                    print("\nResetting - both lights RED")
                    self.arduino.set_red_1()
                    self.arduino.set_red_2()
                    self.current_green_side = None
                    self.last_switch_time = time.time()
                elif key == ord('+') or key == ord('='):
                    self.confidence_threshold = min(0.95, self.confidence_threshold + 0.05)
                    print(f"\nConfidence threshold increased to {self.confidence_threshold:.2f}")
                elif key == ord('-') or key == ord('_'):
                    self.confidence_threshold = max(0.05, self.confidence_threshold - 0.05)
                    print(f"\nConfidence threshold decreased to {self.confidence_threshold:.2f}")
                elif key == ord('p'):
                    self.enable_preprocessing = not self.enable_preprocessing
                    print(f"\nPreprocessing {'enabled' if self.enable_preprocessing else 'disabled'}")
                elif key == ord('b'):
                    self.brightness_adjust = min(100, self.brightness_adjust + 10)
                    print(f"\nBrightness increased to {self.brightness_adjust}")
                elif key == ord('d'):
                    self.brightness_adjust = max(-100, self.brightness_adjust - 10)
                    print(f"\nBrightness decreased to {self.brightness_adjust}")

        except KeyboardInterrupt:
            print("\nInterrupted by user")

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Clean up resources.
        """
        print("\nCleaning up...")

        # Set both lights to red before disconnecting
        print("Setting both lights to RED...")
        self.arduino.set_red_1()
        self.arduino.set_red_2()
        time.sleep(0.5)

        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
        self.arduino.disconnect()

        print("Cleanup complete. Goodbye!")


def main():
    """
    Main entry point with command line argument support.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Smart Traffic Control System with YOLO')
    parser.add_argument('--model', type=str, default='yolov8s.pt',
                       help='YOLO model to use (yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt)')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--real-cars', action='store_true',
                       help='Use real car mode instead of toy car mode')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("SMART TRAFFIC CONTROL SYSTEM")
    print("="*60)
    print(f"Model: {args.model}")
    print(f"Camera: {args.camera}")
    print(f"Mode: {'REAL CARS' if args.real_cars else 'TOY CARS'}")
    print("="*60 + "\n")

    try:
        # Initialize and run the smart traffic control system
        controller = SmartTrafficControl(
            model_path=args.model,
            camera_index=args.camera,
            toy_car_mode=not args.real_cars
        )
        controller.run()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

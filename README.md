# Smart Traffic Light Control System

An intelligent traffic control system that uses **YOLO computer vision** to detect vehicles and automatically control Arduino traffic lights based on real-time traffic density. Perfect for demonstrating AI-powered traffic management with toy cars or real vehicles.

## Features

### 🚦 Smart Traffic Control (NEW!)
- **AI-powered detection**: Uses YOLOv11 (latest) to detect cars in real-time
- **Automatic light switching**: Green light for side with more cars
- **Toy car mode**: Optimized settings for small toy vehicles
- **Real car mode**: Higher precision for real vehicle detection
- **Live visualization**: See detections with bounding boxes and counts
- **Adjustable sensitivity**: Runtime controls for confidence, brightness, etc.
- **Detection smoothing**: Averages over multiple frames for stable counts

### 🎮 Manual Control
- Control 2 independent traffic lights (Red, Yellow, Green)
- **Manual Mode**: Control each light individually
- **Auto Mode**: Automatic cycling with opposite phases
- **Emergency Mode**: Both lights flash red
- Serial communication with Arduino Uno
- Interactive test mode for debugging

## Hardware Requirements

### For Smart Traffic Control
- **Webcam** (built-in or USB camera)
- **Toy cars or real vehicles** for detection
- Arduino Uno board
- 6x LEDs (2 sets of Red, Yellow, Green)
- 6x 220Ω resistors
- Breadboard and jumper wires
- USB cable for Arduino

### For Basic Controller Only
- Arduino Uno board
- 6x LEDs (2 sets of Red, Yellow, Green)
- 6x 220Ω resistors
- Breadboard and jumper wires
- USB cable for Arduino

### Pin Configuration

**Traffic Light 1:**
- Red: Pin 13
- Yellow: Pin 12
- Green: Pin 11

**Traffic Light 2:**
- Red: Pin 10
- Yellow: Pin 9
- Green: Pin 8

**GND:** Connect all LED cathodes to Arduino GND

## Software Requirements

- Python 3.12+
- PySerial library
- OpenCV (for camera access)
- Ultralytics YOLO11 (latest - for object detection)
- NumPy (for image processing)

## Installation

### Quick Start

1. **Clone or download this repository**

2. **Install all dependencies:**

```bash
pip install -e .
```

Or using uv (recommended):
```bash
uv sync
```

This will install:
- `pyserial>=3.5` - Arduino communication
- `opencv-python>=4.8.0` - Camera and image processing
- `ultralytics>=8.0.0` - YOLO11 object detection

3. **Download YOLO models (optional - auto-downloads on first run):**

```bash
uv download_models.py
```

Select option 1 to download `yolo11s.pt` (recommended for best accuracy/speed balance).

4. **Upload Arduino sketch:**

- Open `traffic_lights.ino` in Arduino IDE
- Connect your Arduino Uno via USB
- Upload the sketch to the board

5. **Wire the LEDs** according to the pin configuration above

## Usage

### 🚦 Smart Traffic Control (AI-Powered)

Run the smart traffic system with computer vision:

```bash
uv smart_traffic_control.py
```

**Default settings:**
- Model: `yolo11s.pt` (small, good balance, latest YOLO version)
- Mode: Toy car detection
- Camera: Index 0 (default camera)

**Advanced options:**

```bash
# Use medium model (better accuracy)
uv smart_traffic_control.py --model yolo11m.pt

# Use for real cars
uv smart_traffic_control.py --real-cars

# Use different camera
uv smart_traffic_control.py --camera 1

# Combine options
uv smart_traffic_control.py --model yolo11m.pt --camera 1 --real-cars
```

**Runtime keyboard controls:**
- `q` - Quit program
- `r` - Reset both lights to red
- `+` / `-` - Increase/decrease confidence threshold
- `b` / `d` - Increase/decrease brightness
- `p` - Toggle image preprocessing on/off

**How it works:**
1. Camera feed is divided into LEFT and RIGHT sides
2. YOLO detects objects on each side
3. Side with more cars gets GREEN light
4. Other side gets RED light
5. Minimum 5 seconds between switches (prevents flickering)

**Display shows:**
- `LEFT: 3 (4) [GREEN]` - Smoothed count: 3, Current: 4, Light is GREEN
- `RIGHT: 2 (2) [RED]` - Smoothed count: 2, Current: 2, Light is RED
- Settings bar at bottom: Confidence, Preprocessing, Brightness, Threshold
- Bounding boxes: Blue = left side, Green = right side

### 🧪 Test the Arduino Connection

Run the test script to verify everything is working:

```bash
uv test_arduino.py
```

This will run 6 automated tests:
1. Connection check
2. Traffic Light 1 (all colors)
3. Traffic Light 2 (all colors)
4. Coordinated sequence (opposite phases)
5. Operating modes (manual, emergency, auto)
6. Special functions (test sequence, off, status)

After tests complete, you can enter **interactive mode** to manually control the lights.

### Interactive Commands

When in interactive mode:

```
r1/y1/g1  - Light 1 Red/Yellow/Green
r2/y2/g2  - Light 2 Red/Yellow/Green
a         - Auto mode (automatic cycling, opposite phases)
m         - Manual mode
e         - Emergency mode (both flashing red)
t         - Run test sequence
off       - Turn all lights off
status    - Show current status
q         - Quit
```

### 🤖 YOLO Model Selection

Different YOLO models offer different trade-offs between speed and accuracy. We now use **YOLO11** - the latest version with improved performance!

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `yolo11n.pt` | 5.5 MB | Fastest | Good | Quick testing, low-end hardware |
| `yolo11s.pt` | 19 MB | Fast | Better | **Recommended - Best balance** |
| `yolo11m.pt` | 40 MB | Medium | Great | Higher accuracy needed |
| `yolo11l.pt` | 52 MB | Slow | Excellent | Maximum accuracy |
| `yolo11x.pt` | 109 MB | Slowest | Best | Professional applications |

**Download models:**
```bash
uv download_models.py
```

The script will automatically download models on first use if not present locally.

### 📚 Using Arduino Controller in Python Code

```python
from arduino_controller import ArduinoController

# Initialize (auto-detects Arduino port)
arduino = ArduinoController()

# Manual control
arduino.set_manual_mode()
arduino.set_red_1()      # Light 1 to RED
arduino.set_green_2()    # Light 2 to GREEN

# Automatic mode (lights cycle with opposite phases)
arduino.set_auto_mode()

# Emergency mode
arduino.set_emergency_mode()

# Cleanup
arduino.disconnect()
```

## Troubleshooting

### Camera Not Opening

If you get "Could not open camera" error:

1. Check if camera is already in use by another application
2. Try different camera index: `--camera 1` or `--camera 2`
3. On Linux, check camera permissions: `ls -l /dev/video*`
4. Test camera with: `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`

### Poor Detection Quality

If toy cars aren't being detected well:

1. **Lower confidence threshold**: Press `-` key during runtime (try 0.10-0.15)
2. **Increase brightness**: Press `b` key multiple times
3. **Enable preprocessing**: Press `p` key to toggle (should be ON)
4. **Better lighting**: Ensure good lighting on your toy cars
5. **Larger model**: Use `--model yolov8m.pt` for better accuracy
6. **Camera focus**: Make sure camera is focused on the cars

### Arduino Not Detected

If you get "Arduino not found" or "Permission denied" error:

1. **Close Arduino IDE** completely (especially Serial Monitor)
2. Check USB cable connection
3. Verify Arduino is powered on
4. **Unplug and replug** the Arduino USB cable
5. Install Arduino drivers if needed
6. On Linux: Add user to dialout group: `sudo usermod -a -G dialout $USER`
7. Manually specify port:
   ```python
   arduino = ArduinoController(port='COM3')      # Windows
   arduino = ArduinoController(port='/dev/ttyUSB0')  # Linux
   ```

### Lights Not Switching

If traffic lights don't change when cars are detected:

1. Check terminal output for "SWITCHING LIGHTS" messages
2. Verify there's a difference in car counts between sides
3. Wait at least 5 seconds between switches (minimum interval)
4. Ensure smoothed counts show difference (not just current counts)
5. Check Arduino lights respond to manual commands: `uv test_arduino.py`

### LEDs Not Working

1. Check wiring matches the pin configuration
2. Verify LED polarity (long leg = anode/positive)
3. Ensure resistors are connected
4. Test Arduino sketch with Serial Monitor in Arduino IDE

### Performance Issues

If detection is slow or laggy:

1. Use smaller model: `--model yolov8n.pt` (fastest)
2. Lower camera resolution (edit line 65-66 in smart_traffic_control.py)
3. Close other applications using the camera
4. Check CPU/GPU usage

### Serial Communication Issues

1. Close Arduino IDE Serial Monitor (can't have multiple connections)
2. Check baud rate matches (9600 in both Python and Arduino)
3. Try unplugging and replugging the Arduino
4. Check available ports:
   ```python
   arduino = ArduinoController()
   print(arduino.list_ports())
   ```

## Project Structure

```
.
├── smart_traffic_control.py  # AI-powered traffic control (main application)
├── download_models.py         # YOLO model download utility
├── arduino_controller.py      # Python serial communication module
├── test_arduino.py            # Test script with interactive mode
├── traffic_lights.ino         # Arduino sketch for dual lights
├── yolo11n.pt                 # YOLO11 nano model (5.5 MB)
├── yolo11s.pt                 # YOLO11 small model (19 MB, recommended)
├── pyproject.toml             # Python dependencies
├── uv.lock                    # Dependency lock file
└── README.md                  # This file
```

**Key files:**
- `smart_traffic_control.py` - Main application with computer vision
- `arduino_controller.py` - Low-level Arduino communication
- `download_models.py` - Helper to download YOLO models
- `traffic_lights.ino` - Arduino firmware (upload to board once)

## How It Works

### Smart Traffic Control System

**Architecture:**
```
Camera → Image Preprocessing → YOLO11 Detection → Car Counting →
Traffic Logic → Arduino Controller → Physical LEDs
```

**Detection Pipeline:**
1. **Camera Capture**: Reads frames from webcam at high resolution (1280x720)
2. **Preprocessing**: Enhances brightness, contrast, and sharpness for better detection
3. **YOLO Detection**: YOLO11 identifies objects with confidence scores
4. **Side Classification**: Divides frame into LEFT and RIGHT, assigns detections
5. **Smoothing**: Averages counts over last 5 frames to reduce flickering
6. **Decision Logic**: Compares car counts, switches light if one side has more cars
7. **Rate Limiting**: Minimum 5 seconds between switches for stability
8. **LED Control**: Sends serial commands to Arduino (G1/R2 or R1/G2)

**Toy Car Mode:**
- Confidence threshold: 0.15 (very sensitive)
- Detects ALL objects (not just cars)
- Switching threshold: 0 (any difference triggers switch)
- Enhanced preprocessing for small objects

**Real Car Mode:**
- Confidence threshold: 0.5 (more strict)
- Detects only vehicles (cars, trucks, buses, motorcycles)
- Switching threshold: 1 (needs clear difference)
- Standard preprocessing

### Basic Automatic Mode

When in auto mode (without computer vision), the traffic lights cycle realistically:
- **Light 1** cycles: RED → GREEN → YELLOW → RED
- **Light 2** maintains opposite phase (when Light 1 is RED, Light 2 is GREEN)
- Timing: 5s RED, 5s GREEN, 2s YELLOW

### Emergency Mode

Both lights flash red simultaneously at 500ms intervals.

### Manual Mode

Complete independent control of each light via serial commands (R1/Y1/G1/R2/Y2/G2).

## Serial Commands

The Arduino accepts these commands:

- `R1`/`Y1`/`G1` - Light 1 Red/Yellow/Green
- `R2`/`Y2`/`G2` - Light 2 Red/Yellow/Green
- `A` - Auto mode
- `M` - Manual mode
- `E` - Emergency mode
- `T` - Test sequence
- `OFF` - All lights off
- `STATUS` - Display current status

## Quick Start Guide

**For first-time users:**

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Upload Arduino firmware** (one-time):
   - Open `traffic_lights.ino` in Arduino IDE
   - Upload to Arduino Uno

3. **Wire the LEDs** according to pin configuration above

4. **Test basic functionality:**
   ```bash
   uv test_arduino.py
   ```

5. **Run smart traffic control:**
   ```bash
   uv smart_traffic_control.py
   ```

6. **Position toy cars** on left and right sides of camera view

7. **Watch the magic!** Lights switch automatically based on car density

**Tips for best results:**
- Good lighting is crucial for detection
- Use colorful toy cars (easier to detect)
- Keep background simple and uncluttered
- Position camera 1-2 feet above the surface
- Press `-` key to lower confidence if not detecting

## Features Summary

### What Makes This Project Special

✨ **AI-Powered**: Uses state-of-the-art YOLO11 (latest) object detection
🎮 **Interactive**: Real-time adjustable settings via keyboard
🔧 **Flexible**: Works with toy cars AND real vehicles
📊 **Visual**: Live bounding boxes and statistics display
🎯 **Smart**: Detection smoothing prevents erratic behavior
⚡ **Fast**: Real-time performance with optimized inference
🔌 **Hardware Integration**: Direct Arduino control via serial
📦 **Complete**: Includes testing tools and model downloader

### Educational Value

This project demonstrates:
- Computer vision and object detection
- Hardware-software integration
- Real-time system design
- Arduino programming
- Python serial communication
- Traffic control algorithms
- Image preprocessing techniques
- Model selection and optimization

Perfect for:
- STEM education and demos
- Robotics projects
- AI/ML learning
- Arduino workshops
- Science fair projects
- University coursework

## Advanced Configuration

### Adjusting Detection Parameters

Edit `smart_traffic_control.py` to customize:

```python
# Line 33: Confidence threshold
self.confidence_threshold = 0.15  # Lower = more detections

# Line 45-46: Brightness and contrast
self.brightness_adjust = 30       # -100 to 100
self.contrast_adjust = 1.3        # 0.5 to 2.0

# Line 50: Smoothing window
self.detection_history_size = 5   # More frames = more stable

# Line 89: Minimum switch interval
self.min_switch_interval = 5.0    # Seconds between switches

# Line 92: Car count threshold
self.car_count_threshold = 0      # Difference needed to switch
```

### Camera Settings

```python
# Line 65-69: Resolution and quality
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
self.cap.set(cv2.CAP_PROP_FPS, 30)
```

## Contributing

Contributions are welcome! Areas for improvement:
- Additional object tracking algorithms
- Multiple lane support (3+ traffic lights)
- Web interface for remote monitoring
- Data logging and analytics
- Different YOLO model architectures
- Raspberry Pi support

## License

This project is provided as-is for educational purposes.

## Credits

- **YOLO11** by [Ultralytics](https://github.com/ultralytics/ultralytics)
- **OpenCV** for computer vision
- **PySerial** for Arduino communication

---

**Built with ❤️ for education and innovation**

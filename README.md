# Arduino Dual Traffic Light Controller

A Python-based controller for managing two Arduino traffic lights with serial communication. Supports manual control, automatic cycling with opposite phases, and emergency modes.

## Features

- Control 2 independent traffic lights (Red, Yellow, Green)
- **Manual Mode**: Control each light individually
- **Auto Mode**: Automatic cycling with opposite phases (realistic intersection behavior)
- **Emergency Mode**: Both lights flash red
- Serial communication with Arduino Uno
- Interactive test mode for debugging

## Hardware Requirements

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

## Installation

1. **Install Python dependencies:**

```bash
pip install pyserial
```

Or using uv:
```bash
uv sync
```

2. **Upload Arduino sketch:**

- Open `traffic_lights.ino` in Arduino IDE
- Connect your Arduino Uno via USB
- Upload the sketch to the board

3. **Wire the LEDs** according to the pin configuration above

## Usage

### Test the Arduino Connection

Run the test script to verify everything is working:

```bash
python test_arduino.py
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

### Using Arduino Controller in Python Code

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

### Arduino Not Detected

If you get "Arduino not found" error:

1. Check USB cable connection
2. Verify Arduino is powered on
3. Install Arduino drivers if needed
4. Manually specify port:
   ```python
   arduino = ArduinoController(port='COM3')      # Windows
   arduino = ArduinoController(port='/dev/ttyUSB0')  # Linux
   ```

### LEDs Not Working

1. Check wiring matches the pin configuration
2. Verify LED polarity (long leg = anode/positive)
3. Ensure resistors are connected
4. Test Arduino sketch with Serial Monitor in Arduino IDE

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
├── arduino_controller.py   # Python serial communication module
├── test_arduino.py         # Test script with interactive mode
├── traffic_lights.ino      # Arduino sketch for dual lights
├── pyproject.toml         # Python dependencies
└── README.md              # This file
```

## How It Works

### Automatic Mode

When in auto mode, the traffic lights cycle realistically:
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

## License

This project is provided as-is for educational purposes.

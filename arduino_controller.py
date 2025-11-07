"""
Arduino controller module for managing dual traffic lights.
Communicates with Arduino Uno via serial connection.
"""
import serial
import serial.tools.list_ports
import time
from typing import Optional, List


class ArduinoController:
    """Controls Arduino Uno board for dual traffic light management."""

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, timeout: int = 2):
        """
        Initialize Arduino controller.

        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
                  If None, will auto-detect Arduino
            baudrate: Communication speed (default: 9600)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False

        # Try to connect
        self.connect()

    def list_ports(self) -> List[str]:
        """List all available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def auto_detect_arduino(self) -> Optional[str]:
        """
        Auto-detect Arduino Uno port.

        Returns:
            Port name if found, None otherwise
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Arduino Uno typically shows up with these identifiers
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                return port.device
        return None

    def connect(self) -> bool:
        """
        Connect to Arduino board.

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            # Auto-detect if port not specified
            if self.port is None:
                self.port = self.auto_detect_arduino()
                if self.port is None:
                    print("Arduino not found. Available ports:")
                    for port in self.list_ports():
                        print(f"  - {port}")
                    return False

            # Open serial connection
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )

            # Wait for Arduino to reset
            time.sleep(2)

            # Clear any initial data
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            self.connected = True
            print(f"✓ Connected to Arduino on {self.port}")
            return True

        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.connected = False
            return False
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            self.connected = False
            return False

    def send_command(self, command: str) -> bool:
        """
        Send command to Arduino.

        Args:
            command: Command string to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected or self.serial is None:
            return False

        try:
            # Send command with newline
            self.serial.write(f"{command}\n".encode())
            self.serial.flush()
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    def set_red_1(self) -> bool:
        """
        Set traffic light 1 to RED.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("R1")
        if success:
            print("→ Arduino: Light 1 set to RED")
        return success

    def set_yellow_1(self) -> bool:
        """
        Set traffic light 1 to YELLOW.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("Y1")
        if success:
            print("→ Arduino: Light 1 set to YELLOW")
        return success

    def set_green_1(self) -> bool:
        """
        Set traffic light 1 to GREEN.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("G1")
        if success:
            print("→ Arduino: Light 1 set to GREEN")
        return success

    def set_red_2(self) -> bool:
        """
        Set traffic light 2 to RED.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("R2")
        if success:
            print("→ Arduino: Light 2 set to RED")
        return success

    def set_yellow_2(self) -> bool:
        """
        Set traffic light 2 to YELLOW.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("Y2")
        if success:
            print("→ Arduino: Light 2 set to YELLOW")
        return success

    def set_green_2(self) -> bool:
        """
        Set traffic light 2 to GREEN.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("G2")
        if success:
            print("→ Arduino: Light 2 set to GREEN")
        return success

    def set_auto_mode(self) -> bool:
        """
        Enable automatic cycling mode.
        Both traffic lights will cycle automatically with opposite phases.
        Light 1: RED -> GREEN -> YELLOW -> RED
        Light 2: GREEN -> RED (opposite to Light 1)

        Returns:
            True if command sent successfully
        """
        success = self.send_command("A")
        if success:
            print("→ Arduino: Automatic mode enabled (dual lights, opposite phases)")
        return success

    def set_manual_mode(self) -> bool:
        """
        Enable manual control mode.
        Use set_red_1/2(), set_yellow_1/2(), set_green_1/2() to control lights manually.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("M")
        if success:
            print("→ Arduino: Manual mode enabled")
        return success

    def set_emergency_mode(self) -> bool:
        """
        Enable emergency mode (both lights flashing red).

        Returns:
            True if command sent successfully
        """
        success = self.send_command("E")
        if success:
            print("→ Arduino: Emergency mode enabled (both lights flashing red)")
        return success

    def turn_off(self) -> bool:
        """
        Turn all lights OFF.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("OFF")
        if success:
            print("→ Arduino: All lights OFF")
        return success

    def run_test(self) -> bool:
        """
        Run the built-in test sequence on Arduino.
        Tests all LEDs in sequence.

        Returns:
            True if command sent successfully
        """
        success = self.send_command("T")
        if success:
            print("→ Arduino: Running test sequence")
        return success

    def get_status(self) -> bool:
        """
        Request current status from Arduino.

        Returns:
            True if command sent successfully
        """
        return self.send_command("STATUS")

    def read_response(self) -> Optional[str]:
        """
        Read response from Arduino.

        Returns:
            Response string or None if no data available
        """
        if not self.connected or self.serial is None:
            return None

        try:
            if self.serial.in_waiting > 0:
                response = self.serial.readline().decode().strip()
                return response
        except Exception as e:
            print(f"Error reading from Arduino: {e}")

        return None

    def reset(self) -> bool:
        """
        Reset Arduino (set both lights to red).

        Returns:
            True if reset successful
        """
        return self.set_red_1() and self.set_red_2()

    def disconnect(self):
        """Disconnect from Arduino."""
        if self.serial and self.connected:
            try:
                # Set both lights to red before disconnecting
                self.set_red_1()
                self.set_red_2()
                time.sleep(0.5)
                self.serial.close()
                print("✓ Disconnected from Arduino")
            except Exception as e:
                print(f"Error disconnecting: {e}")

        self.connected = False
        self.serial = None

    def is_connected(self) -> bool:
        """Check if Arduino is connected."""
        return self.connected and self.serial is not None and self.serial.is_open

    def __del__(self):
        """Cleanup on object destruction."""
        self.disconnect()

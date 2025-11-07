"""
Arduino connection test script.
Tests serial communication and dual traffic light control.
"""
import time
import sys
from arduino_controller import ArduinoController


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def test_connection(arduino):
    """Test Arduino connection."""
    print_header("TEST 1: Connection Check")

    if arduino.is_connected():
        print("✓ Arduino connected successfully")
        print(f"  Port: {arduino.port}")
        print(f"  Baud rate: {arduino.baudrate}")
        return True
    else:
        print("✗ Arduino not connected")
        print("\nAvailable ports:")
        for port in arduino.list_ports():
            print(f"  - {port}")
        return False


def test_light_1(arduino):
    """Test traffic light 1."""
    print_header("TEST 2: Traffic Light 1")

    print("Testing Light 1 - RED...")
    success_r = arduino.set_red_1()
    if success_r:
        print("✓ Light 1 RED activated")
        time.sleep(1.5)
    else:
        print("✗ Light 1 RED failed")
        return False

    print("\nTesting Light 1 - YELLOW...")
    success_y = arduino.set_yellow_1()
    if success_y:
        print("✓ Light 1 YELLOW activated")
        time.sleep(1.5)
    else:
        print("✗ Light 1 YELLOW failed")
        return False

    print("\nTesting Light 1 - GREEN...")
    success_g = arduino.set_green_1()
    if success_g:
        print("✓ Light 1 GREEN activated")
        time.sleep(1.5)
        return True
    else:
        print("✗ Light 1 GREEN failed")
        return False


def test_light_2(arduino):
    """Test traffic light 2."""
    print_header("TEST 3: Traffic Light 2")

    print("Testing Light 2 - RED...")
    success_r = arduino.set_red_2()
    if success_r:
        print("✓ Light 2 RED activated")
        time.sleep(1.5)
    else:
        print("✗ Light 2 RED failed")
        return False

    print("\nTesting Light 2 - YELLOW...")
    success_y = arduino.set_yellow_2()
    if success_y:
        print("✓ Light 2 YELLOW activated")
        time.sleep(1.5)
    else:
        print("✗ Light 2 YELLOW failed")
        return False

    print("\nTesting Light 2 - GREEN...")
    success_g = arduino.set_green_2()
    if success_g:
        print("✓ Light 2 GREEN activated")
        time.sleep(1.5)
        return True
    else:
        print("✗ Light 2 GREEN failed")
        return False


def test_light_sequence(arduino):
    """Test coordinated traffic light sequence."""
    print_header("TEST 4: Coordinated Light Sequence")

    print("Testing coordinated sequence (opposite phases)...")

    sequences = [
        ("Light 1: RED, Light 2: GREEN", arduino.set_red_1, arduino.set_green_2),
        ("Light 1: GREEN, Light 2: RED", arduino.set_green_1, arduino.set_red_2),
        ("Light 1: YELLOW, Light 2: RED", arduino.set_yellow_1, arduino.set_red_2),
        ("Light 1: RED, Light 2: GREEN", arduino.set_red_1, arduino.set_green_2)
    ]

    all_success = True
    for desc, func1, func2 in sequences:
        print(f"\n{desc}...")
        success1 = func1()
        success2 = func2()
        if success1 and success2:
            print(f"✓ Sequence activated")
            time.sleep(1.5)
        else:
            print(f"✗ Sequence failed")
            all_success = False

    return all_success


def test_modes(arduino):
    """Test different operating modes."""
    print_header("TEST 5: Operating Modes")

    print("\n1. Testing MANUAL mode...")
    if arduino.set_manual_mode():
        print("✓ Manual mode activated")
        time.sleep(1)

        print("\n2. Testing manual control of both lights...")
        arduino.set_green_1()
        arduino.set_red_2()
        print("  Light 1: GREEN, Light 2: RED")
        time.sleep(2)
    else:
        print("✗ Manual mode failed")
        return False

    print("\n3. Testing EMERGENCY mode...")
    if arduino.set_emergency_mode():
        print("✓ Emergency mode activated (both lights flashing red)")
        time.sleep(3)
    else:
        print("✗ Emergency mode failed")
        return False

    print("\n4. Testing AUTO mode...")
    if arduino.set_auto_mode():
        print("✓ Auto mode activated (dual lights, opposite phases)")
        print("  Watching automatic cycling for 10 seconds...")
        time.sleep(10)
    else:
        print("✗ Auto mode failed")
        return False

    return True


def test_special_functions(arduino):
    """Test special functions."""
    print_header("TEST 6: Special Functions")

    print("\n1. Testing built-in test sequence...")
    if arduino.run_test():
        print("✓ Test sequence command sent")
        print("  (Watch the Arduino for test sequence)")
        time.sleep(5)
    else:
        print("✗ Test sequence failed")
        return False

    print("\n2. Testing OFF command...")
    if arduino.turn_off():
        print("✓ All lights turned OFF")
        time.sleep(2)
    else:
        print("✗ OFF command failed")
        return False

    print("\n3. Testing STATUS command...")
    if arduino.get_status():
        print("✓ Status command sent")
        time.sleep(1)

        # Try to read status response
        print("\nReading Arduino response...")
        for _ in range(5):
            response = arduino.read_response()
            if response:
                print(f"  {response}")
            time.sleep(0.1)
    else:
        print("✗ Status command failed")
        return False

    return True


def interactive_test(arduino):
    """Interactive test mode."""
    print_header("INTERACTIVE TEST MODE")

    print("\nCommands:")
    print("  r1/y1/g1 - Light 1 Red/Yellow/Green")
    print("  r2/y2/g2 - Light 2 Red/Yellow/Green")
    print("  a        - Auto mode (automatic cycling, opposite phases)")
    print("  m        - Manual mode")
    print("  e        - Emergency mode (both flashing red)")
    print("  t        - Run test sequence")
    print("  off      - Turn all lights off")
    print("  status   - Show current status")
    print("  q        - Quit")
    print("\nEnter commands:")

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd == 'q':
                break
            elif cmd == 'r1':
                arduino.set_red_1()
                print("Light 1: RED")
            elif cmd == 'y1':
                arduino.set_yellow_1()
                print("Light 1: YELLOW")
            elif cmd == 'g1':
                arduino.set_green_1()
                print("Light 1: GREEN")
            elif cmd == 'r2':
                arduino.set_red_2()
                print("Light 2: RED")
            elif cmd == 'y2':
                arduino.set_yellow_2()
                print("Light 2: YELLOW")
            elif cmd == 'g2':
                arduino.set_green_2()
                print("Light 2: GREEN")
            elif cmd == 'a':
                arduino.set_auto_mode()
                print("Mode: AUTOMATIC (dual lights, opposite phases)")
            elif cmd == 'm':
                arduino.set_manual_mode()
                print("Mode: MANUAL")
            elif cmd == 'e':
                arduino.set_emergency_mode()
                print("Mode: EMERGENCY (both lights flashing)")
            elif cmd == 't':
                arduino.run_test()
                print("Running test sequence...")
            elif cmd == 'off':
                arduino.turn_off()
                print("All lights: OFF")
            elif cmd == 'status':
                arduino.get_status()
                time.sleep(0.2)
                # Read responses
                for _ in range(10):
                    response = arduino.read_response()
                    if response:
                        print(response)
                    time.sleep(0.05)
            else:
                print("Unknown command")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nExiting interactive mode...")


def main():
    """Main test routine."""
    print_header("ARDUINO DUAL TRAFFIC LIGHT TEST")

    print("\nThis script will test your Arduino connection and dual traffic lights.")
    print("Make sure your Arduino is:")
    print("  1. Connected via USB")
    print("  2. Loaded with traffic_lights.ino sketch")
    print("  3. LEDs wired to correct pins:")
    print("     Light 1: Red=13, Yellow=12, Green=11")
    print("     Light 2: Red=10, Yellow=9, Green=8")

    input("\nPress Enter to start tests...")

    # Initialize Arduino
    print("\nInitializing Arduino connection...")

    try:
        arduino = ArduinoController()

        # Run tests
        tests_passed = 0
        tests_total = 6

        # Test 1: Connection
        if test_connection(arduino):
            tests_passed += 1
        else:
            print("\n✗ Cannot proceed without Arduino connection")
            print("\nTroubleshooting:")
            print("  1. Check USB cable")
            print("  2. Verify Arduino is powered on")
            print("  3. Upload traffic_lights.ino to Arduino")
            print("  4. Try specifying port manually:")
            print("     arduino = ArduinoController(port='COM3')  # Windows")
            print("     arduino = ArduinoController(port='/dev/ttyUSB0')  # Linux")
            return 1

        # Test 2: Traffic Light 1
        if test_light_1(arduino):
            tests_passed += 1

        # Test 3: Traffic Light 2
        if test_light_2(arduino):
            tests_passed += 1

        # Test 4: Light sequence
        if test_light_sequence(arduino):
            tests_passed += 1

        # Test 5: Operating modes
        if test_modes(arduino):
            tests_passed += 1

        # Test 6: Special functions
        if test_special_functions(arduino):
            tests_passed += 1

        # Summary
        print_header("TEST SUMMARY")
        print(f"\nTests passed: {tests_passed}/{tests_total}")

        if tests_passed == tests_total:
            print("✓ All tests passed! Your Arduino dual traffic light system is ready.")
        else:
            print("⚠ Some tests failed. Check your wiring and connections.")

        # Interactive mode
        print("\n" + "-" * 60)
        response = input("\nRun interactive test? (y/n): ").strip().lower()

        if response == 'y':
            interactive_test(arduino)

        # Cleanup
        print("\nCleaning up...")
        arduino.disconnect()
        print("✓ Done!")

        return 0

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

/*
 * Dual Traffic Light System
 * Arduino Uno Sketch
 *
 * This sketch controls 2 traffic lights with realistic operation modes.
 * Each traffic light has Red, Yellow, and Green LEDs.
 *
 * Pin Configuration:
 * GND: Connected directly to Arduino GND
 * Traffic Light 1: Red=13, Yellow=12, Green=11
 * Traffic Light 2: Red=10, Yellow=9, Green=8
 *
 * Modes:
 * - AUTO: Automatically cycles through traffic light sequence (opposite phases)
 * - MANUAL: Controlled via serial commands
 * - EMERGENCY: Flashing red for emergency situations
 *
 * Serial Commands:
 * - R1/Y1/G1: Set Light 1 to Red/Yellow/Green (manual mode)
 * - R2/Y2/G2: Set Light 2 to Red/Yellow/Green (manual mode)
 * - A: Enable automatic cycling mode
 * - M: Enable manual mode
 * - E: Enable emergency mode (flashing red)
 * - T: Run test sequence
 * - OFF: Turn all lights off
 * - STATUS: Display current mode and state
 */

// Pin definitions for Traffic Light 1
const int RED_PIN_1 = 13;
const int YELLOW_PIN_1 = 12;
const int GREEN_PIN_1 = 11;

// Pin definitions for Traffic Light 2
const int RED_PIN_2 = 10;
const int YELLOW_PIN_2 = 9;
const int GREEN_PIN_2 = 8;

// Timing configurations (in milliseconds)
const unsigned long GREEN_DURATION = 5000;   // 5 seconds green
const unsigned long YELLOW_DURATION = 2000;  // 2 seconds yellow
const unsigned long RED_DURATION = 5000;     // 5 seconds red
const unsigned long EMERGENCY_BLINK = 500;   // 0.5 seconds for emergency flash

// Operating modes
enum Mode {
  MANUAL,
  AUTO,
  EMERGENCY
};

// Traffic light states
enum State {
  RED,
  YELLOW,
  GREEN,
  OFF
};

// Current operating mode and state
Mode currentMode = AUTO;  // Start in automatic mode
State currentState1 = RED;    // Light 1 state
State currentState2 = GREEN;  // Light 2 state (opposite to Light 1)
State previousState = OFF;

// Timing variables
unsigned long lastStateChange = 0;
unsigned long currentStateDuration = RED_DURATION;
bool emergencyBlinkState = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Set all pins as OUTPUT for both traffic lights
  pinMode(RED_PIN_1, OUTPUT);
  pinMode(YELLOW_PIN_1, OUTPUT);
  pinMode(GREEN_PIN_1, OUTPUT);
  pinMode(RED_PIN_2, OUTPUT);
  pinMode(YELLOW_PIN_2, OUTPUT);
  pinMode(GREEN_PIN_2, OUTPUT);

  // Initial state: All off
  setLightState(1, OFF);
  setLightState(2, OFF);

  // Start with RED on Light 1, GREEN on Light 2 in AUTO mode
  currentState1 = RED;
  currentState2 = GREEN;
  setLightState(1, RED);
  setLightState(2, GREEN);
  lastStateChange = millis();

  Serial.println("=================================");
  Serial.println("Dual Traffic Light System Ready");
  Serial.println("=================================");
  Serial.println("Mode: AUTOMATIC");
  Serial.println("Light 1 Pins: Red=13, Yellow=12, Green=11");
  Serial.println("Light 2 Pins: Red=10, Yellow=9, Green=8");
  Serial.println("");
  Serial.println("Commands:");
  Serial.println("  A - Automatic cycling mode");
  Serial.println("  M - Manual control mode");
  Serial.println("  E - Emergency mode (flashing red)");
  Serial.println("  R1/Y1/G1 - Set Light 1 to Red/Yellow/Green (manual)");
  Serial.println("  R2/Y2/G2 - Set Light 2 to Red/Yellow/Green (manual)");
  Serial.println("  T - Test sequence");
  Serial.println("  OFF - All lights off");
  Serial.println("  STATUS - Show current status");
  Serial.println("=================================");
  Serial.println("");
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove whitespace
    processCommand(command);
  }

  // Handle automatic mode cycling
  if (currentMode == AUTO) {
    unsigned long currentTime = millis();

    // Check if it's time to change state
    if (currentTime - lastStateChange >= currentStateDuration) {
      advanceTrafficLight();
      lastStateChange = currentTime;
    }
  }

  // Handle emergency mode flashing
  else if (currentMode == EMERGENCY) {
    unsigned long currentTime = millis();

    if (currentTime - lastStateChange >= EMERGENCY_BLINK) {
      emergencyBlinkState = !emergencyBlinkState;

      if (emergencyBlinkState) {
        digitalWrite(RED_PIN_1, HIGH);
        digitalWrite(RED_PIN_2, HIGH);
      } else {
        digitalWrite(RED_PIN_1, LOW);
        digitalWrite(RED_PIN_2, LOW);
      }

      lastStateChange = currentTime;
    }
  }
}

void processCommand(String command) {
  if (command.length() < 1) {
    return;
  }

  command.toUpperCase();  // Convert to uppercase for easier comparison

  if (command == "A") {
    // Switch to automatic mode
    currentMode = AUTO;
    currentState1 = RED;
    currentState2 = GREEN;
    setLightState(1, RED);
    setLightState(2, GREEN);
    lastStateChange = millis();
    currentStateDuration = RED_DURATION;
    Serial.println("Mode: AUTOMATIC - Traffic lights will cycle automatically");

  } else if (command == "M") {
    // Switch to manual mode
    currentMode = MANUAL;
    Serial.println("Mode: MANUAL - Use R1/Y1/G1 and R2/Y2/G2 commands to control lights");

  } else if (command == "E") {
    // Switch to emergency mode
    currentMode = EMERGENCY;
    setLightState(1, OFF);
    setLightState(2, OFF);
    lastStateChange = millis();
    emergencyBlinkState = false;
    Serial.println("Mode: EMERGENCY - Both lights flashing red");

  } else if (command == "R1") {
    if (currentMode != MANUAL) {
      currentMode = MANUAL;
      Serial.println("Switched to MANUAL mode");
    }
    setLightState(1, RED);
    currentState1 = RED;
    Serial.println("Light 1: RED");

  } else if (command == "Y1") {
    if (currentMode != MANUAL) {
      currentMode = MANUAL;
      Serial.println("Switched to MANUAL mode");
    }
    setLightState(1, YELLOW);
    currentState1 = YELLOW;
    Serial.println("Light 1: YELLOW");

  } else if (command == "G1") {
    if (currentMode != MANUAL) {
      currentMode = MANUAL;
      Serial.println("Switched to MANUAL mode");
    }
    setLightState(1, GREEN);
    currentState1 = GREEN;
    Serial.println("Light 1: GREEN");

  } else if (command == "R2") {
    if (currentMode != MANUAL) {
      currentMode = MANUAL;
      Serial.println("Switched to MANUAL mode");
    }
    setLightState(2, RED);
    currentState2 = RED;
    Serial.println("Light 2: RED");

  } else if (command == "Y2") {
    if (currentMode != MANUAL) {
      currentMode = MANUAL;
      Serial.println("Switched to MANUAL mode");
    }
    setLightState(2, YELLOW);
    currentState2 = YELLOW;
    Serial.println("Light 2: YELLOW");

  } else if (command == "G2") {
    if (currentMode != MANUAL) {
      currentMode = MANUAL;
      Serial.println("Switched to MANUAL mode");
    }
    setLightState(2, GREEN);
    currentState2 = GREEN;
    Serial.println("Light 2: GREEN");

  } else if (command == "T") {
    Mode previousMode = currentMode;
    runTestSequence();
    currentMode = previousMode;
    Serial.print("Restored mode: ");
    printMode();

  } else if (command == "OFF") {
    currentMode = MANUAL;
    setLightState(1, OFF);
    setLightState(2, OFF);
    currentState1 = OFF;
    currentState2 = OFF;
    Serial.println("Mode: MANUAL");
    Serial.println("All Lights: OFF");

  } else if (command == "STATUS") {
    printStatus();

  } else {
    Serial.print("Error: Unknown command: ");
    Serial.println(command);
    Serial.println("Valid commands: A, M, E, R1/Y1/G1, R2/Y2/G2, T, OFF, STATUS");
  }
}

// Set the physical light state for a specific traffic light
void setLightState(int lightNumber, State state) {
  int redPin, yellowPin, greenPin;

  // Select pins based on light number
  if (lightNumber == 1) {
    redPin = RED_PIN_1;
    yellowPin = YELLOW_PIN_1;
    greenPin = GREEN_PIN_1;
  } else {
    redPin = RED_PIN_2;
    yellowPin = YELLOW_PIN_2;
    greenPin = GREEN_PIN_2;
  }

  // Turn all lights off first for this traffic light
  digitalWrite(redPin, LOW);
  digitalWrite(yellowPin, LOW);
  digitalWrite(greenPin, LOW);

  // Turn on the appropriate light
  switch (state) {
    case RED:
      digitalWrite(redPin, HIGH);
      break;
    case YELLOW:
      digitalWrite(yellowPin, HIGH);
      break;
    case GREEN:
      digitalWrite(greenPin, HIGH);
      break;
    case OFF:
      // All lights already off
      break;
  }
}

// Advance to next state in traffic light sequence
void advanceTrafficLight() {
  previousState = currentState1;

  // Standard traffic light sequence: GREEN -> YELLOW -> RED -> GREEN
  // Light 1 progresses normally
  switch (currentState1) {
    case GREEN:
      currentState1 = YELLOW;
      currentStateDuration = YELLOW_DURATION;
      Serial.println("AUTO: Light 1 changed to YELLOW");
      break;

    case YELLOW:
      currentState1 = RED;
      currentStateDuration = RED_DURATION;
      Serial.println("AUTO: Light 1 changed to RED");
      break;

    case RED:
      currentState1 = GREEN;
      currentStateDuration = GREEN_DURATION;
      Serial.println("AUTO: Light 1 changed to GREEN");
      break;

    case OFF:
      // If somehow in OFF state, start with RED
      currentState1 = RED;
      currentStateDuration = RED_DURATION;
      Serial.println("AUTO: Light 1 changed to RED");
      break;
  }

  // Light 2 is opposite to Light 1
  // When Light 1 is RED, Light 2 is GREEN
  // When Light 1 is YELLOW (going to RED), Light 2 stays GREEN
  // When Light 1 is GREEN, Light 2 is RED
  switch (currentState1) {
    case GREEN:
      currentState2 = RED;
      Serial.println("AUTO: Light 2 changed to RED");
      break;
    case YELLOW:
      currentState2 = GREEN;  // Stay green while other is yellow
      Serial.println("AUTO: Light 2 remains GREEN");
      break;
    case RED:
      currentState2 = GREEN;
      Serial.println("AUTO: Light 2 changed to GREEN");
      break;
    case OFF:
      currentState2 = OFF;
      break;
  }

  setLightState(1, currentState1);
  setLightState(2, currentState2);
}

// Print current status
void printStatus() {
  Serial.println("");
  Serial.println("=== CURRENT STATUS ===");
  Serial.print("Mode: ");
  printMode();

  Serial.print("Light 1: ");
  printState(currentState1);

  Serial.print("Light 2: ");
  printState(currentState2);

  if (currentMode == AUTO) {
    unsigned long timeInState = millis() - lastStateChange;
    unsigned long timeRemaining = currentStateDuration - timeInState;
    Serial.print("Time remaining: ");
    Serial.print(timeRemaining / 1000);
    Serial.println(" seconds");
  }

  Serial.println("======================");
  Serial.println("");
}

// Helper function to print mode
void printMode() {
  switch (currentMode) {
    case MANUAL:
      Serial.println("MANUAL");
      break;
    case AUTO:
      Serial.println("AUTOMATIC");
      break;
    case EMERGENCY:
      Serial.println("EMERGENCY");
      break;
  }
}

// Helper function to print state
void printState(State state) {
  switch (state) {
    case RED:
      Serial.println("RED");
      break;
    case YELLOW:
      Serial.println("YELLOW");
      break;
    case GREEN:
      Serial.println("GREEN");
      break;
    case OFF:
      Serial.println("OFF");
      break;
  }
}

void runTestSequence() {
  Mode savedMode = currentMode;
  State savedState1 = currentState1;
  State savedState2 = currentState2;

  Serial.println("");
  Serial.println("=== RUNNING TEST SEQUENCE ===");

  Serial.println("  Testing Light 1 - RED (Pin 13)");
  setLightState(1, RED);
  delay(1000);

  Serial.println("  Testing Light 1 - YELLOW (Pin 12)");
  setLightState(1, YELLOW);
  delay(1000);

  Serial.println("  Testing Light 1 - GREEN (Pin 11)");
  setLightState(1, GREEN);
  delay(1000);

  Serial.println("  Testing Light 2 - RED (Pin 10)");
  setLightState(2, RED);
  delay(1000);

  Serial.println("  Testing Light 2 - YELLOW (Pin 9)");
  setLightState(2, YELLOW);
  delay(1000);

  Serial.println("  Testing Light 2 - GREEN (Pin 8)");
  setLightState(2, GREEN);
  delay(1000);

  Serial.println("  All lights OFF");
  setLightState(1, OFF);
  setLightState(2, OFF);
  delay(500);

  // Blink all lights together
  Serial.println("  Blinking all lights together (3x)");
  for (int i = 0; i < 3; i++) {
    digitalWrite(RED_PIN_1, HIGH);
    digitalWrite(YELLOW_PIN_1, HIGH);
    digitalWrite(GREEN_PIN_1, HIGH);
    digitalWrite(RED_PIN_2, HIGH);
    digitalWrite(YELLOW_PIN_2, HIGH);
    digitalWrite(GREEN_PIN_2, HIGH);
    delay(300);
    digitalWrite(RED_PIN_1, LOW);
    digitalWrite(YELLOW_PIN_1, LOW);
    digitalWrite(GREEN_PIN_1, LOW);
    digitalWrite(RED_PIN_2, LOW);
    digitalWrite(YELLOW_PIN_2, LOW);
    digitalWrite(GREEN_PIN_2, LOW);
    delay(300);
  }

  Serial.println("=== TEST COMPLETE ===");
  Serial.println("");

  // Restore previous state
  currentMode = savedMode;
  currentState1 = savedState1;
  currentState2 = savedState2;
  setLightState(1, currentState1);
  setLightState(2, currentState2);
  lastStateChange = millis();

  Serial.print("Restored Light 1 to: ");
  printState(currentState1);
  Serial.print("Restored Light 2 to: ");
  printState(currentState2);
}

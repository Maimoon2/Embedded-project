// ============================================================
// ESP32 Robot Movement Controller
// Auto-generated from simple_commands.txt
// Total commands: 20
// ============================================================

// ---- PIN CONFIGURATION ----
#define IN1 25
#define IN2 26
#define IN3 27
#define IN4 14

// ---- TIMING CONFIGURATION (milliseconds) ----
#define FORWARD_DURATION  1000
#define TURN_DURATION      600
#define STOP_PAUSE         200

// ---- COMMAND LIST ----
const int TOTAL_COMMANDS = 20;
const char* commands[20] = {
  "STOP",
  "PLANT",
  "FORWARD:7803  # 156.1cm",
  "STOP",
  "PLANT",
  "FORWARD:8100  # 162.0cm",
  "STOP",
  "PLANT",
  "LEFT:1000",
  "FORWARD:12202  # 244.0cm",
  "STOP",
  "PLANT",
  "LEFT:1000",
  "FORWARD:7556  # 151.1cm",
  "STOP",
  "PLANT",
  "FORWARD:8302  # 166.0cm",
  "STOP",
  "PLANT",
  "END"
};

// ---- MOTOR CONTROL FUNCTIONS ----

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  delay(STOP_PAUSE);
}

void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  delay(FORWARD_DURATION);
  stopMotors();
}

void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  delay(TURN_DURATION);
  stopMotors();
}

void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  delay(TURN_DURATION);
  stopMotors();
}

void endMission() {
  stopMotors();
  while (true) { delay(1000); }
}

// ---- COMMAND EXECUTOR ----

void executeCommand(const char* cmd) {
  if (strcmp(cmd, "FORWARD") == 0) {
    moveForward();
  } else if (strcmp(cmd, "LEFT") == 0) {
    turnLeft();
  } else if (strcmp(cmd, "RIGHT") == 0) {
    turnRight();
  } else if (strcmp(cmd, "STOP") == 0) {
    stopMotors();
  } else if (strcmp(cmd, "PLANT") == 0) {
    stopMotors();
    delay(2000);
  } else if (strcmp(cmd, "END") == 0) {
    endMission();
  }
}

// ---- SETUP ----

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stopMotors();
  delay(3000);
}

// ---- MAIN LOOP ----

void loop() {
  for (int i = 0; i < TOTAL_COMMANDS; i++) {
    executeCommand(commands[i]);
    delay(100);
  }

  while (true) { delay(1000); }
}

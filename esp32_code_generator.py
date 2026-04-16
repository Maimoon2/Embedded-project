# esp32_code_generator.py
# Usage: python esp32_code_generator.py simple_commands.txt

import sys

def parse_commands(filename):
    commands = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            commands.append(line)
    return commands

def generate_esp32_code(commands):
    cmd_entries = []
    for cmd in commands:
        cmd_entries.append(f'  "{cmd}"')

    cmd_array = ",\n".join(cmd_entries)
    cmd_count = len(commands)

    code = f'''\
// ============================================================
// ESP32 Robot Movement Controller
// Auto-generated from simple_commands.txt
// Total commands: {cmd_count}
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
const int TOTAL_COMMANDS = {cmd_count};
const char* commands[{cmd_count}] = {{
{cmd_array}
}};

// ---- MOTOR CONTROL FUNCTIONS ----

void stopMotors() {{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  delay(STOP_PAUSE);
}}

void moveForward() {{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  delay(FORWARD_DURATION);
  stopMotors();
}}

void turnLeft() {{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  delay(TURN_DURATION);
  stopMotors();
}}

void turnRight() {{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  delay(TURN_DURATION);
  stopMotors();
}}

void endMission() {{
  stopMotors();
  while (true) {{ delay(1000); }}
}}

// ---- COMMAND EXECUTOR ----

void executeCommand(const char* cmd) {{
  if (strcmp(cmd, "FORWARD") == 0) {{
    moveForward();
  }} else if (strcmp(cmd, "LEFT") == 0) {{
    turnLeft();
  }} else if (strcmp(cmd, "RIGHT") == 0) {{
    turnRight();
  }} else if (strcmp(cmd, "STOP") == 0) {{
    stopMotors();
  }} else if (strcmp(cmd, "PLANT") == 0) {{
    stopMotors();
    delay(2000);
  }} else if (strcmp(cmd, "END") == 0) {{
    endMission();
  }}
}}

// ---- SETUP ----

void setup() {{
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stopMotors();
  delay(3000);
}}

// ---- MAIN LOOP ----

void loop() {{
  for (int i = 0; i < TOTAL_COMMANDS; i++) {{
    executeCommand(commands[i]);
    delay(100);
  }}

  while (true) {{ delay(1000); }}
}}
'''
    return code


def main():
    if len(sys.argv) < 2:
        print("Usage: python esp32_code_generator.py <simple_commands.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    commands = parse_commands(input_file)

    if not commands:
        print("No commands found in file.")
        sys.exit(1)

    print(f"Parsed {len(commands)} commands: {commands}")

    output_file = "robot_controller.ino"
    code = generate_esp32_code(commands)

    with open(output_file, 'w') as f:
        f.write(code)

    print(f"Done! Saved to: {output_file}")


if __name__ == "__main__":
    main()
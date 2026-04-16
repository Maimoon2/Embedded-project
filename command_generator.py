import json
import math
from typing import List, Tuple

class CommandGenerator:
    def __init__(self, robot_config=None):
        self.commands = []
        self.config = self._default_config()
        if robot_config:
            self.config.update(robot_config)

    def _default_config(self):
        """Default robot movement configuration"""
        return {
            "forward_speed": "SLOW",
            "turn_speed": "MEDIUM",
            "distance_per_command": 50,
            "angle_per_turn": 90,
            "stop_at_points": True,
            "pause_duration": 2.0,

            # --- Calibration values (SET THESE FOR YOUR ROBOT) ---
            # Step 1: Measure your image scale
            #   Place a ruler or known object in the image,
            #   measure its pixel width and real width, then:
            #   cm_per_pixel = real_size_cm / pixel_size
            "cm_per_pixel": 1.0,  # <-- SET THIS (e.g. 0.5 means 1px = 0.5cm)

            # Step 2: Measure your robot's forward speed
            #   Run robot for 1000ms, measure distance in cm
            #   robot_speed_cm_per_s = distance_cm / 1.0
            "robot_speed_cm_per_s": 20.0,  # <-- SET THIS

            # Step 3: Measure your robot's turn speed
            #   Run one LEFT/RIGHT for 1000ms, measure degrees turned
            #   turn_speed_deg_per_s = degrees / 1.0
            "turn_speed_deg_per_s": 90.0,  # <-- SET THIS (e.g. 90 deg/s = 1000ms per 90deg turn)
        }

    def calculate_heading(self, current: Tuple[float, float], target: Tuple[float, float]) -> float:
        """Calculate heading angle from current to target point (adjusted for image coordinates)"""
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        angle = math.degrees(math.atan2(-dy, dx))
        if angle < 0:
            angle += 360
        return angle

    def normalize_angle(self, angle: float) -> float:
        """Normalize angle to 0-360 range"""
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle

    def calculate_turn_direction(self, current_heading: float, target_heading: float):
        """Calculate the turn direction and amount (corrected for image Y-axis)"""
        current_heading = self.normalize_angle(current_heading)
        target_heading = self.normalize_angle(target_heading)

        # Swapped because image Y increases downward (mirrored coordinate system)
        right_turn = (target_heading - current_heading) % 360
        left_turn  = (current_heading - target_heading) % 360

        if left_turn < right_turn:
            return "TURN_LEFT", left_turn
        else:
            return "TURN_RIGHT", right_turn

    def distance_to_move(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Calculate pixel distance between two points"""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)

    def pixel_distance_to_delay_ms(self, pixel_distance: float) -> int:
        """Convert pixel distance to real-world motor delay in milliseconds"""
        real_distance_cm = pixel_distance * self.config["cm_per_pixel"]
        delay_s = real_distance_cm / self.config["robot_speed_cm_per_s"]
        return int(round(delay_s * 1000))

    def angle_to_delay_ms(self, angle_deg: float) -> int:
        """Convert turn angle to motor delay in milliseconds"""
        delay_s = angle_deg / self.config["turn_speed_deg_per_s"]
        return int(round(delay_s * 1000))

    def generate_movement_commands(self, path: List[Tuple[int, int]]) -> List[dict]:
        """Generate movement commands from planned path"""
        if len(path) < 2:
            print("Path must have at least 2 points")
            return []

        self.commands = []

        for i in range(len(path) - 1):
            current_point = path[i]
            next_point = path[i + 1]

            target_heading = self.calculate_heading(current_point, next_point)

            if i == 0:
                current_heading = 0.0
                turn_dir, turn_amount = self.calculate_turn_direction(current_heading, target_heading)
                if turn_amount > 5:
                    self.add_turn_command(turn_dir, turn_amount)
                self.add_move_command(current_point, next_point)
                if self.config["stop_at_points"]:
                    self.add_stop_command()
                    self.add_pause_command()
            else:
                prev_point = path[i - 1]
                current_heading = self.calculate_heading(prev_point, current_point)
                turn_dir, turn_amount = self.calculate_turn_direction(current_heading, target_heading)
                if turn_amount > 5:
                    self.add_turn_command(turn_dir, turn_amount)
                self.add_move_command(current_point, next_point)
                if self.config["stop_at_points"]:
                    self.add_stop_command()
                    self.add_pause_command()

        self.add_stop_command()
        self.add_end_command()

        return self.commands

    def add_turn_command(self, direction: str, angle: float):
        """Add turn command to command list"""
        turn_units = int(round(angle / self.config["angle_per_turn"]))
        delay_ms = self.angle_to_delay_ms(angle)

        if turn_units > 0:
            for _ in range(turn_units):
                self.commands.append({
                    "type": direction,
                    "angle": self.config["angle_per_turn"],
                    "speed": self.config["turn_speed"],
                    "delay_ms": delay_ms
                })
            print(f"Turn {direction.replace('_', ' ').lower()} by {angle:.1f}° → {delay_ms}ms")

    def add_move_command(self, from_point: Tuple[int, int], to_point: Tuple[int, int]):
        """Add move command to command list"""
        distance = self.distance_to_move(from_point, to_point)
        delay_ms = self.pixel_distance_to_delay_ms(distance)

        if distance > 0:
            self.commands.append({
                "type": "FORWARD",
                "distance_px": round(distance, 2),
                "distance_cm": round(distance * self.config["cm_per_pixel"], 2),
                "delay_ms": delay_ms,
                "speed": self.config["forward_speed"],
                "from": from_point,
                "to": to_point
            })
            print(f"Move FORWARD {distance:.1f}px = {distance * self.config['cm_per_pixel']:.1f}cm → {delay_ms}ms")

    def add_stop_command(self):
        self.commands.append({
            "type": "STOP",
            "reason": "Reached target point"
        })

    def add_pause_command(self):
        self.commands.append({
            "type": "PLANT",
            "duration": self.config["pause_duration"],
            "reason": "Planting seed"
        })

    def add_end_command(self):
        self.commands.append({
            "type": "END",
            "reason": "Path completed"
        })

    def generate_simple_commands(self, path: List[Tuple[int, int]]) -> List[str]:
        """
        Generate simplified command list with exact delays embedded.
        Format: FORWARD:1450  LEFT:600  RIGHT:600
        Delay is in milliseconds calculated from real-world distance/angle.
        """
        simple_commands = []

        if self.config["stop_at_points"]:
            simple_commands.append("STOP")
            simple_commands.append("PLANT")

        for i in range(len(path) - 1):
            current_point = path[i]
            next_point = path[i + 1]

            target_heading = self.calculate_heading(current_point, next_point)

            if i == 0:
                current_heading = 0.0
            else:
                prev_point = path[i - 1]
                current_heading = self.calculate_heading(prev_point, current_point)

            turn_dir, turn_amount = self.calculate_turn_direction(current_heading, target_heading)

            if turn_amount > 5:
                turn_units = int(round(turn_amount / self.config["angle_per_turn"]))
                turn_delay_ms = self.angle_to_delay_ms(self.config["angle_per_turn"])  # per 90deg unit

                if turn_dir == "TURN_LEFT":
                    simple_commands.extend([f"LEFT:{turn_delay_ms}"] * turn_units)
                else:
                    simple_commands.extend([f"RIGHT:{turn_delay_ms}"] * turn_units)

            # Calculate forward delay from pixel distance
            pixel_dist = self.distance_to_move(current_point, next_point)
            forward_delay_ms = self.pixel_distance_to_delay_ms(pixel_dist)
            real_cm = round(pixel_dist * self.config["cm_per_pixel"], 1)

            simple_commands.append(f"FORWARD:{forward_delay_ms}  # {real_cm}cm")

            if self.config["stop_at_points"]:
                simple_commands.append("STOP")
                simple_commands.append("PLANT")

        simple_commands.append("END")

        return simple_commands

    def save_commands(self, commands: List[dict], filename: str = "commands.json"):
        data = {
            "total_commands": len(commands),
            "robot_config": self.config,
            "commands": commands
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved {len(commands)} commands to {filename}")
        return filename

    def save_simple_commands(self, simple_commands: List[str], filename: str = "simple_commands.txt"):
        with open(filename, 'w') as f:
            f.write("# Robot Movement Commands (with exact delays in ms)\n")
            f.write(f"# Total commands: {len(simple_commands)}\n")
            f.write("# Format: COMMAND:DELAY_MS  (delay = real-world calibrated time)\n")
            f.write(f"# Calibration: cm_per_pixel={self.config['cm_per_pixel']}, "
                    f"robot_speed={self.config['robot_speed_cm_per_s']}cm/s, "
                    f"turn_speed={self.config['turn_speed_deg_per_s']}deg/s\n\n")

            for cmd in simple_commands:
                f.write(f"{cmd}\n")

        print(f"Saved simple commands to {filename}")
        return filename

    def print_commands_summary(self, commands: List[dict]):
        print("\n" + "=" * 50)
        print("COMMAND SUMMARY")
        print("=" * 50)
        command_types = {}
        for cmd in commands:
            ctype = cmd['type']
            command_types[ctype] = command_types.get(ctype, 0) + 1
        for ctype, count in command_types.items():
            print(f"{ctype:<12}: {count} commands")
        print("=" * 50)

    def print_simple_commands(self, simple_commands: List[str]):
        print("\n" + "=" * 50)
        print("SIMPLE COMMAND SEQUENCE (with delays)")
        print("=" * 50)
        for i, cmd in enumerate(simple_commands, 1):
            print(f"{i:3d}. {cmd}")
        print("=" * 50)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python command_generator.py <path_file.json>")
        print("\nOptional calibration args:")
        print("  --cm-per-pixel 0.5          (default: 1.0)")
        print("  --robot-speed 20            (cm/s, default: 20.0)")
        print("  --turn-speed 90             (deg/s, default: 90.0)")
        sys.exit(1)

    path_file = sys.argv[1]

    # Parse optional calibration args
    robot_config = {}
    args = sys.argv[2:]
    for j, arg in enumerate(args):
        if arg == "--cm-per-pixel" and j + 1 < len(args):
            robot_config["cm_per_pixel"] = float(args[j + 1])
        elif arg == "--robot-speed" and j + 1 < len(args):
            robot_config["robot_speed_cm_per_s"] = float(args[j + 1])
        elif arg == "--turn-speed" and j + 1 < len(args):
            robot_config["turn_speed_deg_per_s"] = float(args[j + 1])

    try:
        with open(path_file, 'r') as f:
            data = json.load(f)

        path = [tuple(p) for p in data['points']]

        generator = CommandGenerator(robot_config=robot_config if robot_config else None)

        commands = generator.generate_movement_commands(path)
        generator.save_commands(commands)

        simple_commands = generator.generate_simple_commands(path)
        generator.save_simple_commands(simple_commands)

        generator.print_commands_summary(commands)
        generator.print_simple_commands(simple_commands)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
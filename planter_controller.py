#!/usr/bin/env python3
"""
Planting Robot Controller
---------------------------
A complete system for planning robot paths for planting seeds.

Workflow:
1. Take a photo of the planting area
2. Load the photo and mark planting spots
3. Plan the optimal path through all spots
4. Generate movement commands for the robot
5. Output commands in a simple format the robot can execute

Usage:
    python planter_controller.py --image <path/to/image.jpg> --start <x,y> --end <x,y>
    python planter_controller.py --load-points <points.json>
"""

import argparse
import sys
import os
import json
import cv2
import numpy as np
from point_selector import PointSelector
from path_planner import PathPlanner
from command_generator import CommandGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Planting Robot Path Planner and Command Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--image', '-i',
                       help='Path to the image of planting area')
    parser.add_argument('--load-points', '-l', metavar='FILE',
                       help='Load previously selected points from JSON file')
    parser.add_argument('--start', '-s', metavar='X,Y',
                       help='Start point coordinates (e.g., "50,100")')
    parser.add_argument('--end', '-e', metavar='X,Y',
                       help='End point coordinates (e.g., "200,150")')
    parser.add_argument('--no-visualize', '-nv', action='store_true',
                       help='Skip visualizations')
    parser.add_argument('--output-dir', '-o', default='.',
                       help='Directory to save output files')
    parser.add_argument('--config', '-c', metavar='FILE',
                       help='Robot configuration file (JSON)')

    args = parser.parse_args()

    image_path = None
    points_file = None

    # Step 1: Load or select points
    if args.load_points:
        points_file = args.load_points
        if not os.path.exists(points_file):
            print(f"Error: Points file '{points_file}' not found")
            sys.exit(1)
        print(f"Loading points from {points_file}")
    elif args.image:
        image_path = args.image
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_path}' not found")
            sys.exit(1)

        print("Step 1: Select planting spots")
        print("=" * 50)

        try:
            selector = PointSelector(image_path)
            points = selector.select_points()

            if not points:
                print("No points selected. Exiting.")
                sys.exit(0)

            points_file = selector.save_points(points)
            print(f"\nSelected {len(points)} points")
        except Exception as e:
            print(f"Error selecting points: {e}")
            if not args.no_visualize:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    else:
        print("Error: Either --image or --load-points must be specified")
        parser.print_help()
        sys.exit(1)

    # Step 2: Plan path
    print("\nStep 2: Planning optimal path")
    print("=" * 50)

    try:
        planner = PathPlanner()
        points = planner.load_points(points_file)

        print(f"Loaded {len(points)} points")

        # Parse start and end points if provided
        if args.start:
            start_x, start_y = map(int, args.start.split(','))
            start_point = (start_x, start_y)

            if args.end:
                end_x, end_y = map(int, args.end.split(','))
                end_point = (end_x, end_y)
            else:
                end_point = start_point

            planner.set_start_end(start_point, end_point)

        # Plan and optimize path
        path = planner.optimize_path(max_iterations=200)

        print(f"\nPath planned successfully!")
        print(f"Total points in path: {len(path)}")

        path_file = planner.save_path(path, "planned_path.json")

        # Visualize if requested
        if not args.no_visualize and image_path:
            with open(path_file, 'r') as f:
                data = json.load(f)
                path_points = [tuple(p) for p in data['points']]
            planner.visualize_path(path_points, image_path)

    except Exception as e:
        print(f"Error planning path: {e}")
        if not args.no_visualize:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Step 3: Generate commands
    print("\nStep 3: Generating robot commands")
    print("=" * 50)

    try:
        # Load robot config if provided
        robot_config = None
        if args.config and os.path.exists(args.config):
            with open(args.config, 'r') as f:
                robot_config = json.load(f)
            print(f"Loaded robot configuration from {args.config}")

        generator = CommandGenerator(robot_config)

        # Generate detailed JSON commands
        commands = generator.generate_movement_commands(path)
        generator.save_commands(commands, "robot_commands.json")

        # Generate simple text commands
        simple_commands = generator.generate_simple_commands(path)
        generator.save_simple_commands(simple_commands, "simple_commands.txt")

        # Print summary
        generator.print_commands_summary(commands)
        generator.print_simple_commands(simple_commands)

        print("\n" + "=" * 50)
        print("SUCCESS!")
        print("=" * 50)
        print(f"All planning completed successfully!")
        print(f"\nOutput files:")
        print(f"  - Selected points: points.json")
        print(f"  - Planned path: planned_path.json")
        print(f"  - Detailed commands: robot_commands.json")
        print(f"  - Simple commands: simple_commands.txt")

        if image_path:
            print(f"  - Path visualization: path_visualization.png")

        print("\nNext steps:")
        print("1. Review the commands in simple_commands.txt")
        print("2. Send commands to your robot via your communication method")
        print("3. Place robot at the start position before execution")
        print("4. Monitor robot during first run")

    except Exception as e:
        print(f"Error generating commands: {e}")
        if not args.no_visualize:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def interactive_mode():
    """Run in interactive mode if no arguments provided"""
    print("=== Planting Robot Controller ===")
    print("Interactive Mode\n")

    # Get image path
    image_path = input("Enter path to your planting area image: ").strip()

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    try:
        # Step 1: Select points
        print("\nStep 1: Select planting spots")
        print("Instructions will appear in the image window...")

        selector = PointSelector(image_path)
        points = selector.select_points()

        if not points:
            print("No points selected. Goodbye!")
            return

        points_file = selector.save_points(points)

        # Step 2: Optional start/end points
        print("\nOptional: Set start and end points")
        start_point = None
        end_point = None

        response = input("Set custom start point? (y/n): ").lower()
        if response == 'y':
            x = int(input("Start X coordinate: "))
            y = int(input("Start Y coordinate: "))
            start_point = (x, y)

            response = input("Set different end point? (y/n): ").lower()
            if response == 'y':
                x = int(input("End X coordinate: "))
                y = int(input("End Y coordinate: "))
                end_point = (x, y)
            else:
                end_point = start_point

        # Step 3: Plan path
        print("\nStep 2: Planning path...")
        planner = PathPlanner()
        planner.load_points(points_file)

        if start_point:
            planner.set_start_end(start_point, end_point)

        path = planner.optimize_path()
        path_file = planner.save_path(path)

        planner.visualize_path(path, image_path)

        # Step 4: Generate commands
        print("\nStep 3: Generating commands...")
        generator = CommandGenerator()
        commands = generator.generate_movement_commands(path)
        generator.save_commands(commands)

        simple_commands = generator.generate_simple_commands(path)
        generator.save_simple_commands(simple_commands)

        generator.print_commands_summary(commands)

        print("\nAll done! Commands saved to:")
        print("  - robot_commands.json (detailed)")
        print("  - simple_commands.txt (simple)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        main()

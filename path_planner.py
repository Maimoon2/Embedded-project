import json
import math
import numpy as np
from typing import List, Tuple

class PathPlanner:
    def __init__(self):
        self.points = []
        self.start_point = None
        self.end_point = None

    def load_points(self, filename: str) -> List[Tuple[int, int]]:
        """Load points from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        self.points = [(int(p[0]), int(p[1])) for p in data['points']]
        return self.points

    def distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def set_start_end(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Set start and end points"""
        self.start_point = start
        self.end_point = end
        print(f"Start point set to: {start}")
        print(f"End point set to: {end}")

    def nearest_neighbor_path(self) -> List[Tuple[int, int]]:
        """Generate path using nearest neighbor algorithm"""
        if not self.points:
            raise ValueError("No points loaded")

        unvisited = self.points.copy()
        path = []

        if self.start_point:
            current = self.start_point
            path.append(current)
            print(f"Starting at: {current}")
        else:
            current = unvisited.pop(0)
            path.append(current)

        unvisited_set = set(unvisited)
        total_distance = 0

        while unvisited_set:
            nearest = min(unvisited_set, key=lambda p: self.distance(current, p))
            dist = self.distance(current, nearest)
            total_distance += dist
            path.append(nearest)
            unvisited_set.remove(nearest)
            current = nearest

        if self.end_point and self.end_point != path[-1]:
            total_distance += self.distance(current, self.end_point)
            path.append(self.end_point)

        print(f"Path planned with {len(path)} points")
        print(f"Total estimated distance: {total_distance:.2f} pixels")

        return path

    def optimize_path(self, max_iterations: int = 100) -> List[Tuple[int, int]]:
        """Optimize path using 2-opt algorithm"""
        path = self.nearest_neighbor_path()

        if len(path) < 4:
            return path

        best_path = path.copy()
        best_distance = self.calculate_path_distance(path)

        improved = True
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1

            for i in range(1, len(path) - 2):
                for j in range(i + 2, len(path)):
                    new_path = self.two_opt_swap(path, i, j)
                    new_distance = self.calculate_path_distance(new_path)

                    if new_distance < best_distance:
                        best_path = new_path
                        best_distance = new_distance
                        improved = True
                        path = new_path
                        break

                if improved:
                    break

        print(f"Optimization completed after {iteration} iterations")
        print(f"Optimized path distance: {best_distance:.2f} pixels")

        return best_path

    def two_opt_swap(self, path: List[Tuple[int, int]], i: int, j: int) -> List[Tuple[int, int]]:
        """Perform 2-opt swap on path"""
        new_path = path[:i]
        new_path.extend(reversed(path[i:j]))
        new_path.extend(path[j:])
        return new_path

    def calculate_path_distance(self, path: List[Tuple[int, int]]) -> float:
        """Calculate total distance of a path"""
        if not path or len(path) < 2:
            return 0

        total = 0
        for i in range(len(path) - 1):
            total += self.distance(path[i], path[i + 1])
        return total

    def save_path(self, path: List[Tuple[int, int]], filename: str = "path.json"):
        """Save planned path to JSON file"""
        data = {
            "points": [(int(p[0]), int(p[1])) for p in path],
            "num_points": len(path),
            "total_distance": self.calculate_path_distance(path)
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Path saved to {filename}")
        return filename

    def visualize_path(self, path: List[Tuple[int, int]], image_path: str, output_path: str = "path_visualization.png"):
        """Visualize the planned path on the image"""
        try:
            import cv2
            import numpy as np

            image = cv2.imread(image_path)
            if image is None:
                print(f"Warning: Could not load image from {image_path}")
                return

            path_image = image.copy()

            for i, point in enumerate(path):
                cv2.circle(path_image, point, 8, (0, 255, 0), -1)
                cv2.putText(path_image, str(i + 1), (point[0] + 10, point[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            for i in range(len(path) - 1):
                cv2.line(path_image, path[i], path[i + 1], (255, 0, 0), 2)

            cv2.imwrite(output_path, path_image)
            print(f"Path visualization saved to {output_path}")

            cv2.namedWindow("Path Visualization", cv2.WINDOW_NORMAL)
            cv2.imshow("Path Visualization", path_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        except ImportError:
            print("OpenCV not available for visualization")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python path_planner.py <points_file.json>")
        sys.exit(1)

    planner = PathPlanner()
    points_file = sys.argv[1]

    try:
        planner.load_points(points_file)
        path = planner.optimize_path()

        print(f"\nPlanned path order:")
        for i, point in enumerate(path):
            print(f"{i + 1}. {point}")

        planner.save_path(path)

        data = json.load(open(points_file))
        if 'image_path' in data:
            planner.visualize_path(path, data['image_path'])

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

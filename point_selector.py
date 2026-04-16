import cv2
import numpy as np
import json
import os

class PointSelector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image from {image_path}")

        self.clone = self.image.copy()
        self.points = []
        self.window_name = "Planting Spot Selector"

    def click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv2.circle(self.clone, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(self.clone, str(len(self.points)), (x + 10, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow(self.window_name, self.clone)
            print(f"Point {len(self.points)} selected at: ({x}, {y})")

        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.points:
                self.points.pop()
                self.clone = self.image.copy()
                for i, point in enumerate(self.points):
                    cv2.circle(self.clone, point, 5, (0, 255, 0), -1)
                    cv2.putText(self.clone, str(i + 1), (point[0] + 10, point[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.imshow(self.window_name, self.clone)
                print("Last point removed")

    def select_points(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.click_event)
        cv2.imshow(self.window_name, self.clone)

        print("\nInstructions:")
        print("- LEFT CLICK to select a planting spot")
        print("- RIGHT CLICK to remove the last point")
        print("- Press 'q' to finish and save points")
        print("- Press 'c' to clear all points")
        print("- Press 'r' to reset the image")

        while True:
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('c'):
                self.points = []
                self.clone = self.image.copy()
                cv2.imshow(self.window_name, self.clone)
                print("All points cleared")
            elif key == ord('r'):
                self.clone = self.image.copy()
                for i, point in enumerate(self.points):
                    cv2.circle(self.clone, point, 5, (0, 255, 0), -1)
                    cv2.putText(self.clone, str(i + 1), (point[0] + 10, point[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.imshow(self.window_name, self.clone)

        cv2.destroyAllWindows()
        return self.points

    def save_points(self, points, output_file="points.json"):
        data = {
            "image_path": os.path.abspath(self.image_path),
            "points": points,
            "num_points": len(points)
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nSaved {len(points)} points to {output_file}")
        return output_file

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python point_selector.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        selector = PointSelector(image_path)
        points = selector.select_points()

        if points:
            selector.save_points(points)
        else:
            print("No points selected!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

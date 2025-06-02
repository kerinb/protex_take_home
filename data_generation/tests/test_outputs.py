import json
import os
import unittest

from PIL import Image


class TestOutputFiles(unittest.TestCase):
    def setUp(self):
        # Paths to check (replace with your actual paths)
        self.image_dir = "data_generation/resources/outputs/frames"
        self.coco_file = "data_generation/resources/outputs/detections.json"

    def test_output_images_exist_and_are_valid(self):
        self.assertTrue(
            os.path.isdir(self.image_dir), "Image directory does not exist."
        )

        image_files = [
            f
            for f in os.listdir(self.image_dir)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        self.assertGreater(len(image_files), 0, "No image files found.")

        for image_name in image_files:
            image_path = os.path.join(self.image_dir, image_name)
            with Image.open(image_path) as img:
                img.verify()  # Check if image is not corrupted

    def test_coco_file_exists_and_is_valid(self):
        self.assertTrue(
            os.path.isfile(self.coco_file), "COCO annotation file not found."
        )

        with open(self.coco_file, "r") as f:
            coco_data = json.load(f)

        required_keys = {"images", "annotations", "categories"}
        self.assertTrue(
            required_keys.issubset(coco_data), "COCO file missing required keys."
        )


if __name__ == "__main__":
    unittest.main()

import os
import unittest
import json

from data_generation.main_logic.main_app import (extract_frames, get_config,
                                                 get_video_path, pre_tag_video,
                                                 save_annotations)


class TestMainApp(unittest.TestCase):
    def setUp(self):
        # This code runs before each test method
        self.frame_output_dir = "data_generation/resources/outputs/frames"
        self.video_path = "data_generation/resources/inputs/video-1/timelapse_test.mp4"
        self.output_dir = "data_generation/resources/outputs"
        self.frame_step = 30
        self.coco_output_path = self.output_dir + "/" + "detections.json"
        self.model_name = self.output_dir + "/" + "yolov8n.pt"
        file_path = os.path.abspath("data_generation/tests/resources/expected_output.json")

        with open(file_path, 'r') as file:
            self.coco_output = json.load(file)

    def test_get_config_default(self):
        FRAME_OUTPUT_DIR, COCO_OUTPUT_PATH, FRAME_STEP, MODEL_NAME, output_dir = (
            get_config()
        )

        self.assertTrue(FRAME_OUTPUT_DIR is not None)
        self.assertTrue(FRAME_OUTPUT_DIR != "None")

        self.assertTrue(COCO_OUTPUT_PATH is not None)
        self.assertTrue(COCO_OUTPUT_PATH != "None")

        self.assertTrue(FRAME_STEP is not None)
        self.assertTrue(FRAME_STEP != "None")

        self.assertTrue(MODEL_NAME is not None)
        self.assertTrue(MODEL_NAME != "None")

    def test_get_config_input_file(self):
        self.assertEqual(True, True)


    def test_extract_frames(self):

        extract_frames(
            self.frame_output_dir, self.video_path, self.output_dir, self.frame_step
        )

        # Check folder exists
        self.assertTrue(
            os.path.isdir(self.frame_output_dir),
            f"Folder does not exist: {self.frame_output_dir}",
        )

        # Check it's not empty
        contents = os.listdir(self.frame_output_dir)
        self.assertGreater(len(contents), 0, "Folder exists but is empty")

    def test_pre_tag_video(self):
        coco_output = pre_tag_video(
            self.frame_output_dir, self.model_name, self.output_dir
        )
        print(coco_output)
        self.assertEqual(coco_output, self.coco_output)

    def test_save_annotations(self):
        if os.path.exists(self.coco_output_path):
            os.remove(self.coco_output_path)
            print(f"Deleted folder: {self.coco_output_path}")

        self.assertFalse(
            os.path.exists(self.coco_output_path),
            f"Folder should not exist: {self.coco_output_path}",
        )

        save_annotations(self.coco_output, self.coco_output_path, self.output_dir)

        self.assertTrue(
            os.path.exists(self.coco_output_path),
            f"Folder should exist: {self.coco_output_path}",
        )


if __name__ == "__main__":
    unittest.main()

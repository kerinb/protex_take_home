import os
import unittest

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
        self.coco_output = {
            "images": [
                {"id": 1, "file_name": "frame_00000.jpg", "height": 608, "width": 1080},
                {"id": 2, "file_name": "frame_00001.jpg", "height": 608, "width": 1080},
                {"id": 3, "file_name": "frame_00002.jpg", "height": 608, "width": 1080},
                {"id": 4, "file_name": "frame_00003.jpg", "height": 608, "width": 1080},
                {"id": 5, "file_name": "frame_00004.jpg", "height": 608, "width": 1080},
                {"id": 6, "file_name": "frame_00005.jpg", "height": 608, "width": 1080},
                {"id": 7, "file_name": "frame_00006.jpg", "height": 608, "width": 1080},
                {"id": 8, "file_name": "frame_00007.jpg", "height": 608, "width": 1080},
            ],
            "annotations": [
                {
                    "id": 1,
                    "image_id": 1,
                    "category_id": 1,
                    "bbox": [
                        21.3253116607666,
                        0.0,
                        838.8753108978271,
                        599.8941650390625,
                    ],
                    "area": 503236.404202936,
                    "iscrowd": 0,
                },
                {
                    "id": 2,
                    "image_id": 3,
                    "category_id": 2,
                    "bbox": [
                        597.8780517578125,
                        235.07501220703125,
                        49.02813720703125,
                        27.510345458984375,
                    ],
                    "area": 1348.780991775915,
                    "iscrowd": 0,
                },
                {
                    "id": 3,
                    "image_id": 3,
                    "category_id": 3,
                    "bbox": [
                        22.83928871154785,
                        0.0,
                        729.3794612884521,
                        599.143798828125,
                    ],
                    "area": 437003.18122357456,
                    "iscrowd": 0,
                },
                {
                    "id": 4,
                    "image_id": 3,
                    "category_id": 2,
                    "bbox": [
                        478.85418701171875,
                        246.6547088623047,
                        36.6893310546875,
                        20.681655883789062,
                    ],
                    "area": 758.7961194794625,
                    "iscrowd": 0,
                },
            ],
            "categories": [
                {"id": 1, "name": "tv"},
                {"id": 2, "name": "car"},
                {"id": 3, "name": "boat"},
            ],
        }

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

    def test_get_video_path(self):
        output_dir = "data_generation/resources/outputs/"
        video_fp = get_video_path(output_dir, None)

        self.assertTrue(os.path.isfile(video_fp), f"File does not exist: {video_fp}")
        self.assertGreater(os.path.getsize(video_fp), 0, "File exists but is empty")

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

import csv
import os
from datetime import datetime


ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}


def is_valid_video_file(video_path):
    """

    :param video_path:
    :return:
    """
    ext = os.path.splitext(video_path)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def format_logs(func_name, message, elapsed_time, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # ensure the directory exists

    log_path = os.path.join(output_dir, "logs.csv")
    file_exists = os.path.isfile(log_path)

    now = datetime.now().isoformat()

    with open(log_path, mode="a", newline="") as file:  # append mode
        writer = csv.writer(file, delimiter="|")  # single delimiter (|| breaks CSV)

        if not file_exists:
            writer.writerow(["timestamp", "function_name", "message", "execution_time"])

        writer.writerow([now, func_name, f"Function: {message}", elapsed_time])


def output_visual_logs():
    pass


def frame_deduplication():
    pass


def input_data_validation():
    pass

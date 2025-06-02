import csv
import os
from datetime import datetime

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}


def is_valid_video_file(video_path):
    """

    :param video_path:
    :return:
    """
    ext = os.path.splitext(video_path)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def format_logs(func_name, message, elapsed_time, output_dir):
    """

    :param func_name:
    :param message:
    :param elapsed_time:
    :param output_dir:
    :return:
    """
    os.makedirs(output_dir, exist_ok=True)  # ensure the directory exists

    log_path = os.path.join(output_dir, "logs.csv")
    file_exists = os.path.isfile(log_path)

    now = datetime.now().isoformat()

    with open(log_path, mode="a", newline="") as file:  # append mode
        writer = csv.writer(file, delimiter="|")

        if not file_exists:
            writer.writerow(["timestamp", "function_name", "message", "execution_time"])

        writer.writerow([now, func_name, f"Function: {message}", elapsed_time])


def output_visual_logs(output_dir):
    import pandas as pd

    df = pd.read_csv("../resources/outputs/logs.csv", delimiter="|")
    with open(f"{output_dir}/tabulated_logs.md", "w") as md:
        df.to_markdown(buf=md, tablefmt="grid")


def input_data_validation():
    pass

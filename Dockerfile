FROM python:3.9

# Set a working directory (inside the container)
WORKDIR /app

# Copy contents into the container’s working directory
COPY . .

ENV INPUT_PATH="data_generation/resources/input/video-1" \
    OUTPUT_PATH="data_generation/resources/output/" \
    MODEL_CONFIG="data_generation/resources/input/config"

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 && \
    rm -rf /var/lib/apt/lists/*


RUN echo "INPUT_PATH is: $INPUT_PATH" && \
    echo "OUTPUT_PATH is: $OUTPUT_PATH" && \
    echo "MODEL_CONFIG is: $MODEL_CONFIG" && \
    # RUN apt-get update && apt-get install -y libgl1-mesa-glx && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "data_generation/main_logic/main_app.py"]

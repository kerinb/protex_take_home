FROM python:3.9

ENV INPUT_PATH="data_generation/resources/inputs/video-1" \
    OUTPUT_PATH="data_generation/resources/outputs/" \
    MODEL_CONFIG="data_generation/resources/inputs/config"

WORKDIR /app

COPY requirements/ requirements/
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt



COPY . .

CMD ["python", "data_generation/main_logic/main_app.py"]

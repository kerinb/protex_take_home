FROM python:3.9

ADD / .

ENV INPUT_PATH="data_generation/resources/input/video"
ENV OUTPUT_PATH="data_generation/resources/output/"
ENV MODEL_CONFIG="data_generation/resources/input/config"

RUN echo "INPUT_PATH is: $INPUT_PATH"
RUN echo "OUTPUT_PATH is: $OUTPUT_PATH"
RUN echo "MODEL_CONFIG is: $MODEL_CONFIG"

RUN pip install -r requirements.txt

CMD ["python", "main/main_app.py"]
FROM tensorflow/tensorflow:2.10.0

RUN pip install --upgrade pip

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY bird_data /bird_data
COPY api /api
COPY uploaded_images /uploaded_images
COPY birdies_code /birdies_code
COPY dirty_model_5 /dirty_model_5

# RUN pip install .

#COPY Makefile /Makefile
#RUN make reset_local_files

#CMD uvicorn api.api:app --host 0.0.0.0 --port $PORT

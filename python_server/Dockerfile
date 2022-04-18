FROM python:3.8.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 
# RUN apt-get install libgl1 -y

RUN mkdir /app
WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "image_to_text:app", "--bind", "0.0.0.0:8000", "--reload"]
# CMD ["uvicorn", "image_to_text:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim-bullseye

# for opencv2 (a lot of packages; maybe too much; but works)
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR app

CMD ["sh", "start.sh"]

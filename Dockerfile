FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y wget git\
    && wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_97.0.4692.71-1_amd64.deb

RUN apt install -y ./google-chrome-stable_97.0.4692.71-1_amd64.deb \
    && apt-get -f install

ADD ./backend /app

RUN pip install --no-cache-dir -r /app/deploy/requirements.txt

EXPOSE 8000
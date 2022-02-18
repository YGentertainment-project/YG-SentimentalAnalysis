FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y wget git\
    && wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_97.0.4692.71-1_amd64.deb

RUN apt install -y ./google-chrome-stable_97.0.4692.71-1_amd64.deb \
    && apt-get -f install

RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential

ADD ./backend /app

RUN pip3 install --no-cache-dir -r /app/deploy/requirements.txt

RUN bash /app/deploy/entrypoint.sh

EXPOSE 8000
FROM tensorflow/tensorflow:2.7.0-gpu-jupyter

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update \
    && apt-get install -y wget \
    fonts-liberation libasound2 libatk-bridge2.0-0 libcairo2 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0\
    libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils \
    && wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_97.0.4692.71-1_amd64.deb

RUN dpkg -i ./google-chrome-stable_97.0.4692.71-1_amd64.deb \
    && apt-get install -f

RUN pip install -r requirements.txt

EXPOSE 8000

COPY ./web /app/
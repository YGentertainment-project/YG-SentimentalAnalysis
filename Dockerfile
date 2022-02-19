FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime
ENV YG_ENV production

RUN apt-get update \
    && apt-get install -y wget git\
    && wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_97.0.4692.71-1_amd64.deb

RUN apt install -y ./google-chrome-stable_97.0.4692.71-1_amd64.deb \
    && apt-get -f install

# mysqlclient, gcc, wget, curl 설치
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential gcc wget

# pip 업그레이드
RUN cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    ln -s /usr/bin/pip3 pip && \
    pip3 install --upgrade pip

# apt cleanse
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD ./backend /app
WORKDIR /app

RUN pip install --no-cache-dir -r /app/deploy/requirements.txt

ARG DATA=/data
RUN mkdir -p ${DATA}/config
RUN if [ ! -f "${DATA}/config/secret.key" ] ; then echo $(cat /dev/urandom | head -1 | md5sum | head -c 32) > "${DATA}/config/secret.key" ; fi

# mecab 설치 및 사용자 사전 적용
RUN bash /app/deploy/entrypoint.sh

EXPOSE 8000
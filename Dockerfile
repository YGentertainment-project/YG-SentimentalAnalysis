FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime
ENV YG_ENV production

ADD ./backend /app
WORKDIR /app

RUN apt-get update \
    && apt-get install -y wget git curl make gcc g++ default-jdk default-jre python-dev python3-dev \
    fonts-liberation libasound2 libatk-bridge2.0-0 libcairo2 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 \
    libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils \
    && wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_97.0.4692.71-1_amd64.deb

# 향후에 필요하면 크롬 드라이버 설치해주기
# RUN dpkg -i ./google-chrome-stable_97.0.4692.71-1_arm64.deb \
#    && apt-get install -f

# pip 업그레이드
RUN cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    ln -s /usr/bin/pip3 pip && \
    pip3 install --upgrade pip

# apt cleanse
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install konlpy JPype1-py3

RUN curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh | bash -s

RUN apt-get update \
    && apt-get install -y wget

# py-hanspell 설치
WORKDIR /app
RUN mkdir py-hanspell
RUN git clone https://github.com/ssut/py-hanspell.git /app/py-hanspell
WORKDIR /app/py-hanspell
RUN python setup.py install


WORKDIR /app
RUN rm -rf /py-hanspell
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y default-libmysqlclient-dev

RUN pip install --no-cache-dir -r /app/deploy/requirements.txt
RUN pip install sentencepiece
ARG DATA=/data
RUN mkdir -p ${DATA}/config
RUN if [ ! -f "${DATA}/config/secret.key" ] ; then echo $(cat /dev/urandom | head -1 | md5sum | head -c 32) > "${DATA}/config/secret.key" ; fi


EXPOSE 8000
#!/bin/bash

apt update
apt-get -y install openjdk-8-jdk python-dev python3-dev curl
pip3 install konlpy jpype1-py3

bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)

cd /tmp/mecab-ko-dic-2.1.1-20180720
ldconfig
ldconfig -p | grep /usr/local/lib

cd /tmp/mecab-0.996-ko-0.9.2
./configure
make
make check
make install

cd /tmp/mecab-ko-dic-2.1.1-20180720
./autogen.sh
./configure
make
make install

cp /app/deploy/*.csv /tmp/mecab-ko-dic-2.1.1-20180720/user-dic/
cd /tmp/mecab-ko-dic-2.1.1-20180720/tools
./add-userdic.sh
cd /tmp/mecab-ko-dic-2.1.1-20180720
make install
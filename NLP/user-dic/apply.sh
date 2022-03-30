cp ./user-dic/*.csv /tmp/mecab-ko-dic-2.1.1-20180720/user-dic/
cd /tmp/mecab-ko-dic-2.1.1-20180720/tools
./add-userdic.sh
cd /tmp/mecab-ko-dic-2.1.1-20180720
make install

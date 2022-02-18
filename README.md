# SKKU_YGE_COOP
SKKU &amp; YGEntertainment COOP



## Rabbitmq

```
$ docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management 
```


## Celery worker-beat
```
$ celery -A crawler worker --beat --loglevel=info
```



## py-hansepll pip 설치시 오류

requirements.txt에 따라 설치할 때 py-hanspell 설치 오류가 발생하면 아래의 방법을 사용하시길 바랍니다.

1. py-hanspell clone - 적당한 곳에 clone 진행(프로젝트을 실행시킨 가상환경이 켜져있는 터미널로 진행하세요)


```
$ git clone https://github.com/ssut/py-hanspell
```

2. clone 된 프로젝트 폴더로 이동해 

```
$ python setup.py install
```

3. 설치 확인 - py-hanspell 이 있는지 확인
```
$ pip freeze
```


위 과정으로 진행하면 hanspell을 설치 할 수 있습니다.

[출처] - https://hasiki.tistory.com/71

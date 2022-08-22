FROM docker.io/tjbredow/pigeon-operator

RUN pip install kubernetes

COPY . /app

WORKDIR /app

CMD ["sh","-c","python3","operator.py"]
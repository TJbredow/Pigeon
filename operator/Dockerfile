FROM docker.io/tjbredow/pigeon-operator

RUN pip install kubernetes

COPY . /app

WORKDIR /app

CMD ["python3","pigeonOperator.py"]
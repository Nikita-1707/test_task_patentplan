FROM python:3.10

RUN mkdir /tenderplan

WORKDIR /tenderplan

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
FROM python:3.9.5-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /etl
COPY requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . /app/etl
WORKDIR /app/etl

CMD ["python", "app.py"]
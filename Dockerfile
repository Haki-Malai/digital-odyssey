FROM python:3.10.10-slim-buster

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN FLASK_CONFIG=testing FLASK_APP=index.py flask test

ENV FLASK_CONFIG=production
ENV FLASK_APP=index

RUN flask fake
RUN ls

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "index:app", "--conf", "gunicorn.conf.py"]

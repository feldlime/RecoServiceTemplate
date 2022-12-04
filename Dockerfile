FROM python:3.8-slim-buster

ENV PYTHONOPTIMIZE true
ENV DEBIAN_FRONTEND noninteractive
# setup timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/app

RUN apt-get -y update \
    && apt-get install -y gcc libgtk2.0-dev build-essential python3-dev libusb-0.1-4 \
    && apt-get autoremove -y \
    && apt-get clean

RUN pip install --upgrade --no-cache-dir --no-input  pip setuptools wheel pipenv

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "main:app", "-c", "gunicorn.config.py"]

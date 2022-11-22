FROM python:3.8-buster as build

COPY . .
RUN pip install -U --no-cache-dir pip poetry setuptools wheel && \
    poetry build -f wheel && \
    poetry export -f requirements.txt -o requirements.txt --without-hashes && \
    pip wheel -w dist -r requirements.txt


FROM python:3.8-slim-buster as runtime

WORKDIR /usr/src/app

ENV PYTHONOPTIMIZE true
ENV DEBIAN_FRONTEND noninteractive

# setup timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY --from=build dist dist
COPY --from=build main.py gunicorn.config.py ./


RUN apt-get update && \
    apt-get install libgomp1 && \
    pip install gdown && \
    gdown --id '1HCALVMCHKVPekBPq8_8HXW6oubM5Kgjv' && \
    gdown --id '1-FOStMxn6Z-VA22xE70aeLa0noWZEfIq' && \
    pip install -U --no-cache-dir pip dist/*.whl && \
    rm -rf dist

CMD ["gunicorn", "main:app", "-c", "gunicorn.config.py"]

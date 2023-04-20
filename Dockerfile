FROM python:3.8 as build

ENV APP_DIR /usr/src/app
WORKDIR $APP_DIR

COPY . $APP_DIR

RUN pip install -U --no-cache-dir pip poetry setuptools wheel && \
	poetry add implicit==0.4.4 lightfm==1.16 --lock && \
    poetry build -f wheel && \
    poetry export -f requirements.txt -o requirements.txt --without-hashes && \
    pip wheel -w dist -r requirements.txt


FROM python:3.8 as runtime

ENV APP_DIR /usr/src/app
WORKDIR $APP_DIR

COPY . $APP_DIR

ENV PYTHONOPTIMIZE true
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUTF8 1

# setup timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY --from=build $APP_DIR/dist $APP_DIR/dist
#COPY --from=build main.py gunicorn.config.py ./

RUN pip install -U --no-cache-dir pip $APP_DIR/dist/*.whl && \
    rm -rf $APP_DIR/dist

# OpenMP (Multi Processing)
ENV OMP_NUM_THREADS 12

# NMSLIB
# RUN pip install --no-binary :all: nmslib

#CMD ["gunicorn", "main:app", "-c", "gunicorn.config.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

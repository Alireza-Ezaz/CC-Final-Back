FROM python:3.8-alpine AS build
ARG BUILD_DEPS="build-base gcc libffi-dev openssl-dev"

 

RUN apk add --no-cache ${BUILD_DEPS} \

 && python -m venv .venv \

 && .venv/bin/pip install --no-cache-dir -U pip setuptools

COPY . .
RUN pip3 install -r requirements.txt


FROM python:3.8-alpine AS target
ARG RUNTIME_DEPS="libcrypto1.1 libssl1.1"

RUN apk add --no-cache ${RUNTIME_DEPS}
COPY --from=build . .

CMD [ "python3", "app.py"]
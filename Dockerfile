FROM python:2.7.14-alpine3.7 as build

ARG BUILD_ARTIFACTS_AUDIT=/audit/*

COPY ./requirements*.txt ./

# Install requirements
RUN pip install -r requirements_dev.txt

# Audit
RUN mkdir /audit/
RUN pip freeze | tee /audit/pip.lock


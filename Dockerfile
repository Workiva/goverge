FROM python:3.7.0 as build

ARG BUILD_ARTIFACTS_AUDIT=/audit/
ARG BUILD_ARTIFACTS_AUDIT=/goverge

COPY ./requirements*.txt ./

# Install requirements
RUN pip install -r requirements_dev.txt

# Install pyinstaller to package goverge as a binary
RUN pip install pyinstaller

# Audit
RUN mkdir /audit/
RUN pip freeze > /audit/pip.lock

COPY ./goverge ./goverge
RUN cd goverge && pyinstaller --onefile --windowed main.py
RUN cp goverge/dist/main ./goverge

FROM scratch

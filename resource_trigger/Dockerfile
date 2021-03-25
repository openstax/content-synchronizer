FROM python:3.8.3-alpine3.11

WORKDIR /opt/resource/

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install requests

COPY check.py /opt/resource/check
COPY in.py /opt/resource/in
COPY out.py /opt/resource/out
COPY utils.py /opt/resource/utils.py

RUN chmod +x /opt/resource/check /opt/resource/in /opt/resource/out
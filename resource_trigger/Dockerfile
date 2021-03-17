FROM python:3-alpine

WORKDIR /opt/resource/

COPY dist/concourse-version-checker-resource-*.tar.gz .
RUN pip install concourse-version-checker-resource-*.tar.gz

COPY /src/check.py /opt/resource/check
COPY /src/in.py /opt/resource/in
COPY /src/out.py /opt/resource/out
COPY /src/utils.py /opt/resource/utils.py

RUN chmod +x /opt/resource/check /opt/resource/in /opt/resource/out
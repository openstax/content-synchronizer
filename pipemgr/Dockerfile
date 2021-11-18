FROM openstax/python3-poetry:20211117.174217 as builder
WORKDIR /app

# Build the pipemgr package with poetry
COPY . .
RUN poetry build -f wheel

# Get fly cli
RUN apt-get update && \
    apt-get install curl && \
    curl 'https://concourse-v7.openstax.org/api/v1/cli?arch=amd64&platform=linux' -o fly

# ------

# Create the environment to run in
FROM python:3.8-alpine
LABEL maintainer="OpenStax Content Engineering"
ENV ENV="/root/.ashrc"
WORKDIR /app
COPY --from=builder /app .
RUN cd env && mv $(ls -A) ~ && cd - && \
    rmdir env && \
    chmod +x fly && \
    mv fly /usr/local/bin && \
    pip install dist/pipemgr-*.whl && \
    rm -rf dist
CMD ["/bin/sh"]
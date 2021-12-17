FROM openstax/python3-poetry:20211117.174217 as builder
WORKDIR /app

# Build the pipemgr package with poetry
COPY . .
RUN poetry build -f wheel

# ------

# Create the environment to run in
FROM openstax/python3-base:20211117.170559
ARG CONCOURSE_USERNAME
ARG CONCOURSE_PASSWORD
ENV CONCOURSE_USERNAME=${CONCOURSE_USERNAME} CONCOURSE_PASSWORD=${CONCOURSE_PASSWORD}
WORKDIR /app
COPY --from=builder /app .
RUN cd env && mv $(ls -A) ~ && cd - && \
    rmdir env && \
    pip install --no-cache-dir dist/pipemgr-*.whl && \
    rm -rf dist
CMD ["/bin/bash"]

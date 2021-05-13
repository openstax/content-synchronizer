FROM python:3.8.3-alpine3.11

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY licenses/* .
COPY create_book_repo.py .

ENTRYPOINT [ "executable" ]
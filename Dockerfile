FROM python:3.8-alpine

WORKDIR /usr/src/app
RUN apk add --no-cache zip \
    gcc musl-dev
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "server.py", "--debug", "--delay", "1", "--photo_dir", "test_photos", "--fragment", "100"]
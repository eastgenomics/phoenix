FROM python:3

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

LABEL org.opencontainers.image.source=https://github.com/eastgenomics/phoenix
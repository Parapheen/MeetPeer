FROM python:3.8-slim-buster
WORKDIR /meetpeer
COPY bot/ bot/
COPY Makefile .
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["make polling"]
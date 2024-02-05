FROM python:3.12-bookworm

RUN apt-get -y update
RUN apt-get install -y chromium chromium-driver dnsutils

RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "-u", "app.py"]

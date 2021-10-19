FROM python:3

COPY . /gertrude

WORKDIR /gertrude

RUN pip install --upgrade -r requirements.txt
RUN apt -y update && \
    apt -y upgrade && \
    apt install -y ffmpeg

CMD python run.py
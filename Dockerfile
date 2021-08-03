FROM python:3.8.5

COPY ./mediaserver /mediaserver
COPY ./.env /

COPY ./requirements.txt /
RUN pip install -r requirements.txt
RUN pip install pydantic[dotenv]

EXPOSE 7000

WORKDIR /mediaserver

CMD ["python", "main.py"]

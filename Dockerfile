FROM python:3.8

COPY . /myshorturl/

WORKDIR /myshorturl

VOLUME /myshorturl

RUN pip install -r requirements.txt

ENV FLASK_APP=myshorturl.py
ENV FLASK_ENV=development
ENV SECRET_KEY=thisjacketisblue

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]
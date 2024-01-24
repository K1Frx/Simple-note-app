FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["waitress-serve", "--port=8000", "mysite.wsgi:application"]
FROM python:3.9.16-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#Expose Nginx Port
EXPOSE 80

ENTRYPOINT ["python"]

CMD ["app.py"]
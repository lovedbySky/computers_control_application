FROM ubuntu

WORKDIR /var/www/panel

COPY . .

EXPOSE 5000
EXPOSE 5002

VOLUME ["/var/www/panel/bots"]
VOLUME ["/var/www/panel/database"]
VOLUME ["/var/www/panel/files"]

RUN apt update -y && apt install python3 -y && apt install pip -y && python3 -m pip install -r requirements.txt

CMD python3 -m gunicorn -b 0.0.0.0:5000 -w 4 project:app

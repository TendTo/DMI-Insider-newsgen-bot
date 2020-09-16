FROM python:3.8.5

ARG TOKEN=none
ARG WEBHOOK_ENABLED=false
ARG WEB_URL=none

ENV BOT_DIR    /app

WORKDIR $BOT_DIR

COPY requirements.txt .
#Install requirements
RUN pip3 install -r requirements.txt

COPY . .
#Setup settings and databases
RUN mv config/settings.yaml.dist config/settings.yaml &&\
  python3 settings.py -t ${TOKEN} -w ${WEBHOOK_ENABLED} -u ${WEB_URL}

#Start the bot
CMD [ "python3", "main.py" ]
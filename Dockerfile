FROM python:3.8.5-slim-buster

ARG TOKEN=none
ARG WEBHOOK_ENABLED=false
ARG WEB_URL=none
ARG GROUPS=none

ENV BOT_DIR    /app

WORKDIR $BOT_DIR

COPY requirements.txt .
#Install requirements
RUN pip3 install --upgrade pip &&\
  pip3 install -r requirements.txt

COPY . .
#Setup settings.yaml
RUN mv config/settings.yaml.dist config/settings.yaml &&\
  python3 settings.py -t ${TOKEN} -w ${WEBHOOK_ENABLED} -u ${WEB_URL} -g ${GROUPS}

#Start the bot
CMD [ "python3", "main.py" ]
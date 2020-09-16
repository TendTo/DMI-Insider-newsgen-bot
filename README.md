# DMI-Insider-newsgen-bot

### Usage
Live version on telegram [**@testtendTo_bot**](https://telegram.me/testtendTo_bot) (only temporarily)

## :wrench: Setting up a local istance

#### System requirements
- Python 3
- python-pip3

#### Install with *pip3*
Listed in requirements.txt
- python-telegram-bot
- requests
- PyYAML
- Pillow

### Steps:
- Clone this repository
- Rename "config/settings.yaml.dist" in "config/settings.yaml" and edit the desired parameters:
	- **debug:**
		- **db_log:** save each and every message in a log file. Make sure the path "logs/messages.log" is valid before putting it to true
	- **image**
		- **resize_mode:** how you want the image to be resized. Can be 'crop' or 'scale'
		- **blur:** how much blur you want to apply to the image
	- **token:** the token for your telegram bot
	- **webhook:**
		- **enabled:** whether or not the bot should use webhook (false recommended for local)
		- **url:** the url used by the webhook
- **Run** `python3 main.py`

## :whale: Setting up a Docker container

#### System requirements
- Docker

### Steps:
- Clone this repository
- In "config/settings.yaml.dist", edit the desired values. Be mindful that the one listed below will overwrite the ones in "config/settings.yaml.dist", even if they aren't used in the command line
- **Run** `docker build --tag botimage --build-arg TOKEN=<token_arg> [...] .` 

| In the command line <br>(after each --build-arg) | Type | Function | Optional |
| --- | --- | --- | --- |
| **TOKEN=<token_args>** | string | the token for your telegram bot | REQUIRED |
| **WEBHOOK_ENABLED=<webhook_enabled>** | bool | whether or not the bot should use webhook<br>(false recommended for local) | OPTIONAL - defaults to false |
| **WEB_URL=<web_url>** | string | the url used by the webhook | REQUIRED IF<br>webhook_enabled = true |

- **Run** `docker run -d --name botcontainer botimage`

### To stop/remove the container:
- **Run** `docker stop botcontainer` to stop the container
- **Run** `docker rm -f botcontainer` to remove the container
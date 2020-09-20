# DMI-Insider-newsgen-bot

## Usage
This bot is meant to easily generate images with a set template for the DMI-Insider collective 

## :red_circle: Try it live
Live version on telegram [**@DMI_newsgen_Bot**](https://telegram.me/DMI_newsgen_Bot)

## Image creation flow diagram

	+----V----+     +-------------------+     +-----------+     +-------------+
	| /create +---->+ template callback +---->+ title msg +---->+ caption msg |
	+---------+     +-------------------+     +-----------+     +------+------+
	                                                                   |
	                                                                   V
	                                 +----------------+     +----------------------+
	                                 | background_msg +<----+ resize mode callback |
	                                 +-------+--------+     +----------------------+
	                                         |
	                       +----------------------------------------+
	                       |                 |                      |
	if resize mode =     scale              crop                  random
	                       |                 |     +----+           |      +----+
	                       v                 v     v    |           v      v    |
	                 +-----+-----+   +-------+-----+-+  |  +--------+------+-+  |
	                 | end photo |   | crop_callback +--+  | random callback +--+
	                 +-----V-----+   +-------+-------+     +--------+--------+
	                                         |                      |
	                                         v                      |
	                                   +-----+-----+          +-----+-----+
	                                   | end photo |          | end photo |
	                                   +-----V-----+          +-----V-----+

## :wrench: Setting up a local istance

#### System requirements
- Python 3
- python-pip3

#### Install with *pip3*
Listed in requirements.txt. The main ones are:
- python-telegram-bot
- requests
- PyYAML
- Pillow

### Steps:
- Clone this repository
- Rename "config/settings.yaml.dist" in "config/settings.yaml" and edit the desired parameters:
	- **debug:**
		- **db_log:** save each and every message in a log file. Make sure the path "logs/messages.log" is valid before putting it to true
	- **groups:** list of chats or groups allowed to create images. If left [], all chats or groups will be allowed to create images
	- **image**
		- **blur:** how much blur you want to apply to the image
		- **thread:** whether or not the image creation should be handled in a separated thread instead of the main thread
	- **test:**
		- **api_hash:** hash of the telegram app used for testing
  		- **api_id:** id of the telegram app used for testing
  		- **groups:**  same of **groups** above. Overrides it during testing
  		- **session:** session of the telegram app used for testing
  		- **tag:** tag of the bot used for testing
  		- **token:** token for the bot used for testing
	- **token:** the token for your telegram bot
	- **webhook:**
		- **enabled:** whether or not the bot should use webhook (false recommended for local)
		- **url:** the url used by the webhook
- _[Optional]_ Edit the images in "data/img". These images WON'T be blurred by the bot
- **Run** `python3 main.py`

## :whale: Setting up a Docker container

#### System requirements
- Docker

### Steps:
- Clone this repository
- In "config/settings.yaml.dist", edit the desired values. Be mindful that the one listed below will overwrite the ones in "config/settings.yaml.dist", even if they aren't used in the command line
- _[Optional]_ Edit the images in "data/img". These images WON'T be blurred by the bot
- **Run** `docker build --tag botimage --build-arg TOKEN=<token_arg> [...] .` 

| In the command line <br>(after each --build-arg) | Type | Function | Optional |
| --- | --- | --- | --- |
| **TOKEN=<token_args>** | string | the token for your telegram bot | REQUIRED |
| **WEBHOOK_ENABLED=<webhook_enabled>** | bool | whether or not the bot should use webhook<br>(false recommended for local) | OPTIONAL - defaults to false |
| **WEB_URL=<web_url>** | string | the url used by the webhook | REQUIRED IF<br>webhook_enabled = true |
| **GROUPS=<grou_id(s)>** | List<br>"string string ..." | list of ids of authorized groups/chats | OPTIONAL - defaults to authorize every group/chat |

- **Run** `docker run -d --name botcontainer botimage`

### To stop/remove the container:
- **Run** `docker stop botcontainer` to stop the container
- **Run** `docker rm -f botcontainer` to remove the container

## :bar_chart: _[Optional]_ Setting up testing

### Create a Telegram app:

#### Steps [(source)](https://dev.to/blueset/how-to-write-integration-tests-for-a-telegram-bot-4c0e):
- Sign in your Telegram account with your phone number here. Then choose “API development tools”
- If it is your first time doing so, it will ask you for an app name and a short name, you can change both of them later if you need to. Submit the form when you have completed it
- You will then see the **api_id** and **api_hash** for your app. These are unique to your app, and not revocable.
- Put those values in the "conf/settings.yaml" file for local or in the "conf/settings.yaml.dist" file if you are setting up a docker container
- **Run** `python3 tests/conftest.py ` follow the procedure and copy the value it provides in the settings file in "testing:session"
- Edit the remaining values in the settings file as you like
- After this, see the steps below

### In local:

#### Install with *pip3*
- telethon
- pytest
- pytest-asyncio

#### Steps:
- **Run** `pytest`

### In a docker container:

#### Steps:
- Add telethon, pytest and pytest-asyncio to the requirements.txt file
- Access the container and **Run** `pytest` or edit the Dockerfile to do so

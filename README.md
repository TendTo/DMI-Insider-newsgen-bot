

# DMI-Insider-newsgen-bot

## Usage
This bot is meant to easily generate images with a set template for the DMI-Insider collective 

## :red_circle: Try it live
Live version on telegram [**@DMI_newsgen_Bot**](https://telegram.me/DMI_newsgen_Bot)

## Table of contents

- **[:wrench: Setting up a local istance](#wrench-setting-up-a-local-istance)**
- **[:whale: Setting up a Docker container](#whale-setting-up-a-docker-container)**
- **[:bar_chart: _\[Optional\]_ Setting up testing](#bar_chart-optional-setting-up-testing)**
- **[:books: Documentation](#books-documentation)**
- **[:arrow_upper_right:  Image creation flow diagram](#arrow_upper_right-image-creation-flow-diagram)**
- **[:twisted_rightwards_arrows: About Pull Requests...](#twisted_rightwards_arrows-about-pull-requests...)**

## :wrench: Setting up a local istance

#### System requirements
- [Python 3](https://www.python.org/downloads/)
- python-pip3

#### Install with *pip3*
Complete list in requirements.txt. The main ones to install are:
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/)
- [requests](https://pypi.org/project/requests/)
- [PyYAML](https://pypi.org/project/PyYAML/)
- [Pillow](https://pypi.org/project/Pillow/)

### Steps:
- Clone this repository
- Rename _config/settings.yaml.dist_ in _config/settings.yaml_ and edit the desired parameters:
 ```yaml
debug:
    db_log: save each and every message in a log file. If true, make sure the path "logs/messages.log" is valid
    
 groups: list of chats or groups allowed to create images. If [], all chats or groups will be allowed to create images

image:
    blur: how much blur you want to apply to the image
    font_size_title: font size of the title
    font_size_caption: font size of the caption
    thread: whether or not the image creation should be handled in a separated thread instead of the main thread
    
test:
    api_hash: hash of the telegram app used for testing
    api_id: id of the telegram app used for testing
    groups:  same of groups above. Overrides it during testing
    session: session of the telegram app used for testing
    tag: tag of the telegram bot used for testing. Include the '@' character
    token: token for the telegram bot used for testing

token: the token for your telegram bot

webhook:
    enabled: whether or not the bot should use webhook (false recommended for local)
    url: the url used by the webhook
```
- _[Optional]_ Edit the images in _data/img_. These images WON'T be blurred by the bot
- **Run** `python3 main.py`

## :whale: Setting up a Docker container

#### System requirements
- [Docker](https://www.docker.com/get-started)

### Steps:
- Clone this repository
- In _config/settings.yaml.dist_, edit the desired values. Be mindful that the one listed below will overwrite the ones in _config/settings.yaml.dist_, even if they aren't specified in `docker build`
- _[Optional]_ Edit the images in _data/img_. These images WON'T be blurred by the bot
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

#### Steps:
- Sign in your Telegram account with your phone number **[here](https://my.telegram.org/auth)**. Then choose “API development tools”
- If it is your first time doing so, it will ask you for an app name and a short name, you can change both of them later if you need to. Submit the form when you have completed it
- You will then see the **api_id** and **api_hash** for your app. These are unique to your app, and not revocable.
- Put those values in the _conf/settings.yaml_ file for local or in the _conf/settings.yaml.dist_ file if you are setting up a docker container
```yaml
test:
    api_hash: HERE
    api_id: HERE
	...
```
- Copy the file _tests/conftest.py_ in the root folder and **Run** `python3 conftest.py `. Follow the procedure and copy the session string it provides in the settings file:
```yaml
test:
	...
    session: HERE
	...
```
- You can then delete the _conftest.py_ file present in the root folder, you won't need it again
- Edit the remaining values in the file as you see fit

**Check [here](https://dev.to/blueset/how-to-write-integration-tests-for-a-telegram-bot-4c0e) you you want to have more information on the steps above**

### In local:

#### Install with *pip3*
- [telethon](https://pypi.org/project/Telethon/)
- [pytest](https://pypi.org/project/pytest/)
- [pytest-asyncio](https://pypi.org/project/pytest-asyncio/)

#### Steps:
- **Run** `pytest`

### In a docker container:

#### Steps:
- Add telethon, pytest and pytest-asyncio to the requirements.txt file
- Access the container and **Run** `pytest` or edit the Dockerfile to do so

## :books: Documentation
[Link to the documentation](https://tendto.github.io/DMI-Insider-newsgen-bot/)

## :arrow_upper_right: Image creation flow diagram

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
	if resize mode =     scale             crop                  random
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

## :twisted_rightwards_arrows: About Pull Requests...
Upon submitting a Pull Request, a github action will be triggered. The workflow will run all the tests to make sure everything still works correctly

The workflow will fail if your repository lacks even one of the following secrets:
| SECRET | Type | Function |
| --- | --- | --- |
| **API_ID** | int | id of the telegram app used for testing |
| **API_HASH** | string | hash of the telegram app used for testing |
| **SESSION** | string | session of the telegram app used for testing |
| **TEST_TAG** | string | tag of the bot used for testing |
| **TEST_TOKEN** | string | token for the bot used for testing |

**To pass the workflow is not mandatory, but is highly suggested**
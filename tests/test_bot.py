"""Tests the bot functionality"""
import time
import pytest
from telethon.sync import TelegramClient
from telethon.tl.custom.message import Message
from telethon.tl.custom.conversation import Conversation
from modules.data.data_reader import config_map, read_md

TIMEOUT = 8
bot_tag = config_map['test']['tag']


def teardown():
    """Makes so that there is a fixed timeout between each test
    """
    time.sleep(1)


def get_telegram_md(message_text: str) -> str:
    """Gets the message received from the bot and reverts it to the Markdowm_v2 used to send messages with it

    Args:
        message_text (str): text of the message received from the bot

    Returns:
        str: the same text of the message, but with the Markdown_v2 conventions
    """
    return message_text.replace("__", "_").replace("**", "*").replace("-", "\\-").replace(".", "\\.")


@pytest.mark.asyncio
async def test_start_cmd(client: TelegramClient):
    """Tests the start command

    Args:
        client (TelegramClient): client used to simulate the user
    """
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT) as conv:
        await conv.send_message("/start")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("start") == get_telegram_md(resp.text)


@pytest.mark.asyncio
async def test_help_cmd(client: TelegramClient):
    """Tests the help command

    Args:
        client (TelegramClient): client used to simulate the user
    """
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT) as conv:
        await conv.send_message("/help")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("help") == get_telegram_md(resp.text)


@pytest.mark.asyncio
async def test_settings_cmd(client: TelegramClient):
    """Tests the settings command

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['blur'] = config_map['image']['font_size'] = config_map['image']['line_width'] = 30
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT) as conv:
        for button_index in (1, 2, 3):
            await conv.send_message("/settings")  # send a command
            resp: Message = await conv.get_response()

            assert read_md("settings") == get_telegram_md(resp.text)

            await resp.click(button_index)  # click inline keyboard (Sfocatura, Dimensioni testo, Caratteri per linea)
            resp: Message = await conv.get_edit()

            assert read_md("settings") == get_telegram_md(resp.text)

            await resp.click(text="➕")  # click inline keyboard (➕)
            resp: Message = await conv.get_edit()

            assert read_md("settings") == get_telegram_md(resp.text)

            await resp.click(text="➖")  # click inline keyboard (➖)
            resp: Message = await conv.get_edit()

            assert read_md("settings") == get_telegram_md(resp.text)

            await resp.click(text="Chiudi")  # click inline keyboard (Chiudi)
            resp: Message = await conv.get_edit()

        assert 30 == config_map['image']['blur'] == config_map['image']['font_size'] == config_map['image']['line_width']


@pytest.mark.asyncio
async def test_cancel_cmd(client: TelegramClient):
    """Tests the cancel command

    Args:
        client (TelegramClient): client used to simulate the user
    """
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()
        await conv.send_message("/cancel")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("cancel") == get_telegram_md(resp.text)


@pytest.mark.asyncio
async def test_templates_conversation(client: TelegramClient):
    """Tests the selection of all the possible templates in the create conversation

    Args:
        client (TelegramClient): client used to simulate the user
    """
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT) as conv:
        for template in ('DMI', 'DMI vuoto', 'Informatica', 'Informatica vuoto', 'Matematica', 'Matematica vuoto'):
            await conv.send_message("/create")  # send a command
            resp: Message = await conv.get_response()
            await resp.click(text=template)  # click inline keyboard (Vuoto, DMI, Informatica, Matematica)
            resp: Message = await conv.get_edit()

            assert read_md("template") == get_telegram_md(resp.text)

            await conv.send_message("/cancel")  # send a command
            resp: Message = await conv.get_response()

            assert read_md("cancel") == get_telegram_md(resp.text)


@pytest.mark.asyncio
async def test_fail_conversation(client: TelegramClient):
    """Tests the create conversation when the user inputs some invalid text when asked for the image

    Args:
        client (TelegramClient): client used to simulate the user
    """
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()
        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()
        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()
        await conv.send_message("Test descrizione")  # send a message
        resp: Message = await conv.get_response()
        await resp.click(text="Ridimensiona")  # click inline keyboard
        resp: Message = await conv.get_edit()
        await conv.send_message("Fail message")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("fail") == get_telegram_md(resp.text)

        await conv.send_message("/cancel")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("cancel") == get_telegram_md(resp.text)


@pytest.mark.asyncio
async def test_create_scale_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the default image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = False
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(text="Ridimensiona")  # click inline keyboard
        resp: Message = await conv.get_edit()

        await conv.send_file("data/img/bg_test.png")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_crop_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the user provided image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = False
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(text="Ritaglia")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_file("data/img/bg_test.png")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="⬆️")  # click inline keyboard
        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="Genera")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_scale_crop_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the user provided image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = False
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(2)  # click inline keyboard (Ridimensiona & Ritaglia)
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_file("data/img/bg_test.png")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="⬆️")  # click inline keyboard
        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="Genera")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_random_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the user provided image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = False
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(text="Mi sento 🍀")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_file("data/img/bg_test.png")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="No, ritenta")  # click inline keyboard
        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="Si")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_scale_thread_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the default image
    The image creation is handled by a newly created thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = True
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 4) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(text="Ridimensiona")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_message("none")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_crop_thread_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the user provided image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = True
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(text="Ritaglia")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_message("none")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="⬆️")  # click inline keyboard
        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="Genera")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_scale_crop_thread_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the user provided image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = True
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(2)  # click inline keyboard (Ridimensiona & Ritaglia)
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_message("none")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="⬆️")  # click inline keyboard
        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="Genera")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert resp.photo is not None


@pytest.mark.asyncio
async def test_create_random_thread_conversation(client: TelegramClient):
    """Tests the whole flow of the create conversation with the user provided image
    The image creation is handled by the main thread

    Args:
        client (TelegramClient): client used to simulate the user
    """
    config_map['image']['thread'] = True
    conv: Conversation
    async with client.conversation(bot_tag, timeout=TIMEOUT * 2) as conv:
        await conv.send_message("/create")  # send a command
        resp: Message = await conv.get_response()

        assert read_md("create") == get_telegram_md(resp.text)

        await resp.click(text="DMI")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("template") == get_telegram_md(resp.text)

        await conv.send_message("Test titolo")  # send a message
        resp: Message = await conv.get_response()

        assert read_md("title") == get_telegram_md(resp.text)

        await conv.send_message("Test descrizione")  # send message
        resp: Message = await conv.get_response()

        assert read_md("caption") == get_telegram_md(resp.text)

        await resp.click(text="Mi sento 🍀")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert read_md("resize_mode") == get_telegram_md(resp.text)

        await conv.send_message("none")  # send message
        resp: Message = await conv.get_response()

        assert read_md("background") == get_telegram_md(resp.text)

        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="No, ritenta")  # click inline keyboard
        resp: Message = await conv.get_response()

        assert resp.photo is not None

        await resp.click(text="Si")  # click inline keyboard
        resp: Message = await conv.get_edit()

        assert resp.photo is not None

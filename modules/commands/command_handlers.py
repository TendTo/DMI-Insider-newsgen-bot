"""Handles the commands"""
import os
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from modules.various.utils import get_message_info
from modules.various.photo_utils import build_photo_path, generate_photo, build_bg_path
from modules.data.data_reader import read_md, config_map

STATE = {
    'background': 1,
    'template': 2,
    'title': 3,
    'caption': 4,
    'resize_mode': 5,
    'crop': 6,
    'random': 7,
    'end': -1
}  # represents the various states for the creation of the image

TEMPLATE = {
    'DMI': "data/img/template_DMI.png",
    'matematica': "data/img/template_matematica.png",
    'informatica': "data/img/template_informatica.png"
}


def start_cmd(update: Update, context: CallbackContext):
    """Handles the /start command
    Sends a short welcoming message

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("start")
    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)


def help_cmd(update: Update, context: CallbackContext):
    """Handles the /help command
    Sends a short summary of the bot's commands

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("help")
    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)


def settings_cmd(update: Update, context: CallbackContext):
    """Handles the /settings command
    Let the user set some values used to create the image. Those settings apply to all users

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_message_info(update, context)
    text = read_md("settings")
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(" -- Impostazioni --", callback_data="_")],
        [
            InlineKeyboardButton("Sfocatura", callback_data="settings_blur"),
        ],
        [
            InlineKeyboardButton("️Dimensione titolo", callback_data="settings_font_size_title"),
            InlineKeyboardButton("Dimensione descrizione", callback_data="settings_font_size_caption")
        ],
    ])
    info['bot'].send_message(chat_id=info['chat_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=inline_keyboard)


def create_cmd(update: Update, context: CallbackContext) -> int:
    """Handles the /settings command
    Start the process aimed to create the requested image
    Puts the conversation in the "template" state if all goes well, "end" state otherwise

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_message_info(update, context)
    inline_keyboard = None
    return_state = STATE['end']
    if config_map['groups'] and info['chat_id'] not in config_map['groups']:  # the group is not among the allowed ones
        text = "Questo gruppo/chat non è fra quelli supportati"
    elif os.path.exists(f"data/img/{str(info['sender_id'])}.png"):  # if the bot is already making an image for the user
        text = read_md("create_fail")
    else:
        text = read_md("create")
        return_state = STATE['template']
        inline_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="DMI", callback_data="template_DMI"),
                InlineKeyboardButton(text="DMI vuoto", callback_data="template_DMI_vuoto")
            ],
            [
                InlineKeyboardButton(text="Informatica", callback_data="template_informatica"),
                InlineKeyboardButton(text="Informatica vuoto", callback_data="template_informatica_vuoto")
            ],
            [
                InlineKeyboardButton(text="Matematica", callback_data="template_matematica"),
                InlineKeyboardButton(text="Matematica vuoto", callback_data="template_matematica_vuoto")
            ]
        ])

    info['bot'].send_message(chat_id=info['chat_id'],
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=inline_keyboard)
    return return_state


def cancel_cmd(update: Update, context: CallbackContext) -> int:
    """Handles the /cancel command
    Cancels the current cretion of the image
    Puts the conversation in the "end" state

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_message_info(update, context)
    text = read_md("cancel")

    # Clear the disk space used by the images, if present
    bg_path = build_bg_path(info['sender_id'])
    photo_path = build_photo_path(info['sender_id'])
    if os.path.exists(bg_path):
        os.remove(bg_path)
    if os.path.exists(photo_path):
        os.remove(photo_path)

    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)
    return STATE['end']


def title_msg(update: Update, context: CallbackContext) -> int:
    """Handles the title message
    Saves the title so it can be used as the title of the image

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_message_info(update, context)
    context.user_data['title'] = info['text'].upper()
    text = read_md("title")
    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)
    return STATE['caption']


def caption_msg(update: Update, context: CallbackContext) -> int:
    """Handles the caption message
    Saves the caption so it can be used as the caption of the image

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_message_info(update, context)
    context.user_data['caption'] = info['text']
    text = read_md("caption")

    inline_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Ritaglia", callback_data="image_resize_mode_crop"),
            InlineKeyboardButton(text="Ridimensiona", callback_data="image_resize_mode_scale")
        ],
        [
            InlineKeyboardButton(text="Mi sento 🍀", callback_data="image_resize_mode_random")
        ]
    ])

    info['bot'].send_message(chat_id=info['chat_id'],
                             text=text,
                             reply_markup=inline_keyboard,
                             parse_mode=ParseMode.MARKDOWN_V2)
    return STATE['resize_mode']


def background_msg(update: Update, context: CallbackContext) -> int:
    """Handles the background message
    Saves the photo so it can be used as the background of the image

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_message_info(update, context)
    text = read_md("background")
    photo = update.message.photo
    resize_mode = context.user_data['resize_mode']

    if photo:  # if an actual photo was sent
        bg_image = info['bot'].getFile(photo[-1].file_id)
        bg_image.download(build_bg_path(info['sender_id']))

    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)

    generate_photo(info, context.user_data)

    if resize_mode == "crop":
        return STATE['crop']
    elif resize_mode == "random":
        return STATE['random']
    else:
        return STATE['end']


def fail_msg(update: Update, context: CallbackContext) -> None:
    """Handles the fail message
    The message sent during the creation of the image was not valid
    The state of the conversation stays the same

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        None: new state of the conversation
    """
    info = get_message_info(update, context)
    text = read_md("fail")
    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)

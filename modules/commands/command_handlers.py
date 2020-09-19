"""Handles the commands"""
import os
from threading import Thread
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from modules.various.utils import get_message_info, get_callback_info
from modules.various.photo_utils import build_photo_path, generate_photo, send_image
from modules.data.data_reader import read_md, config_map

STATE = {
    'background': 1,
    'template': 2,
    'title': 3,
    'caption': 4,
    'tune': 5,
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
        inline_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="DMI", callback_data="template_DMI"),
            InlineKeyboardButton(text="Informatica", callback_data="template_informatica"),
            InlineKeyboardButton(text="Matematica", callback_data="template_matematica")
        ]])

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
    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)
    return STATE['background']


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

    sender_id = info['sender_id']

    if photo:  # if an actual photo was sent
        bg_image = info['bot'].getFile(photo[-1].file_id)
        bg_image.download(build_photo_path(sender_id))

    info['bot'].send_message(chat_id=info['chat_id'], text=text, parse_mode=ParseMode.MARKDOWN_V2)

    # Fill default image's tuning settings
    context.user_data['background_offset'] = {
        'x': 0,
        'y': 0,
    }

    generate_photo(info, context.user_data)

    return STATE['tune']

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

def resize_image(im: Image, fg: Image, offset: dict):
    """Resizes the image with the method specified in the "config/settings.yaml" file

    Args:
        im (Image): image to resize
        fg (Image): images wich dimensions will be used to resize the former image
    """
    orig_w, orig_h = im.size  # size of the bg image
    temp_w, temp_h = fg.size  # size of the template image
    if config_map['image']['resize_mode'] == "crop":  # crops the image in the center
        im = im.crop(box=((orig_w - temp_w) / 2 + offset['x'], (orig_h - temp_h) / 2, (orig_w + temp_w) / 2 + offset['y'], (orig_h + temp_h) / 2))
        im = im.resize(fg.size)  # resize if it's too small
    elif config_map['image']['resize_mode'] == "scale":  # scales the image so that it fits (ignores proportions)
        im = im.resize(fg.size)
    return im

def draw_text(draw_im: ImageDraw, w: int, text: str, y_text: float, font: any) -> int:
    """Draws the text on the image of width w, starting at height y_text

    Args:
        draw_im (ImageDraw): image to draw on
        w (int): with of the image
        text (str): text to write
        y_text (int): height of the text
        font (any): font of the text

    Returns:
        int: final height of the text
    """
    return_text = text.split("\n")  # split the title based on the return char \n
    multiline_text = []
    for return_line in return_text:
        for line in textwrap.wrap(return_line, width=35):  # split the line based on the lenght of the string
            multiline_text.append(line)
    for line in multiline_text:  # write each line of the title
        t_w, t_h = font.getsize(line)
        draw_im.multiline_text(xy=((w - t_w) / 2, y_text), text=line, fill="white", font=font)
        y_text += t_h
    return y_text

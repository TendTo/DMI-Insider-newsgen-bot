import os
from threading import Thread
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CallbackContext
from modules.various.utils import get_message_info, get_callback_info
from modules.data.data_reader import read_md, config_map

def build_photo_path(sender_id):
    return f"data/img/{str(sender_id)}.png"  # the user_id indentifies the image of each user

def generate_photo(info, user_data):
    photo_path = build_photo_path(info['sender_id'])

    if config_map['image']['thread']:
        t = Thread(target=send_image, args=(info, user_data, photo_path))
        t.start()
    else:
        send_image(info=info, data=user_data, photo_path=photo_path)

def send_image(info: dict, data: dict, photo_path: str, message_id = None):
    """Creates and sends the requested image

    Args:
        info (dict): {'bot': bot used to send the image, 'chat_id': id of the chat that will receive the image}
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used}
        photo_path (str): path where the image is stored
    """
    bot = info['bot']
    chat_id = info['chat_id']

    create_image(data=data, photo_path=photo_path)

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(" -- Posizione sfondo --", callback_data="_")],
        [
            InlineKeyboardButton(" ", callback_data="_"),
            InlineKeyboardButton("⬆️", callback_data="image_crop,up"),
            InlineKeyboardButton(" ", callback_data="_")
        ],[
            InlineKeyboardButton("️️⬅️", callback_data="image_crop,left"),
            InlineKeyboardButton("️Reset", callback_data="image_crop,reset"),
            InlineKeyboardButton("➡️", callback_data="image_crop,right")
        ],[
            InlineKeyboardButton(" ", callback_data="_"),
            InlineKeyboardButton("⬇️", callback_data="image_crop,down"),
            InlineKeyboardButton(" ", callback_data="_")
        ]
    ])

    fd = open(photo_path, "rb")

    if message_id:
        info['bot'].edit_message_media(chat_id=info['chat_id'],
                                  message_id=info['message_id'],
                                  media=InputMediaPhoto(media="photo_path"))
    else:
        bot.send_photo(chat_id=chat_id, photo=fd, reply_markup=reply_markup)


    fd.close()
    os.remove(photo_path)  # free the space no longer needed on disk

def create_image(data: dict, photo_path: str):
    """Creates the image with the data provided

    Args:
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used}
        photo_path (str): path that will be used to save the image
    """
    title = data['title']
    caption = data['caption']
    template = data['template']
    background_offset = data['background_offset']

    if os.path.exists(photo_path):
        im: Image.Image = Image.open(photo_path).filter(ImageFilter.GaussianBlur(config_map['image']['blur']))
    else:
        im: Image.Image = Image.open(f"data/img/bg_{template}.png")

    fg: Image.Image = Image.open(f"data/img/template_{template}.png")

    im = resize_image(im=im, fg=fg, offset=background_offset)  # resize the image with the chosen method

    im.paste(fg, box=(0, 0), mask=fg)  # paste the template foreground

    draw_im = ImageDraw.Draw(im)
    font = ImageFont.truetype("data/font/UbuntuCondensed-Regular.ttf", 33)
    w, h = im.size

    y_title = draw_text(draw_im=draw_im, w=w, text=title, y_text=h / 2 - 120, font=font)  # draw the title
    draw_text(draw_im=draw_im, w=w, text=caption, y_text=max(y_title + 30, h / 2 - 20), font=font)  # draw the caption

    im.save(photo_path)
    im.close()
    fg.close()

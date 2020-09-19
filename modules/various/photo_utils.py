"""Generates the image based on the user's settings"""
import os
from typing import Optional
from threading import Thread
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from modules.data.data_reader import config_map


def build_bg_path(sender_id: int) -> str:
    """Builds the path for the background image sent by the user

    Args:
        sender_id (int): id of the userd that sent the image

    Returns:
        str: path where to save/find the image
    """
    return f"data/img/bg_{str(sender_id)}.png"  # the user_id indentifies the image of each user


def build_photo_path(sender_id: int) -> str:
    """Builds the path for the edited image requested by the user

    Args:
        sender_id (int): id of the userd that sent the image

    Returns:
        str: path where to save/find the image
    """
    return f"data/img/{str(sender_id)}.png"  # the user_id indentifies the image of each user


def generate_photo(info: dict, user_data: dict, message_id: Optional[int] = None):
    """Generates the image based on the user's settings

    Args:
        info (dict): {'bot': bot used to send the image, 'chat_id': id of the chat that will receive the image}
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used, 'background_offset': offset used to crop the image}
        message_id (Optional[int], optional): id of the previous message that needs to be deleted. Defaults to None.
    """
    photo_path = build_photo_path(info['sender_id'])

    # if config_map['image']['thread']:
    #     t = Thread(target=send_image, args=(info, user_data, photo_path, message_id))
    #     t.start()
    # else:
    send_image(info=info, data=user_data, photo_path=photo_path, message_id=message_id)


def send_image(info: dict, data: dict, photo_path: str, message_id=None):
    """Creates and sends the requested image

    Args:
        info (dict): {'bot': bot used to send the image, 'chat_id': id of the chat that will receive the image}
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used, 'background_offset': offset used to crop the image}
        photo_path (str): path where the image is stored
    """
    bot = info['bot']
    chat_id = info['chat_id']

    create_image(data=data, sender_id=info['sender_id'], photo_path=photo_path)

    if config_map['image']['resize_mode'] == "crop":  # crops the image in the center
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(" -- Posizione sfondo --", callback_data="_")],
            [
                InlineKeyboardButton("↖️", callback_data="image_crop_up-left"),
                InlineKeyboardButton("⬆️", callback_data="image_crop_up"),
                InlineKeyboardButton("↗️", callback_data="image_crop_up-right")
            ],
            [
                InlineKeyboardButton("️️⬅️", callback_data="image_crop_left"),
                InlineKeyboardButton("️Reset", callback_data="image_crop_reset"),
                InlineKeyboardButton("➡️", callback_data="image_crop_right")
            ],
            [
                InlineKeyboardButton("↙️", callback_data="image_crop_down-left"),
                InlineKeyboardButton("⬇️", callback_data="image_crop_down"),
                InlineKeyboardButton("↘️", callback_data="image_crop_down-right")
            ],
            [InlineKeyboardButton("Genera", callback_data="image_crop_finish")],
        ])
    else:
        reply_markup = None

    fd = open(photo_path, "rb")

    if message_id:
        info['bot'].delete_message(chat_id=info['chat_id'], message_id=info['message_id'])

    bot.send_photo(chat_id=chat_id, photo=fd, reply_markup=reply_markup)

    fd.close()


def create_image(data: dict, sender_id: int, photo_path: str):
    """Creates the image with the data provided

    Args:
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used}
        photo_path (str): path that will be used to save the image
    """
    title = data['title']
    caption = data['caption']
    template = data['template']
    background_offset = data['background_offset'] if config_map['image']['resize_mode'] == "crop" else None

    # Load background
    background_path = build_bg_path(sender_id)

    if os.path.exists(background_path):
        im: Image.Image = Image.open(background_path).filter(ImageFilter.GaussianBlur(config_map['image']['blur']))
    else:
        im: Image.Image = Image.open(f"data/img/bg_{template}.png")

    # Apply foreground
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


def resize_image(im: Image, fg: Image, offset: dict) -> Image:
    """Resizes the image with the method specified in the "config/settings.yaml" file

    Args:
        im (Image): image to resize
        fg (Image): images wich dimensions will be used to resize the former image
        offset (dict): offset used to crop the image

    Returns:
        Image: newly resized image
    """
    orig_w, orig_h = im.size  # size of the bg image
    temp_w, temp_h = fg.size  # size of the template image
    if config_map['image']['resize_mode'] == "crop":  # crops the image in the center
        im = im.crop(box=((orig_w - temp_w) / 2 + offset['x'], (orig_h - temp_h) / 2 + offset['y'],
                          (orig_w + temp_w) / 2 + offset['x'], (orig_h + temp_h) / 2 + offset['y']))
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

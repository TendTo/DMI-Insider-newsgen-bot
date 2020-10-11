"""Generates the image based on the user's settings"""
import os
import random
from threading import Thread
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from modules.data.data_reader import config_map
from modules.various.utils import get_keyboard_crop, get_keyboard_random


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


def generate_photo(info: dict, user_data: dict, delete_message: bool = False):
    """Generates the image based on the user's settings, then sends it
    The process can be executed on the main thread or on a separate thread, based on the settings

    Args:
        info (dict): {'bot': bot used to send the image, 'chat_id': id of the chat that will receive the image}
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used,
            'resize_mode': how to resize the image, 'background_offset': offset used to crop the image}
        message_id (bool, optional): whther or not the previous message needs to be deleted. Defaults to False.
    """
    if delete_message:  # delete the last message sent
        info['bot'].delete_message(chat_id=info['chat_id'], message_id=info['message_id'])

    if config_map['image']['thread']:
        t = Thread(target=send_image, args=(info, user_data))
        t.start()
    else:
        send_image(info=info, data=user_data)


def send_image(info: dict, data: dict):
    """Creates and sends the requested image

    Args:
        info (dict): {'bot': bot used to send the image, 'chat_id': id of the chat that will receive the image}
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used,
            'resize_mode': how to resize the image, 'background_offset': offset used to crop the image}
    """
    bot = info['bot']
    chat_id = info['chat_id']
    bg_path = build_bg_path(info['sender_id'])
    photo_path = build_photo_path(info['sender_id'])
    resize_mode = data['resize_mode']

    create_image(data=data, bg_path=bg_path, photo_path=photo_path)  # create the image to send

    # Set the inline keyboard and whether the images should be deleted from the disk immediatly, based on the resize_mode
    if resize_mode in "crop":
        clear = False
        reply_markup = get_keyboard_crop()
    elif resize_mode == "scale":
        clear = True
        reply_markup = None
    elif resize_mode == "random":
        clear = False
        reply_markup = get_keyboard_random()

    fd = open(photo_path, "rb")

    bot.send_photo(chat_id=chat_id, photo=fd, reply_markup=reply_markup)

    fd.close()

    if clear:  # clear the disk space used by the images
        if os.path.exists(bg_path):
            os.remove(bg_path)
        os.remove(photo_path)


def create_image(data: dict, bg_path: str, photo_path: str):
    """Creates the image with the data provided

    Args:
        data (dict): {'title': title of the image, 'caption': caption of the image, 'template': template to be used,
            'resize_mode': how to resize the image, 'background_offset': offset used to crop the image}
        bg_path (str): path where to find the bg_image, if provided
        photo_path (str): path that will be used to save the image
    """
    title = data['title']
    caption = data['caption']
    template = data['template']
    resize_mode = data['resize_mode']
    background_offset = data['background_offset'] if resize_mode == "crop" else None

    # Load background
    if os.path.exists(bg_path):
        im: Image.Image = Image.open(bg_path).filter(ImageFilter.GaussianBlur(config_map['image']['blur']))
    else:
        im: Image.Image = Image.open(f"data/img/bg_{template.replace('_vuoto', '')}.png")  # remove "_vuoto" the template path

    fg: Image.Image = Image.open(f"data/img/template_{template}.png")

    im = resize_image(im=im, fg=fg, resize_mode=resize_mode, offset=background_offset)  # resize the image

    im.paste(fg, box=(0, 0), mask=fg)  # apply foreground

    draw_im = ImageDraw.Draw(im)
    w, h = im.size

    y_title = draw_text(draw_im=draw_im, w=w, text=title, y_text=h / 2 - 120,
                        font_size=config_map['image']['font_size_title'])  # draw the title

    draw_text(draw_im=draw_im, w=w, text=caption, y_text=y_title + 30,
              font_size=config_map['image']['font_size_caption'])  # draw the caption

    im.save(photo_path)
    im.close()
    fg.close()


def resize_image(im: Image, fg: Image, resize_mode: str, offset: dict) -> Image:
    """Resizes the image with the method specified in resize_mode

    Args:
        im (Image): image to resize
        fg (Image): images wich dimensions will be used to resize the former image
        resize_mode (str): how to resize the image
        offset (dict): offset used to crop the image

    Returns:
        Image: newly resized image
    """
    orig_w, orig_h = im.size  # size of the bg image
    temp_w, temp_h = fg.size  # size of the template image

    if resize_mode == "crop":  # crops the image from the center + the offset
        ratio = max(temp_w / orig_w, temp_h / orig_h)
        if ratio > 1:
            im = im.resize((int(orig_w * ratio), int(orig_h * ratio)))
        orig_w, orig_h = im.size
        im = im.crop(box=((orig_w - temp_w) / 2 + offset['x'], (orig_h - temp_h) / 2 + offset['y'],
                          (orig_w + temp_w) / 2 + offset['x'], (orig_h + temp_h) / 2 + offset['y']))
    elif resize_mode == "scale":  # scales the image so that it fits (ignores proportions)
        im = im.resize(fg.size)
    elif resize_mode == "random":  # crops the image from the center + the random offset
        ratio = max(temp_w / orig_w, temp_h / orig_h)
        if ratio > 1:
            im = im.resize((int(orig_w * ratio), int(orig_h * ratio)))
        orig_w, orig_h = im.size
        x_offset = random.randint(-abs(orig_w - temp_w) // 2, abs(orig_w - temp_w) // 2)
        y_offset = random.randint(-abs(orig_h - temp_h) // 2, abs(orig_h - temp_h) // 2)
        im = im.crop(box=((orig_w - temp_w) / 2 + x_offset, (orig_h - temp_h) / 2 + y_offset, (orig_w + temp_w) / 2 + x_offset,
                          (orig_h + temp_h) / 2 + y_offset))
    return im


def draw_text(draw_im: ImageDraw, w: int, text: str, y_text: float, font_size: int) -> int:
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
    font = ImageFont.truetype(font="data/font/UbuntuCondensed-Regular.ttf", size=font_size)
    for line in wrap_text(text=text, max_w=w / 3 * 2, font=font):  # write each line of the text
        t_w, t_h = font.getsize(line)
        draw_im.multiline_text(xy=((w - t_w) / 2, y_text), text=line, fill="white", font=font)
        y_text += t_h + 5
    return y_text


def wrap_text(text: str, max_w: int, font: any) -> list:
    """Wraps the text so that no line is longer than the max width allowed

    Args:
        text (str): text to wrap
        max_w (int): max width the text is allowed to be
        font (any): font the text will use

    Returns:
        list: list of lines (str)
    """
    lines = []

    if font.getsize(text)[0] < max_w:
        lines.append(text)
        return lines

    for row in text.split("\n"):
        line = None
        for word in row.split():
            if not line:
                line = word
            elif font.getsize(line + word)[0] < max_w:
                line += " " + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines

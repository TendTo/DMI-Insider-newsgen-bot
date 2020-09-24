"""Handles the callbacks"""
import os
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from modules.various.utils import get_callback_info, get_keyboard_setting
from modules.various.photo_utils import generate_photo, build_bg_path, build_photo_path
from modules.data.data_reader import read_md
from modules.commands.command_handlers import STATE

OFFSET_VALUES = {
    'up': {
        'x': 0,
        'y': 50
    },
    'down': {
        'x': 0,
        'y': -50
    },
    'left': {
        'x': 50,
        'y': 0
    },
    'right': {
        'x': -50,
        'y': 0
    },
    'up-left': {
        'x': 50,
        'y': 50
    },
    'up-right': {
        'x': -50,
        'y': 50
    },
    'down-left': {
        'x': 50,
        'y': -50
    },
    'down-right': {
        'x': -50,
        'y': -50
    },
}


def settings_callback(update: Update, context: CallbackContext):
    """Handles the template callback
    Select the desidered template

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_callback_info(update, context)
    setting = info["query_data"][9:]
    text = read_md("settings")
    info['bot'].edit_message_text(chat_id=info['chat_id'],
                                  message_id=info['message_id'],
                                  text=text,
                                  reply_markup=get_keyboard_setting(setting=setting),
                                  parse_mode=ParseMode.MARKDOWN_V2)


def alter_setting_callback(update: Update, context: CallbackContext):
    """Handles the template callback
    Select the desidered template

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler
    """
    info = get_callback_info(update, context)
    setting = info["query_data"][9:]
    text = read_md("settings")
    info['bot'].edit_message_text(chat_id=info['chat_id'],
                                  message_id=info['message_id'],
                                  text=text,
                                  reply_markup=get_keyboard_setting(setting=setting),
                                  parse_mode=ParseMode.MARKDOWN_V2)


def template_callback(update: Update, context: CallbackContext) -> int:
    """Handles the template callback
    Select the desidered template
    Puts the conversation in the "title" state

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_callback_info(update, context)
    context.user_data['template'] = info["query_data"][9:]
    text = read_md("template")
    info['bot'].edit_message_text(chat_id=info['chat_id'],
                                  message_id=info['message_id'],
                                  text=text,
                                  parse_mode=ParseMode.MARKDOWN_V2)
    return STATE['title']


def image_resize_mode_callback(update: Update, context: CallbackContext) -> int:
    """Handles the image resize mode crop callback
    Sets the resize mode of the image ('crop', 'scale', 'random')
    Puts the conversation in the "background" state

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_callback_info(update, context)
    context.user_data['resize_mode'] = info["query_data"][18:]

    if info["query_data"][18:] == "crop":  # set default crop offset
        context.user_data['background_offset'] = {
            'x': 0,
            'y': 0,
        }

    text = read_md("resize_mode")
    info['bot'].edit_message_text(chat_id=info['chat_id'],
                                  message_id=info['message_id'],
                                  text=text,
                                  parse_mode=ParseMode.MARKDOWN_V2)
    return STATE['background']


def image_crop_callback(update: Update, context: CallbackContext) -> int:
    """Handles the image crop callback
    Modifies the cropping parameters
    The conversation remains in the "crop" state or is put in the "end" state

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_callback_info(update, context)

    operation = info["query_data"][11:]

    if operation == 'reset':
        context.user_data['background_offset'] = {'x': 0, 'y': 0}
    elif operation == 'finish':
        sender_id = info['sender_id']

        info['bot'].edit_message_reply_markup(chat_id=info['chat_id'], message_id=info['message_id'], reply_markup=None)

        if os.path.exists(build_bg_path(sender_id)):
            os.remove(build_bg_path(sender_id))
        os.remove(build_photo_path(sender_id))

        return STATE['end']
    else:
        offset_value = OFFSET_VALUES[operation]

        context.user_data['background_offset'] = {
            'x': context.user_data['background_offset']['x'] + offset_value['x'],
            'y': context.user_data['background_offset']['y'] + offset_value['y']
        }

    generate_photo(info=info, user_data=context.user_data, delete_message=True)

    return STATE['crop']


def image_random_callback(update: Update, context: CallbackContext) -> int:
    """Handles the image random callback
    Makes yhe user try the generation again
    The conversation remains in the "random" state or is put in the "end" state

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        int: new state of the conversation
    """
    info = get_callback_info(update, context)

    operation = info["query_data"][13:]

    if operation == 'finish':
        sender_id = info['sender_id']

        info['bot'].edit_message_reply_markup(chat_id=info['chat_id'], message_id=info['message_id'], reply_markup=None)

        if os.path.exists(build_bg_path(sender_id)):
            os.remove(build_bg_path(sender_id))
        os.remove(build_photo_path(sender_id))

        return STATE['end']

    generate_photo(info=info, user_data=context.user_data, delete_message=True)

    return STATE['random']

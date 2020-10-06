"""Common operation for each command/callback"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from modules.data.data_reader import config_map


def get_message_info(update: Update, context: CallbackContext) -> dict:
    """Get the classic info from the update and context parameters

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        dict: {bot, chat_id, text, message_id, sender_first_name, sender_id}
    """
    return {
        'bot': context.bot,
        'chat_id': update.message.chat_id,
        'text': update.message.text,
        'message_id': update.message.message_id,
        'sender_first_name': update.message.from_user.first_name,
        'sender_id': update.message.from_user.id
    }


def get_callback_info(update: Update, context: CallbackContext) -> dict:
    """Get the classic info from the update and context parameters for callbacks

    Args:
        update (Update): update event
        context (CallbackContext): context passed by the handler

    Returns:
        dict: {bot, chat_id, text, message_id, sender_first_name, sender_id, query_data}
    """
    return {
        'bot': context.bot,
        'chat_id': update.callback_query.message.chat_id,
        'text': update.callback_query.message.text,
        'message_id': update.callback_query.message.message_id,
        'sender_first_name': update.callback_query.from_user.first_name,
        'sender_id': update.callback_query.from_user.id,
        'query_data': update.callback_query.data
    }


def get_keyboard_setting(setting: str) -> InlineKeyboardMarkup:
    """Generates the InlineKeyboardMarkup for the settings command

    Returns:
        InlineKeyboardMarkup: reply markup to apply at the message
    """
    if setting == "blur":
        title = " -- Sfocatura -- "
    elif setting == "font_size_title":
        title = " -- Dimensione titolo -- "
    elif setting == "font_size_caption":
        title = " -- Dimensione descrizione -- "

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(title, callback_data="_")],
        [
            InlineKeyboardButton("➖", callback_data=f"alter_setting_{setting},-"),
            InlineKeyboardButton(str(config_map['image'][setting]), callback_data="_"),
            InlineKeyboardButton("➕", callback_data=f"alter_setting_{setting},+"),
        ],
        [
            InlineKeyboardButton("Chiudi", callback_data=f"alter_setting_{setting},cancel"),
            InlineKeyboardButton("️Salva tutto su file", callback_data=f"alter_setting_{setting},save"),
        ],
    ])


def get_keyboard_crop() -> InlineKeyboardMarkup:
    """Generates the InlineKeyboardMarkup for the crop callback

    Returns:
        InlineKeyboardMarkup: reply markup to apply at the message
    """
    return InlineKeyboardMarkup([
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


def get_keyboard_random() -> InlineKeyboardMarkup:
    """Generates the InlineKeyboardMarkup for the random callback

    Returns:
        InlineKeyboardMarkup: reply markup to apply at the message
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(" -- Sei stato fortunato? --", callback_data="_")],
        [
            InlineKeyboardButton("No, ritenta", callback_data="image_random_again"),
            InlineKeyboardButton("Si", callback_data="image_random_finish"),
        ],
    ])

"""Main module"""
# region imports
# libs
import os
import warnings
# telegram
from telegram import BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler,\
    Filters, Dispatcher
# debug
from modules.debug.log_manager import log_message
# data
from modules.data.data_reader import config_map
# commands
from modules.commands.command_handlers import STATE, start_cmd, help_cmd, settings_cmd, create_cmd, background_msg,\
    title_msg, caption_msg, cancel_cmd, fail_msg
# callbacks
from modules.callbacks.callback_handlers import template_callback, image_resize_mode_callback,\
    image_crop_callback, image_random_callback, settings_callback, alter_setting_callback
# endregion


def add_commands(up: Updater):
    """Adds the list of commands with their description to the bot

    Args:
        up (Updater): supplyed Updater
    """
    commands = [
        BotCommand("start", "presentazione iniziale del bot"),
        BotCommand("create", "avvia il processo di creazione dell'immagine"),
        BotCommand("cancel ", "annulla la procedura in corso e resetta il bot"),
        BotCommand("help ", "funzionamento e scopo del bot"),
        BotCommand("settings", "modifica vari parametri utilizzati nella creazione dell'immagine")
    ]
    up.bot.set_my_commands(commands=commands)


def add_handlers(dp: Dispatcher):
    """Add all the needed handlers to the dipatcher

    Args:
        dp (Dispatcher): supplyed dispacther
    """
    if config_map['debug']['local_log']:  # add MessageHandler only if log_message is enabled
        dp.add_handler(MessageHandler(Filters.all, log_message), 1)

    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("settings", settings_cmd))

    dp.add_handler(CallbackQueryHandler(settings_callback, pattern=r"^settings\.*"))
    dp.add_handler(CallbackQueryHandler(alter_setting_callback, pattern=r"^alter_setting\.*"))

    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('create', create_cmd)],
            states={
                STATE['template']: [CallbackQueryHandler(template_callback, pattern=r"^template\.*")],
                STATE['background']:
                [MessageHandler(Filters.photo | (Filters.text & Filters.regex(r"^[Nn]one$")), background_msg)],
                STATE['title']: [MessageHandler(Filters.text & ~Filters.command, title_msg)],
                STATE['caption']: [MessageHandler(Filters.text & ~Filters.command, caption_msg)],
                STATE['resize_mode']: [CallbackQueryHandler(image_resize_mode_callback, pattern=r"^image_resize_mode\.*")],
                STATE['crop']: [CallbackQueryHandler(image_crop_callback, pattern=r"^image_crop\.*")],
                STATE['random']: [CallbackQueryHandler(image_random_callback, pattern=r"^image_random\.*")]
            },
            fallbacks=[CommandHandler('cancel', cancel_cmd),
                       MessageHandler(Filters.all & ~Filters.command, fail_msg)],
            allow_reentry=False))


def main():
    """Main function
    """
    updater = Updater(config_map['token'], request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, use_context=True)
    add_commands(updater)
    add_handlers(updater.dispatcher)

    if config_map['webhook']['enabled']:  # if the webhook is enabled, start the webhook...
        PORT = int(os.environ.get('PORT', 5000))
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=config_map['token'])
        updater.bot.setWebhook(config_map['webhook']['url'] + config_map['token'])
    else:  # ... else, start the polling
        updater.start_polling()

    updater.idle()


warnings.filterwarnings("ignore",
                        message="If 'per_message=False', 'CallbackQueryHandler' will not be tracked for every message.")
if __name__ == "__main__":
    main()

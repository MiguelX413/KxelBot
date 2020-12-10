import logging
import os
from uuid import uuid4
import scriptcon
from telegram import (
    InlineQueryResultArticle,
    ParseMode,
    InputTextMessageContent,
    Update,
)
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
import json


try:
    with open("dict.json", "r") as f:
        dictdata = json.loads(f.read())
except FileNotFoundError:
    print("ERROR: No dict.json found, attempting to make one")
    try:
        import dictgen
    except ModuleNotFoundError:
        print("No dictgen.py found, unable to generate dict.json, exiting script")
        exit()
    with open("dict.json", "r") as f:
        dictdata = json.loads(f.read())


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query
    cyrillicResult = scriptcon.convert(query, dictdata["Cyrillic"])
    katakanaResult = scriptcon.convert(query.lower(), dictdata["Katakana"])
    lontaraResult = scriptcon.convert(query.lower(), dictdata["Lontara"])
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Cyrillic",
            description=cyrillicResult,
            input_message_content=InputTextMessageContent(cyrillicResult),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Katakana",
            description=katakanaResult,
            input_message_content=InputTextMessageContent(katakanaResult),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Lontara",
            description=lontaraResult,
            input_message_content=InputTextMessageContent(lontaraResult),
        ),
    ]

    update.inline_query.answer(results, cache_time=30)


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

updater = Updater(os.environ["TG_TOKEN"], use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(InlineQueryHandler(inlinequery))
updater.start_polling()
updater.idle()

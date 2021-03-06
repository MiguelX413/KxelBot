import logging
import os
import scriptcon
import re

try:
    import ujson

    json = ujson
except ModuleNotFoundError:
    try:
        import json
    except ModuleNotFoundError:
        print("json module not found, can't read dict")


from telegram import (
    InlineQueryResultArticle,
    ParseMode,
    InputTextMessageContent,
    Update,
)
from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler,
    CallbackContext,
)
from telegram.utils.helpers import escape_markdown

url_regex = re.compile(
    r"\s?(((about|ftp(s)?|filesystem|git|ssh|http(s)?):(\/\/)?)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\s?)"
)

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Runs TG bot")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Enabled Debugging mode",
    )
    if (sys.version_info[0] >= 3) and (sys.version_info[1] >= 9):
        parser.add_argument(
            "-r",
            "--rich",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Enables rich output",
        )
    else:
        parser.add_argument(
            "-r",
            "--rich",
            action="store_true",
            default=True,
            help="Enables rich output",
        )
        parser.add_argument(
            "--no-rich",
            action="store_false",
            dest="rich",
            help="Disables rich output",
        )
    do_rich = parser.parse_args().rich
    debug = parser.parse_args().debug

if do_rich:
    try:
        import rich
        from rich.progress import track, Progress
        from rich.logging import RichHandler
    except ModuleNotFoundError:
        do_rich = False

logging_args = {
    "level": logging.DEBUG if debug else logging.INFO,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}
if do_rich:
    logging_args["handlers"] = [RichHandler(rich_tracebacks=True)]
logging.basicConfig(**logging_args)


try:
    with open("dict.json", "r") as f:
        dictdata = json.loads(f.read())
except FileNotFoundError:
    print("ERROR: No dict.json found, attempting to make one")
    try:
        import dictgen

        dictgen.main(do_rich)
    except ModuleNotFoundError:
        print("No dictgen.py found, unable to generate dict.json, exiting script")
        exit()
    with open("dict.json", "r") as f:
        dictdata = json.loads(f.read())


def url_separate(text) -> tuple:
    working_text = text
    results = []
    if url_regex.search(text) is not None:
        while url_regex.search(working_text) is not None:
            partitions = working_text.partition(url_regex.search(working_text).group(0))
            results.append(partitions[0])
            results.append(partitions[1])
            working_text = partitions[2]
        else:
            results.append(working_text)
        return tuple(results)
    else:
        return tuple([text])


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Ка̄ла!\nカーラ゚！\nᨀᨕᨒ!")


def convert(text, dictionary) -> str:
    result = ""
    for x in url_separate(text):
        if url_regex.match(x) is None:
            result += scriptcon.convert(
                scriptcon.convert(x, dictdata["Latin"]),
                dictionary,
            )
        else:
            result += x
    return result


def genfunc(dictionary):
    def function(update: Update, _: CallbackContext) -> None:
        if update.message.reply_to_message is not None:
            if update.message.reply_to_message.text is not None:
                text = update.message.reply_to_message.text
            elif update.message.reply_to_message.caption is not None:
                text = update.message.reply_to_message.caption
            else:
                text = ""
            update.message.reply_text(convert(text, dictionary))

    return function


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query
    cyrillicResult = ""
    katakanaResult = ""
    lontaraResult = ""
    latinResult = ""
    for x in url_separate(query):
        if url_regex.match(x) is None:
            latinConversion = scriptcon.convert(x, dictdata["Latin"])
            latinResult += latinConversion
            cyrillicResult += scriptcon.convert(latinConversion, dictdata["Cyrillic"])
            katakanaResult += scriptcon.convert(latinConversion, dictdata["Katakana"])
            lontaraResult += scriptcon.convert(latinConversion, dictdata["Lontara"])
        else:
            latinResult += x
            cyrillicResult += x
            katakanaResult += x
            lontaraResult += x
    results = [
        InlineQueryResultArticle(
            id=1,
            title="Cyrillic",
            description=cyrillicResult,
            input_message_content=InputTextMessageContent(cyrillicResult),
        ),
        InlineQueryResultArticle(
            id=2,
            title="Katakana",
            description=katakanaResult,
            input_message_content=InputTextMessageContent(katakanaResult),
        ),
        InlineQueryResultArticle(
            id=3,
            title="Lontara",
            description=lontaraResult,
            input_message_content=InputTextMessageContent(lontaraResult),
        ),
        InlineQueryResultArticle(
            id=4,
            title="Latin",
            description=latinResult,
            input_message_content=InputTextMessageContent(latinResult),
        ),
    ]

    update.inline_query.answer(results, cache_time=30)


def main() -> None:
    token = os.environ["TG_TOKEN"]
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("cyrillic", genfunc(dictdata["Cyrillic"])))
    dispatcher.add_handler(CommandHandler("katakana", genfunc(dictdata["Katakana"])))
    dispatcher.add_handler(CommandHandler("lontara", genfunc(dictdata["Lontara"])))

    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

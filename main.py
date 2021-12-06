import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from collections.abc import Mapping
from os.path import isfile

import pandas
from binance import Client
from ta.momentum import rsi
from enum import Enum
from dataclasses_json import dataclass_json

from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class ExchangeType(Enum):
    Binance = 'binance'
    FTX = 'ftx'


@dataclass_json
@dataclass
class TradeTask:
    type: str


@dataclass_json
@dataclass
class User:
    telegram_id: int
    exchange_type: ExchangeType
    exchange_api_key: str


@dataclass_json
@dataclass
class DeepTrader:
    telegram_token: str = ''
    users: dict[int, User] = field(default_factory=dict)


trader = DeepTrader()


def go(fn, args=()):
    threading.Thread(target=fn, args=args)


def tg_start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def tg_help(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def tg_echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)

def tg_log(update: Update, context: CallbackContext):
    logging.info(update)


# if __name__ == '__main__':
#     bn = Client()
#     klines = bn.get_klines(symbol="SOLUSDT", interval="15m")
#     data = pandas.DataFrame(klines, columns=[
#         'open_time', 'open', 'high', 'low', 'close', 'volume',
#         'close_time', 'quote_asset_volume', 'trades',
#         'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
#     data['open_time'] = pandas.to_datetime(data['open_time'], unit='ms')
#     data['open'] = pandas.to_numeric(data['open'])
#     data['close'] = pandas.to_numeric(data['close'])
#
#     data.set_index('open_time', inplace=True)
#     print(data)
#     print(type(data["close"]))
#     print(rsi(data["close"]))

db_filename = "config.json"


def read_db():
    if not isfile(db_filename):
        return
    with open(db_filename, "r") as f:
        global trader
        content = f.read()
        trader = DeepTrader.from_json(content)
        logging.info("read db")


def write_db():
    with open(db_filename, "r") as f:
        f.write(trader.to_json())
        logging.info("write db")


def main():
    read_db()
    logging.info(trader)

    updater = Updater(trader.telegram_token)
    dispatcher: Dispatcher = updater.dispatcher
    bot: Bot = dispatcher.bot
    logging.info(bot)
    dispatcher.add_handler(CommandHandler("start", tg_start))
    dispatcher.add_handler(CommandHandler("help", tg_help))
    dispatcher.add_handler(MessageHandler(Filters.text, tg_log))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, tg_echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

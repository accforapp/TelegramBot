import telebot
import requests
import json
import data_load


bot = telebot.TeleBot('1277099406:AAErhXQK6Djcwu6D-xKFxyYAM8ouZU5r7uQ')

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text='Текущий курс', callback_data='current rate'),
                 telebot.types.InlineKeyboardButton(text='Архив', callback_data='archive'))
    bot.send_message(message.chat.id, 'Привет, выберите пункт меню', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def choose_rate(call):
    data_load.load()
    if call.data == 'current rate':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Рубль', callback_data='rur_cur'),
                     telebot.types.InlineKeyboardButton(text='Доллар', callback_data='usd_cur'))
        keyboard.row(telebot.types.InlineKeyboardButton(text='Евро', callback_data='eur_cur'),
                     telebot.types.InlineKeyboardButton(text='Биткойн', callback_data='btc'))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите валюту", reply_markup=keyboard)

    elif call.data == 'archive':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='Рубль', callback_data='rub_arch'),
                     telebot.types.InlineKeyboardButton(text='Доллар', callback_data='usd_arch'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Евро', callback_data='eur_arch'))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите валюту", reply_markup=keyboard)

    if call.data == 'rur_cur' or call.data == 'usd_cur' or call.data == 'eur_cur' or call.data == 'btc':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='В начало', callback_data='start'),
                     telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_cur'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=out_rate(call.data[:3].upper(), 'cur'), reply_markup=keyboard)
    elif call.data == 'rub_arch' or call.data == 'usd_arch' or call.data == 'eur_arch':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(text='В начало', callback_data='start'),
                     telebot.types.InlineKeyboardButton(text='Назад', callback_data='back_arch'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=out_rate(call.data[:3].upper(), 'arch'), reply_markup=keyboard)
    if call.data == 'start':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start_message(call.message)
    elif call.data == 'back_cur':
        call.data = 'current rate'
        choose_rate(call)
    elif call.data == 'back_arch':
        call.data = 'archive'
        choose_rate(call)


def out_rate(ccy, text):
    result = ''

    if text == 'cur':
        for r in json.loads(requests.get('https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11').text):
            if r['ccy'] == ccy:
                result += ccy + " -> " + r['base_ccy'] + "\n" + "Покупка: " + r['buy'] + "\n" + "Продажа: " + r['sale']
    elif text == 'arch':
        with open('rate_archive.json', 'r') as read_file:
            data = json.load(read_file)
        for d in data:
            if d['ccy'] == ccy:
                result += d['date'] + ' ' + ccy + ' -> UAH\n' + 'Покупка: ' + d['buy'] + '\n' + 'Продажа: ' \
                          + d['sale'] + '\n' + '------------------------------------------\n'
    return result


bot.polling()

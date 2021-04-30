# Copyright (C) 2017, 2018, 2019, 2020  alfred richardsn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import config
from .database import database
from . import lang
from . import croco
from . import gallows
from .game import role_titles, stop_game
from .stages import stages, go_to_next_stage, format_roles, get_votes
from .bot import bot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import re
import random
from time import time
from uuid import uuid4
from datetime import datetime
from pymongo.collection import ReturnDocument


def get_name(user):
    return '@' + user.username if user.username else user.first_name


def get_full_name(user):
    result = user.first_name
    if user.last_name:
        result += ' ' + user.last_name
    return result


def user_object(user):
    return {'id': user.id, 'name': get_name(user), 'full_name': get_full_name(user)}


def command_regexp(command):
    return f'^/{command}(@{bot.get_me().username})?$'


@bot.message_handler(regexp=command_regexp('help'))
@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['start'])
def start_command(message, *args, **kwargs):
    answer = (
        f'Salam, mən {bot.get_me().first_name}!\n'
        'Mən söz oynuyam. /game komandası vermək bəs edir. Uğurlar!\n'
        '@JasperAzerbaijan'
    )
    bot.send_message(message.chat.id, answer)


def get_mafia_score(stats):
    return 2 * stats.get('win', 0) - stats['total']


def get_croco_score(stats):
    result = 3 * stats['croco'].get('win', 0)
    result += stats['croco'].get('guesses', 0)
    result -= stats['croco'].get('cheat', 0)
    return result / 25


@bot.message_handler(regexp=command_regexp('stats'))
def stats_command(message, *args, **kwargs):
    stats = database.stats.find_one({'id': message.from_user.id, 'chat': message.chat.id})

    if not stats:
        bot.send_message(message.chat.id, f'Statistika {get_name(message.from_user)} boşdur.')
        return

    paragraphs = []

    if 'croco' in stats:
        answer = f'Hesab {get_name(message.from_user)} {get_croco_score(stats)}'
        total = stats['croco'].get('total')
        if total:
            win = stats['croco'].get('win', 0)
            answer += f'\nQələbə: {win}/{total} ({100 * win // total}%)'
        guesses = stats['croco'].get('guesses')
        if guesses:
            answer += f'\nTəxminən: {guesses}'
        paragraphs.append(answer)

    bot.send_message(message.chat.id, '\n\n'.join(paragraphs))


def update_rating(rating, name, score, maxlen):
    place = None
    for i, (_, rating_score) in enumerate(rating):
        if score > rating_score:
            place = i
            break
    if place is not None:
        rating.insert(place, (name, score))
        if len(rating) > maxlen:
            rating.pop(-1)
    elif len(rating) < maxlen:
        rating.append((name, score))


def get_rating_list(rating):
    return '\n'.join(f'{i + 1}. {n}: {s}' for i, (n, s) in enumerate(rating))


@bot.message_handler(regexp=command_regexp('rating'))
def rating_command(message, *args, **kwargs):
    chat_stats = database.stats.find({'chat': message.chat.id})

    if not chat_stats:
        bot.send_message(message.chat.id, 'Qrupda statistika boşdur.')
        return

    mafia_rating = []
    croco_rating = []
    for stats in chat_stats:
        if 'croco' in stats:
            update_rating(croco_rating, stats['name'], get_croco_score(stats), 3)

    paragraphs = []
    if croco_rating:
        paragraphs.append('Oyunçu reytinqi::\n' + get_rating_list(croco_rating))

    bot.send_message(message.chat.id, '\n\n'.join(paragraphs))


@bot.group_message_handler(regexp=command_regexp('game'))
def play_croco(message, game, *args, **kwargs):
    if game:
        bot.send_message(message.chat.id, 'Oyun artıq davam edir.')
        return
    word = croco.get_word()[:-2]
    id = str(uuid4())[:8]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text='Sözə baxın',
            callback_data=f'get_word {id}'
        )
    )
    name = get_name(message.from_user)
    database.games.insert_one({
        'game': 'croco',
        'id': id,
        'player': message.from_user.id,
        'name': name,
        'full_name': get_full_name(message.from_user),
        'word': word,
        'chat': message.chat.id,
        'time': time() + 60,
        'stage': 0
    })
    bot.send_message(
        message.chat.id,
        f'Oyun başladı! {name.capitalize()}, sözü izah etmək üçün 2 dəqiqə vaxtınız var.',
        reply_markup=keyboard
    )


@bot.group_message_handler(regexp=command_regexp('gallows'))
def play_gallows(message, game, *args, **kwargs):
    if game:
        if game['game'] == 'gallows':
            bot.send_message(message.chat.id, 'Oyun artıq davam edir.', reply_to_message_id=game['message_id'])
        else:
            bot.send_message(message.chat.id, 'Oyun artıq davam edir.')
        return
    word = croco.get_word()[:-2]
    sent_message = bot.send_message(
        message.chat.id,
        lang.gallows.format(
            result='', word=' '.join(['_'] * len(word)), attempts='', players=''
        ) % gallows.stickman[0],
        parse_mode='HTML'
    )
    database.games.insert_one({
        'game': 'gallows',
        'chat': message.chat.id,
        'word': word,
        'wrong': {},
        'right': {},
        'names': {},
        'message_id': sent_message.message_id
    })


@bot.callback_query_handler(func=lambda call: call.data.startswith('get_word'))
def get_word(call):
    game = database.games.find_one(
        {'game': 'croco', 'id': call.data.split()[1], 'player': call.from_user.id}
    )
    if game:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=True,
            text=f'Sənin sözün: {game["word"]}.'
        )
    else:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text='Bu oyun üçün söz tapa bilmirsiniz.'
        )

@bot.group_message_handler(regexp=command_regexp('end'))
def force_game_end(message, game, *args, **kwargs):
    create_poll(message, game, 'end', 'Oyunu bitir')


@bot.group_message_handler(regexp=command_regexp('skip'))
def skip_current_stage(message, game, *args, **kwargs):
    create_poll(message, game, 'skip', 'Cari mərhələni atla')

def reset(message, *args, **kwargs):
    database.games.delete_many({})
    bot.send_message(message.chat.id, 'Oyun verilənlər bazasının sıfırlanması!')


@bot.message_handler(
    func=lambda message: message.from_user.id == config.ADMIN_ID,
    regexp=command_regexp('database')
)
def print_database(message, *args, **kwargs):
    print(list(database.games.find()))
    bot.send_message(message.chat.id, 'Oyun bazasının bütün sənədləri terminalda göstərilir!')


@bot.group_message_handler(content_types=['text'])
def game_suggestion(message, game, *args, **kwargs):
    if not game or message.text is None:
        return
    suggestion = message.text.lower().replace('ё', 'е')
    user = user_object(message.from_user)
    if game['game'] == 'gallows':
        return gallows.gallows_suggestion(suggestion, game, user, message.message_id)
    elif game['game'] == 'croco':
        return croco.croco_suggestion(suggestion, game, user, message.message_id)

@bot.group_message_handler()
def default_handler(message, *args, **kwargs):
    pass

# This file is part of Hycon (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyrogram import Client, filters
from pyrogram.types import Message, User
from kantex.html import (Bold, Code, KanTeXDocument, KeyValueItem, Section,
                         SubSection)
from .. import COMMANDS_HELP

COMMANDS_HELP["misc"] = {
    "name": "Misc",
    "commands": {
        "user": {
            "id <user|reply>?": "Get (user|chat) id.",
            "info <user|reply>?": "Get a user info."
        }
    },
    "text": "Here you can play a little with the miscellaneous section.",
    "help": True
}


@Client.on_message(filters.reply & filters.cmd('info$'))
async def on_info_r_m(c: Client, m: Message):
    reply = m.reply_to_message
    user = reply.from_user
    await on_info_u(c, m, user)


@Client.on_message(~filters.reply & filters.cmd('info$'))
async def on_info_me_m(c: Client, m: Message):
    user = m.from_user
    await on_info_u(c, m, user)


@Client.on_message(filters.cmd('info (?P<user>.+)'))
async def on_info_m(c: Client, m: Message):
    user = m.matches[0]['user']
    try:
        user = int(user)
    except BaseException:
        pass
    try:
        user = await c.get_users(user)
    except BaseException:
        user = m.from_user
    await on_info_u(c, m, user)


@Client.on_message(filters.cmd('id$'))
async def on_id_m(c: Client, m: Message):
    reply = m.reply_to_message
    name, id = '', 0

    if reply:
        name = 'User ' + reply.from_user.first_name
        id = reply.from_user.id
    else:
        name = 'This chat'
        id = m.chat.id

    await m.reply_text(text=f'{name}\'s id is: <code>{id}</code>.')


async def on_info_u(c: Client, m: Message, user: User):
    doc = KanTeXDocument(
        Section(user.first_name,
                SubSection('General',
                           KeyValueItem('id', Code(user.id)),
                           KeyValueItem('first_name', Code(user.first_name)),
                           KeyValueItem('last_name', Code(user.last_name)),
                           KeyValueItem('username', Code(user.username)))))
    # TODO: add mention
    await m.reply_text(doc)

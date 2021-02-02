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
from pyrogram.types import CallbackQuery, Message
from pyromod.helpers import ikb
from .. import bot, COMMANDS_HELP

import html


@Client.on_message(filters.private & filters.cmd(r"(help|start)$"))
async def on_start_m(c: Client, m: Message):
    await on_start_u(c, m)


@Client.on_message(~filters.private & filters.cmd(r"help (?P<module>.+)"))
async def on_help_module_m(c: Client, m: Message):
    module = m.matches[0]['module']
    await m.reply_text(text='Press the button below to continue.', reply_markup=ikb([[('Check in PM', f'https://t.me/{bot.me.username}?start=help_{module}', 'url')]]))


@Client.on_message(filters.private & filters.cmd(r"start (?P<any>.+)"))
async def on_start_any_m(c: Client, m: Message):
    any = m.matches[0]['any']
    if 'help' in any:
        module = any.split('_')[1]
        await on_help_module_u(c, m, module)


@Client.on_message(filters.private & filters.cmd(r"help (?P<module>.+)"))
async def on_help_module_pm_m(c: Client, m: Message):
    module = m.matches[0]['module']
    await on_help_module_u(c, m, module)


async def on_start_u(c: Client, u: Message, edit: bool = False):
    text = "Below are some of my modules, tap on one and learn how to use it."
    help_count = 0
    for key, value in COMMANDS_HELP.items():
        if value['help']:
            help_count += 1
    lines_count = help_count / 3
    lines_count = int(lines_count) if int(
        str(lines_count).split('.')[1]) == 0 else int(lines_count) + 1
    buttons = [[] for a in range(lines_count)]
    help_count = 0
    line = 0
    for key, value in COMMANDS_HELP.items():
        if value['help']:
            help_count += 1
            buttons[line].append((value['name'], f'help_{key}'))
            if help_count > 2:
                help_count = 0
                line += 1
    await (u.edit_text if edit else u.reply_text)(text=text, reply_markup=ikb(buttons))


@Client.on_callback_query(filters.regex('help_(?P<module>.+)'))
async def on_help_module_cq(c: Client, cq: CallbackQuery):
    module = cq.matches[0]['module']
    await on_help_module_u(c, cq.message, module, True)


async def on_help_module_u(c: Client, u: Message, module: str, edit: bool = False):
    text = f'Here you will understand how the <b>{module}</b> module works.\n\n'
    module_d = None
    if module == 'start':
        await on_start_u(c, u, True)
        return
    elif module not in COMMANDS_HELP.keys():
        text = f'The <b>{module}</b> module was not found!\n'
        text += 'See the available modules by touching the button below.'
        await (u.edit_text if edit else u.reply_text)(text=text, reply_markup=ikb([[('<- Back', 'help_start')]]))
        return
    else:
        module_d = COMMANDS_HELP[module]
        text += module_d['text']

    if 'commands' in module_d.keys():
        commands = module_d['commands']
        if len(commands.keys()) > 0:
            for type in commands:
                text += f'\n\n<b>{type.capitalize()} commands</b>:'
                for command, description in commands[type].items():
                    cmd = command.split()[0]
                    arguments = html.escape(command[len(cmd):])
                    text += f'\n- /{cmd}<code>{arguments}</code>: {html.escape(description)}'

    if edit or u.chat.type == 'private':
        await (u.edit_text if edit else u.reply_text)(text=text, reply_markup=ikb([[('<- Back', 'help_start')]]))
    else:
        await (u.edit_text if edit else u.reply_text)(text=text)

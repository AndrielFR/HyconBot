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

import datetime
import humanize
import io
import os
import requests
import sys
import json

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from pyromod.helpers import ikb
from .. import COMMANDS_HELP
from typing import Dict, List


COMMANDS_HELP["devices"] = {
    "name": "Devices",
    "commands": {
        "user": {
            "device <codename>": "Get information about the device and builds with such a code name (if it is officially maintained)."
        }
    },
    "text": "This is the plugin where you can get data about the specific device.",
    "help": True
}


DEVICES_REPO = 'https://github.com/Hycon-Devices/official_devices/raw/master'
BUILDS = {}


@Client.on_message(filters.cmd('device (?P<codename>.+)'))
async def on_device_m(c: Client, m: Message):
    codename = m.matches[0]['codename']
    model = check_device(codename)
    if not model:
        await m.reply_text(text=f'The device <b>{codename}</b> was not found!')
    else:
        await get_device(m, model)


def check_device(device: str) -> bool:
    response = requests.get(DEVICES_REPO+'/devices.json')
    models = json.loads(response.text)
    for model in models:
        if model['codename'] == device:
            return model
    return False


async def get_device(u, model: Dict):
    is_query = isinstance(u, CallbackQuery)
    text = '<b>HyconOS</b>\n'
    text += '\n'
    text += f'<b>Brand</b>: <code>{model["brand"]}</code>\n'
    text += f'<b>Device</b>: <code>{model["name"]}</code>\n'
    text += f'<b>Codename</b>: <code>{model["codename"]}</code>\n'
    versions = []
    maintainers = []
    for version in model['supported_versions']:
        maintainers.append(version['maintainer_name'] + ' ' + '(' + version['version_name'] + ')')
        versions.append(version['version_name'] + ' (' + version['version_code'] + ')')
    text += f'<b>Maintainer(s)</b>: <code>{", ".join(maintainers)}</code>\n'
    text += f'<b>Version(s)</b>: <code>{", ".join(versions)}</code>\n'
    keyboard = []
    builds = get_builds(model['codename'])
    text += f'<b>Builds</b>: <code>{len(builds)}</code>\n'
    if len(builds) > 0:
        id = len(BUILDS.keys())
        BUILDS[str(id)] = {
             'user_id': u.from_user.id,
             'chat_id': u.message.chat.id if is_query else u.chat.id,
             'codename': model['codename'],
             'builds': builds
        }
        keyboard.append(('📓 Builds', f'get_builds {id} 1'))
    kwargs = {}
    if len(keyboard) > 0:
        kwargs['reply_markup'] = ikb([keyboard])
    await (u.edit_message_text if is_query else u.reply_text)(text=text, **kwargs)


def get_builds(device: str) -> List:
    builds = []
    response = requests.get(DEVICES_REPO+f'/builds/{device}.json')
    data = json.loads(response.text)
    if isinstance(data, List):
        for item in data:
            item['changelog'] = get_changelog(device, item['filename'])
        builds = data
    return builds


def get_changelog(device: str, filename: str) -> str:
    response = requests.get(DEVICES_REPO+f'/changelogs/{device}/{filename}.txt')
    data = response.text
    changelog = data
    return changelog


@Client.on_callback_query(filters.regex('^get_builds (?P<id>\d+) (?P<page>\d+)$'))
async def on_get_builds_cq(c: Client, cq: CallbackQuery):
    id = int(cq.matches[0]['id'])
    page = int(cq.matches[0]['page'])
    builds = BUILDS[str(id)]
    codename = builds['codename']
    if cq.message.chat.id == builds['chat_id']:
        if cq.from_user.id == builds['user_id']:
            builds = builds['builds']
            build = builds[page-1]
            keyboard = []
            text = f'<b>HyconOS {codename} build (<i>#{page}</i>)</b>\n\n'
            text += f'<b>ID</b>: <code>{build["id"]}</code>\n'
            size = humanize.naturalsize(build['size'])
            text += f'<b>Size</b>: <code>{size}</code>\n'
            text += f'<b>Hash</b>: <code>{build["filehash"]}</code>\n'
            text += f'<b>Device</b>: <code>{codename}</code>\n'
            text += f'<b>Version</b>: <code>{build["version"]}</code>\n'
            date = datetime.datetime.fromtimestamp(build['datetime'])
            released = humanize.naturaltime(date)
            text += f'<b>Released</b>: <code>{released}</code>\n'
            text += f'<b>File name</b>: <code>{build["filename"]}</code>\n'
            text += f'<b>Maintainer(s)</b>: <code>{build["maintainer"]}</code>\n'
            download_keyboard = []
            xda = build['forum_url']
            if len(xda) > 0:
                download_keyboard.append(('🌐 XDA', xda, 'url'))
            changelog = build['changelog']
            if len(changelog) < 1200:
                text += f'\n<b>Changelog</b>: \n<code>{changelog}</code>\n'
            else:
                download_keyboard.append(('📜 Changelog', f'get_changelog {id} {page}'))
            download_keyboard.append(('⬇️ Download', build["url"], 'url'))
            keyboard.append(download_keyboard)
            page_keyboard = []
            if not len(builds) == page:
                page_keyboard.append(('⬅️ Previous', f'get_builds {id} {page-2}'))
            if len(builds) > page:
                page_keyboard.append(('➡️ Next', f'get_builds {id} {page+1}'))
            if len(page_keyboard) > 0:
                keyboard.append(page_keyboard)
            keyboard.append([('🔙 Back', f'get_device {id}')])
            kwargs = {
                'reply_markup': ikb(keyboard)
            }
            await cq.edit_message_text(text=text, **kwargs)


@Client.on_callback_query(filters.regex('^get_device (?P<id>\d+)$'))
async def on_get_device_cq(c: Client, cq: CallbackQuery):
    id = int(cq.matches[0]['id'])
    builds = BUILDS[str(id)]
    codename = builds['codename']
    if cq.message.chat.id == builds['chat_id']:
        if cq.from_user.id == builds['user_id']:
            model = check_device(codename)
            await get_device(cq, model)
    
    
@Client.on_callback_query(filters.regex('^get_changelog (?P<id>\d+) (?P<page>\d+)$'))
async def on_get_changelog_cq(c: Client, cq: CallbackQuery):
    id = int(cq.matches[0]['id'])
    page = int(cq.matches[0]['page'])
    builds = BUILDS[str(id)]
    if cq.message.chat.id == builds['chat_id']:
        if cq.from_user.id == builds['user_id']:
            builds = builds['builds']
            build = builds[page-1]
            text = '<b>HyconOS changelog</b>\n\n'
            text += f'<b>File name</b>: <code>{build["filename"]}</code>\n'
            changelog = build['changelog']
            if len(changelog) < 4096:
                text += f'\n<b>Changelog</b>: \n<code>{changelog}</code>\n'
                keyboard = [
                    [('🔙 Back', f'get_builds {id} {page}')]
                ]
                await cq.edit_message_text(text=text, reply_markup=ikb(keyboard))
            else:
                document = io.BytesIO(changelog)
                document.name = build['filename'].replace('.zip', '.txt')
                await c.send_document(chat_id=cq.message.chat.id, document=document)
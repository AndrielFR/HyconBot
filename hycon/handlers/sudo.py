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

import os
import sys

from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.sudo & filters.cmd('restart'))
async def on_restart_m(c: Client, m: Message):
    await m.reply_text('Restarting...')
    os.execv(sys.executable, [sys.executable, '-m', 'hycon'])


@Client.on_message(filters.sudo & filters.cmd('shutdown'))
async def on_shutdown_m(c: Client, m: Message):
    await m.reply_text("Sleeping...")
    sys.exit()

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

from pyrogram import filters, idle
from .config import PREFIXES, SUDO_USERS
from . import bot

import os
import re


def filter_cmd(command, *args, **kwargs):
    prefixes = ''.join(PREFIXES)
    prefix = f"^[{re.escape(prefixes)}]"
    return filters.regex(prefix + command, *args, **kwargs)


def filter_sudo(__, c, m):
    user = m.from_user
    if not user:
        return False
    return user.id in SUDO_USERS


filters.cmd = filter_cmd
filters.sudo = filters.create(filter_sudo, 'FilterSudo')


os.system('clear')
if __name__ == "__main__":
    with bot:
        bot.me = bot.get_me()
        start_message = 'HyconBot started!'
        try:
            for user in SUDO_USERS:
                bot.send_message(chat_id=user, text=start_message)
        except BaseException:
            pass

        idle()

##
# This file is part of the AutoBackups package.
#
# (c) Gabriel Tenita <the.ge.1447624801@tenita.eu>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
##

import sublime
import sublime_plugin
import sys
from imp import reload
from AutoBackups.autobackups import reloader


reloader_name = "AutoBackups.autobackups.reloader"
if reloader_name in sys.modules:
    reload(sys.modules[reloader_name])


class AutoBackupsDonateCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        sublime.message_dialog("AutoBackups: Thanks for your support ^_^")
        webbrowser.open_new_tab(
            "https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=akalongman@gmail.com&item_name=Donation to Sublime Text - AutoBackups&item_number=1&no_shipping=1"
        )

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
from AutoBackups.autobackups import bootstrap
from AutoBackups.autobackups import reloader
from AutoBackups.autobackups.paths_helper import PathsHelper


reloader_name = "AutoBackups.autobackups.reloader"
if reloader_name in sys.modules:
    reload(sys.modules[reloader_name])


def plugin_loaded():
    global settings
    global hashes
    settings, hashes = bootstrap.init()


class AutoBackupsOpenBackupsFolderCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        self.openDir(settings.get('backup_dir'))

    def openDir(self, dirpath):
        if sublime.platform() == "windows":
            import subprocess
            dirpath = dirpath.replace("^", "^^")
            subprocess.Popen(['explorer', dirpath])
        else:
            sublime.active_window().run_command("open_dir", {"dir": dirpath})

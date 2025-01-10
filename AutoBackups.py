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
import os
import shutil
import re
import hashlib
import time
import threading
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

    backup_time = settings.get("delete_old_backups", 0)
    if backup_time > 0:
        sublime.set_timeout(gc, 10000)


def gc():
    backup_time = settings.get("delete_old_backups", 0)
    if backup_time > 0:
        thread = AutoBackupsGcBackup(backup_time)
        thread.start()


class AutoBackupsEventListener(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        self.save_backup(view, 0)

    def on_load_async(self, view):
        if settings.get("backup_on_open_file"):
            self.save_backup(view, 1)

    def save_backup(self, view, on_load_event):
        if view.is_read_only():
            return

        view_size = view.size()
        max_backup_file_size = settings.get("max_backup_file_size_bytes")
        if view_size is None:
            self.console("View size not available.")
            return

        if max_backup_file_size is None:
            self.console("Max size allowed by config not available.")
            return

        # don't save files above configured size
        if view_size > max_backup_file_size:
            self.console("Backup not saved, file too large (%d bytes)." % view.size())
            return

        filepath = view.file_name()
        if filepath == None:
            return

        # Check file path in excluded regexes
        if self.is_excluded(filepath):
            print("AutoBackups: " + filepath + " is excluded");
            return

        # not create file backup if current file is backup
        if on_load_event & self.is_backup_file(filepath):
            return

        newname = PathsHelper.get_backup_filepath(filepath)
        if newname == None:
            return

        self.console("Autobackup to: " + newname)

        buffer_id = view.buffer_id()
        content = filepath + view.substr(sublime.Region(0, view_size))
        content = self.encode(content)
        current_hash = hashlib.md5(content).hexdigest()

        last_hash = ""
        try:
            last_hash = hashes[buffer_id]
        except Exception as e:
            last_hash = ""

        # not create file backup if no changes from last backup
        if last_hash == current_hash:
            return

        # not create file if exists
        if on_load_event & os.path.isfile(newname):
            return

        (backup_dir, file_to_write) = os.path.split(newname)

        if os.access(backup_dir, os.F_OK) == False:
            os.makedirs(backup_dir)

        try:
            shutil.copy(filepath, newname)
        except FileNotFoundError:
            self.console("Backup not saved. File " + filepath + " does not exist!")
            return False

        hashes[buffer_id] = current_hash
        # self.console('Backup saved to: '+newname.replace('\\', '/'))

    def is_backup_file(self, path):
        backup_per_time = settings.get("backup_per_time")
        path = PathsHelper.normalise_path(path)
        base_dir = PathsHelper.get_base_dir(False)
        base_dir = PathsHelper.normalise_path(base_dir)
        if backup_per_time == "folder":
            base_dir = base_dir[:-7]

        backup_dir_len = len(base_dir)
        sub = path[0:backup_dir_len]

        if sub == base_dir:
            return True
        else:
            return False

    def is_excluded(self, filepath):
        # check
        ignore_regexes = settings.get("ignore_regexes")

        if ignore_regexes is None or ignore_regexes == "":
            return False

        for regex in ignore_regexes:
            prog = re.compile(".*" + regex + ".*")
            result = prog.match(filepath)
            if result is not None:
                return True

        return False

    def console(self, text):
        print(text)
        return

    def fileChanged(self, text):
        return

    def encode(self, text):
        if isinstance(text, str):
            text = text.encode("UTF-8")
        return text


class AutoBackupsGcBackup(threading.Thread):
    backup_time = 0

    def __init__(self, back_time):
        self.backup_time = back_time
        threading.Thread.__init__(self)

    def run(self):
        import datetime

        basedir = PathsHelper.get_base_dir(True)
        backup_time = self.backup_time

        if backup_time < 1:
            return

        diff = (backup_time + 1) * 24 * 3600
        deleted = 0
        now_time = time.time()
        for folder in os.listdir(basedir):
            match = re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", folder)
            if match is not None:
                folder_time = time.mktime(
                    datetime.datetime.strptime(folder, "%Y-%m-%d").timetuple()
                )
                if now_time - folder_time > diff:
                    fldr = basedir + "/" + folder
                    try:
                        shutil.rmtree(fldr, onerror=self.onerror)
                        deleted = deleted + 1
                    except Exception as e:
                        print(e)

        if deleted > 0:
            diff = backup_time * 24 * 3600
            dt = now_time - diff
            date = datetime.datetime.fromtimestamp(dt).strftime("%Y-%m-%d")
            print(
                "AutoBackups: Deleted "
                + str(deleted)
                + " backup folders older than "
                + date
            )

    def onerror(self, func, path, exc_info):
        import stat

        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

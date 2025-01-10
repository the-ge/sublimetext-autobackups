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
import re
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


class AutoBackupsOpenBackupFolderCommand(sublime_plugin.TextCommand):
    datalist = []
    curline = 1

    def run(self, edit):
        backup_per_day = settings.get("backup_per_day")

        window = sublime.active_window()
        view = window.active_view()

        if backup_per_day:
            f_files = self.getData(False)

            if not f_files:
                sublime.error_message("Backups for this file do not exist!")
                return

            backup_per_time = settings.get("backup_per_time")
            if backup_per_time:
                window.show_quick_panel(f_files, self.timeFolders)
            else:
                window.show_quick_panel(f_files, self.openFile)
            return

        else:
            filepath = view.file_name()
            backup_path = PathsHelper.get_backup_path(filepath)
            self.openDir(backup_path)


    def getData(self, time_folder):
        filepath = PathsHelper.normalise_path(self.view.file_name(), True)
        basedir = PathsHelper.get_base_dir(True)

        backup_per_time = settings.get("backup_per_time")
        if backup_per_time:
            if backup_per_time == "folder":
                f_files = []
                if time_folder is not False:
                    tm_folders = self.getData(False)
                    tm_folder = tm_folders[time_folder][0]
                    basedir = basedir + "/" + tm_folder

                    if not os.path.isdir(basedir):
                        sublime.error_message("Folder " + basedir + " not found!")

                    for folder in os.listdir(basedir):
                        fl = basedir + "/" + folder + "/" + filepath
                        match = re.search(r"^[0-9+]{6}$", folder)
                        if os.path.isfile(fl) and match is not None:
                            folder_name, file_name = os.path.split(fl)
                            f_file = []
                            time = self.formatTime(folder)
                            f_file.append(time + " - " + file_name)
                            f_file.append(fl)
                            f_files.append(f_file)
                else:
                    path, flname = os.path.split(filepath)
                    (filepart, extpart) = os.path.splitext(flname)
                    for folder in os.listdir(basedir):
                        match = re.search(r"^[0-9+]{4}-[0-9+]{2}-[0-9+]{2}$", folder)
                        if match is not None:
                            folder_name, file_name = os.path.split(filepath)
                            f_file = []
                            basedir2 = basedir + "/" + folder
                            count = 0
                            last = ""
                            for folder2 in os.listdir(basedir2):
                                match = re.search(r"^[0-9+]{6}$", folder2)
                                if match is not None:
                                    basedir3 = (
                                        basedir
                                        + "/"
                                        + folder
                                        + "/"
                                        + folder2
                                        + "/"
                                        + filepath
                                    )
                                    if os.path.isfile(basedir3):
                                        count += 1
                                        last = folder2
                            if count > 0:
                                f_file.append(folder)
                                f_file.append(
                                    "Backups: "
                                    + str(count)
                                    + ", Last edit: "
                                    + self.formatTime(last)
                                )
                                f_files.append(f_file)
            elif backup_per_time == "file":
                f_files = []
                if time_folder is not False:
                    tm_folders = self.getData(False)
                    tm_folder = tm_folders[time_folder][0]
                    path, flname = os.path.split(filepath)
                    basedir = basedir + "/" + tm_folder + "/" + path
                    (filepart, extpart) = os.path.splitext(flname)

                    if not os.path.isdir(basedir):
                        sublime.error_message("Folder " + basedir + " not found!")

                    for folder in os.listdir(basedir):
                        fl = basedir + "/" + folder
                        match = re.search(
                            r"^"
                            + re.escape(filepart)
                            + "_([0-9+]{6})"
                            + re.escape(extpart)
                            + "$",
                            folder,
                        )

                        if os.path.isfile(fl) and match is not None:
                            time = self.formatTime(match.group(1))
                            f_file = []
                            f_file.append(time + " - " + flname)
                            f_file.append(fl)
                            f_files.append(f_file)
                else:
                    path, flname = os.path.split(filepath)
                    (filepart, extpart) = os.path.splitext(flname)
                    for folder in os.listdir(basedir):
                        match = re.search(r"^[0-9+]{4}-[0-9+]{2}-[0-9+]{2}$", folder)
                        if match is not None:
                            folder_name, file_name = os.path.split(filepath)
                            f_file = []
                            basedir2 = basedir + "/" + folder + "/" + path
                            count = 0
                            last = ""
                            if os.path.isdir(basedir2):
                                for sfile in os.listdir(basedir2):
                                    match = re.search(
                                        r"^"
                                        + re.escape(filepart)
                                        + "_([0-9+]{6})"
                                        + re.escape(extpart)
                                        + "$",
                                        sfile,
                                    )
                                    if match is not None:
                                        count += 1
                                        last = match.group(1)
                            if count > 0:
                                f_file.append(folder)
                                f_file.append(
                                    "Backups: "
                                    + str(count)
                                    + ", Last edit: "
                                    + self.formatTime(last)
                                )
                                f_files.append(f_file)
        else:
            f_files = []
            for folder in os.listdir(basedir):
                fl = basedir + "/" + folder + "/" + filepath
                match = re.search(r"^[0-9+]{4}-[0-9+]{2}-[0-9+]{2}$", folder)
                if os.path.isfile(fl) and match is not None:
                    folder_name, file_name = os.path.split(fl)
                    f_file = []
                    f_file.append(folder + " - " + file_name)
                    f_file.append(fl)
                    f_files.append(f_file)
        f_files.sort(key=lambda x: x[0])
        f_files.reverse()
        self.datalist = f_files
        return f_files

    def timeFolders(self, parent):
        if parent == -1:
            return

        # open file
        f_files = self.getData(parent)
        show_previews = settings.get("show_previews", True)
        if show_previews:
            sublime.set_timeout_async(
                lambda: self.view.window().show_quick_panel(
                    f_files, self.openFile, on_highlight=self.showFile
                ),
                100,
            )
        else:
            sublime.set_timeout_async(
                lambda: self.view.window().show_quick_panel(f_files, self.openFile), 100
            )

        return

    def showFile(self, file):
        if file == -1:
            return

        f_files = self.datalist
        filepath = f_files[file][1]
        window = self.view.window()

        view = window.open_file(
            filepath + ":" + str(self.curline),
            sublime.ENCODED_POSITION | sublime.TRANSIENT,
        )
        view.set_read_only(True)

    def openDir(self, dirpath):
        if sublime.platform() == "windows":
            import subprocess
            dirpath = dirpath.replace("^", "^^")
            subprocess.Popen(['explorer', dirpath])
        else:
            sublime.active_window().run_command("open_dir", {"dir": dirpath})

    def openFile(self, file):
        if file == -1:
            window = sublime.active_window()
            window.focus_view(self.view)
            return

        f_files = self.datalist
        filepath = f_files[file][1]

        window = self.view.window()
        view = window.open_file(
            filepath + ":" + str(self.curline), sublime.ENCODED_POSITION
        )
        view.set_read_only(True)
        window.focus_view(view)

    def formatTime(self, time):
        time = time[0:2] + ":" + time[2:4] + ":" + time[4:6]
        return time

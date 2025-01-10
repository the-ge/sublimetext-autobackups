##
# This file is part of the AutoBackups package.
#
# (c) Gabriel Tenita <the.ge.1447624801@tenita.eu>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
##

import sublime
import sys
from imp import reload
from AutoBackups.autobackups.paths_helper import PathsHelper


def init():
    hashes = {}
    platform = sublime.platform().title()

    if platform == "Osx":
        platform = "OSX"
    settings = sublime.load_settings("AutoBackups (" + platform + ").sublime-settings")

    backup_dir = settings.get("backup_dir")
    backup_per_day = settings.get("backup_per_day")
    backup_per_time = settings.get("backup_per_time")
    backup_name_mode = settings.get("backup_name_mode")

    PathsHelper.initialize(
        platform, backup_dir, backup_per_day, backup_per_time, backup_name_mode
    )
    #print('AutoBackups:    dir={}    per_day={}    per_time={}    name_mode={}'.format(backup_dir, backup_per_day, backup_per_time, backup_name_mode))

    return settings, hashes
# -*- coding: utf-8 -*-
# Licensed under the EUPL v1.2
# © 2019 bicobus <bicobus@keemail.me>
import os
import json
import logging
import tempfile
import shutil
import atexit
import gzip

from collections.abc import MutableMapping
from appdirs import AppDirs
from PyQt5.QtCore import QTimer

logger = logging.getLogger(__name__)
dirs = AppDirs(appname='qmm', appauthor=False)


def get_config_dir(filename=None, extra_directories=None) -> str:
    """Return the full path of the user config dir.

    Args:
        filename: If provided, gets added at the end of the string.
        extra_directories: If provided, extends on the returned path.
    """
    config_path = []
    if extra_directories and isinstance(extra_directories, list):
        config_path.extend(extra_directories)
    if filename:
        config_path.append(filename)
    path = os.path.join(dirs.user_config_dir, *config_path)
    return path


class Config(MutableMapping):
    """Influenced by deluge's config object."""

    def __init__(self, filename, config_dir=None, defaults=None,
                 compress=False):
        self._data = {}
        self._save_timer = False
        self._compress = compress

        if defaults:
            for key, val in defaults.items():
                self[key] = val

        if config_dir:
            self._filename = os.path.join(config_dir, filename)
        else:
            self._filename = get_config_dir(filename)

        if self._compress:
            self._filename = "{}.gz".format(self._filename)

        # self._timer = QTimer(parent)
        # Force saving config file at termination of the software
        atexit.register(self.save)

        self.load(self._filename)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if key not in self._data:
            self._data[key] = value
            return

        if self._data[key] == value:
            return
        self._data[key] = value

        logger.debug("Config key state changed, save timer state is: %s", self._save_timer)
        if not self._save_timer:
            self.delayed_save()

    def __delitem__(self, key):
        del self._data[key]

        logger.debug("Deleting config key, save timer state is: %s", self._save_timer)
        if not self._save_timer:
            self.delayed_save()

    def _get_data_from_file(self, filename=None):
        if not os.path.exists(filename):
            return None

        try:
            if self._compress:
                with gzip.GzipFile(filename, 'r') as fp:
                    json_bytes = fp.read()
                data = json.loads(json_bytes.decode('utf-8'))
            else:
                with open(filename, 'r', encoding="utf-8") as f:
                    data = json.load(f)
        except IOError as e:
            logger.warning("Unable ti load config file %s: %s", filename, e)
            return None
        return data

    def load(self, filename=None):
        if not filename:
            filename = self._filename
        if self._compress and os.path.splitext(filename)[1] != ".gz":
            filename = "{}.gz".format(filename)

        logger.debug("Loading information from settings file: %s", filename)
        data = self._get_data_from_file(filename)
        if data:
            self._data.update(data)

    def delayed_save(self, msec=5000):
        """Schedule a save in the future if one isn't already planned."""
        if not self._save_timer:
            QTimer.singleShot(msec, self.save)
            self._save_timer = True
            logger.debug("Initializing delayed save.")

    def _disable_save_timer(self):
        if self._save_timer:
            self._save_timer = False

    def save(self, filename=None):
        if not filename:
            filename = self._filename
        elif self._compress and os.path.splitext(filename) != ".gz":
            filename = "{}.gz".format(filename)

        logger.debug("Saving file %s", filename)
        # Do not save anything if the contents are the same.
        data = self._get_data_from_file(filename)
        if self._data == data:
            logger.debug("Save triggered but data is unchanged: doing nothing.")
            self._disable_save_timer()
            return True

        try:
            with tempfile.NamedTemporaryFile(delete=False) as fp:
                filename_tmp = fp.name
                jdump = json.dumps(self._data, indent=4).encode('utf-8')
                if self._compress:
                    jdump = gzip.compress(jdump)
                fp.write(jdump)
                fp.flush()
                os.fsync(fp)

            filename = os.path.realpath(filename)
            shutil.move(filename, "{}.bak".format(filename))
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            shutil.move(filename_tmp, filename)
        except IOError as e:
            logger.error("An error occured while saving the settings:\n%s", e)
            return False
        else:
            logger.debug(
                "Check save timer at end of save method. Auto save state: %s",
                self._save_timer)
            self._disable_save_timer()
            return True

# Licensed under the EUPL v1.2
# © 2019 bicobus <bicobus@keemail.me>
import os
import logging
import shutil
import yaml

from io import TextIOWrapper
from hashlib import sha256
from zipfile import ZipFile, is_zipfile
from py7zlib import Archive7z, ArchiveError, MAGIC_7Z

from .config import Config
log = logging.getLogger(__name__)


class UnrecognizedArchive(Exception):
    pass


def _check_7zfile(fp):
    try:
        if fp.read(len(MAGIC_7Z)) == MAGIC_7Z:
            return True
    except OSError:
        pass
    return False


def is_7zfile(filename):
    """Check the magic number of a file and ensure it is a 7z archive.

    The filename argument can be an IO stream or a string
    """
    result = False
    try:
        if hasattr(filename, "read"):
            result = _check_7zfile(fp=filename)
        else:
            with open(filename, "rb") as fp:
                result = _check_7zfile(fp)
    except OSError:
        pass
    return result


def _get_mod_folder(config_obj, with_file=None, has_res=False):
    path = [config_obj['game_folder']]
    if not has_res:
        path.extend(['res', 'mods'])
    if with_file:
        path.append(with_file)
    return os.path.join(*path)


class ArchiveInterface:
    def __init__(self, filename):
        self.filename = filename
        if is_zipfile(filename):
            self.filetype = "zip"
        elif is_7zfile(filename):
            self.filetype = "7z"
        else:
            raise UnrecognizedArchive("Unsupported archive: %s", filename)

        self._archive_object = None

    def __exit__(self, type, value, traceback):
        self.close()

    def _get_archive_object(self):
        """Initialize the file pointer and archive object
        """
        if self._archive_object:
            return self._archive_object

        self._filestream = open(self.filename, 'rb')
        if self.filetype == 'zip':
            self._archive_object = ZipFile(self._filestream)
        elif self.filetype == '7z':
            try:
                self._archive_object = Archive7z(self._filestream)
            except ArchiveError as e:
                log.error("Something bad happened while handling the archive:\n%s", e)
                return False

    def namelist(self):
        """Walk through an archive and yield each member
        """
        if self.filetype == "zip":
            for member in self._archive_object.namelist():
                yield member
        elif self.filetype == "7z":
            for member in self._archive_object.getmembers():
                yield member

    def extract(self, item, destination):
        """Extract one member of an archive to destination.

        If item is from a Archive7z object, make sure the remote folder exists.
        """
        if self.filetype == "zip":
            self._archive_object.extract(item, destination)
        elif self.filetype == "7z":
            if not os.path.exists(os.path.dirname(item)):
                os.makedirs(os.path.dirname(item))
            with open(item, 'wb') as fp:
                fp.write(item.read())

    def close(self):
        """Properly free the resource
        """
        try:
            self._filestream.close()
        except Exception:
            log.exception("Unable to close the archive file.")
            raise
        self._archive_object = None

    @property
    def archive_object(self):
        if not self._archive_object:
            self._get_archive_object()
        return self._archive_object


class ArchiveHandler(ArchiveInterface):
    """Handle specific archive, can unpack and return the sha256 hash"""

    def __init__(self, filename, config_obj):
        super().__init__(filename)

        self._config_obj = config_obj
        self._hash = None
        self._metadata = None

    def _check_file_exist(self, filename, has_res=False):
        """Check if filename already exist in in the game mod folder.
        """
        return os.path.exists(_get_mod_folder(
            config_obj=self._config_obj,
            with_file=filename,
            has_res=has_res))

    def copy_file_to_repository(self):
        if not self._config_obj['local_repository']:
            log.warning("Unable to copy archive: no local repository configured.")
            return False

        dst_folder = os.path.join(
            self._config_obj['local_repository'],
            self.hash[:2]
        )

        new_filename = os.path.join(
            dst_folder,
            os.path.basename(self.filename)
        )

        if os.path.exists(new_filename):
            log.error("Unable to copy archive, a file with a similar name already exists.")
            return False

        try:
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            shutil.copy(self.filename, dst_folder)
        except IOError as e:
            log.error("Error copying archive: %s", e)
            return False
        else:
            self.filename = new_filename
            return True

    def unpack(self):
        if not self._config_obj['game_folder']:
            log.warning("Unable to unpack archive: game location is unknown.")
            return False

        unpacked_files = []
        for member in self.namelist():
            if member == '_metadata.yaml':
                continue

            if member.split('/')[0] == 'res':
                has_res = True

            if self._check_file_exist(member, has_res):
                log.warning(
                    "File '%s' already exists in mod directory.",
                    member
                )
                continue
            self.extract(member, _get_mod_folder(self._config_obj, has_res=has_res))
            unpacked_files.append(member)

    @property
    def metadata(self):
        if self._metadata:
            return self._metadata

        mdata_filename = '_metadata.yaml'
        if self.filetype == 'zip':
            if mdata_filename in self.archive_object.namelist():
                x = TextIOWrapper(self.archive_object.open(mdata_filename))
                self._metadata = yaml.load(x.read())
        elif self.filetype == '7z':
            if mdata_filename in self.archive_object.getnames():
                x = self.archive_object.getmember(mdata_filename)
                self._metadata = yaml.load(x.read().decode('utf-8'))

        if not self._metadata:
            self._metadata = {
                'name': '',
                'author': '',
                'description': '',
                'category': []
            }

        self._metadata['filename'] = os.path.basename(self.filename)

        return self._metadata

    @property
    def hash(self):
        if not self._hash:
            with open(self.filename, 'rb') as fp:
                m = sha256(fp.read())
            self._hash = m.hexdigest()
        return self._hash

    @hash.setter
    def hash(self, value):
        pass

    @property
    def name(self):
        return self._metadata['name'] if self._metadata['name'] else self._metadata['filename']


class ArchiveManager:
    """The ArchiveManager keep tracks, install and uninstall the differents
    archives of the repository.
    """

    def __init__(self, config_obj):
        self._config_obj = config_obj
        self._files_index = Config("files_index.json", compress=True)
        self._file_list = dict()
        self.load()

    def add_file(self, filename):
        """Adds a file to the repository.
        """
        my_file = ArchiveHandler(filename, self._config_obj)
        if my_file.hash in self._files_index:
            log.warning("Duplicate archive, ignored: %s", my_file.filename)
            return False
        my_file.copy_file_to_repository()
        file_hash = my_file.hash
        self._files_index[file_hash] = {
            'filename': my_file.filename,
            'installed': False,
            'installed_files': []
        }
        self._file_list[file_hash] = my_file
        # XXX: the auto-save doesn't trigger
        self._files_index.save()
        return file_hash

    def remove_file(self, file_hash):
        if file_hash not in self._files_index:
            log.error("Unable to remove an unexisting file: %s", file_hash)

        filename = self._file_list[file_hash].filename
        self._file_list[file_hash].close()
        del(self._file_list[file_hash])
        del(self._files_index[file_hash])
        try:
            os.remove(filename)
        except OSError as e:
            log.error("Unable to remove file from drive: %s", e)

    def install_mod(self, file_hash):
        """Install the content of an archive into the game mod folder.
        """
        if file_hash not in self._files_index:
            log.error("Installation failure, hash not found: %s", file_hash)
            return
        files = self._file_list[file_hash].unpack()
        self._files_index[file_hash]['installed'] = True
        self._files_index[file_hash]['installed_files'] = files
        self._files_index.save()

    def uninstall_mod(self, file_hash):
        dir_list = []
        for item in self._files_index[file_hash]['installed_files']:
            has_res = (item.split('/')[0] == 'res')
            filename = _get_mod_folder(self._config_obj, with_file=item, has_res=has_res)
            log.debug("Trying to delete file: %s", filename)
            if os.path.isdir(filename):
                dir_list.append(filename)
            else:
                try:
                    os.remove(filename)
                except OSError as e:
                    log.error("Unable to remove file %s: %s", item, e)

        dir_list.sort(reverse=True)
        for item in dir_list:
            try:
                os.rmdir(item)
            except OSError as e:
                log.debug("Directory not removed because: %s", e)
                log.warning("Ignoring non-empty directory: %s", item)

        self._files_index[file_hash].update({
            'installed': False,
            'installed_files': []
        })
        self._files_index.delayed_save()

    def load(self):
        """Builds the internal list of files
        """
        if len(self._files_index) == 0 or len(self._file_list) > 0:
            return False

        for file_hash, data in self._files_index.items():
            self._file_list[file_hash] = ArchiveHandler(data['filename'], self._config_obj)

    def get_files(self):
        for file_hash, file in self._file_list.items():
            yield file

    def get_file(self, file_hash):
        return self._file_list[file_hash]

    def get_state_by_hash(self, file_hash):
        return self._files_index[file_hash]['installed']

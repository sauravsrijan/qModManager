# -*- coding: utf-8 -*-
# Licensed under the EUPL v1.2
# © 2020 bicobus <bicobus@keemail.me>
"""Contains a bunch of helper function to display Qt's dialogs."""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, qApp, QDialog

from .ui_qprogress import Ui_Dialog


def qError(message, **kwargs):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("An error occurred")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    _do_message(msg, **kwargs)


def qWarning(message, **kwargs):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("An warning occurred")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    _do_message(msg, **kwargs)


def qWarningYesNo(message, **kwargs):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Warning")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    r = _do_message(msg, **kwargs)
    return bool(r == QMessageBox.Ok)


def qInformation(message, **kwargs):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("An error occurred")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    _do_message(msg, **kwargs)


def _do_message(mobject, informative=None, detailed=None):
    if informative:
        mobject.setInformativeText(informative)
    if detailed:
        mobject.setDetailedText(detailed)

    return mobject.exec_()


class SplashProgress(QDialog, Ui_Dialog):
    def __init__(self, parent, title, message):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(title)
        self.message.setText(message)
        self.category.setText("Booting")
        self.informative.setText("Booting")

    def progress(self, text: str, category: str = None):
        if category:
            self.category.setText(f"{category}: ")
        self.informative.setText(text)
        # processEvents needs to be called in order to touch QT event's loop.
        # Without it, the event loop will stall until all progress call have
        # been made.
        qApp.processEvents()
        # sleep(0.005)

#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import json
import _pkg
import sys

from glob import glob
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication,
                            QGraphicsDropShadowEffect, QLabel, QListWidgetItem, QMainWindow, 
                            QMenu, QStackedWidget, QSystemTrayIcon, QWidget)
from plugin_settings import PluginSettings
from _settings import MainWindowSettings
from _methods import  Controls
from _window import Ui_Form as app_ui
from _default_mode import DefaultModeItems
from _user_commands import UserCommandCreator

base_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "")

__keywords__ = ["small", "install", "download", 
                "about", "exit", "quit", "resize",
                "killme", "close-kangaroo", "quit-kangaroo",
                "update", "refresh", "clone", "add-cmd", 
                "add-shortcut", "test"]

class MainWindow(QWidget, app_ui):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        QWidget.__init__(self)
        self.setupUi(self)
        
        ## create system tray
        self.createActions()
        self.createTrayIcon()
        self.trayIcon.show()

        ## window setting
        self.win_setting = MainWindowSettings(self)
        self.win_setting.init_setup()
        self.win_setting.small_mode()

        ## variables
        self.exts = {}         # {key: {count, object, path, icon}}
        self.user_cmd = json.load(open(base_dir + "Json/user_commands.json", "r"))
        self.count = 0
        __keywords__.extend(list(self.user_cmd.keys()))
        
        self.init_ui()

        ## signal/sloat
        self.input.textChanged.connect(self.split_check)
        self.input.returnPressed.connect(self.built_in_func)

        self.set_sys_icon()
    
    def enforce_line_edit_suffix(self):
        """This method parses the QLineEdit text and makes sure the desired suffix is there."""
        text = self.input.text()
        for i in list(self.exts.keys()):
            if text in i:
                self.input.blockSignals(True)
                self.input.setText(text + i[len(text):])
                self.input.setCursorPosition(int(len(text)))
                self.input.cursorForward(True, int(len(text)) + int(len(i)))
                self.input.blockSignals(False)

    def init_ui(self):
        self.get_all_plugins()
        self.set_stacked_widget()

    ####################### get all plugins and set them to self.exts var #######################
    def get_all_plugins(self):
        Plugins = glob(base_dir + f"exts/__{self.get_platform}__/*.ext/")
        Plugins.extend(glob(base_dir + f"exts/__all__/*.ext/"))

        for rd in Plugins:
            dic = self.get_json(rd + "package.json")
            if dic:
                try:
                    obj = _pkg.Import(rd + dic.get("script")).Plugin
                    kw = str(dic.get("key")).strip()

                    self.exts.update({kw: {
                        "count": self.count, 
                        "object": obj, 
                        "path": rd, 
                        "icon": rd + dic.get("icon"),
                        "json": dic}})

                    self.count += 1

                except (AttributeError, 
                        FileNotFoundError, 
                        ModuleNotFoundError, 
                        json.decoder.JSONDecodeError) as err:
                        
                    print(f"Error-add: {rd}: ", err)
                    continue

    @property
    def get_platform(self):
        platform = ""
        if sys.platform.startswith("linux"):
            platform = "linux"
        elif sys.platform.startswith("win"):
            platform = "windows"
        elif sys.platform.startswith("drawen"):
            platform = "macos"
        else:
            platform = "all"
        return platform

    ####################### built in functions and commands #######################
    def built_in_func(self):
        text = self.input.text().strip().lower()
        
        if text in ("exit", "quit"):
            self.hide()
            self.input.clear()
            self.win_setting.small_mode()

        elif text in ("small", "resize"):
            self.win_setting.small_mode()

        elif text in ("killme", "close-kangaroo", "quit-kangaroo"):
            QApplication.instance().quit()
            
        elif text in ("update", "refresh"): 
            self.get_all_plugins()
            self.user_cmd = json.load(open(base_dir + "Json/user_commands.json", "r"))
            self.input.clear()
            self.win_setting.small_mode()

        elif text in ("download", "install", "clone"):
            PluginSettings(win=self).install_url()

        elif text in ("add-cmd", "add-shortcut"):
            self.hide()
            UserCommandCreator(self, keywords=__keywords__).show()

        elif text in list(self.user_cmd.keys()):
            _pkg.run_app(self.user_cmd.get(text.strip()).get("cmd"))

    ####################### get line edit text and process it #######################
    def split_check(self, text: str):
        key, val = self.get_kv(text)
        key = key.rstrip(":")
        exts_keys = list(self.exts.keys())

        try:
            key = self.input.text().strip().split(maxsplit=0)[0].strip().lower() if not key else key
        except IndexError:
            pass

        if key in ("kng", "kangaroo"):
            self.btn_ext.setIcon(QIcon(base_dir + "icons/main/plugin_settings.png"))
            self.stackedWidget.insertWidget(0, PluginSettings(win=self))
            self.stackedWidget.setCurrentIndex(0)
            self.win_setting.extend_mode()
            
        elif key == "test":
            if os.path.exists(val) and not os.path.isdir(val) and val.endswith(".py"):
                self.stackedWidget.insertWidget(
                    0, _pkg.Import(val).Plugin(_pkg, Controls(self)))
                self.stackedWidget.setCurrentIndex(0)
            else:
                self.set_sys_icon()
                self.win_setting.small_mode()

        elif key and key in exts_keys:
            self.btn_ext.show()
            self.run_plugin(key)
            self.win_setting.extend_mode()

        elif not key in exts_keys and text.strip() and not key in __keywords__:
            for pt in exts_keys:
                if (key in self.exts.get(pt).get("json").get("name").lower()):

                    plug_items = DefaultModeItems(self)
                    self.stackedWidget.insertWidget(0, plug_items)
                    self.stackedWidget.setCurrentIndex(0)
                    self.win_setting.extend_mode()
        else:
            self.set_sys_icon()
            self.win_setting.small_mode()

    def set_sys_icon(self):
        def_icon = base_dir + "icons/systems/" + self.get_platform + ".png"
        self.btn_ext.setIcon(QIcon(def_icon))

    ####################### Create new Stacked Widget #######################
    def set_stacked_widget(self):
        self.stackedWidget = QStackedWidget(self)
        self.main_grid_layout.addWidget(self.stackedWidget)

    ####################### Run/Set Plugin Code #######################
    def run_plugin(self, key: str):
        plugin = self.exts.get(key)
        icon = base_dir + "icons/unknow_plugin.png"
        def_icon = plugin.get("icon")

        self.btn_ext.setIcon(QIcon(def_icon if os.path.exists(def_icon) else icon))
        self.stackedWidget.insertWidget(0, plugin.get("object")(_pkg, Controls(self)))
        self.stackedWidget.setCurrentIndex(0)
        
    ####################### Static Methods #######################
    @staticmethod
    def get_js_value(_file: str, key: str, value: str=""):
        return json.load(open(_file, "r")).get(key.lower().strip(), value)

    @staticmethod
    def get_json(_file: str):
        return json.load(open(_file, "r"))

    @staticmethod
    def get_kv(text: str):
        try:
            k, v = text.split(maxsplit=1)
            return (k.strip().lower(), v.strip())
        except (IndexError, ValueError):
            return ("", "")

    ####################### Create System Tray #######################
    def createActions(self):
        self.hideAction = QAction("H&ide/S&how", self, shortcut="Alt+Space", triggered=self.check_win)
        self.quitAction = QAction(_pkg.get_sys_icon("application-exit"), "&Quit", self, triggered=QApplication.instance().quit)

    def createTrayIcon(self):
        self.trayIconMenu = QMenu(self)

        self.trayIconMenu.addAction(self.hideAction)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(_pkg.icon_path("logo.png", True))
        self.trayIcon.setContextMenu(self.trayIconMenu)

        self.trayIcon.activated.connect(self.check_win)

    def showMessage(self, title: str, body: str, icon: int=1, limit: int=5):
        tray = QSystemTrayIcon(_pkg.icon_path("logo.png", True))
        icon_ = tray.MessageIcon(icon)

        tray.showMessage(title, body, icon_, limit * 2000)
        tray.show()

    def check_win(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def set_item(self, text: str, icon: str=""):
        att = QListWidgetItem()
        att.setText(text)
        if icon: att.setIcon(QIcon(icon))
        return att

    def set_shadow(self, blur: int = 5, point: tuple = (5, 5), color: str = "black"):
        # creating a QGraphicsDropShadowEffect object
        shadow = QGraphicsDropShadowEffect()

        shadow.setXOffset(20.0)
        # shadow.setYOffset(20.0)

        # setting blur radius (optional step)
        shadow.setBlurRadius(blur)

        ## set shadow possation
        shadow.setOffset(QPointF(point[0], point[1]))

        ## set a property option
        shadow.setProperty("color", color)

        return shadow

    def dragEnterEvent(self, e):
        data = e.mimeData()
        if data.hasUrls():
            # We are passed urls as a list, but only accept one.
            url = data.urls()[0].toLocalFile()
            print("from drag: ", url)
            # if os.path.splitext(url)[1].lower() == '.zip':
            #     e.accept()

    def dropEvent(self, e):
        data = e.mimeData()
        path = data.urls()[0].toLocalFile()
        print("from drop: ", path)

def main():
    app = QApplication(sys.argv)
    win =  MainWindow()

    try:
        if ('--hide') in sys.argv[1:]:
            win.hide()
        else:
            win.show()
    except IndexError:
        win.show()

    app.setQuitOnLastWindowClosed(False)
    exit(app.exec_())

if __name__ == "__main__":
    main()


"""mac theme
dark: #3d3a3c / #59595b
    - selected: #353534 / #4f4f51

light: #d6d5d8 / #f4f3f6
    - selected: #c5c6c7 / #e7e6e9


rounded selected item
custom selected item color/background

@Alfred
@Ulauncher
@Albert
"""
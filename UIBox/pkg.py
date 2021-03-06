#!/usr/bin/python3

import os
import sys
import json
import subprocess

from glob import glob
from threading import Thread
from PyQt5.QtCore import QFileInfo, QPointF, QSize, QUrl, Qt, QRect
from PyQt5.QtGui import QColor, QDesktopServices, QFont, QImage, QIcon, QBrush, QPixmap, QPainter, QWindow
from PyQt5.QtWidgets import QFileIconProvider, QGraphicsDropShadowEffect, QListWidgetItem

base_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "")

user_home_dirs = [
        "~/Downloads/",
        "~/Documents/",
        "~/Desktop/",
        "~/Videos/",
        "~/Pictures/",
        "~/Music/"]

## return os.path
def icon_path(_file: str, icon: bool=False):
    if icon: 
        return QIcon(base_dir + "icons/" + _file)
    else:
        return base_dir + "icons/" + _file

def ui_path(_file: str):
    return base_dir + "ui/" + _file

def style_path(_file: str):
    return base_dir + "styles/" + _file

# function to alter image
def mask_image(imgdata, img_size: tuple=(100, 100), size: int=64):

    imgtype = os.path.splitext(os.path.split(imgdata)[1])[1]

    # Load image
    image = QImage.fromData(open(imgdata, "rb").read(), imgtype)

    # convert image to 32-bit ARGB (adds an alpha
    # channel ie transparency factor):
    image.convertToFormat(QImage.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) // 2,
        (image.height() - imgsize) // 2,
        imgsize,
        imgsize)

    image = image.copy(rect)

    # Create the output image with the same dimensions
    # and an alpha channel and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
    out_img.fill(Qt.transparent)

    # Create a texture brush and paint a circle
    # with the original image onto the output image:
    brush = QBrush(image)

    # Paint the output image
    painter = QPainter(out_img)
    painter.setBrush(brush)

    # Don't draw an outline
    painter.setPen(Qt.NoPen)

    # drawing circle
    painter.drawEllipse(0, 0, imgsize, imgsize)

    # closing painter event
    painter.end()

    # Convert the image to a pixmap and rescale it.
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(img_size[0], img_size[1], Qt.KeepAspectRatio,
                   Qt.SmoothTransformation)

    # return back the pixmap data
    return pm

def add_item(obj, icon: QIcon, text: str="", tooltip: str="", selectable: bool=False, 
            select: bool=False, checkable: bool=False, check: bool=False, hide: bool=False, 
            font_size: int=10, icon_size=(25, 25), enabled: bool=True, dis_bg: str="#efeeef", 
            alignment=None, icon_theme: bool=False, icon_provider: bool=False):

    font = QFont()
    font.setPixelSize(font_size)

    att = QListWidgetItem()
    att.setText(text)
    att.setHidden(hide)
    att.setFont(font)

    if icon and isinstance(icon, str):
        if icon_provider:
            icon = icon_types(icon)
        elif icon_theme:
            icon = QIcon.fromTheme(icon)
        else:
            icon = QIcon(icon)
        att.setIcon(icon)
    else:
        att.setIcon(icon)

    if tooltip: 
        att.setToolTip(tooltip)
    if checkable:
        att.setCheckState(check)
    if selectable:
        att.setSelected(select)

    obj.setIconSize(QSize(icon_size[0], icon_size[1]))

    if not enabled:
        att.setFlags(Qt.NoItemFlags)
        att.setBackground(QColor(dis_bg))
    
    if not alignment == None: 
        att.setTextAlignment(alignment)

    return att

def get_line(obj):
    text = str(obj.text()).strip()
    try:
        ext = text.split(":")
        suffix = ""

        for i in ext[1:]:
            suffix += " " + i

        if len(ext) >= 2:
            return ext[0], suffix.strip()
    
    except IndexError:
        return None

def icon_types(_file: str, is_file: list=[False, ""]):
    file_type = os.path.splitext(os.path.split(_file)[1])[1].strip(".")
    ## set image/video icon
    if file_type in json.load(open(base_dir + "api/icons.json")).get("Image"):
        if not is_file[0]:
            return QIcon(_file)
        else:
            return _file

    ## Default System Icons
    else:
        fileInfo = QFileInfo(_file)
        iconProvider = QFileIconProvider()
        icon = iconProvider.icon(fileInfo)

        if not is_file[0]:
            return icon
        else:
            iconProvider.icon(fileInfo).pixmap(200, 200).save(is_file[1], "png")
            return is_file[1]
            
def api_icons(_type: str, default: list=[]):
    try:
        return json.load(open(base_dir + "api/icons.json")).get(_type, default)
    except KeyError:
        return ""

def Import(_file: str):
    try:
        import importlib
        spec = importlib.util.spec_from_file_location(
            os.path.split(_file)[0].split(".")[0], _file)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
    except Exception:
       import imp
       foo = imp.load_package(os.path.split(_file)[0].split(".")[0], _file)

    return foo

def set_image(_file: str, icon: bool=False, size: int=150):
    if icon:
        return _file.pixmap(QSize(size, size))
    else:
        return QIcon(_file).pixmap(QSize(size, size))

def add_item_widget(item, item_widget, text: str="", 
                    subtitle: str="", hotkey: str="", 
                    no_subtitle: bool=False, item_size=(250, 40)):

    frame = item_widget
    frame.title.setText(text)
    frame.hotkey.setText(hotkey)
    
    if no_subtitle:
        frame.subtitle.hide()
        frame.subtitle.setStyleSheet("")
    else:
        frame.subtitle.show()
        frame.subtitle.setText(subtitle)

    item.setSizeHint(QSize(item_size[0], item_size[1]))

    return (item, frame)

def get_sys_icon(_name: str):
    _icon = QIcon.fromTheme(_name)
    return _icon
        
def _ext_json(_path: str, key: str, value: str=""):
    return json.load(open(str(_path + "package.json"))).get(key.lower(), value)

def set_item_widget(obj, item):
    obj.addItem(item[0])
    obj.setItemWidget(item[0], item[1])

def set_item(obj, item):
    obj.addItem(item)

def run_app(cmd: object):
    Thread(target=lambda: subprocess.call(cmd, shell=True, stderr=None, stdin=None, stdout=None), daemon=True).start()

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

try:
    import vlc
    class video_player:
        def __init__(self, frame, file: str="", on_changed: object=None):
            self.frame = frame
            self.file = file
            self.on_changed = on_changed

            self.__instance = vlc.Instance()
            self.__mediaplayer = self.__instance.media_player_new()

            if self.on_changed:
                self.__vlc_event_manager = self.__mediaplayer.event_manager()
                self.__vlc_event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self.on_changed)

            if sys.platform.startswith("linux"):
                self.__mediaplayer.set_xwindow(self.frame.winId())
            
            elif sys.platform == "win32":
                self.__mediaplayer.set_hwnd(self.frame.winId())
            
            elif sys.platform == "darwin":
                self.__mediaplayer.set_nsobject(self.frame.winId())

            if self.file: 
                media = self.__instance.media_new(self.file)
                self.__mediaplayer.set_media(media)

        @property
        def media(self):
            return self.__mediaplayer
        
        @property
        def instance(self):
            return self.__instance
        
        def set_media(self, file):
            media = self.__instance.media_new(file)
            self.__mediaplayer.set_media(media)

except (ImportError, ImportWarning, ModuleNotFoundError):
    pass

def set_box_shadow(blur: int = 5, point: tuple = (5, 5), color: str = "black"):
    # creating a QGraphicsDropShadowEffect object
    shadow = QGraphicsDropShadowEffect()

    # setting blur radius (optional step)
    shadow.setBlurRadius(blur)

    ## set shadow possation
    shadow.setOffset(QPointF(point[0], point[1]))

    ## set a property option
    shadow.setProperty("color", color)

    return shadow

def find_in_all(query: str, path: str="~/"):
    result = {}
    paths = glob(os.path.expanduser(path) + "*")
    
    if query.strip():
        for dn in paths:
            if os.path.isdir(dn):
                paths.extend(glob(dn + "/*"))
                result.update({os.path.split(dn)[1]: dn})
            elif query.strip() in dn.strip():
                result.update({os.path.split(dn)[1]: dn})

    return result

def find_in(query: str, path: object="~/"):
    result = {}

    if query.strip() and isinstance(path, str):
        for i in glob(os.path.expanduser(os.path.expandvars(path)) + "*"):
            if query in i:
                result.update({os.path.splitext(os.path.split(i)[1])[0]: i})
    
    elif query.strip() and isinstance(path, list) or isinstance(path, tuple):
        for i in path:
            for j in glob(os.path.expanduser(os.path.expandvars(i)) + "*"):
                if query in j:
                    result.update({os.path.splitext(os.path.split(j)[1])[0]: j})
    return result


def get_split_file(_file):
    return (
        os.path.dirname(_file),
        os.path.splitext(os.path.basename(_file))[0],
        os.path.splitext(os.path.basename(_file))[1]
    )

def get_platform():
    if sys.platform.startswith(("linux")):
        platform = "linux"
    elif sys.platform.startswith("win"):
        platform = "windows"
    elif sys.platform.startswith("darw"):
        platform = "macos"
    else:
        platform = "all"

    return platform

def get_system_name():
    if sys.platform.startswith(("linux")):
        platform = "Linux"
    elif sys.platform.startswith("win"):
        platform = "Windows"
    elif sys.platform.startswith("darw"):
        platform = "MacOS"
    else:
        platform = "UnKnow"

    return platform

def open_url(_file: str):
    QDesktopServices.openUrl(QUrl.fromUserInput(_file))

def cmd_open_url(_file: str):
    run_app("xdg-open '%s'" % _file)

def run_thread(func: object, *args, **kwargs):
    Thread(target=func, daemon=True, args=args, kwargs=kwargs).start()

def get_cmd_output(*args):
    t = ""
    for i in args:
        t += i + " "
    return os.popen(t, "r")

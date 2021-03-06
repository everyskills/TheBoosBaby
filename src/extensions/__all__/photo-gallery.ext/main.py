#!/usr/bin/python3

import os
from glob import glob
from UIBox import pkg
from PyQt5.QtCore import QUrl

base_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "")
keys = {
    "images": [],
    "thumbnail_slider_css": "file://" + base_dir + "static/thumbnail-slider.css",
    "ninja_slider_css": "file://" + base_dir + "static/ninja-slider.css",
    "thumbnail_slider_js": "file://" + base_dir + "static/thumbnail-slider.js",
    "ninja_slider_js": "file://" + base_dir + "static/ninja-slider.js"
}

os.chdir(os.path.expanduser("~/"))

def Results(parent):
    items = []
    keys["images"].clear()

    for n, i in enumerate(glob(os.path.expandvars(os.path.expanduser(parent.text)) + "*")):
        is_img = i.lower().endswith(tuple(pkg.api_icons("Image")))
        if os.path.isdir(i) or is_img:
            items.append({
                "title": os.path.split(i)[1], 
                "key": i,
                "icon": i if is_img else ''
            })

        if i.lower().endswith(tuple(pkg.api_icons("Image"))):
            _image = QUrl.fromUserInput(i).toString()
            keys["images"].append((n, _image))

    return {
        "html": (parent.include_file("index.html")) if keys.get("images", []) else "<h3> %s </h3>" % parent.text,
        "keywords": keys,
        "jinja": True,
        "items": items
    }

def ItemClicked(parent, item):
    parent.set_text(
        (item.key if parent.text.startswith(("~", "/")) else "~/" + item.key) + ("/" if not item.key.endswith("/") and os.path.isdir(item.key) else "")
    )

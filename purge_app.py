# -*- coding: utf-8 -*-
"""
purge_app.py
© Rémi Héneault (@codesamuraii)
https://github.com/codesamuraii
"""
import os
import plistlib
from pathlib import Path


def read_plist(app_path):
    """This function returns a tuple which contains (bundle_identifier , bundle_name , bundle_signature) of an app"""

    try:
        plist_path = Path(app_path, "Contents/Info.plist").resolve(strict=True)
    except FileNotFoundError:
        # The name of the app
        return [plist_path.parents[1].stem]

    plist_content = plistlib.loads(plist_path.read_bytes())

    identifiers = ["CFBundleIdentifier", "CFBundleName", "CFBundleSignature"]
    relevant_infos = {plist_content.get(id) for id in identifiers}
    relevant_infos.discard(None)
    relevant_infos.discard('????')

    return relevant_infos


def scan(path_to_app):

    hints = read_plist(path_to_app)
    print("[*] Found following hints : {}".format(hints))

    search_directories = {
        Path.home() / "Library",
        "/Library",
        "/System/Library",
        "/var"
    }

    def check_hints(str_path):
        return any(h in str_path for h in hints)

    for directory in search_directories:
        print("[i] Searching in {}...".format(directory))

        subdirs = Path(directory).glob("**")

        for dir in subdirs:
            relative_path = str(dir.relative_to(directory))

            if check_hints(relative_path):
                print("  - {}".format(relative_path))
                # relative_path.rmdir()

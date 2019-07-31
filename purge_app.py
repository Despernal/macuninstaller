# -*- coding: utf-8 -*-
"""
purge_app.py
© Rémi Héneault (@codesamuraii)
https://github.com/codesamuraii
"""
import os
import plistlib
from pathlib import Path


SEARCH_DIRECTORIES = {
    Path.home() / "Library",
    "/Library",
    "/System/Library",
    "/var"
}


def read_plist(app_path):
    """This function returns a set containing the informations of an app."""

    try:
        plist_path = Path(app_path, "Contents/Info.plist").resolve(strict=True)
    except FileNotFoundError:
        # The name of the app
        return {plist_path.parents[1].stem}

    plist_content = plistlib.loads(plist_path.read_bytes())

    # Relevant identifiers to read
    identifiers = ["CFBundleIdentifier", "CFBundleName", "CFBundleSignature"]
    relevant_infos = {plist_content.get(id) for id in identifiers}

    # Removing not found values
    relevant_infos.discard(None)
    relevant_infos.discard('????')

    return relevant_infos


def path_walk(start_path, hints):
    """Equivalent to `os.walk` using pathlib."""

    def check_hints(str_path):
        return any(h in str_path for h in hints)

    names = start_path.iterdir()

    dirs = (node for node in names if node.is_dir() is True)
    nondirs = (node for node in names if node.is_dir() is False)

    for name in dirs:
        if check_hints(str(name)):
            yield name

        elif not name.is_symlink():
            for x in path_walk(name, hints):
                yield x

    for name in nondirs:
        if check_hints(str(name)):
            yield name


def scan(path_to_app):

    hints = read_plist(path_to_app)

    results = set()

    for directory in SEARCH_DIRECTORIES:
        print("[i] Searching in {}...".format(directory))

        # REVIEW: Not efficient
        subdirs = Path(directory).iterdir()

        for dir in subdirs:

            relative_path = str(dir.relative_to(directory))

            if check_hints(relative_path):
                results.add(dir)
                # relative_path.rmdir()

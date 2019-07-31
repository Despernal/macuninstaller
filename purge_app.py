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
    Path("/Library"),
    Path("/System/Library"),
    Path("/var")
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


def check_hints(path_name, hints):
    return any(h in str(path_name) for h in hints)


def path_walk(start_path, hints):
    """Equivalent to `os.walk` using pathlib."""

    try:
        names = list(start_path.iterdir())
    except PermissionError:
        return

    dirs = (node for node in names if node.is_dir())
    nondirs = (node for node in names if node.is_file())

    for name in dirs:

        if check_hints(name, hints):
            yield name

        elif not name.is_symlink():
            yield from path_walk(name, hints)

    for name in nondirs:
        if check_hints(name, hints):
            yield name


def scan(path_to_app):

    hints = read_plist(path_to_app)
    results = set()

    for directory in SEARCH_DIRECTORIES:
        print("[i] Searching in {}...".format(directory))

        for match in path_walk(directory, hints):
            results.add(match)

    return results

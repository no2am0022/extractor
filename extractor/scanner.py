import os
import pathlib
import typing


def scan_xml_files(base_dir: pathlib.Path) -> typing.Generator[pathlib.Path, None, None]:
    yield from _scan(base_dir)


def _scan(base_dir: pathlib.Path):
    for entry in os.scandir(base_dir):
        if entry.is_dir():
            child_dir = base_dir.joinpath(entry.name)
            yield from _scan(child_dir)

        elif entry.name.endswith(".xml"):
            yield pathlib.Path(entry.path)


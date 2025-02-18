#!/usr/bin/env python3
# Copyright Cleber Akira Nakandakare
# SPDX-License-Identifier: MIT

# Requires infi.systray. Install it with `pip install infi.systray`
# Monitors a file and creates a systray icon for Timewarrior.

import shlex
from pathlib import Path
from threading import Event
from time import sleep

from infi.systray import SysTrayIcon

MONITORED_FILE = Path(
    r"C:\Users\cakira\.local\state\timewarrior\current_tags.txt")
ICON_FOLDER = Path("icons")
ICON_DEFAULT = ICON_FOLDER / "timewarrior.ico"
ICON_EMPTY = ICON_FOLDER / "timewarrior_empty.ico"


class TimewarriorSystray:

    def __init__(self):
        self.stop_event = Event()
        self.systray_icon = SysTrayIcon(str(ICON_DEFAULT),
                                        "uninitialized",
                                        on_quit=self._on_quit_callback)

    def _on_quit_callback(self, _systray):
        """Handles systray exit."""
        self.stop_event.set()

    def find_icon_for_tags(self, tags):
        """Finds an icon matching the first valid tag in the icons folder."""
        for tag in tags:
            icon_path = ICON_FOLDER / f"{tag}.ico"
            if icon_path.exists():
                return str(icon_path)
        return str(ICON_DEFAULT if tags else ICON_EMPTY)

    def monitor_file(self):
        """Monitors the file and updates the systray icon."""
        last_state = None

        with self.systray_icon:
            while not self.stop_event.is_set():
                try:
                    with MONITORED_FILE.open() as current_tags_file:
                        tags = shlex.split(current_tags_file.readline().strip(
                        ))  # Handle quoted tags
                except FileNotFoundError:
                    tags, icon = [], str(ICON_EMPTY)
                else:
                    icon = self.find_icon_for_tags(tags)

                new_state = (icon, " ".join(tags) if tags else "None")
                if new_state != last_state:  # Update only if changed
                    self.systray_icon.update(icon, new_state[1])
                    last_state = new_state

                sleep(5)


if __name__ == "__main__":
    app = TimewarriorSystray()
    app.monitor_file()

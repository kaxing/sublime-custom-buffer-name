from datetime import datetime
import platform
import re
import sublime
import sublime_plugin

default_prefix = "%Y-%m-%d %A %H:%M "
current_os = platform.system()
invalid_filename_chars = r'[<>:"/\\|?*]'
known_window_ids = set()
total_buffer_count = 0

def plugin_loaded():
    global total_buffer_count
    unique_buffer_ids = {view.buffer().id() for window in sublime.windows() for view in window.views()}
    total_buffer_count = len(unique_buffer_ids)

def sanitize_filename(filename):
    if current_os == "Windows":
        filename = re.sub(r':', '꞉', re.sub(invalid_filename_chars, '_', filename))
    return filename

def get_current_time_formatted():
    settings = sublime.load_settings("CustomBufferName.sublime-settings")
    custom_prefix = settings.get("custom_prefix")
    now = datetime.now()
    return now.strftime(custom_prefix)

class setCustomBufferNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        options = [
            "Input your own prefix: (example: yourPrefix1, yourPrefix2, yourPrefix3)",
            "Use package default prefix: (example: '2023-09-22 Friday 15:35 42')",
            "Use classic prefix: (example: untitled 1, untitled 2, untitled 3)"
        ]
        self.view.window().show_quick_panel(options, self.on_select)

    def on_select(self, index):
        if index == -1:
            return

        if index == 0:
            self.view.window().show_input_panel("Enter Your Custom Prefix:", "", self.on_done, None, None)
        elif index == 1:
            self.on_done(None)
        elif index == 2:
            self.on_done("untitled ")

    def on_done(self, user_input):
        settings = sublime.load_settings("CustomBufferName.sublime-settings")
        
        if user_input == "untitled ":
            settings.set("custom_prefix", user_input)
        elif user_input is None:
            settings.set("custom_prefix", default_prefix)
        else:
            settings.set("custom_prefix", user_input)
        
        sublime.save_settings("CustomBufferName.sublime-settings")

class runCustomBufferNameCommand(sublime_plugin.EventListener):
    def on_new_async(self, view):
        global total_buffer_count
        global known_window_ids

        window = view.window()
        if window is None:
            return

        window_id = window.id()
        if window_id not in known_window_ids:
            known_window_ids.add(window_id)

        total_buffer_count += 1

        formatted_buffer_name = get_current_time_formatted()
        new_buffer_name = f"{formatted_buffer_name}{total_buffer_count}"
        sanitized_buffer_name = sanitize_filename(new_buffer_name)
        view.set_name(sanitized_buffer_name)

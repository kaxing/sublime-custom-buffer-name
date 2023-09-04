from datetime import datetime
import platform
import re
import sublime
import sublime_plugin

current_os = platform.system()
default_custom_name = "%Y-%M-%d %A %H:%M "
invalid_filename_chars = r'[<>:"/\\|?*]'
known_window_ids = set()
total_buffer_count = 0

def plugin_loaded():
    global total_buffer_count
    unique_buffer_ids = {view.buffer().id() for window in sublime.windows() for view in window.views()}
    total_buffer_count = len(unique_buffer_ids)
    
    settings = sublime.load_settings("CustomBufferName.sublime-settings")
    if not settings.get("custom_prefix"):
        settings.set("custom_prefix", default_custom_name)
        sublime.save_settings("CustomBufferName.sublime-settings")
    
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
        settings = sublime.load_settings("CustomBufferName.sublime-settings")
        current_custom_prefix = settings.get("custom_prefix") or default_custom_name
        options = ["Input custom name", "Use suggested name", "Simple untitle with number"]
        self.view.window().show_quick_panel(options, self.on_select)

    def on_select(self, index):
        if index == -1:
            return

        settings = sublime.load_settings("CustomBufferName.sublime-settings")
        current_custom_prefix = settings.get("custom_prefix")
        if index == 0:
            self.view.window().show_input_panel("Enter Custom Name:", "", self.on_done, None, None)
        elif index == 1:
            self.on_done(default_custom_name)
        elif index == 2:
            self.on_done("untitled ")

    def on_done(self, user_input):
        settings = sublime.load_settings("CustomBufferName.sublime-settings")
        settings.set("custom_prefix", user_input or default_custom_name)
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

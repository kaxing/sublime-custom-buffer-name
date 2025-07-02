from datetime import datetime
import platform
import re
import sublime
import sublime_plugin

# Constants
DEFAULT_PREFIX = "%Y-%m-%d %A %H:%M "
INVALID_FILENAME_CHARS = r'[<>:"/\\|?*]'
CLASSIC_PREFIX = "untitled "

# Options for the quick panel
PREFIX_OPTIONS = [
    "Input your own prefix: (example: yourPrefix1, yourPrefix2, yourPrefix3)",
    "Use package default prefix: (example: '2023-09-22 Friday 15:35 42')",
    "Use classic prefix: (example: untitled 1, untitled 2, untitled 3)"
]

# Global state
class BufferState:
    def __init__(self):
        self.known_window_ids = set()
        self.total_buffer_count = 0
        self.current_os = platform.system()
    
    def increment_buffer_count(self):
        self.total_buffer_count += 1
        return self.total_buffer_count
    
    def add_window_id(self, window_id):
        self.known_window_ids.add(window_id)
    
    def initialize_buffer_count(self):
        unique_buffer_ids = {
            view.buffer().id() 
            for window in sublime.windows() 
            for view in window.views()
        }
        self.total_buffer_count = len(unique_buffer_ids)

buffer_state = BufferState()

def plugin_loaded():
    buffer_state.initialize_buffer_count()

def sanitize_filename(filename):
    if buffer_state.current_os == "Windows":
        filename = re.sub(r':', '꞉', re.sub(INVALID_FILENAME_CHARS, '_', filename))
    return filename

def get_current_time_formatted():
    settings = sublime.load_settings("CustomBufferName.sublime-settings")
    custom_prefix = settings.get("custom_prefix", DEFAULT_PREFIX)
    now = datetime.now()
    return now.strftime(custom_prefix)

class SetCustomBufferNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_quick_panel(PREFIX_OPTIONS, self.on_select)

    def on_select(self, index):
        if index == -1:
            return

        if index == 0:
            self._prompt_custom_prefix()
        elif index == 1:
            self._set_default_prefix()
        elif index == 2:
            self._set_classic_prefix()

    def _prompt_custom_prefix(self):
        self.view.window().show_input_panel(
            "Enter Your Custom Prefix:", 
            "", 
            self._save_custom_prefix, 
            None, 
            None
        )

    def _set_default_prefix(self):
        self._save_prefix(DEFAULT_PREFIX)

    def _set_classic_prefix(self):
        self._save_prefix(CLASSIC_PREFIX)

    def _save_custom_prefix(self, user_input):
        self._save_prefix(user_input)

    def _save_prefix(self, prefix):
        settings = sublime.load_settings("CustomBufferName.sublime-settings")
        settings.set("custom_prefix", prefix)
        sublime.save_settings("CustomBufferName.sublime-settings")

class RunCustomBufferNameCommand(sublime_plugin.EventListener):
    def on_new_async(self, view):
        window = view.window()
        if window is None:
            return

        window_id = window.id()
        buffer_state.add_window_id(window_id)

        buffer_count = buffer_state.increment_buffer_count()
        formatted_buffer_name = get_current_time_formatted()
        new_buffer_name = f"{formatted_buffer_name}{buffer_count}"
        sanitized_buffer_name = sanitize_filename(new_buffer_name)
        view.set_name(sanitized_buffer_name)

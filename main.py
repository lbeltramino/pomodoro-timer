import rumps
import yaml
import os
from Foundation import *
from AppKit import *
from windows import ProgressWindowController, SettingsWindowController, StatisticsWindowController

DEFAULT_SETTINGS = {
    "intervals": {
        "work_duration": 25,
        "short_break_duration": 5,
        "long_break_duration": 15,
        "long_break_after": 4,
        "target_per_day": 8
    },
    "general": {
        "launch_at_startup": False,
        "shortcut_start_pause": "cmd+shift+s",
        "shortcut_skip": "cmd+shift+n"
    }
}

class PomodoroTimer(rumps.App):
    def __init__(self):
        super(PomodoroTimer, self).__init__("🍅")
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize timer state
        self.is_running = False
        self.is_break = False
        self.timer = None
        self.work_time = self.settings["intervals"]["work_duration"] * 60
        self.short_break_time = self.settings["intervals"]["short_break_duration"] * 60
        self.long_break_time = self.settings["intervals"]["long_break_duration"] * 60
        self.remaining_time = self.work_time
        
        # Initialize session tracking
        self.session_count = 0
        self.sessions_before_long_break = self.settings["intervals"]["long_break_after"]
        
        # Add statistics tracking
        self.today_sessions = 0
        self.today_work_time = 0
        
        # Menu items
        self.button_start = rumps.MenuItem("Start Work Timer", callback=self.start_work)
        self.button_stop = rumps.MenuItem("Stop Timer", callback=self.stop_timer)
        self.button_progress = rumps.MenuItem("Show Progress", callback=self.show_progress)
        self.button_stats = rumps.MenuItem("Statistics", callback=self.show_stats)
        self.button_settings = rumps.MenuItem("Settings", callback=self.show_settings)
        
        self.menu = [
            self.button_start,
            self.button_stop,
            None,
            self.button_progress,
            self.button_stats,
            None,
            self.button_settings
        ]

    def load_settings(self):
        try:
            with open('pomodoro_settings.yaml', 'r') as f:
                settings = yaml.safe_load(f)
                if not settings:
                    settings = DEFAULT_SETTINGS
        except FileNotFoundError:
            settings = DEFAULT_SETTINGS
            self.save_settings(settings)
        return settings

    def save_settings(self, settings):
        with open('pomodoro_settings.yaml', 'w') as f:
            yaml.dump(settings, f)

    def update_settings(self, new_settings):
        self.settings = new_settings
        self.save_settings(new_settings)
        
        # Update runtime values
        self.work_time = new_settings["intervals"]["work_duration"] * 60
        self.short_break_time = new_settings["intervals"]["short_break_duration"] * 60
        self.long_break_time = new_settings["intervals"]["long_break_duration"] * 60
        self.sessions_before_long_break = new_settings["intervals"]["long_break_after"]
        
        # Update remaining time if not running
        if not self.is_running:
            self.remaining_time = self.work_time if not self.is_break else (
                self.long_break_time if self.session_count % self.sessions_before_long_break == 0 
                else self.short_break_time
            )

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    @rumps.clicked("Start Work Timer")
    def start_work(self, _):
        if not self.is_running:
            self.is_running = True
            self.is_break = False
            if not self.timer:  # Only reset time if starting fresh
                self.remaining_time = self.work_time
            self.timer = rumps.Timer(self.update_timer, 1)
            self.timer.start()
            self.button_start.title = "Pause Timer"
        else:
            # Pause functionality
            self.is_running = False
            if self.timer:
                self.timer.stop()
            self.button_start.title = "Resume Timer"

    @rumps.clicked("Stop Timer")
    def stop_timer(self, _):
        if self.timer:
            self.timer.stop()
        self.is_running = False
        self.button_start.title = "Start Work Timer"
        self.title = "🍅"

    def update_timer(self, _):
        if self.remaining_time <= 0:
            self.timer.stop()
            self.is_running = False
            
            if self.is_break:
                print(f"Ending break, starting work session {self.session_count + 1}")
                self.button_start.title = "Start Work Timer"
                self.is_break = False
                self.remaining_time = self.work_time
            else:
                self.session_count += 1
                print(f"Ending work session {self.session_count}")
                print(f"Next break will be: {'long' if self.session_count % self.sessions_before_long_break == 0 else 'short'}")
                self.today_sessions += 1
                self.today_work_time += self.work_time
                self.button_start.title = "Start Break"
                self.is_break = True
                if self.session_count % self.sessions_before_long_break == 0:
                    self.remaining_time = self.long_break_time
                else:
                    self.remaining_time = self.short_break_time
            
            self.title = "🍅"
            return

        self.remaining_time -= 1
        self.title = self.format_time(self.remaining_time)
        
        # Update progress window if it's open
        if hasattr(self, 'progress_controller') and self.progress_controller:
            self.progress_controller.updateProgress_(self.remaining_time)

    def show_progress(self, _):
        total_time = self.work_time if not self.is_break else (
            self.long_break_time if self.session_count % self.sessions_before_long_break == 0 
            else self.short_break_time
        )
        
        session_type = "Break" if self.is_break else "Work"
        next_session = "Work" if self.is_break else "Break"
        
        # Fix the next break duration calculation
        next_duration = self.work_time if self.is_break else (
            # If this is a work session, check if the next break should be long
            self.long_break_time if (self.session_count + 1) % self.sessions_before_long_break == 0 
            else self.short_break_time
        )
        
        self.progress_controller = ProgressWindowController.alloc().\
            initWithProgress_total_type_count_next_(
                self.remaining_time,
                total_time,
                session_type,
                self.session_count + 1,
                f"{next_session} ({self.format_time(next_duration)})"
            )
        self.progress_controller.showWindow_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def show_settings(self, _):
        self.settings_controller = SettingsWindowController.alloc().\
            initWithSettings_callback_(self.settings, self.update_settings)
        self.settings_controller.showWindow_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def show_stats(self, _):
        stats = {
            'today_sessions': self.today_sessions,
            'today_work_time': self.format_time(self.today_work_time)
        }
        
        self.stats_controller = StatisticsWindowController.alloc().\
            initWithStats_(stats)
        self.stats_controller.showWindow_(None)
        NSApp.activateIgnoringOtherApps_(True)

if __name__ == "__main__":
    PomodoroTimer().run()

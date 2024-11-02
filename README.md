# Pomodoro Timer

A simple but powerful Pomodoro Timer app for macOS that lives in your menu bar.

## Features

- 🍅 Menu bar timer with customizable work/break intervals
- 📊 Statistics tracking for daily sessions and work time
- ⚙️ Configurable settings:
  - Work duration (default: 25 minutes)
  - Short break duration (default: 5 minutes) 
  - Long break duration (default: 15 minutes)
  - Number of sessions before long break (default: 4)
  - Daily target sessions (default: 8)
- 🎯 Progress window showing current session details
- ⌨️ Customizable keyboard shortcuts
- 🚀 Optional launch at startup

## Usage

### Basic Controls
- Click the tomato (🍅) icon in the menu bar to access controls
- Start/Stop timer from the menu
- View progress in a floating window
- Check daily statistics
- Configure settings

### Default Intervals
- Work: 25 minutes
- Short Break: 5 minutes
- Long Break: 15 minutes
- Long break occurs after 4 work sessions

### Settings
You can customize:
- Work duration
- Short break duration
- Long break duration
- Number of sessions before long break
- Daily target sessions

## Requirements

- macOS 10.15+
- Python 3.10+

## Dependencies

- rumps - Menu bar app framework
- PyYAML - YAML file handling
- pyobjc-core - Python-Objective-C bridge
- pyobjc-framework-Cocoa - macOS Cocoa bindings


## Building from Source

1. Install development dependencies:

```bash
pip install -r requirements.txt
```

2. Install correct setuptools version:

```bash
pip install setuptools==67.6.1
```

3. Build the app:

```bash
python setup.py py2app
```

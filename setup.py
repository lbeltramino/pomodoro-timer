from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps'],
    'plist': {
        'CFBundleName': "Pomodoro Timer",
        'CFBundleDisplayName': "Pomodoro Timer",
        'CFBundleGetInfoString': "A simple Pomodoro Timer",
        'CFBundleIdentifier': "com.yourdomain.pomodoro-timer",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'LSUIElement': True,  # Makes it a status bar app
    }
}

setup(
    app=APP,
    name='Pomodoro Timer',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['rumps'],
) 
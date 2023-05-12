pyinstaller --icon=logo.ico --onefile ChatGPTConsole.py
pyinstaller --icon=logo.ico --onefile ChatGPTMidServer.py
pyinstaller --icon=logo.ico --onefile ChatGPTMidServerWatchDog.py
pyinstaller --icon=logo.ico --onefile -w ChatGPTGUI.py
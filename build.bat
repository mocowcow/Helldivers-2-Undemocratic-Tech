@echo off
pyinstaller ^
    --onefile ^
    --noconsole ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
    --add-data "stratagems-svg;stratagems-svg" ^
    --add-data "ui/lock_on.svg;ui" ^
    --add-data "ui/lock_off.svg;ui" ^
    --add-data "vision/templates;vision/templates" ^
    --add-data "locales;locales" ^
    --name "HD2 Undemocratic Tech" ^
    main.py

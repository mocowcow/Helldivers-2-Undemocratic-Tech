# HD2 Undemocratic Tech

[繁體中文](README.md) | [English](README_en.md)

A stratagem, chat, and terminal assistant for Helldivers 2.

## Features

1. **Stratagem hotkeys**: Bind keys to automatically enter directional commands.
2. **Chat assistance**: Bind keys to send preset messages, or open a separate window to type a full message.
3. **HUD and estimated cooldowns**: Display stratagem icons and cooldown countdowns. Adjust the HUD position and apply ship upgrades and planetary environmental modifiers when calculating cooldowns.
4. **Terminal arrow recognition**: Bind a key to capture the screen, recognize the arrow sequence, and enter it automatically.

## Screenshots

### Hotkey bindings

![Hotkey binding interface](docs/binding.jpg)

### Stratagem selection

![Stratagem selection interface](docs/stratagem_selector.jpg)

### Settings

![Settings interface](docs/setting.jpg)

## Run and build

Run:

```bat
python -m pip install -r requirements.txt
python main.py
```

Build:

```bat
python -m pip install pyinstaller
.\build.bat
```

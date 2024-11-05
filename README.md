# GEIA.AI Arduino ESP8266/ESP32 Boards Flashing Tool

**Version:** 0.1  

This tool simplifies the process of flashing firmware onto ESP-based boards using the `esptool.py` library (version 4.7.0). It provides a GUI for users to select connected ESP boards, manage firmware files, and initiate flashing without needing to use the command line.


## Screenshot

![Main screen of the tool](./images/GEIA-Arduino-Firmware-Flasher-Tool-screenshot-2024.png)

## Download compiled version for your OS


## Prerequisites

Ensure you have the following installed:
- **Python 3.x**
- **esptool.py v4.7.0**
- Required Python libraries: `tkinter`, `serial`, `requests`

1. Clone the repository
2. Install dependencies with:
```bash
pip install esptool pyserial requests
```

## Usage

1. Launch the GUI tool:
```bash
python flash.py
```
2. Connect the Board: Connect your ESP board to your computer via USB.
3. Select COM Port: The tool will list all available ports.
4. Select your board: Select your ESP8266/ESP32 compatible boards.
5. Flash: Click the "Flash" button to begin the flashing process. The progress and any relevant messages will be displayed in the GUI.


## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Support
For any issues or feature requests, please open an issue on the GitHub repository.

# GEIA Arduino Compatible boards Flashing tool using esptool.py v4.7.0
# Developed by Junell Abdi
# Email: junell@geia.ai
# version: 0.1

import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import requests
import esptool
import sys
import requests
import os
import tempfile
import threading
import subprocess
import re
import time


def get_firmware_data(board_name):
    url = "https://api.geia.ai/firmware/node/firmware-mapping.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        # Parse JSON and get data for the specified board
        firmware_data = response.json()
        board_info = firmware_data.get(board_name)
        
        return board_info if board_info else None

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve firmware data: {str(e)}")
        return None


def download_firmware(url):
    try:
        # Make a GET request to fetch the firmware binary
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        # Create a temporary file to save the firmware
        temp_dir = tempfile.gettempdir()
        firmware_path = os.path.join(temp_dir, "firmware.bin")

        with open(firmware_path, "wb") as firmware_file:
            for chunk in response.iter_content(chunk_size=8192):
                firmware_file.write(chunk)

        return firmware_path

    except requests.RequestException as e:
        # Show error if download fails
        messagebox.showerror("Download Error", f"Failed to download firmware: {str(e)}")
        return None
# Flash firmware function
# Create main GUI window
def create_gui():
    global flash_button, progress, output_text

    root = tk.Tk()
    root.title("GEIA.AI ESP8266 Firmware Flasher Tool")
    root.geometry("400x400")  # Adjusted height for better layout

    # Background
    background = tk.PhotoImage(file="background.png")
    background_label = tk.Label(root, image=background)
    background_label.place(relwidth=1, relheight=1)

    # Board selection
    board_label = tk.Label(root, text="Select Board:")
    board_label.pack(pady=(10, 0))  # Add padding
    board_dropdown = ttk.Combobox(root, values=["ESP8266-01", "ESP8266-12E", "NodeMCU", "Wemos D1 Mini", "Wemos Mini", "Wemos D1", "Wemos D1 R2", "GEIA Board V0.5", "GEIA Dose Mate", "GEIA LiveCam"])  
    board_dropdown.pack(pady=5)

    # Serial port selection
    port_label = tk.Label(root, text="Select Serial Port:")
    port_label.pack(pady=(10, 0))  # Add padding
    port_dropdown = ttk.Combobox(root, values=get_serial_ports())
    port_dropdown.pack(pady=5)

    # Flash button
    flash_button = tk.Button(root, text="Flash Firmware", command=lambda: threading.Thread(target=flash_firmware, args=(board_dropdown.get(), port_dropdown.get())).start())
    flash_button.pack(pady=(10, 0))

    # Progress bar
    progress = ttk.Progressbar(root, length=320)
    progress.pack(pady=(10, 0))  # Show progress bar with padding
    progress.pack_forget()  # Hide the progress bar initially

    # Output text box
    output_text = tk.Text(root, height=10, width=48)
    output_text.pack(pady=10)  # Show output text box with padding
    output_text.pack_forget()  # Hide the output text box initially

    root.mainloop()

def reset_ui():
    flash_button.config(state=tk.NORMAL)  # Re-enable the flash button
    progress['value'] = 0  # Reset progress bar value
    progress.pack_forget()  # Hide the progress bar
    #output_text.pack_forget()  # Hide the output text box
    

def flash_firmware(board_name, port_name):
    flash_button.config(state=tk.DISABLED)  # Disable the flash button
    output_text.pack_forget()
    output_text.delete(1.0, tk.END)  # Clear previous output
    progress.pack(pady=10)  # Show progress bar
    output_text.pack(pady=10)  # Show output text box
    progress['value'] = 0  # Reset progress bar

    board_info = get_firmware_data(board_name)
    if not board_info:
        messagebox.showerror("Error", "Firmware not found for the selected board.")
        reset_ui()
        return

    firmware_path = download_firmware(board_info["url"])
    if not firmware_path:
        messagebox.showerror("Error", "Firmware path not found")
        reset_ui()
        return
        
    # Retrieve flash parameters with defaults if not specified
    flash_size = board_info.get("flash_size", "1MB")  # Default to 1MB if not provided
    flash_mode = board_info.get("flash_mode", "dio")  # Default to "dio" if not provided
    flash_freq = board_info.get("flash_freq", "40m")  # Default to 40 MHz if not provided
    spiffs_size = board_info.get("spiffs_size", "0x10000")  # Default SPIFFS size if not provided
    chip = board_info.get("chip", "esp8266") 
    # Extract additional parameters if available
    reset_pin = board_info.get("reset_pin", "N/A")
    led_pin = board_info.get("led_pin", "N/A")


    # Extract reset and LED pin labels
    #reset_label.config(text=f"Reset Pin: {reset_pin}")
    #led_label.config(text=f"LED Pin: {led_pin}")

    # Run esptool command with additional SPIFFS size if applicable **spiff don't need to be specified, its handled by firmware**
    command = [
       "esptool.py",
        "--port", port_name,
        "--baud", "115200",
        "--chip", chip,
        "write_flash",
        "--flash_size", flash_size,
        "--flash_mode", flash_mode,
        "--flash_freq", flash_freq,

        "0x00000", firmware_path
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)



    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break  # Exit if no more output and process is done

        if output:
            print(output.strip())  # Debug output
            output_text.insert(tk.END, output)  # Append output to the text box
            output_text.see(tk.END)  # Scroll to the end of the output
            if "Writing at" in output:
                # Extract progress information from output
                match = re.search(r'Writing at 0x([0-9a-f]+)', output)
                if match:
                    # Example: Assume firmware size is known (1 MB for this case)
                    firmware_size = 1024 * 1024  # Example: 1 MB firmware
                    written_address = int(match.group(1), 16)
                    # Update progress based on how much has been written
                    progress_percentage = (written_address / firmware_size) * 100
                    progress['value'] = progress_percentage  # Update progress bar value
                    progress.update_idletasks()  # Refresh the GUI

            if "Done" in output:
                break

    process.wait()  # Wait for the process to finish
    reset_ui()
    
# Helper to list available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    filtered_ports = []

    for port in ports:
        if sys.platform.startswith("linux"):
            # Only add ttyUSB or ttyACM ports on Linux
            if "ttyUSB" in port.device or "ttyACM" in port.device:
                filtered_ports.append(port.device)
        elif sys.platform.startswith("win"):
            # Only add COM ports (usually COM3 and above)
            if port.device.startswith("COM") and int(port.device[3:]) >= 3:
                filtered_ports.append(port.device)
        elif sys.platform.startswith("darwin"):
            # Only add cu.usbserial or cu.usbmodem ports on macOS
            if "cu.usbserial" in port.device or "cu.usbmodem" in port.device:
                filtered_ports.append(port.device)

    return filtered_ports

if __name__ == "__main__":
    create_gui()

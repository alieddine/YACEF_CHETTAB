import time
import pyautogui
import keyboard

is_running = False

# Set up a hotkey to toggle the script
keyboard.add_hotkey('ctrl+alt+m', lambda: toggle_script())

def move_mouse():
    pyautogui.move(5, 0)  # Move the mouse by 5 pixels to the right

def toggle_script():
    global is_running
    is_running = not is_running

# Run the script
while True:
    if is_running:
        move_mouse()
    time.sleep(0.1)

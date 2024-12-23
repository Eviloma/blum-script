import pyautogui
import cv2
import numpy as np
from pynput import keyboard
import time
import threading

# Variables to control the clicking loop
clicking_enabled = False
stop_thread = False
interval = 0.001  # 1 millisecond

# Define the target color in BGR space
target_color_tr_start = np.array([58, 120, 245])
target_color_tr_end = np.array([78, 140, 255])

target_color_hr_start = np.array([150, 178, 235])
target_color_hr_end = np.array([177, 208, 255])

target_color_bgr_low = np.array([0, 210, 53])
target_color_bgr_high = np.array([0, 255, 73])

sameCounter = 0
prevPos = -1, -1

def click_on_target_elements():
    global clicking_enabled, stop_thread, sameCounter, prevPos

    while not stop_thread:
        if clicking_enabled:
            # Take a screenshot
            screenshot = pyautogui.screenshot(region=(30, 200, 350, 500))
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            # Find the target color in the screenshot
            mask_tr = cv2.inRange(screenshot_bgr, target_color_tr_start, target_color_tr_end)
            locations = cv2.findNonZero(mask_tr)
            
            if locations is None:
                mask_hr = cv2.inRange(screenshot_bgr, target_color_hr_start, target_color_hr_end)
                locations = cv2.findNonZero(mask_hr)

                if locations is None:
                    mask = cv2.inRange(screenshot_bgr, target_color_bgr_low, target_color_bgr_high)
                    locations = cv2.findNonZero(mask)

            if locations is not None:
                for loc in locations:
                    x, y = loc[0]
                    if prevPos == (x, y):
                        sameCounter +=1
                        if (sameCounter >= 5):
                            sameCounter = 0
                            playClicked = True
                            pyautogui.scroll(-300)
                            pyautogui.click(250, 780)
                            break
                    elif len(prevPos) >= 2:
                        if prevPos[0] >= x - 20 and prevPos[0] <= x + 20 and prevPos[1] >= y - 20 and prevPos[1] <= y + 20:
                            continue
                    prevPos = x, y
                    pyautogui.click(x+30, y+200)
                    break
            else:
                sameCounter +=1
                if (sameCounter >= 5):
                    sameCounter = 0
                    pyautogui.scroll(-300)
                    pyautogui.click(250, 780)     

        time.sleep(interval)  # Sleep briefly to avoid high CPU usage

def on_press(key):
    global clicking_enabled, stop_thread
    try:
        if key == keyboard.Key.f9:
            clicking_enabled = not clicking_enabled
            print(f"Clicking {'enabled' if clicking_enabled else 'disabled'}")
        elif key == keyboard.Key.f10:
            stop_thread = True
            print("Stopping script.")
            return False  # Stop the listener
    except AttributeError:
        pass

def start_key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    print("Press F9 to start the script.")
    print("Press F10 to stop the script.")
    print("Розташуйте BLUM в лівому верхньому куті основного монітору.")
    
    click_thread = threading.Thread(target=click_on_target_elements)
    click_thread.start()
    
    start_key_listener()
    click_thread.join()

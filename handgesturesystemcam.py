import cv2
import time
from cvzone.HandTrackingModule import HandDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui

# --------- Volume Setup ---------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

last_volume_change = 0
last_pause_action = 0
last_arrow_action = 0

# --------- Hand Detector ---------
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

def change_volume(delta):
    global last_volume_change
    current_time = time.time()
    if current_time - last_volume_change > 0.3:
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(max(current + delta, 0.0), 1.0)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        print(f"Volume changed to {new_vol*100:.0f}%")
        last_volume_change = current_time

def toggle_pause():
    global last_pause_action
    current_time = time.time()
    if current_time - last_pause_action > 1:
        pyautogui.press('space')
        print("Play/Pause toggled")
        last_pause_action = current_time

def press_arrow(key):
    global last_arrow_action
    current_time = time.time()
    if current_time - last_arrow_action > 0.2:
        pyautogui.press(key)
        print(f"{key} arrow pressed")
        last_arrow_action = current_time

print("Gesture control started... Press 'q' to quit.")

while True:
    success, img = cap.read()
    if not success:
        continue

    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)

        # Peace sign: Volume Up
        if fingers == [0, 1, 1, 0, 0]:
            change_volume(+0.1)

        # Thumb + Index: Volume Down
        elif fingers == [1, 1, 0, 0, 0]:
            change_volume(-0.1)

        # Fist: Pause/Play
        elif fingers == [0, 0, 0, 0, 0]:
            toggle_pause()

        # Only Pinky: Right Arrow
        elif fingers == [0, 0, 0, 0, 1]:
            press_arrow('right')

        # Ring + Pinky: Left Arrow
        elif fingers == [0, 0, 0, 1, 1]:
            press_arrow('left')

    cv2.imshow("Gesture Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

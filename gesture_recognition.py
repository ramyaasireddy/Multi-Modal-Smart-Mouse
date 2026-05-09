mport cv2
import mediapipe as mp
import pyautogui
import time
import os
import warnings
import webbrowser
                
# -----------------------------
# Suppress warnings
# -----------------------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

# -----------------------------
# Screen setup
# -----------------------------
screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = False

prev_x, prev_y = 0, 0
smoothening = 5

paused = False

gesture_time = 0
gesture_delay = 0.8

last_screenshot_time = 0
screenshot_cooldown = 2

wifi_last_toggle = 0
wifi_cooldown = 3


# -----------------------------
# Finger detection
# -----------------------------
def fingers_up(hand):

    tips = [4,8,12,16,20]
    fingers = []

    # Thumb
    if hand.landmark[tips[0]].x < hand.landmark[tips[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for i in range(1,5):
        if hand.landmark[tips[i]].y < hand.landmark[tips[i]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():

    global prev_x, prev_y, paused
    global gesture_time, last_screenshot_time, wifi_last_toggle

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    print("Gesture Mouse Started")
    print("Press Q to quit")

    while True:

        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame,1)

        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:

            for hand in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                lm = hand.landmark
                fingers = fingers_up(hand)

                current_time = time.time()

                # -----------------------------
                # PAUSE / RESUME
                # -----------------------------
                if fingers == [1,0,0,1,0] and current_time - gesture_time > gesture_delay:

                    paused = not paused
                    print("Paused" if paused else "Resumed")
                    gesture_time = current_time

                if paused:
                    cv2.putText(frame,"PAUSED",(20,50),
                                cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                    continue


                # -----------------------------
                # MOVE CURSOR
                # -----------------------------
                if fingers[1] == 1:

                    x = lm[8].x
                    y = lm[8].y

                    screen_x = int((1-x) * screen_width)
                    screen_y = int(y * screen_height)

                    curr_x = prev_x + (screen_x-prev_x)/smoothening
                    curr_y = prev_y + (screen_y-prev_y)/smoothening

                    pyautogui.moveTo(curr_x, curr_y)

                    prev_x, prev_y = curr_x, curr_y


                # -----------------------------
                # LEFT CLICK
                # -----------------------------
                if fingers == [0,1,1,0,0] and current_time - gesture_time > gesture_delay:

                    pyautogui.click()
                    print("Left Click")
                    gesture_time = current_time


                # -----------------------------
                # RIGHT CLICK
                # -----------------------------
                if fingers == [1,1,0,0,0] and current_time - gesture_time > gesture_delay:

                    pyautogui.rightClick()
                    print("Right Click")
                    gesture_time = current_time


                # -----------------------------
                # DOUBLE CLICK
                # -----------------------------
                if fingers == [0,1,1,1,0] and current_time - gesture_time > gesture_delay:

                    pyautogui.doubleClick()
                    print("Double Click")
                    gesture_time = current_time


                # -----------------------------
                # SCROLL UP
                # -----------------------------
                if fingers == [1,1,1,1,1] and current_time - gesture_time > gesture_delay:

                    pyautogui.scroll(400)
                    print("Scroll Up")
                    gesture_time = current_time


                # -----------------------------
                # SCROLL DOWN
                # -----------------------------
                if fingers == [0,0,0,0,0] and current_time - gesture_time > gesture_delay:

                    pyautogui.scroll(-400)
                    print("Scroll Down")
                    gesture_time = current_time


                # -----------------------------
                # VOLUME UP
                # -----------------------------
                if fingers == [1,0,0,0,1] and current_time - gesture_time > gesture_delay:

                    os.system("amixer -D pulse sset Master 5%+")
                    print("Volume Up")
                    gesture_time = current_time


                # -----------------------------
                # VOLUME DOWN
                # -----------------------------
                if fingers == [0,0,0,0,1] and current_time - gesture_time > gesture_delay:

                    os.system("amixer -D pulse sset Master 5%-")
                    print("Volume Down")
                    gesture_time = current_time


                # -----------------------------
                # SCREENSHOT
                # -----------------------------
                if fingers == [1,1,1,0,0]:

                    if current_time-last_screenshot_time > screenshot_cooldown:

                        path = os.path.expanduser("~/Pictures")
                        filename = f"screenshot_{int(current_time)}.png"

                        pyautogui.screenshot(os.path.join(path,filename))

                        print("Screenshot Saved")

                        last_screenshot_time = current_time


                # -----------------------------
                # WIFI TOGGLE
                # -----------------------------
                if fingers == [1,0,1,1,0]:

                    if current_time-wifi_last_toggle > wifi_cooldown:

                        os.system("nmcli radio wifi off && sleep 1 && nmcli radio wifi on")

                        print("WiFi toggled")

                        wifi_last_toggle = current_time


                # -----------------------------
                # BRIGHTNESS INCREASE
                # -----------------------------
                if fingers == [1,1,0,0,1] and current_time - gesture_time > gesture_delay:

                    os.system("brightnessctl set +10%")
                    print("Brightness Increased")

                    gesture_time = current_time


                # -----------------------------
                # BRIGHTNESS DECREASE
                # -----------------------------
                if fingers == [1,0,0,1,1] and current_time - gesture_time > gesture_delay:

                    os.system("brightnessctl set 10%-")
                    print("Brightness Decreased")

                    gesture_time = current_time


                # -----------------------------
                # OPEN NEW TAB
                # -----------------------------
                if fingers == [0,1,1,0,1] and current_time - gesture_time > gesture_delay:

                    pyautogui.hotkey('ctrl', 't')
                    print("New Tab Opened")

                    gesture_time = current_time


                # ==================================================
                # NEW FEATURES (NO CONFLICT WITH OLD GESTURES)
                # ==================================================

                # OPEN BROWSER
                if fingers == [0,1,1,1,1] and current_time - gesture_time > gesture_delay:

                    webbrowser.open("https://www.google.com")
                    print("Browser Opened")

                    gesture_time = current_time


                # CLOSE BROWSER
                if fingers == [1,1,1,0,1] and current_time - gesture_time > gesture_delay:

                    pyautogui.hotkey("alt","f4")
                    print("Browser Closed")

                    gesture_time = current_time


                # CLOSE TAB
                if fingers == [1,0,1,1,1] and current_time - gesture_time > gesture_delay:

                    pyautogui.hotkey("ctrl","w")
                    print("Tab Closed")

                    gesture_time = current_time


                # COPY
                if fingers == [1,1,1,0,0] and current_time - gesture_time > gesture_delay:

                    pyautogui.hotkey("ctrl","c")
                    print("Copied")

                    gesture_time = current_time


                # PASTE
                if fingers == [1,1,1,0,1] and current_time - gesture_time > gesture_delay:

                    pyautogui.hotkey("ctrl","v")
                    print("Pasted")

                    gesture_time = current_time


                # SHOW DESKTOP
                if fingers == [0,1,0,0,1] and current_time - gesture_time > gesture_delay:

                    pyautogui.hotkey("win","d")
                    print("Desktop")

                    gesture_time = current_time


                # LOCK SCREEN
                if fingers == [0,1,0,1,0] and current_time - gesture_time > gesture_delay:

                    os.system("gnome-screensaver-command -l")
                    print("Locked")

                    gesture_time = current_time


                # DRAG MODE
                if fingers == [0,1,0,0,0]:

                    pyautogui.mouseDown()

                else:

                    pyautogui.mouseUp()


        cv2.imshow("Gesture Mouse", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main() 
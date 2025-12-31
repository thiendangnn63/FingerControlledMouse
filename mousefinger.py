import pyautogui
import cv2
import math
import numpy as np
import time
from hand import HandDetector

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

class MouseFinger:
    def __init__(self, screenW, screenH, detectList=[4, 8, 17, 20]):
        self.screenW = screenW
        self.screenH = screenH
        self.detectList = detectList
        
        self.plocX, self.plocY = 0, 0 
        self.clocX, self.clocY = 0, 0
        self.smoothness = 5 

        self.mode = "Click"
        self.clicked = False
        self.dragging = False

        self.clickDelay = 1.0
        self.lastClickTime = 0

    def moveMouse(self):
        stime = 0
        etime = 0

        detector = HandDetector(maxHands=1, modelComplexity=0)
        cap = cv2.VideoCapture(0)

        screen_w, screen_h = pyautogui.size()

        window_name = "Hand Tracking"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
        cv2.resizeWindow(window_name, 1920, 1080)

        frameR = 100

        while True:
            success, img = cap.read()
            etime = time.time()
            if not success: break
            
            img = cv2.flip(img, 1)
            h, w, c = img.shape
            
            img = detector.findHands(img)
            allHands = detector.findPosition(img, specific=self.detectList)

            for hand in allHands:
                x4, y4 = 0, 0
                x8, y8 = 0, 0
                x17, y17 = 0, 0
                x20, y20 = 0, 0
                
                found4, found8, found17, found20 = False, False, False, False

                for tip in hand:
                    id, x, y = tip[0], tip[1], tip[2]
                    
                    if id == 4:
                        x4, y4 = x, y
                        found4 = True
                    
                    elif id == 8:
                        x8, y8 = x, y
                        found8 = True
                        
                        screen_x = np.interp(x, (frameR, w - frameR), (0, screen_w))
                        screen_y = np.interp(y, (frameR, h - frameR), (0, screen_h))
                        
                        self.clocX = self.plocX + (screen_x - self.plocX) / self.smoothness
                        self.clocY = self.plocY + (screen_y - self.plocY) / self.smoothness
                        
                        pyautogui.moveTo(self.clocX, self.clocY)
                        
                        self.plocX, self.plocY = self.clocX, self.clocY
                    
                    elif id == 17:
                        x17, y17 = x, y
                        found17 = True
                    
                    elif id == 20:
                        x20, y20 = x, y
                        found20 = True
                
                if found17 and found20:
                    pinky = math.hypot(x20 - x17, y20 - y17) > 20

                    if pinky:
                        if (time.time() - self.lastClickTime) >= self.clickDelay:
                            if self.mode != "Drag":
                                self.mode = "Drag"
                            else:
                                self.mode = "Click"
                                pyautogui.mouseUp()
                                self.dragging = False
                    
                            self.lastClickTime = time.time()
                    
                if found4 and found8 and self.mode == "Drag":
                    length = math.hypot(x8 - x4, y8 - y4)
                    
                    if length < 20: 
                        if not self.dragging:
                            pyautogui.mouseDown()
                            self.dragging = True
                        cv2.circle(img, (x8, y8), 15, (0, 255, 0), cv2.FILLED)

                    elif length > 20:
                        if self.dragging:
                            pyautogui.mouseUp()
                            self.dragging = False
                
                if found4 and found8 and self.mode == "Click":
                    length = math.hypot(x8 - x4, y8 - y4)
                    
                    if length < 25:
                        if not self.clicked:
                            pyautogui.click()
                            self.clicked = True
                        cv2.circle(img, (x8, y8), 15, (0, 255, 0), cv2.FILLED)
                    else:
                        self.clicked = False
            
            if (etime - stime) > 0:
                fps = 1 / (etime - stime)
                cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
            stime = etime
            cv2.putText(img, f'Mode: {self.mode}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

            cv2.imshow(window_name, img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

def main():
    mouseFinger = MouseFinger(*pyautogui.size())
    mouseFinger.moveMouse()

if __name__ == "__main__":
    main()
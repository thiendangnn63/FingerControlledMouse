import cv2
import math
import numpy as np
import time
from hand import HandDetector

class DraggableSquare:
    def __init__(self, x, y, w=100, h=100, color=(255, 0, 255)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.default_color = color
        self.drag_color = (0, 255, 0)
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def check_hover(self, cursor_x, cursor_y):
        return (self.x < cursor_x < self.x + self.w) and \
               (self.y < cursor_y < self.y + self.h)

    def start_drag(self, cursor_x, cursor_y):
        self.is_dragging = True
        self.offset_x = self.x - cursor_x
        self.offset_y = self.y - cursor_y

    def stop_drag(self):
        self.is_dragging = False

    def update_position(self, cursor_x, cursor_y):
        if self.is_dragging:
            self.x = cursor_x + self.offset_x
            self.y = cursor_y + self.offset_y

    def draw(self, img):
        overlay = img.copy()
        current_color = self.drag_color if self.is_dragging else self.default_color
        
        cv2.rectangle(overlay, (int(self.x), int(self.y)), 
                     (int(self.x + self.w), int(self.y + self.h)), 
                     current_color, -1)
        
        alpha = 0.5 
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

class DragDropApp:
    def __init__(self):
        self.plocX, self.plocY = 0, 0 
        self.smoothness = 3 

        self.squares = []
        for i in range(5):
            self.squares.append(DraggableSquare(x=50 + (i * 150), y=100, 
                                                color=(np.random.randint(0, 255), 
                                                       np.random.randint(0, 255), 
                                                       np.random.randint(0, 255))))

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)

        detector = HandDetector(maxHands=1, modelComplexity=0)
        active_square = None 

        while True:
            success, img = cap.read()
            if not success: break
            
            img = cv2.flip(img, 1)
            img = detector.findHands(img)
            allHands = detector.findPosition(img, specific=[4, 8])

            cursor_x, cursor_y = 0, 0
            is_pinching = False

            if allHands:
                hand = allHands[0]
                x4, y4, x8, y8 = 0, 0, 0, 0
                found4, found8 = False, False

                for tip in hand:
                    if tip[0] == 4: x4, y4, found4 = tip[1], tip[2], True
                    if tip[0] == 8: x8, y8, found8 = tip[1], tip[2], True

                if found4 and found8:
                    length = math.hypot(x8 - x4, y8 - y4)
                    is_pinching = length < 50
                    cx, cy = (x8 + x4) // 2, (y8 + y4) // 2

                    self.plocX = self.plocX + (cx - self.plocX) / self.smoothness
                    self.plocY = self.plocY + (cy - self.plocY) / self.smoothness
                    cursor_x, cursor_y = int(self.plocX), int(self.plocY)

                    color = (0, 255, 0) if is_pinching else (255, 0, 255)
                    cv2.circle(img, (cursor_x, cursor_y), 10, color, cv2.FILLED)

            if is_pinching:
                if active_square:
                    active_square.update_position(cursor_x, cursor_y)
                else:
                    for sq in reversed(self.squares):
                        if sq.check_hover(cursor_x, cursor_y):
                            active_square = sq
                            active_square.start_drag(cursor_x, cursor_y)
                            break
            else:
                if active_square:
                    active_square.stop_drag()
                    active_square = None

            for sq in self.squares:
                sq.draw(img)

            cv2.imshow("Multi-Square Drag Drop", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = DragDropApp()
    app.run()
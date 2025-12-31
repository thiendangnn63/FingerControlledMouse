import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        model_complexity=self.modelComplexity,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        self.landmarks = results.multi_hand_landmarks

        if self.landmarks:
            for lmk in self.landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, lmk, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True, specific=None):
        allHands = [] 
        
        if self.landmarks:
            for hand in self.landmarks:
                myHand = []
                for id, lm in enumerate(hand.landmark):
                    h, w, c = img.shape
                    if specific != None:
                        if id in specific:
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            myHand.append([id, cx, cy])
                    else:    
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        myHand.append([id, cx, cy])
                allHands.append(myHand)
                
        return allHands
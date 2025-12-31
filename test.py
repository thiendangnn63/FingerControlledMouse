import cv2
import mediapipe as mp
from hand import HandDetector

def main():
    detectList = [4, 8, 12, 16, 20] 

    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    while True:
        success, img = cap.read()
        if not success: break

        img = detector.findHands(img)
        allHands = detector.findPosition(img, specific=None)

        for hand in allHands:
            for tip_id in detectList:
                lm_data = hand[tip_id] 
                
                x, y = lm_data[1], lm_data[2]
                cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(tip_id), (x + 10, y - 10), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
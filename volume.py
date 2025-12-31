import cv2
import numpy as np
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from hand import HandDetector

class VolumeController:
    def __init__(self):
        self.device = AudioUtilities.GetSpeakers()
        self.volume = self.device.EndpointVolume
        self.min_vol, self.max_vol = self.volume.GetVolumeRange()[:2]

    def calculate_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))
    
    def set_volume(self, distance, min_distance=30, max_distance=200):
        vol = np.interp(distance, [min_distance, max_distance], [self.min_vol, self.max_vol])
        self.volume.SetMasterVolumeLevel(vol, None)

    def run(self):
        cap = cv2.VideoCapture(0)
        detector = HandDetector(maxHands=1)

        while True:
            success, img = cap.read()
            if not success:
                break

            img = detector.findHands(img)
            allHands = detector.findPosition(img, specific=[4, 8])

            if allHands:
                lmList = allHands[0]
                x1, y1 = lmList[0][1], lmList[0][2]
                x2, y2 = lmList[1][1], lmList[1][2]

                distance = self.calculate_distance((x1, y1), (x2, y2))
                self.set_volume(distance)

                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(img, f'Vol Dist: {int(distance)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

            cv2.imshow("Volume Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    volume_controller = VolumeController()
    volume_controller.run()
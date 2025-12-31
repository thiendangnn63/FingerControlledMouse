hand.py has the base class of HandDetector that tracks hands using Mediapipe
mousefinger.py use HandDetector's movement tracking to control the mouse, and it has 2 modes:
- Click
- Drag and Drop

Switch between modes by raising your pinky, it will display on the screen when it switches (1 second cooldown)
test.py is a demo of the class in hand.py

import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
import tkinter as tk
from PIL import Image, ImageTk

class GestureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cute Gesture Recognition App")
        self.root.configure(bg="#FBE9E7")  # Set background color

        self.left_frame = tk.Frame(root, bg="#FBE9E7")
        self.left_frame.pack(side="left", padx=20)

        self.right_frame = tk.Frame(root, bg="#FBE9E7")
        self.right_frame.pack(side="right", padx=20)

        self.finger_spell_var = tk.BooleanVar(value=False)
        self.finger_spell_checkbox = tk.Checkbutton(self.right_frame, text="Perform Finger Spell", variable=self.finger_spell_var, command=self.toggle_finger_spell, bg="#FBE9E7", font=("Comic Sans MS", 14), padx=10)
        self.finger_spell_checkbox.pack(pady=20)

        self.video_frame = tk.Label(self.left_frame, bg="#FBE9E7")
        self.video_frame.pack()

        self.cap = cv2.VideoCapture(0)

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

        self.labels_dict_fingerspell = {
            0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
            10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
            19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z', 26: 'SPACE',
            27: 'DELETE'
        }

        self.labels_dict_normal = {
            0: 'AsalamOAlikum', 1: 'Mein', 2: 'Ap', 3: 'Mera', 4: 'Apka', 5: 'Haan', 6: 'Nahi', 7: 'Hai', 8: 'Kya',
            9: 'Kaisy',
            10: 'BhutShukriya'
        }

        self.sentence = ""
        self.gesture_start_time = None
        self.gesture_hold_threshold = 3.0  # Changed to 3 seconds
        self.space_added = False
        self.model = None

        self.update()

    def toggle_finger_spell(self):
        self.sentence = ""
        self.gesture_start_time = None
        self.space_added = False
        self.load_model()

    def load_model(self):
        if self.finger_spell_var.get():
            try:
                model_dict = pickle.load(open('./model.p', 'rb'))
                self.model = model_dict['model']
            except:
                self.model = None
        else:
            try:
                model_dict = pickle.load(open('./modelA.p', 'rb'))
                self.model = model_dict['model']
            except:
                self.model = None

    def update(self):
        ret, frame = self.cap.read()

        if self.model is not None:
            self.process_gesture(frame)

        if ret:
            self.display_frame(frame)

        self.root.after(10, self.update)

    def process_gesture(self, frame):
        data_aux = []
        x_ = []
        y_ = []

        H, W, _ = frame.shape

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y

                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

            prediction = self.model.predict([np.asarray(data_aux)])
            if self.finger_spell_var.get():
                predicted_character = self.labels_dict_fingerspell[int(prediction[0])]
            else:
                predicted_character = self.labels_dict_normal[int(prediction[0])]

            if predicted_character == 'SPACE':
                if self.gesture_start_time is None:
                    self.gesture_start_time = time.time()
                elif time.time() - self.gesture_start_time >= self.gesture_hold_threshold:
                    if not self.space_added:
                        self.sentence += " "
                        self.space_added = True
                    self.gesture_start_time = None
            elif predicted_character == 'DELETE':
                if self.gesture_start_time is None:
                    self.gesture_start_time = time.time()
                elif time.time() - self.gesture_start_time >= self.gesture_hold_threshold:
                    if self.sentence:
                        self.sentence = self.sentence[:-1]  # Remove the last character
                    self.gesture_start_time = None
            else:
                self.space_added = False  # Reset space_added flag for non-space gestures
                if self.gesture_start_time is None:
                    self.gesture_start_time = time.time()
                elif time.time() - self.gesture_start_time >= self.gesture_hold_threshold:
                    if self.sentence == "" or self.sentence[-1] != predicted_character:
                        self.sentence += predicted_character
                    self.gesture_start_time = None

            # Display the forming sentence on the frame
            cv2.putText(frame, "Forming Sentence:", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, self.sentence, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if x_ and y_:
                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10

                x2 = int(max(x_) * W) - 10
                y2 = int(max(y_) * H) - 10

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                            cv2.LINE_AA)

    def display_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.video_frame.image = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
        self.video_frame.config(image=self.video_frame.image)

    def quit(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    root.mainloop()

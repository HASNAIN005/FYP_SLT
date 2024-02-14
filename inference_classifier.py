from flask import Flask, request, jsonify, send_file
import cv2
import pickle
import mediapipe as mp
import numpy as np
import time
from gtts import gTTS
import subprocess
from PIL import Image
from io import BytesIO

app = Flask(__name__)

class GestureApp:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
        self.labels_dict_fingerspell = {
            0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
            10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
            19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z', 26: 'SPACE',
            27: 'DELETE'
        }
        self.labels_dict_normal = {
            0: 'AsalamOAlikum', 1: 'Mein', 2: 'muje', 3: 'Mera', 4: 'hai', 5: 'Hun', 6: 'ka', 7: 'ap',
            8: 'kesy', 9: 'both', 10: 'Shukriya', 11: 'kya', 12: 'Acha', 13: 'khobsurat', 14: 'Bhagna',
            15: 'Choti', 16: 'Yaad', 17: 'Delete', 18: 'Space'
        }
        self.sentence = ""
        self.formed_sentence = ""
        self.gesture_start_time = None
        self.gesture_hold_threshold = 3.0
        self.space_added = False
        self.model_fingerspell = None
        self.model_normal = None
        self.load_models()

    def load_models(self):
        try:
            model_dict_fingerspell = pickle.load(open('./model.p', 'rb'))
            self.model_fingerspell = model_dict_fingerspell['model']
        except:
            self.model_fingerspell = None
        try:
            model_dict_normal = pickle.load(open('./modelA.p', 'rb'))
            self.model_normal = model_dict_normal['model']
        except:
            self.model_normal = None
        self.model = self.model_normal

    def process_gesture(self, frame_data):
        data_aux = []
        x_ = []
        y_ = []
        frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
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
                        self.sentence = self.sentence[:-1]
                    self.gesture_start_time = None
            else:
                self.space_added = False
                if self.gesture_start_time is None:
                    self.gesture_start_time = time.time()
                elif time.time() - self.gesture_start_time >= self.gesture_hold_threshold:
                    if self.sentence == "" or self.sentence[-1] != predicted_character:
                        self.sentence += predicted_character
                    self.gesture_start_time = None
            self.formed_sentence = self.sentence

    def display_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(frame_rgb)
        img_io = BytesIO()
        image_pil.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')

    def speak_sentence(self):
        if self.formed_sentence:
            tts = gTTS(text=self.formed_sentence, lang="en")
            audio_file = "temp_audio.mp3"
            tts.save(audio_file)
            subprocess.call(["ffplay", "-nodisp", "-autoexit", audio_file])

    def clear_sentence(self):
        self.sentence = ""
        self.formed_sentence = ""

gesture_app = GestureApp()

@app.route("/process_gesture", methods=["POST"])
def process_gesture():
    frame_data = request.data
    gesture_app.process_gesture(frame_data)
    return "Gesture processed successfully!"

@app.route("/speak_sentence")
def speak_sentence():
    gesture_app.speak_sentence()
    return "Sentence spoken!"

@app.route("/clear_sentence")
def clear_sentence():
    gesture_app.clear_sentence()
    return "Sentence cleared!"

if __name__ == "__main__":
    app.run(debug=True)

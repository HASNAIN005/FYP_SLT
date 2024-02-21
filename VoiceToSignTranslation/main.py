from tkinter import *
from PIL import Image, ImageTk
import speech_recognition as sr

# Define the dictionary mapping characters to image paths
image_dictionary = {
     'A': r'D:\detection\letters\A.png',
    'B': r'D:\detection\letters\B.png',
    'C': r'D:\detection\letters\C.png',
    'D': r'D:\detection\letters\D.png',
    'E': r'D:\detection\letters\E.png',
    'F': r'D:\detection\letters\F.png',
    'G': r'D:\detection\letters\G.png',
    'H': r'D:\detection\letters\H.png',
    'I': r'D:\detection\letters\I.png',
    'J': r'D:\detection\letters\J.png',
    'K': r'D:\detection\letters\K.png',
    'L': r'D:\detection\letters\L.png',
    'M': r'D:\detection\letters\M.png',
    'N': r'D:\detection\letters\oN.png',
    'O': r'D:\detection\letters\O.png',
    'P': r'D:\detection\letters\P.png',
    'Q': r'D:\detection\letters\Q.png',
    'R': r'D:\detection\letters\R.png',
    'S': r'D:\detection\letters\S.png',
    'T': r'D:\detection\letters\T.png',
    'U': r'D:\detection\letters\oU.png',
    'V': r'D:\detection\letters\V.png',
    'W': r'D:\detection\letters\W.png',
    'X': r'D:\detection\letters\X.png',
    'Y': r'D:\detection\letters\Y.png',
    'Z': r'D:\detection\letters\Z.png',
    'SPACE': r'D:\detection\letters\SPACE.png'
}

def set_color_scheme(widget, bg_color, fg_color):
    widget.configure(background=bg_color)
    widget.configure(foreground=fg_color)

root = Tk()
root.title("Voice to Sign Translation")

# Set background and foreground colors
bg_color = "#F0F0F0"  # Light gray background
fg_color = "black"

# Set the background color for the Canvas
canvas = Canvas(root, bg=bg_color)
canvas.pack(fill="both", expand=True)

# Add a scrollbar to the canvas
scrollbar = Scrollbar(canvas, orient="horizontal", command=canvas.xview)
scrollbar.pack(side="bottom", fill="x")
canvas.configure(xscrollcommand=scrollbar.set)

# Create a label to display the recognized sentence
sentence_label = Label(root, text="", font=("Helvetica", 16))
sentence_label.pack()

# Set color scheme for labels and buttons
set_color_scheme(sentence_label, bg_color, fg_color)

# List to hold PhotoImage objects
photo_images = []

# Function to convert text to sign language images
def text_to_sign_language(text):
    sign_language_images = []
    for char in text:
        if char in image_dictionary:
            image_path = image_dictionary[char]
            img = Image.open(image_path)
            img = img.resize((100, 100))  # Adjust the image size as needed
            photo = ImageTk.PhotoImage(img)
            sign_language_images.append(photo)
            photo_images.append(photo)
        elif char == ' ':
            space_image_path = image_dictionary['SPACE']
            img = Image.open(space_image_path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            sign_language_images.append(photo)
            photo_images.append(photo)
    return sign_language_images

# Function to clear the sentence and images
def clear_sentence():
    sentence_label.config(text="")
    for img in photo_images:
        canvas.delete(img)
    photo_images.clear()

# Function for recording and translating
def record_and_translate():
    clear_sentence()  # Clear previous sentence and images
    with sr.Microphone() as source:
        sentence_label.config(text="Listening...")
        audio = recognizer.listen(source)

    try:
        sentence = recognizer.recognize_google(audio)
        sentence_label.config(text="Recognized sentence: " + sentence)

        # Process the recognized sentence (e.g., remove unwanted characters and convert to uppercase)
        processed_sentence = sentence.upper()

        # Translate the sentence to sign language images
        sign_language_images = text_to_sign_language(processed_sentence)

        # Display the sign language images on the Canvas with horizontal scrolling
        x = 10
        for img in sign_language_images:
            label = Label(image=img)
            label.photo = img  # Keep a reference to prevent it from being garbage collected
            canvas.create_window(x, 10, anchor="w", window=label)
            x += 120  # Adjust spacing as needed
            root.update_idletasks()

        # Update the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))

    except sr.UnknownValueError:
        sentence_label.config(text="Google Web Speech API could not understand audio.")
    except sr.RequestError as e:
        sentence_label.config(text="Could not request results from Google Web Speech API; {0}".format(e))

# Speech recognition
recognizer = sr.Recognizer()

# Set color scheme for buttons
record_button = Button(root, text="Speak", command=record_and_translate, font=("Helvetica", 16), padx=20, pady=10)
clear_button = Button(root, text="Clear", command=clear_sentence, font=("Helvetica", 16), padx=20, pady=10)
set_color_scheme(record_button, bg_color="#009688", fg_color="white")  # Dark teal background
set_color_scheme(clear_button, bg_color="#FF6347", fg_color="white")  # Tomato red background

# Position the buttons at the bottom of the interface
record_button.pack(side="left")
clear_button.pack(side="right")

root.mainloop()

import cv2
import threading
import mediapipe as mp
import pyautogui
import time
import math
import os
import playsound
import pygame
import tkinter as tk
import subprocess
import speech_recognition as sr
import keyboard


def launch_another_program():
    # file chuong trinh
    path_to_another_program = './HandiKey.py'

    if path_to_another_program:
        try:
            subprocess.Popen(['python', path_to_another_program])
        except FileNotFoundError:
            print(f"File not found: {path_to_another_program}")


def on_button_click():
    root.destroy()


# file voice
def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load('./voice.mp3')
    pygame.mixer.music.play(1)
    root.after(15000, root.destroy)


# day la tui cai phat 2 lan, ong muon may lan thi thay so thoi

# Main code starts here
root = tk.Tk()
root.title("Launch Another Program")

# Set the window size to 1000x667 pixels
root.geometry("1000x667")

# file anh
background_image = tk.PhotoImage(file='./background.gif')

# Create a canvas with the background image
canvas = tk.Canvas(root, width=1000, height=667)
canvas.pack()
canvas.create_image(0, 0, anchor='nw', image=background_image)

# Draw the circular button with white text and blue border
button = tk.Button(root, text='Bắt đầu', font=('Helvetica', 16), fg='white', bg='black', activebackground='gray',
                   activeforeground='white', width=10, height=2, command=on_button_click, bd=5, relief='raised')
button.place(relx=0.69, rely=0.73, relwidth=0.15, relheight=0.1)

# Play the background music when the program starts
play_background_music()

root.mainloop()

cap = cv2.VideoCapture(0)

mp_face_mesh = mp.solutions.face_mesh


def track_nose():
    # Lấy kích thước màn hình
    screen_width, screen_height = pyautogui.size()

    with mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5) as face_mesh:

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # Lấy tọa độ điểm mũi
                nose_point = face_landmarks.landmark[1]

                # Tính toán tỷ lệ
                nose_x = int(nose_point.x * frame.shape[1])
                nose_y = int(nose_point.y * frame.shape[0])

                # Chuyển đổi tọa độ
                nose_x = int(nose_x / frame.shape[1] * screen_width)
                nose_y = int(nose_y / frame.shape[0] * screen_height)

                nose_x_origin = nose_x

                # Tính toán tọa độ x mới cho chuột
                mouse_x = screen_width - nose_x_origin

                # Di chuyển con trỏ chuột
                pyautogui.moveTo(mouse_x, nose_y)

            time.sleep(0.01)


def check_left_blink():
    with mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5) as face_mesh:

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # Lấy trạng thái nháy mắt trái
                left_eye_top = face_landmarks.landmark[145]
                point_1 = (left_eye_top.x * frame.shape[1], left_eye_top.y * frame.shape[0])

                left_eye_bottom = face_landmarks.landmark[159]
                point_2 = (left_eye_bottom.x * frame.shape[1], left_eye_bottom.y * frame.shape[0])

                distance = math.sqrt((point_2[0] - point_1[0]) ** 2 + (point_2[1] - point_1[1]) ** 2)

                try:
                    if distance < 4:
                        pyautogui.click()
                        pygame.mixer.init()
                        pygame.mixer.music.load('./click2.mp3')
                        pygame.mixer.music.play(1)
                except Exception:
                    pass

            # Đợi một khoảng thời gian
            time.sleep(0.01)
def key_board():
    r = sr.Recognizer()

    # Sử dụng microphone như là nguồn âm thanh
    with sr.Microphone() as source:
        print("Hãy nói gì đó...")

        # Tự động điều chỉnh nền tiếng ồn để cải thiện nhận dạng
        r.adjust_for_ambient_noise(source)

        while True:
            # Nghe nguồn âm thanh từ microphone
            audio = r.listen(source)

            try:
                text = r.recognize_google(audio, language="vi-VN")
                print("Bạn đã nói:" + text)
                type_text_in_word(text)


            except sr.UnknownValueError:
                print("Không thể nhận dạng giọng nói.")

            except sr.RequestError as e:
                print("Lỗi trong quá trình nhận dạng: {0}".format(e))


def type_text_in_word(text):
    keyboard.write(text)


if __name__ == "__main__":
    while True:
        key_board()


# Khởi tạo các luồng
key_board_def = threading.Thread(target=key_board)
nose_thread = threading.Thread(target=track_nose)
blink_thread = threading.Thread(target=check_left_blink)

# Bắt đầu các luồng
nose_thread.start()
blink_thread.start()
key_board_def.start()

# Đợi các luồng kết thúc
nose_thread.join()
blink_thread.join()
key_board_def.join()

# Giải phóng camera
cap.release()

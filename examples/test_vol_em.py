import tkinter as tk
import soundfile as sf
import sounddevice as sd
import os
import threading
import numpy as np
from sk_speech import sk_volume as vm

# Глобальные переменные
norm_file = 'test_em_sber_norm.wav'
input_file = 'test_em_sber5.wav'
output_file = 'out_change_speech.wav'

options = {"freq": True, "amplitude": True, "period": True,
           "pitch": True, "formants": True, "vowels": True, "formant_max": 5}
speech = vm.init_speech(norm_file, options=options)
cur_speech = vm.speech_params(input_file, speech)

current_volume = 0
current_emotion = 0
changed = True
cx, cy = 0, 0  # Центр формы
mouse_pressed = False  # Флаг для отслеживания нажатия мыши
circle = None  # Переменная для хранения объекта круга


def play_audio_loop():
    global current_volume, current_emotion, speech, cur_speech, changed

    while True:
        if changed:
            # Обновляем аудио при каждом цикле воспроизведения
            y_new, sr_new = vm.change_speech(speech, cur_speech, volume=current_volume, emotion=current_emotion)

            # Сохраняем новое аудио
            sf.write(output_file, y_new, sr_new)
            changed = False

        # Загружаем и проигрываем аудио
        if os.path.exists(output_file):
            data, samplerate = sf.read(output_file)
            sd.play(data, samplerate)
            sd.wait()  # Ждем завершения воспроизведения


def on_mouse_move(event):
    global cx, cy, current_volume, current_emotion, mouse_pressed, changed, canvas, circle
    if mouse_pressed:
        # Расчет координат относительно центра
        xx = event.x - cx
        yy = event.y - cy

        # Рассчет volume и emotion
        new_volume = np.clip(yy / cy, -1, 1)
        new_emotion = np.clip(xx / cx, -1, 1)

        # Если значения изменились, обновляем текущие параметры и положение круга
        if abs(current_volume - new_volume) > 0.05 or abs(current_emotion - new_emotion) > 0.05:
            current_volume = new_volume
            current_emotion = new_emotion
            changed = True

            # Обновляем положение круга
            update_circle_position()


def update_circle_position():
    global canvas, circle, current_volume, current_emotion, cx, cy

    # Рассчитываем новые координаты круга
    circle_x = cx + current_emotion * cx
    circle_y = cy + current_volume * cy

    # Обновляем положение круга на холсте
    canvas.coords(circle, circle_x - 20, circle_y - 20, circle_x + 20, circle_y + 20)


def on_mouse_press(event):
    global mouse_pressed
    mouse_pressed = True  # Включаем флаг при нажатии кнопки мыши


def on_mouse_release(event):
    global mouse_pressed
    mouse_pressed = False  # Выключаем флаг при отпускании кнопки мыши


def create_interface():
    global cx, cy, canvas, circle
    # Создаем графическое окно
    root = tk.Tk()
    root.title("Audio Control")

    # Устанавливаем размер окна
    window_width = 600
    window_height = 600
    root.geometry(f"{window_width}x{window_height}")

    # Рассчитываем центр окна
    cx = window_width // 2
    cy = window_height // 2

    # Добавляем canvas для отрисовки
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack()

    # Разделение на 4 части
    canvas.create_line(cx, 0, cx, window_height, fill="black")
    canvas.create_line(0, cy, window_width, cy, fill="black")

    # Добавляем текстовые метки
    canvas.create_text(cx, 10, text="Volume -", font=("Arial", 12), fill="black")  # Верхняя ось Y
    canvas.create_text(cx, window_height - 10, text="Volume +", font=("Arial", 12), fill="black")  # Нижняя ось Y
    canvas.create_text(10, cy, text="Emotion -", font=("Arial", 12), fill="black", anchor="w")  # Левая ось X
    canvas.create_text(window_width - 10, cy, text="Emotion +", font=("Arial", 12), fill="black", anchor="e")  # Правая ось X

    # Подписи осей
    canvas.create_text(window_width // 2 + 100, window_height - 30, text="Emotion", font=("Arial", 14), fill="blue")
    canvas.create_text(30, window_height // 2 - 100, text="Volume", font=("Arial", 14), fill="blue", angle=90)

    # Добавляем круг для отображения текущих значений volume и emotion
    circle_x = cx + current_emotion * cx
    circle_y = cy + current_volume * cy
    circle = canvas.create_oval(circle_x - 20, circle_y - 20, circle_x + 20, circle_y + 20, fill="white", outline="red", width=2)

    # Привязываем события движения мыши, нажатия и отпускания кнопки
    canvas.bind("<Motion>", on_mouse_move)
    canvas.bind("<ButtonPress-1>", on_mouse_press)
    canvas.bind("<ButtonRelease-1>", on_mouse_release)

    # Запускаем главное окно
    root.mainloop()


if __name__ == "__main__":
    # Стартуем поток для проигрывания аудио в фоновом режиме
    threading.Thread(target=play_audio_loop, args=(), daemon=True).start()

    # Запускаем графический интерфейс
    create_interface()

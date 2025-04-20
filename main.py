import tkinter as tk
from tkinter import filedialog, messagebox
import json, random, os, asyncio
import cv2
from PIL import Image, ImageTk

QUIZ_FILE = 'quiz_data.json'
MEDIA_FOLDER = 'media'
ADMIN_PASSWORD = '1234'


class GuessTheMovieGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Угадай фильм?")
        self.quiz_data = self.load_quiz_data()
        self.score = 0
        self.current_quiz = None
        self.cap = None
        self.video_label = None

        self.create_main_menu()

    def load_quiz_data(self):
        if not os.path.exists(QUIZ_FILE):
            return []
        with open(QUIZ_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_quiz_data(self):
        with open(QUIZ_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.quiz_data, f, indent=2, ensure_ascii=False)

    def create_main_menu(self):
        self.clear()
        tk.Label(self.root, text="Угадай фильм?", font=("Helvetica", 24)).pack(pady=10)
        tk.Button(self.root, text="Играть", command=self.start_game, width=30).pack(pady=5)
        tk.Button(self.root, text="Админ-панель", command=self.admin_login, width=30).pack(pady=5)
        tk.Button(self.root, text="Выйти", command=self.root.quit, width=30).pack(pady=5)

    def start_game(self):
        self.score = 0
        self.next_question()

    def next_question(self):
        self.clear()
        if not self.quiz_data:
            tk.Label(self.root, text="Нет данных для викторины").pack()
            return

        self.current_quiz = random.choice(self.quiz_data)
        self.play_video(self.current_quiz['filename'])

    def play_video(self, path):
        self.cap = cv2.VideoCapture(path)
        self.video_label = tk.Label(self.root)
        self.video_label.pack()
        self.root.after(0, self.update_frame)

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (400, 300))
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                self.root.after(30, self.update_frame)
            else:
                self.cap.release()
                self.show_options()

    def show_options(self):
        options = self.current_quiz['options']
        random.shuffle(options)
        tk.Label(self.root, text="Выбери правильный фильм:", font=("Helvetica", 14)).pack(pady=5)
        for opt in options:
            tk.Button(self.root, text=opt, width=40, command=lambda o=opt: self.check_answer(o)).pack(pady=2)

    def check_answer(self, selected):
        correct = self.current_quiz['correct']
        if selected == correct:
            self.score += 1
            self.next_question()
        else:
            self.end_game()

    def end_game(self):
        self.clear()
        tk.Label(self.root, text=f"Ты проиграл!", font=("Helvetica", 16)).pack(pady=5)
        tk.Label(self.root, text=f"Твой счёт: {self.score}").pack(pady=5)
        tk.Button(self.root, text="В меню", command=self.create_main_menu).pack(pady=10)

    def admin_login(self):
        self.clear()
        tk.Label(self.root, text="Введите пароль администратора:").pack(pady=5)
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack()
        tk.Button(self.root, text="Войти", command=self.check_admin).pack(pady=5)

    def check_admin(self):
        if self.pass_entry.get() == ADMIN_PASSWORD:
            self.admin_panel()
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")

    def admin_panel(self):
        self.clear()
        tk.Label(self.root, text="Админ-панель", font=("Helvetica", 18)).pack(pady=10)
        tk.Button(self.root, text="Добавить фильм", command=self.add_quiz).pack(pady=5)
        tk.Button(self.root, text="Показать все фильмы", command=self.show_all_quizzes).pack(pady=5)
        tk.Button(self.root, text="Назад", command=self.create_main_menu).pack(pady=5)

    def add_quiz(self):
        self.clear()
        tk.Label(self.root, text="Выбери видеофайл:").pack(pady=5)
        tk.Button(self.root, text="Выбрать", command=self.browse_file).pack()
        self.selected_file = None

        self.entries = []
        labels = ["Правильный ответ", "Фейк 1", "Фейк 2", "Фейк 3", "Фейк 4"]
        for label in labels:
            tk.Label(self.root, text=label).pack()
            entry = tk.Entry(self.root, width=40)
            entry.pack(pady=2)
            self.entries.append(entry)

        tk.Button(self.root, text="Сохранить", command=self.save_quiz).pack(pady=10)
        tk.Button(self.root, text="Назад", command=self.admin_panel).pack()

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov")])
        if file:
            if not os.path.exists(MEDIA_FOLDER):
                os.makedirs(MEDIA_FOLDER)
            filename = os.path.basename(file)
            dest = os.path.join(MEDIA_FOLDER, filename)
            if not os.path.exists(dest):
                os.rename(file, dest)
            self.selected_file = dest
            messagebox.showinfo("Выбрано", f"Файл: {filename}")

    def save_quiz(self):
        if not self.selected_file:
            messagebox.showerror("Ошибка", "Файл не выбран")
            return

        values = [e.get().strip() for e in self.entries]
        if not all(values):
            messagebox.showerror("Ошибка", "Заполни все поля")
            return

        correct = values[0]
        fakes = values[1:]
        options = fakes + [correct]

        self.quiz_data.append({
            "filename": self.selected_file,
            "correct": correct,
            "options": options
        })

        self.save_quiz_data()
        messagebox.showinfo("Успешно", "Фильм добавлен")
        self.admin_panel()

    def show_all_quizzes(self):
        self.clear()
        tk.Label(self.root, text="Список фильмов:", font=("Helvetica", 14)).pack(pady=5)
        for q in self.quiz_data:
            tk.Label(self.root, text=q['correct']).pack()
        tk.Button(self.root, text="Назад", command=self.admin_panel).pack(pady=10)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = GuessTheMovieGame(root)
    root.mainloop()

import tkinter as tk

root = tk.Tk()
root.title("Тестовое окно")
root.geometry("400x300")

# Явно задаем цвета для всех элементов
root.configure(bg="white")  # Фон главного окна

label = tk.Label(
    root,
    text="Всё работает!",
    font=("Arial", 20),
    fg="red",
    bg="lightgray",
    padx=20,
    pady=10
)
label.pack(pady=50)

button = tk.Button(
    root,
    text="Нажми меня",
    command=lambda: label.config(text="Текст изменён!"),
    bg="#e1e1e1",  # Светло-серый фон кнопки
    fg="black",     # Черный текст на кнопке
    activebackground="#d0d0d0",  # Цвет при нажатии
    borderwidth=2,
    relief="groove"
)
button.pack()

# Для macOS можно добавить специальные настройки
root.tk.call("tk::mac::useThemedTk", 0)  # Отключить системную тему

root.mainloop()
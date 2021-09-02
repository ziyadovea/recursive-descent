import tkinter as tk
from tkinter import ttk
import ctypes
import sys
from tkinter.constants import END
import tkinter.messagebox as mb
from analyzer import Analyzer

############################################################# Создание интерфейса ############################################################

# Для высокого разрешения
ctypes.windll.shcore.SetProcessDpiAwareness(1)

root = tk.Tk()
root.title('Pascal subset')
root.geometry('1000x800+450+100')

error_line = 0

# Перенос строк отключен, иначе нумерация будет работать некорректно
numbers = tk.Text(root, width=4, bg='lightgray', state=tk.DISABLED, relief=tk.FLAT)
numbers.grid(row=0, column=0, sticky='NS')

scroll = ttk.Scrollbar(root)
scroll.grid(row=0, column=2, sticky='NS')

def on_yscrollcommand(*args):
    scroll.set(*args)             # Синхронизация скролбара с текстовым полем
    numbers.yview_moveto(args[0]) # Синхронизация поля с номерами с текстовым полем

text = tk.Text(root, yscrollcommand=on_yscrollcommand, wrap=tk.NONE)
text.grid(row=0, column=1, sticky='NSWE')

def scroll_command(*args):
    # Движение скролбара управляет отображением текста в обоих текстовых полях
    text.yview(*args)
    numbers.yview(*args)

scroll.config(command=scroll_command)

def insert_numbers():
    count_of_lines = text.get(1.0, tk.END).count('\n') + 1
    numbers.config(state=tk.NORMAL)
    numbers.delete(1.0, tk.END)
    numbers.insert(1.0, '\n'.join(map(str, range(1, count_of_lines))))
    numbers.config(state=tk.DISABLED)

insert_numbers()

def on_edit(event):
    # Срабатывает при изменениях в текстовом поле
    global error_line
    text.tag_delete('failed')
    insert_numbers()
    text.edit_modified(0) # Сбрасываем флаг изменения текстового поля

text.bind('<<Modified>>', on_edit)

def tab(arg):
    text.insert(tk.INSERT, " " * 4)
    return 'break'

text.bind('<Tab>', tab)

# Нужно, чтобы текстовое поле автоматически меняло размер при изменении размера окна
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

#################################################################### МЕНЮ ##################################################################

mainmenu = tk.Menu(root) 
root.config(menu=mainmenu) 
 
filemenu = tk.Menu(mainmenu, tearoff=0)

################################################################## Кнопка анализа ##########################################################

def analyze():
    global error_line
    s = text.get(1.0, END)
    analyzer = Analyzer(s)
    # Следующий вывод для теста, он ни на что не влияет.
    #print(analyzer.program1)
    #print(analyzer.program2)
    try:
        analyzer.check()
        mb.showinfo(title='Congratulations!', message='Correct!')
    except Exception as ex:
        number_error_line = analyzer.error_line
        text.tag_add('failed', number_error_line + 0.0, number_error_line + 0.777)
        text.tag_config('failed', background='red')
        mb.showerror(title="Error info", message=ex)

filemenu.add_command(label="Analysis", command=analyze)
filemenu.add_separator()

############################################################################################################################################

def Close(): 
    root.destroy() 
    
filemenu.add_command(label="Exit", command=Close)
 
helpmenu = tk.Menu(mainmenu, tearoff=0) 

def about_message():
    mb.showinfo(
        title="About \'Pascal subset\'",
        message="Лабораторная работа 2 по ОПТ.\nРеализация подмножества языка Pascal.\nНИУ МЭИ, Зиядов Э.А., группа А-13-18, вариант 8."
    )
helpmenu.add_command(label="About", command=about_message)
 
mainmenu.add_cascade(label="File", menu=filemenu)
mainmenu.add_cascade(label="Help", menu=helpmenu)

############################################################# Конец создания интерфейса #########################################################

s = """program abc;\n\nconst a = (-2 * 2) div 5 + (3 - +3) * -5;\nvar i, a, b: integer; \n    flag: boolean;\n\nbegin\n    \n    b := (2 * 3 - 5 div (5 + 5));\n    a := @b;\n    b := a^ + a^;\n        \n   
    for i := 1 to 100 + 1 do\n    flag := false;\n    begin\n        flag := true;\n        for i := 100 + 1 downto 1 do\n        if (i < -5) and (not flag) then\n        begin\n            read(a);\n            write(a);\n        end\n        else\n        begin\n            read(a, b, c);\n            for a := 15 to a do\n            begin\n                write(a, b, c, d);\n            end;\n            write();\n            read();\n        end;\n    end;\n\n    if true then \n        read()\n    else\n        write();\n\nend.\n"""
text.insert(1.0, s)
mb.showinfo(title='Информация.', message='В окне приведен пример корректной программы.\nДля ее анализа надо нажать в меню "файл -> анализ".\nВы можете ввести в текстовое\
 поле любой текст,\nа далее проанализировать его - является ли он корректным с точки зрения языка Паскаль.\n(Редактирование доступно только после одного нажатия на кнопку "анализ")')

if __name__ == '__main__':
    root.mainloop()
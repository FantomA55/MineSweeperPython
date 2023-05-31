#Импортируем нужные модули
import tkinter as tk
from time import time
from random import shuffle
from tkinter.messagebox import showinfo, showerror
#Определяем цвета для цифр (количества мин в соседних клетках) и мин
colors = {
    0: 'white', 
    1: 'blue',
    2: '#008200',
    3: '#FF0000',
    4: '#000084',
    5: '#840000',
    6: '#008284',
    7: '#840084',
    8: '#000000',
}
#Определяем уровни сложности и их параметры
LEVELS = {
    'Легкий': {'rows': 8, 'columns': 8, 'mines': 10},
    'Средний': {'rows': 12, 'columns': 22, 'mines': 40},
    'Сложный': {'rows': 16, 'columns': 30, 'mines': 99},
}
#Создаем класс MyButton, который наследуется от tk.Button и добавляем ему свойства для работы в игре
class MyButton(tk.Button):
    
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False
        
    def __repr__(self):
        return f'MyButton{self.x} {self.y} {self.number} {self.is_mine}'
#Создаем класс MineSweeper  
class MineSweeper:
    
    window = tk.Tk()
    ROW = 8
    COLUMNS = 8
    MINES = 10
    DEFAULT_MINES = 10
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True
    
    def __init__(self):
        
        self.buttons = []
        self.window.title("Сапер")
        MineSweeper.window.resizable(0, 0)
        for i in range(MineSweeper.ROW+2):
            temp = []
            for j in range(MineSweeper.COLUMNS+2):
                btn = MyButton(MineSweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind("<Button-3>", self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
    #Обработка правого клика мыши на кнопке игрового поля
    def right_click(self, event):
        if MineSweeper.IS_GAME_OVER or MineSweeper.IS_FIRST_CLICK:
            return
        cur_btn = event.widget
        if cur_btn['state']=='normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            cur_btn['disabledforeground']='red'
            MineSweeper.MINES -= 1
            self.mines_left_label.config(text=f"Осталось мин: {MineSweeper.MINES}")
        elif cur_btn['text']=='🚩':
            cur_btn['text']=''
            cur_btn['state']='normal'
            MineSweeper.MINES += 1
            self.mines_left_label.config(text=f"Осталось мин: {MineSweeper.MINES}")
    #Обработка левого клика мыши на кнопке игрового поля
    def click(self, clicked_button:MyButton):
        if MineSweeper.IS_GAME_OVER:
            return
        if MineSweeper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            self.print_buttons()
            MineSweeper.IS_FIRST_CLICK = False
            self.start_time = time()
            self.update_timer()
        if clicked_button.is_mine:
            clicked_button.config(text="*", background='red', disabledforeground='black')
            clicked_button.is_open = True
            MineSweeper.IS_GAME_OVER = True
            showinfo('Game over', 'Вы проиграли!')
            for i in range(1, MineSweeper.ROW + 1):
                for j in range(1, MineSweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '*'
        else:
            color = colors.get(clicked_button.count_bomb, 'black')
            if clicked_button.count_bomb:
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.breadth_first_search(clicked_button)
            if self.check_win():
                MineSweeper.IS_GAME_OVER = True
                showinfo('Поздравляем!', 'Вы выиграли!')
        clicked_button.config(state='disabled')
        clicked_button.config(relief=tk.SUNKEN)
    #реализация алгоритма для открытия всех соседних ячеек, которые не содержат бомбы
    def breadth_first_search(self, btn: MyButton):
        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')
            if cur_btn.count_bomb:
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground = color)
            else:
                cur_btn.config(text='', disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state='disabled')
            cur_btn.config(relief=tk.SUNKEN)
            if cur_btn.count_bomb == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        next_btn = self.buttons[x+dx][y+dy]
                        if not next_btn.is_open and 1<=next_btn.x<=MineSweeper.ROW and \
                           1<=next_btn.y<=MineSweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)
    #Функция для перезагрузки игры                
    def reload(self):
        for widget in MineSweeper.window.winfo_children():
            widget.destroy()
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False
        self.start_time = time()
        self.update_timer()
        MineSweeper.MINES = MineSweeper.DEFAULT_MINES
        MineSweeper.FLAGS = 0
        self.timer_label.config(text='00:00')
        self.mines_left_label.config(text=f"Осталось мин: {MineSweeper.MINES}")
        count = 1
    #Метод создания окна настроек       
    def create_settings_win(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Настройки')
        tk.Label(win_settings, text='Количество строк').grid(row=0, column=0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Количество колонок').grid(row=1, column=0)
        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Количество мин').grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        save_btn =tk.Button(win_settings, text='Применить',
                  command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
    #Метод сохранения изменений настроек
    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        #Проверка корректности введенных значений
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильное значение!')
            return
        if int(row.get()) <= 0 or int(column.get()) <= 0:
            showerror('Ошибка', 'Значение количества строк и столбцов должно быть больше 0')
            return
        if int(mines.get()) < 0:
            showerror('Ошибка', 'Количество мин не может быть отрицательным')
            return
        if int(mines.get()) == int(row.get()) * int(column.get()):
            showerror('Ошибка', 'Количество мин не должно равняться количеству ячеек на поле')
            return
        if int(mines.get()) > int(row.get()) * int(column.get()) - 1:
            showerror('Ошибка', 'Количество мин не может быть больше, чем количество ячеек на поле')
            return
        #Изменение настроек игры    
        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())
        MineSweeper.DEFAULT_MINES = int(mines.get())
        MineSweeper.MINES = MineSweeper.DEFAULT_MINES
        self.reload()
    #Метод создания виджетов
    def create_widgets(self):
        #Создание меню
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff = 0)
        #Добавление команд меню
        settings_menu.add_command(label='Играть', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_settings_win)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Игра', menu=settings_menu)
        #Создание меню сложности
        level_menu = tk.Menu(settings_menu, tearoff=0)
        for level in LEVELS:
            level_menu.add_command(label=level, command=lambda level=level: self.set_level(level))
        menubar.add_cascade(label='Уровень сложности', menu=level_menu, underline = 0)
        #Создание кнопок на поле
        count = 1
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i,column=j, sticky='NSEW')    
                count += 1           
        #Конфигурация главного окна tkinter
        for i in range(1, MineSweeper.ROW + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
        for i in range(1, MineSweeper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)
        #Создание меток для времени и количества мин
        self.timer_label = tk.Label(self.window, text="00:00", font='Calibri 15 bold')
        self.timer_label.grid(row=MineSweeper.ROW+1, columnspan=MineSweeper.COLUMNS+1, padx=20, pady=20, sticky='w')

        self.mines_left_label = tk.Label(self.window, text=f"Осталось мин: {MineSweeper.MINES}", font='Calibri 15 bold')
        self.mines_left_label.grid(row=MineSweeper.ROW+1, columnspan=MineSweeper.COLUMNS+1, padx=20, pady=20, sticky='e')
    #Метод обновления таймера игры
    def update_timer(self):
        if not MineSweeper.IS_GAME_OVER and not MineSweeper.IS_FIRST_CLICK:
            elapsed_time = time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_string = f"{minutes:02}:{seconds:02}"
            self.timer_label.config(text=time_string)
            self.window.after(1000, self.update_timer)
    #Метод проверки условия победы
    def check_win(self):
        if MineSweeper.IS_GAME_OVER:
            return False
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if not btn.is_mine and not btn.is_open:
                    return False
        return True
    #Метод задания уровня сложности
    def set_level(self, level):
        params = LEVELS[level]
        MineSweeper.DEFAULT_MINES = params['mines']
        MineSweeper.ROW = params['rows']
        MineSweeper.COLUMNS = params['columns']
        MineSweeper.MINES = params['mines']
        self.reload()
    #Метод открытия всех кнопок
    def open_all_buttons(self):
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text="*", background='red', disabledforeground='black')
                elif btn.is_open:
                    btn.config(state='disabled', relief=tk.SUNKEN)
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, 'black')
                    btn.config(text=btn.count_bomb, fg=color)
    #Метод запуска игры
    def start(self):
        game.create_widgets()
        MineSweeper.window.geometry("+150+50")
        MineSweeper.window.mainloop()
    #Метод отображения кнопок в консоли (для отладки) 
    def print_buttons(self):
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B', end='')
                else:
                    print(btn.count_bomb, end='')
            print()
    #Метод расставления мин на поле
    def insert_mines(self, number:int):
        index_mines = self.get_mines_places(number)
        print(index_mines)
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True
    #Метод вычисления количества мин во всех кнопках игрового поля и сохранения результата в свойство count_bomb объекта MyButton
    def count_mines_in_buttons(self):
        for i in range(1, MineSweeper.ROW+1):
            for j in range(1, MineSweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i+row_dx][j+col_dx]
                            if neighbour.is_mine:
                                count_bomb += 1
                btn.count_bomb = count_bomb
    #Статистический метод, кторый генерирует случайную уникальную последовательность индексов ячеек, в которые будут расставлены мины
    @staticmethod
    def get_mines_places(exclude_number: int):
        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1))
        print('Исключаем кнопку номер',{exclude_number})
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:MineSweeper.MINES]

game = MineSweeper()
game.start()




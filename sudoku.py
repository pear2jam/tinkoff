import pickle
import random


class NotEmptyCell(Exception):
    pass


class SudokuRulesError(Exception):
    pass


class InvalidIndex(Exception):
    pass


class InvalidValue(Exception):
    pass


class LoadRequired(Exception):
    pass


class SaveRequired(Exception):
    pass


class BackError(Exception):
    pass


# структура поля
class Field:
    def __init__(self):
        self.generated = False
        self.field = [[(3*j+i+j//3) % 9 + 1 for i in range(9)] for j in range(9)]
        self.solve_field = [[(3*j+i+j//3) % 9 + 1 for i in range(9)] for j in range(9)]

    # функции перемешивания изначального поля
    # транспонирование
    def transpose(self):
        if random.random() > 0.5:
            return
        self.field = [[self.field[i][j] for i in range(9)] for j in range(9)]

    # перемешивание строк в пределах одного блока
    def row_mix(self):
        for i in range(3):
            a = [0, 1, 2]
            random.shuffle(a)
            self.field[3*i], self.field[3*i+1], self.field[3*i+2] = \
                self.field[3*i+a[0]], self.field[3*i+a[1]], self.field[3*i+a[2]]

    # перемешивание столбцов в пределах одного блока
    def column_mix(self):
        field_copy = [[self.field[i][j] for j in range(9)] for i in range(9)]
        for i in range(3):
            a = [0, 1, 2]
            random.shuffle(a)
            for j in range(9):
                self.field[j][3*i] = field_copy[j][3*i+a[0]]
                self.field[j][3*i+1] = field_copy[j][3*i+a[1]]
                self.field[j][3*i+2] = field_copy[j][3*i+a[2]]

    # перемешивание блоков как строк
    def block_row_mix(self):
        field_copy = [[self.field[i][j] for j in range(9)] for i in range(9)]
        a = [0, 1, 2]
        random.shuffle(a)
        for i in range(3):
            for j in range(9):
                for k in range(3):
                    self.field[3*i+k][j] = field_copy[3*a[i]+k][j]

    # перемешивание блоков как столбцов
    def block_column_mix(self):
        field_copy = [[self.field[i][j] for j in range(9)] for i in range(9)]
        a = [0, 1, 2]
        random.shuffle(a)
        for i in range(3):
            for j in range(9):
                for k in range(3):
                    self.field[j][3 * i + k] = field_copy[j][3 * a[i] + k]

    # вывод поля
    def look(self):
        print("    ", end='')
        for i in range(3):
            for j in range(3):
                print(3*i+j+1, end=' ')
            print('  ', end='')
        print('\n')
        for i in range(3):
            for l in range(3):
                print(3*i+l+1, '   ', sep='', end='')
                for j in range(2):
                    for k in range(3):
                        print(self.field[3*i+l][3*j+k], end=' ')
                    print('| ', end='')
                for j in range(3):
                    print(self.field[3*i+l][6+j], end=' ')
                print()
            if i < 2:
                print('    ---------------------')

    # генерация игрового поля
    def generate(self, cells):
        self.field = [[(3 * j + i + j // 3) % 9 + 1 for i in range(9)] for j in range(9)]
        self.transpose()
        self.row_mix()
        self.column_mix()
        self.block_row_mix()
        self.block_column_mix()
        self.solve_field = [[self.field[i][j] for j in range(9)] for i in range(9)]
        a = [[i, j] for i in range(9) for j in range(9)]
        random.shuffle(a)
        for i in range(81-cells):
            self.field[a[i][0]][a[i][1]] = '+'
        self.generated = True

    # установка цифры в ячейку
    def set(self, x, y, val):
        if x < 1 or x > 9 or y < 1 or y > 9:
            raise InvalidIndex()
        if self.field[x-1][y-1] != '+':
            raise NotEmptyCell()
        if val > 9 or val < 1:
            raise InvalidValue()
        for i in range(9):
            if self.field[i][y-1] == val or self.field[x-1][i] == val:
                raise SudokuRulesError()
        for i in range(3):
            for j in range(3):
                if self.field[3*((x-1)//3)+i][3*((y-1)//3)+j] == val:
                    raise SudokuRulesError()
        self.field[x-1][y-1] = val


# обработчик команд и поля
class Game:
    def __init__(self):
        pass

    @staticmethod
    def greet():
        print("""
        .............................
        .Hello there in Sudoku Game!.
        .............................
        Напишите 'New' для новой игры
                 'Load' для загрузки игры
                 'Save' для сохранения игры
                 'Exit' для того чтобы выйти
                 'Next' для следущего шага компьютера (только режим 2)
        """, end='')

    @staticmethod
    def _print_help():
        print("""Напишите 'New' для новой игры
             'Load' для загрузки игры
             'Save' для сохранения игры
             'Exit' для того чтобы выйти 
             'строка столбец значение' во время игры чтобы
                    заполнить пропуск
             'Back' для отмены хода
             'Help' для просмотра списка доступных команд
        """)

    # совершить шаг в режими игры компьютера
    @staticmethod
    def _play_step(sess):
        for i in range(9):
            for j in range(9):
                if sess.field.field[i][j] == '+':
                    sess.field.set(i + 1, j + 1, sess.field.solve_field[i][j])
                    sess.empties -= 1
                    sess.steps.append([i, j])
                    return i, j

    # начать новую игру
    @staticmethod
    def _new(sess):
        sess.mode = int(input("Введите 1 для ручной игры, 2 для игры компьютера: "))
        cells = int(input("Введите количество заполненных клеток: "))
        while cells > 80 or cells < 1:
            cells = int(input("Введите число от 1 до 80"))
        sess.field.generate(cells)
        sess.empties = 81 - cells
        if sess.mode == 1:
            print("""Для того чтобы заполнить пропуск (+) пишите команды в виде"
            'строка колонка число'""")
        else:
            print("Для следущего шага компьютера введите 'Next'")

# обработать следущую команду игрока
    def play(self, sess):
        if sess.empties == 0 and sess.field.generated:
            print("Судоку решена. Новая судоку:")
            self._new(sess)
            sess.field.look()
        cmd = input().split()
        if len(cmd) != 1 and len(cmd) != 3:
            print("Некорректная команда,\n введите 'Help' для просмотра списка доступных команд'")
            return
        if cmd[0] == 'New':
            self._new(sess)
        elif cmd[0] == 'Load':
            raise LoadRequired
        elif cmd[0] == 'Save':
            raise SaveRequired
        elif cmd[0] == 'Exit':
            exit(0)
        elif cmd[0] == 'Help':
            self._print_help()
            return
        elif cmd[0] == 'Next':
            if sess.mode == 1:
                print("Недоступно в режиме ручной игры")
                return
            x, y = self._play_step(sess)
            print(x + 1, y + 1, sess.field.field[x][y])
        elif cmd[0] == 'Back':
            try:
                self._back(sess)
            except BackError:
                print("Ходов нет")
        elif len(cmd) == 3:
            if sess.mode == 2:
                print("Недоступно в режиме игры компьетера")
                return
            try:
                sess.field.set(int(cmd[0]), int(cmd[1]), int(cmd[2]))
                sess.empties -= 1
                sess.steps.append([int(cmd[0])-1, int(cmd[1])-1])
            except NotEmptyCell:
                print("Здесь уже есть значение")
            except SudokuRulesError:
                print("Число не подходит по правилам")
            except InvalidIndex:
                print("Нет такого столбца или строки")
            except InvalidValue:
                print("Введите цифру от 1 до 9")
        else:
            print("Некорректная команда,\n введите 'Help' для просмотра списка доступных команд'")
            return
        sess.field.look()

    # вернуться на шаг назад
    @staticmethod
    def _back(sess):
        if len(sess.steps) == 0:
            raise BackError
        sess.field.field[sess.steps[-1][0]][sess.steps[-1][1]] = '+'
        del sess.steps[-1]


class Session:
    def __init__(self):
        self.field = Field()
        self.empties = 0
        self.mode = 1
        self.steps = []


# обработчик сессий
class SessionHandler:
    def __init__(self):
        self.sess = Session()
        self.game = Game()
        self.game.greet()

    def start(self):
        while True:
            try:
                self.game.play(self.sess)
            except LoadRequired:
                self._load()
            except SaveRequired:
                self._save()

    def _load(self):
        name = input("Введите имя сохранения: ")
        try:
            with open(name + '.pickle', 'rb') as f:
                self.sess = pickle.load(f)
        except:
            print("Нет такого сохранения")

    def _save(self):
        name = input("Введите название игры: ")
        with open(name + '.pickle', 'wb') as f:
            pickle.dump(self.sess, f)


game = SessionHandler()
game.start()

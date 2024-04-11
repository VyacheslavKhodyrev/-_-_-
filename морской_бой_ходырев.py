

from random import randint
from time import sleep


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return " "*20 + "Координаты вышли за пределы доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return " "*20 + "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot ({self.x}, {self.y})'

class Ship:
    def __init__(self, head_ship, len_ship, direction):
        self.len_ship = len_ship
        self.head_ship = head_ship
        self.life_ship = len_ship
        self.direction = direction

    @property
    def dots(self):
        ship_coords = []
        for i in range(self.len_ship):
            current_x = self.head_ship.x
            current_y = self.head_ship.y

            if self.direction == 0:
                current_x += i

            elif self.direction == 1:
                current_y += i

            ship_coords.append(Dot(current_x, current_y))

        return ship_coords

    def shooten(self, shot):
        return shot in self.dots


class Board:
    ship_cell = '■'
    free_cell = '◯'
    shot_cell = '∘'
    ship_shot_cell = 'X'

    def __init__(self, board_size=6, hid=False):
        self.board_size = board_size
        self.field = [[self.free_cell] * board_size for _ in range(board_size)]
        self.list_ships = []
        self.hid = hid
        self.count = 0
        self.busy = []

    def contur(self, ship, verb=False):
        contur_list = [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1), (0, 0), (0, 1),
                       (1, -1), (1, 0), (1, 1)]
        for coords in ship.dots:
            for coord_x, coord_y in contur_list:
                contur_coords = Dot(coords.x + coord_x, coords.y + coord_y)
                if not (self.out(contur_coords)) and contur_coords not in self.busy:
                    if verb:
                        self.field[contur_coords.x][contur_coords.y] = self.shot_cell
                    self.busy.append(contur_coords)
    def add_ship(self, ship):
        for coords in ship.dots:
            if self.out(coords) or coords in self.busy:
                raise BoardWrongShipException()

        for coords in ship.dots:
            self.field[coords.x][coords.y] = self.ship_cell
            self.busy.append(coords)

        self.list_ships.append(ship)
        self.contur(ship)

    def get_field(self):
        return self.field

    def out(self, coords) -> bool:
        return not ((0 <= coords.x < self.board_size) and (0 <= coords.y < self.board_size))

    def shot(self, coords):
        if self.out(coords):
            raise BoardOutException()

        if coords in self.busy:
            raise BoardUsedException()

        self.busy.append(coords)

        for ship in self.list_ships:
            if ship.shooten(coords):
                ship.life_ship -= 1
                self.field[coords.x][coords.y] = self.ship_shot_cell

                if ship.life_ship == 0:
                    self.count += 1
                    self.contur(ship, verb=True)
                    print(" " * 20 + '-' * 27)
                    print(" "*20 + "Корабль уничтожен!")
                    return False
                else:
                    print(" " * 20 + '-' * 27)
                    print(" "*20 + "Корабль ранен!")
                    return True

        self.field[coords.x][coords.y] = self.shot_cell
        print(" "*20 + '-' * 27)
        print(" "*20 + "Вы промазали!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.list_ships)


class Player:
    def __init__(self, own_board, enemy_board):
        self.own_board = own_board
        self.enemy_board = enemy_board

    def ask(self):
        #pass
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        coords = Dot(randint(0, 5), randint(0, 5))
        print(" " * 20 + '-' * 27)
        print(" "*20 + f"Компьютер сходил: {coords.x + 1}, {coords.y + 1}")
        return coords


class User(Player):
    def ask(self):
        while True:
            print(" "*20 + '-' * 27)
            coords = input(" "*20 + "Ваш выстрел! \n                    Bведите координаты: ").split()

            if len(coords) != 2:
                print(" "*20 + '-' * 27)
                print(" "*20 + "Введите 2 координаты!")
                continue

            coord_x, coord_y = coords

            if not (coord_x.isdigit()) or not (coord_y.isdigit()):
                print('-' * 27)
                print(" "*20 + "Введите числа!")
                continue

            coord_x, coord_y = int(coord_x), int(coord_y)

            return Dot(coord_x - 1, coord_y - 1)


class Game:
    def __init__(self, board_size=6):
        self.board_size = board_size
        self.ship_lens = [3, 2, 2, 1, 1, 1, 1]
        user_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hid = True

        self.user = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)

    def board_random(self):
        board = Board(self.board_size)

        attempts = 0
        for len_ship in self.ship_lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.board_size), randint(0, self.board_size)), len_ship, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.board_random()
        return board

    @staticmethod
    def greet():
        print("-" * 39)
        print("         Вас приветствует игра")
        print("")
        print("              МОРСКОЙ БОЙ")
        print("-" * 39)
        print("Для выстрела по кораблю Вам необходимо")
        print("ввести координаты точки в формате: Х У")
        print("")
        print("Х - координата точки по вертикали")
        print("У - координата точки по горизонтали")
        sleep(3)
    def show_board(self):

        print('-' * 27 + '     ' + '-' * 27)
        print('    Доска    компьютера        ', '   Доска    пользователя        ')
        print('-' * 27 + '     ' + '-' * 27)
        print('  | 1 | 2 | 3 | 4 | 5 | 6 |     ' * 2)
        ai_field = self.ai.own_board
        user_field = self.user.own_board

        for row in range(self.board_size):  # range(n):
            row1 = ' | '.join(self.ai.own_board.field[row])
            row2 = ' | '.join(self.user.own_board.field[row])
            if self.ai.own_board.hid:
                row1 = row1.replace(Board.ship_cell, Board.free_cell)
            print(f'{row + 1} | {row1} |    ', f'{row + 1} | {row2} | ')
        print('-' * 27 + '     ' + '-' * 27)

    def loop(self):
        count = 0
        while True:
            self.show_board()
            if count % 2 == 0:
                print(" "*20 + "Ходит пользователь")
                repeat = self.user.move()
            else:
                print(" "*20 + "Ходит компьютер")
                sleep(3)
                repeat = self.ai.move()
                sleep(3)

            if repeat:
                count -= 1

            if self.ai.own_board.defeat():
                self.show_board()
                print(" "*20 + '-' * 27)
                print(" "*20 + "Выиграл пользователь ! ! !")
                break

            if self.user.own_board.defeat():
                self.show_board()
                print(" "*20 + '-' * 27)
                print(" "*20 + "Выиграл компьютер ! ! !")
                break

            count += 1

    def start(self):
        self.greet()
        sleep(3)
        self.loop()

g = Game()
g.start()

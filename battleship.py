# Battleship
# Author: Jan Zalewski

import random, time, sys
from enum import Enum


GRID = \
"""
{0}
____________________________

      A B C D E F G H I J  
      _ _ _ _ _ _ _ _ _ _   
  1  |{A1}|{B1}|{C1}|{D1}|{E1}|{F1}|{G1}|{H1}|{I1}|{J1}|
  2  |{A2}|{B2}|{C2}|{D2}|{E2}|{F2}|{G2}|{H2}|{I2}|{J2}|
  3  |{A3}|{B3}|{C3}|{D3}|{E3}|{F3}|{G3}|{H3}|{I3}|{J3}|
  4  |{A4}|{B4}|{C4}|{D4}|{E4}|{F4}|{G4}|{H4}|{I4}|{J4}|
  5  |{A5}|{B5}|{C5}|{D5}|{E5}|{F5}|{G5}|{H5}|{I5}|{J5}|
  6  |{A6}|{B6}|{C6}|{D6}|{E6}|{F6}|{G6}|{H6}|{I6}|{J6}|
  7  |{A7}|{B7}|{C7}|{D7}|{E7}|{F7}|{G7}|{H7}|{I7}|{J7}|
  8  |{A8}|{B8}|{C8}|{D8}|{E8}|{F8}|{G8}|{H8}|{I8}|{J8}|
  9  |{A9}|{B9}|{C9}|{D9}|{E9}|{F9}|{G9}|{H9}|{I9}|{J9}|
  10 |{A10}|{B10}|{C10}|{D10}|{E10}|{F10}|{G10}|{H10}|{I10}|{J10}|
____________________________
"""

LETTERS = 'ABCDEFGHIJ'

# ai plays (as player) with ai
PLAYER_AI = False


class Direction(Enum):
    
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    @classmethod
    def get_random_direction(cls):
        """ Return horizontal or vertical direction. """
        return random.choice((cls.HORIZONTAL, cls.VERTICAL))

    @classmethod
    def what_direction(cls, coords1, coords2):
        """ Determine direction based on two coordinates. """
        x1, y1 = coords1
        x2, y2 = coords2

        if x1 == x2:
            return cls.VERTICAL
        elif y1 == y2:
            return cls.HORIZONTAL
        else:
            return cls.NONE


class Report(Enum):
    """ Enum for reporting what happend after shooting. """
    
    NOT_VALID = 0
    HIT = 1
    DESTROYED = 2
    MISSED = 3


class Ship:
    """ Class representing single ship. """
    
    def __init__(self, coords, size, direction = Direction.NONE):
        self.size = size
        
        # number of not yet destroyed parts of the ship
        self.active_units = size

        # ships with single unit have undefined (irrelevant) direction
        if size > 1:
            self.direction = direction
        else:
            self.direction = Direction.NONE

        # initialize every part of the ship with coordinates
        x, y = coords
        self.body_coords = []
        for i in range(size):
            if direction == Direction.HORIZONTAL:
                self.body_coords.append((x + i, y))
            elif direction == Direction.VERTICAL:
                self.body_coords.append((x, y + i))
            else:
                self.body_coords.append((x, y))

    def __repr__(self):
        return str(self.body_coords)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n >= self.size:
            raise StopIteration      
        index = self.n
        self.n += 1
        return self.body_coords[index]

    def get_coords(self, index = 0):
        return self.body_coords[index]

    def get_tail(self):
        """ Return ship's last element coordinates. """
        return self.body_coords[self.size - 1]

    def get_size(self):
        return self.size

    def is_destroyed(self):
        return self.active_units == 0

    def hit(self):
        """ Called when ship gets hit. It reduces member variable
            that counts how many active (not hit) units ship has. """
        self.active_units -= 1


class Cell:
    """ Class representing single cell on board. Cell can have various states
        like: hidden, empty, missed, ship, destroyed. """
    
    def __init__(self):
        self.__hidden = False
        self.__empty = True
        self.__missed = False
        self.__ship = False
        self.__destroyed = False
        self.__value = '_'

    def __repr__(self):
        return self.__value

    def is_empty(self):
        return self.__empty

    def is_ship(self):
        return self.__ship

    def is_destroyed(self):
        return self.__destroyed

    def set_hidden(self):
        self.__hidden = True
        self.__update()

    def set_missed(self):
        self.__hidden = False
        self.__missed = True
        self.__update()

    def set_ship(self):
        self.__ship = True
        self.__empty = False
        self.__update()

    def set_destroyed(self):
        self.__hidden = False
        self.__ship = False
        self.__destroyed = True
        self.__update()

    def get_value(self):
        return self.__value

    # update visible value of the cell based on class's boolean variables
    def __update(self):
        if self.__hidden == True:
            self.__value = '_'
        elif self.__missed == True:
            self.__value = '.'
        elif self.__destroyed == True:
            self.__value = 'X'
        elif self.__ship == True:
            self.__value = 'O'
        elif self.__empty == True:
            self.__value = '_'
            

class Board:
    """ Class representing board on which ships are placed. Game have two
        boards: one for our ships and the other for opponents ships. """
    
    def __init__(self, name, hidden = False):
        # board name
        self.name = name
        # main variable -> dictionary which keeps positions e.g. 'A1' and values as Cell() objects
        self.board = {self.to_position((i, j)) : Cell() for i in range(10) for j in range(10)}
        # list of all ships placed on board
        self.ships = self.__generate_ships(hidden)
        # set of coordinates saved as tuples e.g. (1, 2) which are possible to shoot
        self.possible_moves = {(i, j) for i in range(10) for j in range(10)}

    def __repr__(self):
        return str(self.board)        

    def __get_ships_coords_board(self):
        """ Generate and return two-dimentional list of Boolean values: True - is ship, False - empty. """
        ships_coords_board = []
        ships_coords_list = [cell.is_ship() for cell in self.board.values()]
        for i in range(0, 100, 10):
            ships_coords_board.append(ships_coords_list[i : i + 10])

        return ships_coords_board 

    def __generate_ships(self, hidden):
        """ Used board's constructor to generate and place all ships on board in random locations.
        # Create:
        # 1 ship of size 4
        # 2 ships of size 3
        # 3 ships of size 2
        # 4 ships of size 1
        # Return list of created ships. """

        ships_list = []
        # number - number of ships to generate, starts from 1, ends on 4
        # size - size of each ship, starts from 4, ends on 1
        # loop iterates reversely to place largest ship first
        for number, size in enumerate(range(4, 0, -1), 1):
            for _ in range(number):

                # get 10x10 list of lists with ships' locations
                ships_coords_board = self.__get_ships_coords_board()

                # get random coordinates in range [0, 9]
                coords = self.get_random_coords()

                # get random direction
                direction = Direction.get_random_direction()

                # create temporary ship that will be placed on board
                ship = Ship(coords, size, direction)
                        
                # check if ship can be placed; if not try other random coordinate
                while not self.__ship_can_be_placed(ship, ships_coords_board):
                    coords = self.get_random_coords()
                    direction = Direction.get_random_direction()
                    ship = Ship(coords, size, direction)
                    
                self.__place_ship(ship, hidden)
                ships_list.append(ship)

        return ships_list

    def __ship_is_colliding(self, ship_coords, ships_board):
        """ Check if there is already another ship in given coordinates or around it. """

        x, y = ship_coords
        left, right = x, x
        top, bottom = y, y

        # protect indexes from going out of board's bounds
        if x != 0:
            left = x - 1
        if x != 9:
            right = x + 1
        if y != 0:
            top = y - 1
        if y != 9:
            bottom = y + 1
        
        if ships_board[x][y] == True or \
           ships_board[left][y] == True or \
           ships_board[left][top] == True or \
           ships_board[x][top] == True or \
           ships_board[right][top] == True or \
           ships_board[right][y] == True or \
           ships_board[right][bottom] == True or \
           ships_board[x][bottom] == True or \
           ships_board[left][bottom] == True:
            return True

        return False

    def __ship_can_be_placed(self, ship, ships_coords_board):
        """ Return True if ship can be placed in this place or False otherwise. """

        # check if ship would be placed out of board's bounds
        x, y = ship.get_tail()
        if x > 9 or y > 9:
            return False

        # check if ship would collide with another ship
        for i in range(ship.get_size()):
            coords = ship.get_coords(i)
            if self.__ship_is_colliding(coords, ships_coords_board):
                return False

        return True

    def __place_ship(self, ship, hidden):
        " Place ship in given coordinates. "
        for i in range(ship.get_size()):
            coords = ship.get_coords(i)
            pos = self.to_position(coords)
            self.board[pos].set_ship()
            if hidden:
                self.board[pos].set_hidden()
    
    def are_all_ships_destroyed(self):
        """ Check if every ship on board sank. """
        for ship in self.ships:
            if not ship.is_destroyed():
                return False

        return True
    
    def get_ship_by_coords(self, coords):
        """ Return ship object from ship list that has given coordinates. """
        for ship in self.ships:
            if coords in ship:
                return ship
        # ship with given coordinates doesn't exist or something went wrong
        raise ValueError 

    def get_random_coords(self):
        """ Return random coordinates. """
        x, y = random.randint(0, 9), random.randint(0, 9)
        return (x, y)

    def get_random_possible_position(self):
        """ Return random position from possible moves. """
        coords = random.choice(list(self.possible_moves))
        return self.to_position(coords)

    def get_near_possible_positions(self, position, direction, diagonally = False):
        """ Return possible positions near given position. """
        near_moves = []
        x, y = self.to_coords(position)
        
        # return if possible left, right, up, down positions
        if direction == Direction.NONE or direction == Direction.HORIZONTAL:
            if (x - 1, y) in self.possible_moves:
                near_moves.append((x - 1, y))
            if (x + 1, y) in self.possible_moves:
                near_moves.append((x + 1, y))
        if direction == Direction.NONE or direction == Direction.VERTICAL:
            if (x, y - 1) in self.possible_moves:
                near_moves.append((x, y - 1))
            if (x, y + 1) in self.possible_moves:
                near_moves.append((x, y + 1))

        # return if possible all positions diagonally
        if diagonally:
            if (x - 1, y - 1) in self.possible_moves:
                near_moves.append((x - 1, y - 1))
            if (x + 1, y - 1) in self.possible_moves:
                near_moves.append((x + 1, y - 1))
            if (x - 1, y + 1) in self.possible_moves:
                near_moves.append((x - 1, y + 1))
            if (x + 1, y + 1) in self.possible_moves:
                near_moves.append((x + 1, y + 1))

        # cast all elements from coords to positions
        near_moves = [self.to_position(coords) for coords in near_moves]

        return near_moves  

    def to_position(self, coords):
        """ Return position as string based on x, y coordinates e.g. 'A1' = to_position((0, 0)) """
        
        x, y = coords
        return LETTERS[x] + str(y + 1)

    def to_coords(self, position):
        """ Return coordinates from position e.g. (0, 0) = to_coords('A1') """
        
        coords = []
        coords.append(LETTERS.index(position[0]))
        coords.append(int(position[1:]) - 1)
        
        return tuple(coords) 

    def shoot(self, position):
        """ Shoot at position in board. Return report describing what happend. """
        coords = self.to_coords(position)

        # check if shooting is possible
        # continue if it is, or return if it's not
        if coords in self.possible_moves:
            self.possible_moves.remove(coords)
        else:
            return Report.NOT_VALID

        # cell is empty
        if self.board[position].is_empty():
            self.board[position].set_missed()
            return Report.MISSED
        # there is ship
        elif self.board[position].is_ship():
            # set board's cell to value -> destroyed
            self.board[position].set_destroyed()
            # get board's ship which position was hit
            ship = self.get_ship_by_coords(coords)
            # change ship state
            ship.hit()
            if ship.is_destroyed():
                # ship sank
                # block cells around destroyed ship
                for coords in ship:
                    pos = self.to_position(coords)
                    positions_list = self.get_near_possible_positions(pos, Direction.NONE, True)
                    for pos in positions_list:
                        coords = self.to_coords(pos)
                        self.possible_moves.remove(coords)
                        self.board[pos].set_missed()
                return Report.DESTROYED
            else:
                # ship is still floating
                return Report.HIT

    def print(self):
        """ Show board to user. """
        print(GRID.format(self.name, **self.board))


class Player_AI:

    def __init__(self):
        # possible positions that can be shot by ai if ship was hit
        self.possible_moves = set()
        # position that will be shot next
        self.shoot_pos = None
        # ship's position that was hit as first
        self.first_hit_pos = None
        # if True, ship is not completely destroyed
        self.hit_not_sank = False
        # direction of just hit ship
        self.ship_direction = Direction.NONE

    def get_shoot_position(self, board):
        """ Get position that AI will shoot next. """

        pos = None
        # there is ship that was hit but is not yet destroyed
        if self.hit_not_sank:
            # try to sink the ship that was hit
            if len(self.possible_moves) == 0:
                # get new possible positions based on first hit position
                self.possible_moves = \
                set(board.get_near_possible_positions(self.first_hit_pos, self.ship_direction))

            pos = random.choice(list(self.possible_moves))             
        else:
            # get random position from board
            pos = board.get_random_possible_position()

        self.shoot_pos = pos
        return pos

    def shoot(self, board):
        """ AI uses board's shoot method to shoot at previously saved position, and determines
            new positions to shoot. """
        # use board's method to shoot
        report = board.shoot(self.shoot_pos)
        
        # target was hit but not destroyed, AI will try to sink the ship next
        if report == Report.HIT:
            self.hit_not_sank = True
            # check if it's first hit or next
            if self.first_hit_pos == None:
                self.first_hit_pos = self.shoot_pos
            else:
                # we can determine ship's direction
                first_coords = board.to_coords(self.first_hit_pos)
                second_coords = board.to_coords(self.shoot_pos)
                self.ship_direction = Direction.what_direction(first_coords, second_coords)
            # get all possible positions that ship can have, it may be 0
            self.possible_moves = \
            set(board.get_near_possible_positions(self.shoot_pos, self.ship_direction))
        # target was destroyed, clear all variables
        elif report == Report.DESTROYED:
            self.possible_moves.clear()
            self.first_hit_pos = None
            self.hit_not_sank = False
            self.ship_direction = Direction.NONE
        # it's a miss -> remove this position from AI's possible moves
        elif report == Report.MISSED:
            if self.hit_not_sank:
                self.possible_moves.remove(self.shoot_pos)

        return report

        
def get_player_input():
    """ Function gets user position from standard input. """
    position = ''
    while len(position) < 2 or \
          position[0].upper() not in LETTERS or \
          not position[1:].isdigit() or \
          int(position[1:]) not in range(1, 11):
        print('Twoja tura:')
        position = input()

    return position.upper()


def print_report(report):
    """ Print what happend after shoot. """
    if report == Report.MISSED:
        print('Pudło.')
    elif report == Report.HIT:
        print('Trafiony!')
    elif report == Report.DESTROYED:
        print('Trafiony zatopiony!')


def suspension():
    """ Print loading animation. """
    time.sleep(0.5)
    print('.',end='')
    time.sleep(0.5)
    print('.',end='')
    time.sleep(0.5)
    print('.',end='')
    time.sleep(0.5)
    print()


def player_turn(board):
    """ Player types position and shoot. """

    # Repeat if report NOT_VALID
    report = Report.NOT_VALID
    while report == Report.NOT_VALID:
        pos = get_player_input()
        report = board.shoot(pos)
        
    suspension()
    print_report(report)
    time.sleep(1)

            
def ai_turn(board, ai, name = 'Tura przeciwnika'):
    """ Turn made by AI. Similar to player_turn() function. """
    print(name)
    pos = ai.get_shoot_position(board)
    suspension()
    print(pos)
    time.sleep(1)
    report = ai.shoot(board)
    print_report(report)
    time.sleep(1)


def print_boards(board1, board2):
    """ Prints two boards using boards' print function. """
    board1.print()
    board2.print()

    
def game_over(player_win):
    """ It's game over but player can choose to play again. """
    
    if player_win:
        print('Wygrałeś! ', end='')
    else:
        print('Przegrałeś! ', end='')
        
    print('Chcesz zagrać jeszcze raz (T/N)?: ')
    if input().upper().startswith('T'):
        return
    else:
        print('Dzięki za grę!')
        sys.exit()


def enemy_first():
    """ Decide if enemy's turn should be first. """
    return random.randint(0, 1)



while True:

    # new game
    player_board = Board('Twoje statki', hidden = False)
    enemy_board = Board('Statki przeciwnika', hidden = True)

    # player is replaced by ai
    if PLAYER_AI:
        player_ai = Player_AI()
        
    enemy_ai = Player_AI()

    # print boards
    print_boards(player_board, enemy_board)


    # determine if enemy should start turn first
    print('Losowanie zaczynającego pierwszą turę', end='')
    suspension()
    if enemy_first():
        print('Przeciwnik zaczyna')
        ai_turn(player_board, enemy_ai)
        print_boards(player_board, enemy_board)
    else:
        print('Gracz zaczyna')
        

    # main game loop
    while True:
        # player's turn - ai can be used as player
        if PLAYER_AI:
            ai_turn(enemy_board, player_ai, 'AI gracza')
        else:
            player_turn(enemy_board)

        # print boards
        print_boards(player_board, enemy_board)

        # check game over -> you win
        if enemy_board.are_all_ships_destroyed():
            game_over(player_win = True)
            break
        
        # enemy turn
        ai_turn(player_board, enemy_ai)

        # print boards
        print_boards(player_board, enemy_board)

        # check game over -> you lose
        if player_board.are_all_ships_destroyed():
            game_over(player_win = False)
            break

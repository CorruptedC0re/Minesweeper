import pygame
from random import randint
import pygame_menu
from typing import Any
from math import ceil
from datetime import datetime
from queue import Queue


#cell object, contains some valuable information
class Cell:

    def __init__(self):
        self.has_bomb = False
        self.clicked = False
        self.marked = False
        self.neighbor_bombs = 0
        self.empty_neighbours = []


def count_unclicked(field):
    counter = 0
    for row in range(len(field)):
        for col in range(len(field)):
            if not field[row][col].clicked:
                counter += 1
    return counter

def game():

    #working with the field, creating cell objects, putting bombs and defining neighbours
    global START_CELL
    field = [[Cell() for _ in range(CELLS_QUANTITY)] for _ in range(CELLS_QUANTITY)]

    running = True
    show_bombs = False
    first_click = True
    color_bombs = RED
    remained_to_click = CELLS_QUANTITY*CELLS_QUANTITY
    remained_bombs = BOMBS_QUANTITY
    start_time = datetime.now()

    clock = pygame.time.Clock()

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                START_CELL = None
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not show_bombs:
                process_clicking(pygame.mouse.get_pressed(), pygame.mouse.get_pos(), field, first_click)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                running = False
                START_CELL = None
                game()

            if event.type == LOSE_GAME_EVENT:
                show_bombs = True
                start_time = (datetime.now()-start_time).seconds

            if event.type == WIN_GAME_EVENT:
                remained_bombs = 0
                show_bombs = True
                start_time = (datetime.now() - start_time).seconds
                color_bombs = GREEN

            if event.type == SUCCESSFUL_CELL_CLICK_EVENT:
                remained_to_click = count_unclicked(field)-BOMBS_QUANTITY
                if remained_to_click == 0:
                    pygame.event.post(pygame.event.Event(WIN_GAME_EVENT))

            if event.type == MARK_CELL_EVENT:
                remained_bombs -= 1

            if event.type == UNMARK_CELL_EVENT:
                remained_bombs += 1

            if event.type == PUT_BOMBS_EVENT:
                first_click = False
                field = fill_field_with_bombs(field)

                for row in range(len(field)):
                    for col in range(len(field)):
                        define_neighbours_around(row, col, field)

                uncover_blank_cells(START_CELL)
                remained_to_click = count_unclicked(field)-BOMBS_QUANTITY
                if remained_to_click == 0:
                    pygame.event.post(pygame.event.Event(WIN_GAME_EVENT))

        draw_window(field, remained_bombs, show_bombs, color_bombs, start_time)


def draw_window(field, remained_bombs, show_bombs, color_bombs, start_time):

    WINDOW.fill(UNCLICKED_CELL_COLOR)

    start_x, start_y = 0, 0
    for row in range(len(field)):
        for col in range(len(field)):

            if field[row][col].has_bomb and show_bombs:
                pygame.draw.rect(WINDOW, color_bombs, (start_x, start_y, CELL_WIDTH, CELL_HEIGHT))

            if field[row][col].marked and not show_bombs:
                pygame.draw.rect(WINDOW, MARKED_CELL_COLOR, (start_x, start_y, CELL_WIDTH, CELL_HEIGHT))

            if field[row][col].clicked:
                pygame.draw.rect(WINDOW, CLICKED_CELL_COLOR, (start_x, start_y, CELL_WIDTH,
                                                                CELL_HEIGHT))
                if field[row][col].neighbor_bombs > 0:
                    quantity_font = AMOUNT_FONT.render(str(field[row][col].neighbor_bombs), True,
                                                       FONT_COLORS[field[row][col].neighbor_bombs])
                    WINDOW.blit(quantity_font, (start_x+(CELL_WIDTH//2)-quantity_font.get_width()//2,
                                start_y+(CELL_HEIGHT//2)-quantity_font.get_height()//2))

            pygame.draw.rect(WINDOW, BLACK, (start_x, start_y, CELL_WIDTH, CELL_HEIGHT), width=2)
            start_x += (CELL_WIDTH)
        start_x = 0
        start_y += (CELL_HEIGHT)

    bombs_font = INFO_FONT.render(f"Remained bombs: {remained_bombs}", True, BLACK)
    WINDOW.blit(bombs_font, (0, HEIGHT-(HEIGHT-WIDTH)+15))

    time_font = INFO_FONT.render(f"Elapsed time: {(datetime.now()-start_time).seconds if not show_bombs else start_time} s.", True, BLACK)
    WINDOW.blit(time_font, (0, HEIGHT - (HEIGHT - WIDTH) + 65))

    pygame.display.update()


#randomly putting bombs into the field
def fill_field_with_bombs(field):

    placed_bombs = 0
    while placed_bombs < BOMBS_QUANTITY:
        row = randint(0, CELLS_QUANTITY-1)
        col = randint(0, CELLS_QUANTITY-1)
        if not field[row][col].has_bomb and not field[row][col].clicked:
            field[row][col].has_bomb = True
            placed_bombs += 1

    return field


#How many neighbour cells have bombs
def define_neighbours_around(row, col, field):

    if not field[row][col].has_bomb:

        neighbours = []

        if row - 1 >= 0 and col - 1 >= 0:
            neighbours.append(field[row-1][col-1])

        if row - 1 >= 0:
            neighbours.append(field[row-1][col])

        if row - 1 >= 0 and col + 1 < len(field):
            neighbours.append(field[row-1][col+1])

        if col - 1 >= 0:
            neighbours.append(field[row][col-1])

        if col + 1 < len(field):
            neighbours.append(field[row][col+1])

        if row + 1 < len(field) and col - 1 >= 0:
            neighbours.append(field[row+1][col-1])

        if row + 1 < len(field):
            neighbours.append(field[row+1][col])

        if row + 1 < len(field) and col + 1 < len(field):
            neighbours.append(field[row+1][col+1])

        for neighbour in neighbours:
            if neighbour.has_bomb:
                field[row][col].neighbor_bombs += 1
            else:
                field[row][col].empty_neighbours.append(neighbour)


def process_clicking(pressed_buttons, mouse_pos, field, first_click):
    global START_CELL
    try:
        row = int(mouse_pos[1]//CELL_WIDTH)
        col = int(mouse_pos[0]//CELL_HEIGHT)

        cell = field[row][col]

        #if left mouse button clicked
        if pressed_buttons[0]:
            if not cell.marked and not cell.clicked:
                if not cell.has_bomb:
                    cell.clicked = True
                    pygame.event.post(pygame.event.Event(SUCCESSFUL_CELL_CLICK_EVENT))
                    if first_click:
                        pygame.event.post(pygame.event.Event(PUT_BOMBS_EVENT))
                        START_CELL = field[row][col]
                    else:
                        uncover_blank_cells(cell)
                    return
                pygame.event.post(pygame.event.Event(LOSE_GAME_EVENT))

        #if right mouse button clicked
        elif pressed_buttons[2]:
            if not cell.clicked:
                cell.marked = not cell.marked
                if cell.marked:
                    pygame.event.post(pygame.event.Event(MARK_CELL_EVENT))
                    return
                pygame.event.post(pygame.event.Event(UNMARK_CELL_EVENT))

    except IndexError:
        pass


def uncover_blank_cells(cell):

    q = Queue()
    q.put(cell)
    visited = set()

    while not q.empty():
        current = q.get()
        if not current.marked:
            current.clicked = True

            for neighbour in current.empty_neighbours:
                if neighbour in visited or neighbour.clicked:
                    visited.add(neighbour)
                    continue

                if neighbour.neighbor_bombs <= 2:
                    q.put(neighbour)
            visited.add(current)


def set_cells_number(value: Any) -> None:
    global CELLS_QUANTITY

    CELLS_QUANTITY = int(slider_size.get_value())


    if CELLS_QUANTITY*CELLS_QUANTITY-2 <= BOMBS_QUANTITY:
        slider_bombs.set_value(CELLS_QUANTITY*CELLS_QUANTITY-10)

    update_cell_size()


def set_bombs_number(value: Any) -> None:
    global BOMBS_QUANTITY

    BOMBS_QUANTITY = int(slider_bombs.get_value())

    if BOMBS_QUANTITY >= CELLS_QUANTITY*CELLS_QUANTITY-2:
        slider_bombs.set_value(CELLS_QUANTITY*CELLS_QUANTITY-10)


def update_cell_size():
    global CELL_WIDTH, CELL_HEIGHT
    CELL_WIDTH = WIDTH//CELLS_QUANTITY
    CELL_HEIGHT = (HEIGHT-(HEIGHT-WIDTH))//CELLS_QUANTITY


def exit_game():
    quit()


pygame.init()

FPS = 60
WIDTH = 900
HEIGHT = 1000
BLACK = (0, 0, 0)
UNCLICKED_CELL_COLOR = (219, 219, 219)
CLICKED_CELL_COLOR = (148, 148, 148)
MARKED_CELL_COLOR = (115, 87, 125)
FONT_COLORS = {1: (0, 255, 72), 2: (0, 255, 225), 3: (0, 55, 255),
               4: (221, 255, 0), 5: (255, 59, 0), 6: (127, 6, 6),
               7: (250, 0, 196), 8: (255, 170, 0)}
RED = (255, 0, 0)
GREEN = (0, 255, 0)
AMOUNT_FONT = pygame.font.SysFont("Times New Roman", 20, bold=True)
INFO_FONT = pygame.font.SysFont("Times New Roman", 32, bold=True)
CELLS_QUANTITY = 10
CELL_WIDTH = WIDTH//CELLS_QUANTITY
CELL_HEIGHT = (HEIGHT-(HEIGHT-WIDTH))//CELLS_QUANTITY
BOMBS_QUANTITY = 10

WIN_GAME_EVENT = pygame.USEREVENT + 1
LOSE_GAME_EVENT = pygame.USEREVENT + 2
SUCCESSFUL_CELL_CLICK_EVENT = pygame.USEREVENT + 3
MARK_CELL_EVENT = pygame.USEREVENT + 4
UNMARK_CELL_EVENT = pygame.USEREVENT + 5
PUT_BOMBS_EVENT = pygame.USEREVENT + 6
START_CELL = Cell()

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

Menu = pygame_menu.Menu("Minesweeper", WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_ORANGE)
slider_size = Menu.add.range_slider("Size", 10, (5,30), 1, value_format=lambda x: str(ceil(x)), onchange=set_cells_number)
slider_bombs = Menu.add.range_slider("Bombs", 10, (5,100), 1, value_format=lambda x: str(ceil(x)), onchange=set_bombs_number)
Menu.add.button("Play!", action=game)
Menu.add.button("Quit.", action=exit_game)

if __name__ == "__main__":

    try:
        Menu.mainloop(WINDOW)

    except pygame.error:
        pass

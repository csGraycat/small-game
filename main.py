'''
Import required libraries
'''
import sys

import pygame
import random
import time
import numpy as np
from icecream import ic
import math

'''
Initialize pygame
'''
pygame.init()

'''
Define the game constants
'''
ACTION_POINTS = 2
FIELD_WIDTH = 12
FIELD_HEIGHT = 6
SCREEN_WIDTH = FIELD_WIDTH * 100 + 300
SCREEN_HEIGHT = FIELD_HEIGHT * 100 + 100
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 167, 0)
GRAY = (140, 140, 140)
PLAYER_COLOR = [BLUE, RED, YELLOW]
PLAYER_COLOR_NAMES = ["BLUE", "RED", "YELLOW"]
PLAYER_COUNT = 3
CONTROLS = ["pass", "undo", "take", "put"]

SUDDEN_DEATH = 30

GRASS_COLOR = (0, 154, 23)  # light green
ROAD_COLOR = (201, 149, 89)  # brown
WOODS_COLOR = (56, 117, 58)  # dark green

SQUARE_COLORS = [0, GRASS_COLOR, ROAD_COLOR, WOODS_COLOR]
SQUARE_TYPES = ["base", "grass", "road", "woods"]

available_actions = ACTION_POINTS
player = [0 for i in range(PLAYER_COUNT)]
player_indexes = [i for i in range(PLAYER_COUNT)]
base = [0 for i in range(PLAYER_COUNT)]
base_points = [0 for i in range(PLAYER_COUNT)]
points_in_hand = [0 for i in range(PLAYER_COUNT)]
base_grid = [(0, 0) for i in range(PLAYER_COUNT)]
woods_counter = 0


def victory_screen(player):
    screen.fill(pygame.Color(WHITE), (FIELD_WIDTH * 100 / 2 - 150, FIELD_HEIGHT * 100 / 2 - 20, 400, 60))
    text_winner = text_to_show("winner", player, None)
    text_surface_winner = my_font.render(text_winner, False, BLACK)
    screen.blit(text_surface_winner, (FIELD_WIDTH * 100 / 2 - 150, FIELD_HEIGHT * 100 / 2 - 20))
    text_any_button = text_to_show("any button", None, None)
    text_surface_button = my_font.render(text_any_button, False, BLACK)
    screen.blit(text_surface_button, (FIELD_WIDTH * 100 / 2 - 150, FIELD_HEIGHT * 100 / 2 + 10))
    pygame.display.flip()
    pygame.event.clear()
    while True:
        pygame.display.flip()
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            pygame.quit()
            sys.exit()


def choose_target(players_to_fight):
    global check_battle, selected_player
    text_surface_target = my_font.render("Choose target (SPACE to confirm)", False,
                                         BLACK)
    screen.blit(text_surface_target, (SCREEN_WIDTH - 300, 300))
    i = 0
    if players_to_fight:
        draw_player_selector(players_to_fight[0].index)
    choose_target = True

    while choose_target:
        pygame.display.flip()
        pygame.event.clear()
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and i < len(players_to_fight) - 1:
                i += 1
                draw_player_selector(players_to_fight[i].index)
                pygame.display.flip()
            elif event.key == pygame.K_LEFT and i > 0:
                i -= 1
                draw_player_selector(players_to_fight[i].index)
                pygame.display.flip()
            elif event.key == pygame.K_SPACE:
                if move_cycles < SUDDEN_DEATH:
                    check_battle = handle_fight(game.players[selected_player], players_to_fight[i], False)
                    choose_target = False
                elif move_cycles >= SUDDEN_DEATH:
                    check_battle = handle_fight(game.players[selected_player], players_to_fight[i], True)
                    choose_target = False


def sudden_death():
    global players_total
    global thief_count
    global selected_player
    screen.fill(pygame.Color(WHITE), (FIELD_WIDTH * 100 / 2 - 50, FIELD_HEIGHT * 100 / 2 - 20, 125, 30))
    text_sudden_death = "Sudden death!"
    text_surface_sd = my_font.render(text_sudden_death, False, BLACK)
    screen.blit(text_surface_sd, (FIELD_WIDTH * 100 / 2 - 50, FIELD_HEIGHT * 100 / 2 - 20))
    pygame.display.flip()
    time.sleep(2)
    for i in range(PLAYER_COUNT):
        points_in_hand[i] = 0
    for player in game.players:
        if player.index >= PLAYER_COUNT:
            ic("thieves", player.index)
            player.grid = (FIELD_WIDTH, FIELD_HEIGHT)
        else:
            ic("players", player.index)
            player.grid = game.bases[player.index].grid
    check_collisions()
    for i in range(PLAYER_COUNT, players_total):  # remove thieves
        game.players.pop(PLAYER_COUNT)
        ic(game.players)
    players_total = PLAYER_COUNT
    thief_count = 0
    game.draw(False)
    pygame.display.flip()
    min_base_points = 20

    for player in game.players:  # first turn
        player.active = True
        if min_base_points > game.bases[player.index].points > 0:
            selected_player = player.index
            ic(selected_player)
            min_base_points = game.bases[player.index].points
    game.players[selected_player].selected = True

    players_to_fight_sd = []  # sd = sudden death
    players_remaining_sd = []
    for player in game.players:
        if game.bases[player.index].points > 0:
            players_remaining_sd.append(player)
        else:
            player.active = False
    ic(players_remaining_sd)
    while len(players_remaining_sd) > 1:
        game.draw(True)
        pygame.display.flip()
        players_to_fight_sd.clear()
        for player in game.players:
            if game.bases[player.index].points > 0 and not player.selected:
                players_to_fight_sd.append(player)
        choose_target(players_to_fight_sd)
        players_remaining_sd.clear()
        for player in game.players:
            if game.bases[player.index].points > 0:
                players_remaining_sd.append(player)
            else:
                player.active = False
            ic(player.active)
        game.draw(True)
        pygame.display.flip()
        ic(players_remaining_sd)
        game.players[selected_player].selected = False  # pass turn to next active player
        next_player = selected_player + 1
        selected_player = next_active_player(next_player, True)
        if selected_player == PLAYER_COUNT:
            next_player = 0
            selected_player = next_active_player(next_player, True)
        game.players[selected_player].selected = True
    for player in game.players:
        if player.active == True:
            victory_screen(player)



def battle_end(win_player, lose_player):
    stolen_points = 0
    if lose_player.grid == game.bases[win_player.index].grid:
        lose_player.grid = game.bases[lose_player.index].grid
        while points_in_hand[lose_player.index] > 0 and game.bases[win_player.index].points < 20:
            points_in_hand[lose_player.index] -= 1
            stolen_points += 1
            game.bases[win_player.index].points += 1
    elif lose_player.grid == game.bases[lose_player.index].grid:
        while game.bases[lose_player.index].points > 0 and points_in_hand[win_player.index] < 5:
            game.bases[lose_player.index].points -= 1
            stolen_points += 1
            points_in_hand[win_player.index] += 1
    else:
        while points_in_hand[lose_player.index] > 0 and points_in_hand[win_player.index] < 5:
            points_in_hand[lose_player.index] -= 1
            stolen_points += 1
            points_in_hand[win_player.index] += 1
    return stolen_points


def handle_fight(first_player, second_player, sudden_death: bool):
    global max_attack
    global points_lost
    attacking_player = first_player
    defending_player = second_player
    players_fighting = [attacking_player, defending_player]
    for player in players_fighting:
        player.health = 30
    if defending_player.grid == game.bases[defending_player.index].grid and sudden_death == False:
        defending_player.health += 5
    ic(attacking_player.index, defending_player.index)
    show_hp(players_fighting)
    time.sleep(1)
    max_attack = 15
    points_lost = 0
    while attacking_player.health > 0 and defending_player.health > 0:

        if sudden_death:
            max_attack = game.bases[attacking_player.index].points
        attack(attacking_player, defending_player, players_fighting, max_attack)
        if defending_player.health <= 0 and not sudden_death:
            stolen_points = battle_end(attacking_player, defending_player)
            victory_text(attacking_player, defending_player, stolen_points)
            time.sleep(3.5)
            defending_player.active = False
            check_collisions()
            return False
        if defending_player.health <= 0 and sudden_death:
            while game.bases[defending_player.index].points > 0 and points_lost < 5:
                game.bases[defending_player.index].points -= 1
                points_lost += 1
            victory_text_sd(attacking_player, defending_player, points_lost)
            time.sleep(3.5)
            screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 300, 300, 100))
            return False

        if sudden_death:
            max_attack = game.bases[defending_player.index].points
        attack(defending_player, attacking_player, players_fighting, max_attack)
        if attacking_player.health <= 0 and not sudden_death:
            stolen_points = battle_end(defending_player, attacking_player)
            victory_text(defending_player, attacking_player, stolen_points)
            time.sleep(3.5)
            attacking_player.active = False
            check_collisions()
            return False
        if attacking_player.health <= 0 and sudden_death:
            while game.bases[attacking_player.index].points > 0 and points_lost < 5:
                game.bases[attacking_player.index].points -= 1
                points_lost += 1
            victory_text_sd(defending_player, attacking_player, points_lost)
            time.sleep(3.5)
            screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 300, 300, 100))
            return False


def draw_player_selector(player_index):
    screen.fill(pygame.Color(WHITE),
                (0, FIELD_HEIGHT * 100 + 40, FIELD_WIDTH * 100, SCREEN_HEIGHT - FIELD_HEIGHT * 100 + 40))
    pygame.draw.polygon(screen, BLACK, (
        (50 + player_index * 300, FIELD_HEIGHT * 100 + 80), (100 + player_index * 300, FIELD_HEIGHT * 100 + 40),
        (150 + player_index * 300, FIELD_HEIGHT * 100 + 80)))


def next_active_player(next_player, sudden_death: bool):
    if next_player == PLAYER_COUNT:
        return PLAYER_COUNT
    else:
        if not sudden_death:
            for i in range(next_player, PLAYER_COUNT):
                if game.players[i].active:
                    return i
                else:
                    if not delayed_active[next_player]:
                        ic(delayed_active)
                        delayed_active[next_player] = True
                        ic(delayed_active)
                        check_collisions()
                        pygame.display.flip()
                        return next_active_player(i + 1, False)
                    elif delayed_active[next_player]:
                        ic("else", delayed_active)
                        game.players[next_player].active = True
                        delayed_active[next_player] = False
                        return i
        if sudden_death:
            for i in range(next_player, PLAYER_COUNT):
                if game.players[i].active:
                    return i
                else:
                    return next_active_player(i + 1, True)

def show_hp(players_fighting):
    screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 300, 300, 90))
    i = 0
    for player in players_fighting:
        text_health = ("Player " + PLAYER_COLOR_NAMES[player.index] + " has " + str(
            player.health) + "HP")
        text_surface_health = my_font.render(text_health, False, BLACK)
        screen.blit(text_surface_health, (SCREEN_WIDTH - 300, 300 + i * 30))
        pygame.display.flip()
        i += 1


def player_grid_to_coord(grid):
    return grid[0] * 100 + 50, grid[1] * 100 + 50


def player_coord_to_grid(x, y):
    return int(0.01 * (x - 50)), int(0.01 * (y - 50))


def cursor_grid_to_coord(grid):
    return grid[0] * 100 + 10, grid[1] * 100 + 10


def cursor_coord_to_grid(x, y):
    return int(0.01 * (x - 10)), int(0.01 * (y - 10))


def check_collisions():
    for player in game.players:
        player.x, player.y = player_grid_to_coord(player.grid)
    same_grid = []
    for i in range(PLAYER_COUNT - 1 + thief_count):  # check for collisions (must include thief)
        for j in range(i + 1, players_total):
            if game.players[i].grid == game.players[j].grid:
                same_grid.append(game.players[i].grid)
                same_grid = list(set(same_grid))
    ic(same_grid)
    for grid in same_grid:
        ic(grid)
        players_same_grid = []
        for player in game.players:
            if player.grid == grid:
                players_same_grid.append(player)
        ic(players_same_grid)
        i = 0
        for player in players_same_grid:
            player.x = \
                player_grid_to_coord(player.grid)[0] + 30 * math.cos(
                    2 * i * math.pi / len(players_same_grid) + math.pi / 4)
            player.y = \
                player_grid_to_coord(player.grid)[1] + 30 * math.sin(
                    2 * i * math.pi / len(players_same_grid) + math.pi / 4)
            i += 1
    game.draw(False)
    pygame.display.flip()


def check_thieves():
    players_to_steal_from = []
    thief_stealing = 0
    for i in range(PLAYER_COUNT):
        for j in range(PLAYER_COUNT, PLAYER_COUNT + thief_count):
            if game.players[i].grid == game.players[j].grid and game.players[j].active and game.players[i].active and \
                    points_in_hand[i] > 0:
                players_to_steal_from.append(i)
                thief_stealing = j
    if players_to_steal_from:
        ic(players_to_steal_from)
        i = random.choice(players_to_steal_from)
        print("Thief has stolen points from", str(PLAYER_COLOR_NAMES[i]))
        text_player_lost_points = ("-" + str(points_in_hand[i]))
        player_surface_points = my_font.render(text_player_lost_points, False, (0, 0, 0))
        screen.blit(player_surface_points, player_grid_to_coord(game.players[i].grid))
        pygame.display.flip()
        game.players[thief_stealing].active = False
        ic(thief_stealing)
        points_in_hand[i] = 0
        time.sleep(0.5)


def update_woods():
    woods_counter = 0
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if mat[i][j] == 3:
                woods_counter += 1
    if woods_counter < 5:
        for i in range(FIELD_WIDTH):
            for j in range(FIELD_HEIGHT):
                tree_growth_chance = random.randint(1, 40)
                if tree_growth_chance == 1 and mat[i][j] == 1:
                    mat[i][j] = 3


def text_to_show(param, player_win, player_lose):
    if param == "actions":
        return "Player " + str(PLAYER_COLOR_NAMES[selected_player]) + " has " + str(
            available_actions) + " actions left "
    elif param == "points":
        return "Player " + str(PLAYER_COLOR_NAMES[selected_player]) + " holds " + str(
            points_in_hand[selected_player]) + "/5 points "
    elif param == "controls":
        text = ["<Space>  - end turn", "<Z>  - undo turn", "<E>  - steal points", "<F>  - put points"]
        return text
    elif param == "points all":
        text = []
        for i in range(PLAYER_COUNT):
            text.append("Player " + str(PLAYER_COLOR_NAMES[i]) + " holds " + str(
                points_in_hand[i]) + "/5 points ")
        return text
    elif param == "cycle counter":
        return "Cycle counter: " + str(move_cycles)
    elif param == "sudden death counter":
        return "Until sudden death: " + str(SUDDEN_DEATH - move_cycles)
    elif param == "winner":
        return "Player " + PLAYER_COLOR_NAMES[player_win.index] + " is the winner. Congratulations!"
    elif param == "any button":
        return "Press any button to exit"


def victory_text(player_win, player_lose, stolen_points):
    screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 300, 300, 100))
    text_surface_player_victory = my_font.render(
        "Player " + PLAYER_COLOR_NAMES[player_win.index] + " has won", False, BLACK)
    screen.blit(text_surface_player_victory, (SCREEN_WIDTH - 300, 300))
    text_surface_defender_victory_points = my_font.render("and took " + \
                                                          str(stolen_points) + " points from " +
                                                          PLAYER_COLOR_NAMES[player_lose.index], False, BLACK)
    screen.blit(text_surface_defender_victory_points, (SCREEN_WIDTH - 300, 340))
    pygame.display.flip()


def victory_text_sd(player_win, player_lose, points_lost):
    screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 300, 300, 100))
    text_surface_player_victory = my_font.render(
        PLAYER_COLOR_NAMES[player_win.index] + " has won", False, BLACK)
    screen.blit(text_surface_player_victory, (SCREEN_WIDTH - 300, 300))
    text_surface_lost_points = my_font.render(
        PLAYER_COLOR_NAMES[player_lose.index] + " lost " + str(points_lost) + " points from base", False,
        BLACK)
    screen.blit(text_surface_lost_points, (SCREEN_WIDTH - 300, 340))
    pygame.display.flip()


'''
Create the game window
'''
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

'''
Setup field
'''
mat = np.empty((FIELD_WIDTH, FIELD_HEIGHT), dtype=int)  # define empty matrix
while woods_counter > 20 or woods_counter < 10:
    woods_counter = 0
    for i in range(FIELD_WIDTH):  # assign all elements random number
        for j in range(FIELD_HEIGHT):
            mat[i][j] = random.randint(1, 3)
            if mat[i][j] == 3:
                woods_counter += 1
    ic(woods_counter)

'''
Define the Player class
'''


class Player:

    def __init__(self, x, y, color, index):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 30
        self.selected = False
        self.points = 0
        self.grid = (int(0.01 * (self.x - 50)), int(0.01 * (self.y - 50)))
        self.active = True
        self.health = 30
        self.index = index
        self.is_attacking = False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, width=1)
        if self.index < PLAYER_COUNT:
            text_player_points = (str(points_in_hand[self.index]))
            text_surface_player_points = my_font.render(text_player_points, False, (0, 0, 0))
            screen.blit(text_surface_player_points, (
                self.x - 10,
                self.y - 10))
        if not self.active:
            pygame.draw.line(screen, BLACK, (
                self.x - self.radius * math.cos(math.pi / 4), self.y + self.radius * math.cos(math.pi / 4)), (
                                 self.x + self.radius * math.cos(math.pi / 4),
                                 self.y - self.radius * math.cos(math.pi / 4)))

    def offset(self, dx, dy):
        self.x += dx
        self.y += dy

    def position(self):
        return self.x, self.y

    def square_number_i(self):
        return int((self.x - 50) / 100)

    def square_number_j(self):
        return int((self.y - 50) / 100)


def attack(player_attacking: Player, player_being_attacked: Player, players_fighting, max_attack):
    if player_attacking.health > 0 and player_being_attacked.health > 0:
        attack_roll = random.randint(1, max_attack)
        player_being_attacked.health -= attack_roll
        show_hp(players_fighting)
        time.sleep(1)


def ai_turn(entity: Player):
    time.sleep(0.3)
    ic("ai grid", entity.grid)
    check_collisions()
    check_thieves()
    for i in range(4):
        entity.x, entity.y = player_grid_to_coord(entity.grid)
        if entity.active:
            random_move = random.randint(0, 3)
            ic(random_move)
            if random_move == 0:
                entity.x += 100
                if entity.x > FIELD_WIDTH * 100:
                    entity.x = 50
            if random_move == 1:
                entity.y += 100
                if entity.y > FIELD_HEIGHT * 100:
                    entity.y = 50
            if random_move == 2:
                entity.x -= 100
                if entity.x < 0:
                    entity.x = FIELD_WIDTH * 100 - 50
            if random_move == 3:
                entity.y -= 100
                if entity.y < 0:
                    entity.y = FIELD_HEIGHT * 100 - 50
            entity.grid = player_coord_to_grid(entity.x, entity.y)
            ic("ai grid", entity.grid)
            check_collisions()
            check_thieves()
            game.draw(False)
            pygame.display.flip()
            time.sleep(0.3)


'''
Define the Cursor class
'''


class Cursor:
    def __init__(self):
        self.players = []
        self.x = 10
        self.y = 10
        self.color = ORANGE
        self.grid = (int(0.01 * (self.x - 10)), int(0.01 * (self.y - 10)))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def add_player(self, player):
        self.players.append(player)

    def draw(self):
        for player in self.players:
            if player.selected:
                pygame.draw.rect(screen, self.color, [self.x, self.y, 80, 80], 2)

    def square_number_i(self):
        return int((self.x + 40) / 100)

    def square_number_j(self):
        return int((self.y + 40) / 100)


'''
Define the Base class
'''


class Base:
    def __init__(self, x, y, color, index):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.points = 0
        self.grid = (int(0.01 * self.x), int(0.01 * self.y))
        self.index = index

    def show_points(self):
        return str(self.points)

    def draw(self):
        pygame.draw.rect(screen, self.color, [self.x, self.y, 100, 100])
        text_base_points = my_font.render(self.show_points(), False, (0, 0, 0))
        screen.blit(text_base_points, (self.x, self.y))


'''
Define the Game class
'''


class Game:
    def __init__(self):
        self.players = []
        self.bases = []

    def add_player(self, player):
        self.players.append(player)

    def add_base(self, base):
        self.bases.append(base)

    def move_cursor(self, dx, dy):
        for player in self.players:
            if player.selected:
                cursor.move(dx, dy)

    def get_cursor_square(self):
        for player in self.players:
            if player.selected:
                square_type = mat[cursor.grid[0]][cursor.grid[1]]
                return SQUARE_TYPES[square_type]

    def pass_turn(self, next_player_number):
        if next_player_number == 0:
            self.players[next_player_number].selected = True
            self.players[PLAYER_COUNT - 1].selected = False
        else:
            self.players[next_player_number - 1].selected = False
            self.players[next_player_number].selected = True

    def draw(self, sudden_death: bool):
        screen.fill(WHITE)
        for i in range(FIELD_WIDTH):  # draw field
            for j in range(FIELD_HEIGHT):
                if mat[i][j] == 1 or mat[i][j] == 2 or mat[i][j] == 3:
                    square_position = (100 * i, 100 * j)
                    pygame.draw.rect(screen, SQUARE_COLORS[mat[i][j]], (square_position, (100, 100)))
                    # pygame.draw.rect(screen, BLACK, (square_position, (100, 100)), width=1)

        for base in self.bases:
            base.draw()
            text_base_points = my_font.render(base.show_points(), False, (0, 0, 0))
            screen.blit(text_base_points, (base.x, base.y))
        for player in self.players:
            player.draw()
        for i in range(len(CONTROLS)):
            text_surface_controls = my_font.render(text_to_show("controls", None, None)[i], False, (0, 0, 0))
            screen.blit(text_surface_controls, (SCREEN_WIDTH - 300, 450 + i * 30))

        if not sudden_death:
            if selected_player < PLAYER_COUNT:
                text_surface_actions = my_font.render(text_to_show("actions", None, None), False, (0, 0, 0))
                screen.blit(text_surface_actions, (SCREEN_WIDTH - 300, 100))
                text_surface_points = my_font.render(text_to_show("points", None, None), False, (0, 0, 0))
                screen.blit(text_surface_points, (SCREEN_WIDTH - 300, 140))

        if sudden_death:
            screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 250, 300, 40))
            text_turn_sd = PLAYER_COLOR_NAMES[game.players[selected_player].index]
            text_surface_turn_sd = my_font.render(text_turn_sd, False, BLACK)
            screen.blit(text_surface_turn_sd, (SCREEN_WIDTH - 300, 250))

        for i in range(PLAYER_COUNT):
            text_surface_points_all = my_font.render(text_to_show("points all", None, None)[i], False, (0, 0, 0))
            screen.blit(text_surface_points_all, (10 + i * 300, FIELD_HEIGHT * 100))

        text_surface_cycles = my_font.render(text_to_show("sudden death counter", None, None), False, (0, 0, 0))
        screen.blit(text_surface_cycles, (FIELD_WIDTH * 100, FIELD_HEIGHT * 100))

    def save_state(self, player, actions, base_points, player_points, stepped_on_road):
        return player, actions, base_points, player_points, stepped_on_road

    def handle_roads(self, grid, counter):
        if mat[grid[0]][grid[1]] == 2:
            counter += 1
            return True, counter
        else:
            return False, counter

    def cursor_movement(self, actions):
        if event.key == pygame.K_LEFT:
            game.move_cursor(-100, 0)
            if cursor.x < 0:
                cursor.x = FIELD_WIDTH * 100 - 90
            actions -= 1
        elif event.key == pygame.K_RIGHT:
            game.move_cursor(100, 0)
            if cursor.x > FIELD_WIDTH * 100:
                cursor.x = 10
            actions -= 1
        elif event.key == pygame.K_UP:
            game.move_cursor(0, -100)
            if cursor.y < 0:
                cursor.y = FIELD_HEIGHT * 100 - 90
            actions -= 1
        elif event.key == pygame.K_DOWN:
            game.move_cursor(0, 100)
            if cursor.y > FIELD_HEIGHT * 100:
                cursor.y = 10
            actions -= 1
        return actions


'''
Create an instance of the Game and Cursor classes
'''
game = Game()
cursor = Cursor()

'''
Handle different player count
'''
if PLAYER_COUNT == 2:
    mat[1][2] = 0
    base_grid[0] = (1, 2)
    mat[9][2] = 0
    base_grid[1] = (9, 2)
    thief_count = 1

elif PLAYER_COUNT == 3:
    mat[1][2] = 0
    base_grid[0] = (1, 2)
    mat[5][2] = 0
    base_grid[1] = (5, 2)
    mat[9][2] = 0
    base_grid[2] = (9, 2)
    thief_count = 2

thief_grid = []
players_total = PLAYER_COUNT + thief_count

'''
Add players, thieves and bases (based on player count)
'''
for i in range(PLAYER_COUNT):
    player[i] = Player(base_grid[i][0] * 100 + 50, base_grid[i][1] * 100 + 50, PLAYER_COLOR[i], i)
    base[i] = Base(base_grid[i][0] * 100, base_grid[i][1] * 100, PLAYER_COLOR[i], i)
    game.add_base(base[i])
    game.add_player(player[i])
    cursor.add_player(player[i])
    base[i].points = 0
    base_points[i] = base[i].points

for i in range(thief_count):
    thief_grid.append((base_grid[i][0] + 2, base_grid[i][1] + 2))
    thief = Player(player_grid_to_coord(thief_grid[i])[0], player_grid_to_coord(thief_grid[i])[1], GRAY,
                   PLAYER_COUNT + i)
    game.add_player(thief)

'''
Game loop
'''
running = True
clock = pygame.time.Clock()

stepped_on_road = False
selected_player = 0
player[selected_player].selected = True
cursor.x = player[selected_player].x - 40
cursor.y = player[selected_player].y - 40
cursor.grid = cursor_coord_to_grid(cursor.x, cursor.y)

print(game.get_cursor_square())
print("actions left =", available_actions)

my_font = pygame.font.SysFont('Calibri', 20)

saved_state = game.save_state(selected_player, available_actions, base_points,
                              points_in_hand[selected_player], stepped_on_road)
ic(saved_state)

move_cycles = 0
delayed_active = [False for i in range(PLAYER_COUNT)]
ic(delayed_active)

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if available_actions > 0:  # movement
                available_actions = game.cursor_movement(available_actions)
            cursor.grid = cursor_coord_to_grid(cursor.x, cursor.y)

            if not stepped_on_road:  # road handling
                stepped_on_road, available_actions = game.handle_roads(cursor.grid, available_actions)

            if event.key == pygame.K_SPACE:  # end turn
                check_collisions()
                for player in game.players:
                    if player.index < PLAYER_COUNT and game.bases[player.index].points == 20:
                        victory_screen(player)

                for player in game.players:
                    if player.selected:  # move player to cursor
                        player.grid = cursor.grid
                        player.x, player.y = player_grid_to_coord(player.grid)
                        game.draw(False)
                        pygame.display.flip()

                if game.get_cursor_square() == "woods":  # wood collecting
                    check_collisions()
                    points_found = 0
                    points_found_max = random.randint(1, 3)
                    if points_in_hand[selected_player] < 5:
                        mat[cursor.grid[0]][cursor.grid[1]] = 1
                        while points_found < points_found_max and points_in_hand[selected_player] < 5:
                            points_in_hand[selected_player] += 1
                            points_found += 1

                        screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 140, 300, 40))
                        text_surface_points = my_font.render(text_to_show("points", None, None), False, (0, 0, 0))
                        screen.blit(text_surface_points, (SCREEN_WIDTH - 300, 140))
                        text_player_found_points = ("+" + str(points_found))
                        text_player_points = my_font.render(text_player_found_points, False, (0, 0, 0))
                        screen.blit(text_player_points, (game.players[selected_player].x + 3, game.players[selected_player].y - 10))
                        pygame.display.flip()
                        time.sleep(0.5)

                check_collisions()
                check_thieves()

                players_to_fight = []  # handle fights
                for i in range(PLAYER_COUNT):
                    if game.players[selected_player].grid == game.players[i].grid and selected_player != i and \
                            game.players[i].active:
                        players_to_fight.append(game.players[i])
                        ic(players_to_fight)
                if players_to_fight:
                    text_surface_battle = my_font.render("Initiate battle? (y/n)", False, BLACK)
                    screen.blit(text_surface_battle, (SCREEN_WIDTH - 290, 300))
                    check_battle = True
                    pygame.event.clear()
                    while check_battle:
                        pygame.event.clear()
                        pygame.display.flip()
                        event = pygame.event.wait()
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_y:
                                screen.fill(pygame.Color(WHITE), (SCREEN_WIDTH - 300, 300, 300, 40))
                                if len(players_to_fight) > 1:
                                    choose_target(players_to_fight)
                                else:
                                    check_battle = handle_fight(game.players[selected_player], players_to_fight[0],
                                                                False)
                            elif event.key == pygame.K_n:
                                check_battle = False

                game.players[selected_player].selected = False  # pass turn to next active player
                next_player = selected_player + 1

                selected_player = next_active_player(next_player, False)
                ic(selected_player)

                if selected_player == PLAYER_COUNT:  # end of move cycle
                    for i in range(PLAYER_COUNT, players_total):  # thieves' turn
                        game.players[i].active = True
                        ai_turn(game.players[i])
                    move_cycles += 1
                    if move_cycles == SUDDEN_DEATH:
                        sudden_death()
                        ic(players_total)
                        ic(thief_count)
                    check_collisions()
                    check_thieves()
                    update_woods()
                    next_player = 0
                    selected_player = next_active_player(next_player, False)

                game.players[selected_player].selected = True
                ic(selected_player)

                cursor.grid = game.players[selected_player].grid
                ic(cursor.grid)
                cursor.x, cursor.y = cursor_grid_to_coord(cursor.grid)
                ic(cursor.x, cursor.y)
                available_actions = ACTION_POINTS
                stepped_on_road = False
                if not stepped_on_road:  # road handling
                    stepped_on_road, available_actions = game.handle_roads(cursor.grid, available_actions)
                for i in range(PLAYER_COUNT):
                    base_points[i] = game.bases[i].points
                saved_state = game.save_state(selected_player, available_actions, base_points,
                                              points_in_hand[selected_player], stepped_on_road)
                ic(saved_state)

            elif event.key == pygame.K_z:  # undo
                selected_player = saved_state[0]
                available_actions = saved_state[1]
                for i in range(PLAYER_COUNT):
                    game.bases[i].points = saved_state[2][i]
                points_in_hand[selected_player] = saved_state[3]
                stepped_on_road = saved_state[4]
                for player in cursor.players:
                    if player.selected:
                        cursor.x, cursor.y = cursor_grid_to_coord(player.grid)

            elif event.key == pygame.K_e:  # take points
                if available_actions > 0 and points_in_hand[selected_player] < 5:
                    if game.get_cursor_square() == "base":  # steal points from bases
                        for base in game.bases:
                            if cursor.grid == base.grid and base.points > 0 and game.players[base.index].grid != base.grid:
                                available_actions -= 1
                                while base.points > 0 and points_in_hand[selected_player] < 5:
                                    base.points -= 1
                                    points_in_hand[selected_player] += 1

            elif event.key == pygame.K_f:  # put points
                enemy_in_base = False
                for base in game.bases:
                    if cursor.grid == base.grid:
                        for i in range(players_total):
                            if base.grid == game.players[i].grid and i != selected_player and game.players[i].active == True:
                                enemy_in_base = True
                        if not enemy_in_base and available_actions > 0 and points_in_hand[selected_player] > 0:
                            available_actions -= 1
                            while base.points < 20 and points_in_hand[selected_player] > 0:
                                base.points += 1
                                points_in_hand[selected_player] -= 1

            cursor.grid = cursor_coord_to_grid(cursor.x, cursor.y)
            print(game.get_cursor_square())
            print("actions left =", available_actions)

    game.draw(False)
    cursor.draw()
    pygame.display.flip()
'''
Quit the game
'''
pygame.quit()

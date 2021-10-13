import pygame
import os
import random
import pygame_textinput
import pygame_gui
import pandas as pd
import webbrowser

pygame.font.init()

WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Evaders")

RED_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_blue_small.png"))

PLAYER_SHIP = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "pixel_ship2.png")), (100, 90))
PLAYER_SHIP_SHIELD = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "ship_shield.png")), (100, 90))

WIN_MARK = pygame.image.load(
    os.path.join("assets", "boss_icon.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))

BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
HEAL = pygame.image.load(
    os.path.join("assets", "heal.png"))
SHIELD = pygame.image.load(
    os.path.join("assets", "shield.png"))
LEADERBOARD = './ldb.csv'
F_PATH = './assets/super-legend-boy.otf'

BLACK_BG = pygame.Surface((WIDTH, HEIGHT))
BLACK_BG.fill(pygame.Color('#000000'))

MAIN_BLUE = (7, 235, 197)
MAIN_PINK = (235, 107, 205)
MAIN_GREEN = (0, 201, 56)
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.decrease_health()
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Player(Ship):
    def __init__(self, x, y, name, health=100):
        super().__init__(x, y, health)
        self.player_name = name
        self.ship_img = PLAYER_SHIP
        self.laser_img = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.health = health
        self.score = 0
        self.lives = 3
        self.armor = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if obj.ship_img == GREEN_SPACE_SHIP:
                            self.score += 50
                        elif obj.ship_img == BLUE_SPACE_SHIP:
                            self.score += 75
                        elif obj.ship_img == RED_SPACE_SHIP:
                            self.score += 100
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        if self.armor > 0:
            self.ship_img = PLAYER_SHIP_SHIELD
        else:
            self.ship_img = PLAYER_SHIP
        super().draw(window)

    def absorb_buff(self, TYPE):
        self.score += 150
        if TYPE == 'HEAL':
            if self.health + 20 > 100:
                self.health = 100
            else:
                self.health += 20

        elif TYPE == 'SHIELD':
            self.armor = 100

    def decrease_health(self):
        if self.armor > 0:
            self.armor -= 10

        else:
            self.health -= 20

        if self.health <= 0:
            if self.lives > 0:
                self.lives -= 1
                self.health = 100

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y - 45, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, YELLOW_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move_y(self, vel):
        self.y += vel

    def move_x(self, vel):
        self.x += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Buff:
    def __init__(self):
        self.type = random.choice(['HEAL', 'SHIELD'])
        self.img = HEAL if self.type == 'HEAL' else SHIELD
        self.mask = pygame.mask.from_surface(self.img)
        self.x = random.randint(100, 800)
        self.y = 50

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))


def dp_blit(main_bg, alt_bg, labels):
    if main_bg:
        WIN.blit(BG, (0, 0))
    elif alt_bg:
        WIN.blit(alt_bg, (0, 0))
    for label in labels:
        WIN.blit(label[0], label[1])


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def redraw_window(level, name, player, enemies, buffs, main_font):
    WIN.blit(BG, (0, 0))
    lives_label = main_font.render(f"Lives: {player.lives}", 1, MAIN_BLUE)
    level_label = main_font.render(f"Level: {level}", 1, MAIN_BLUE)
    player_name = main_font.render(f"Name: {name}", 1, MAIN_PINK)
    player_score = main_font.render(f"Score: {player.score}", 1, MAIN_PINK)
    player_health = main_font.render(f"Health: {player.health}", 1, MAIN_PINK)
    if player.armor > 0:
        armor_label = main_font.render(f"Shield: {player.armor}", 1, MAIN_GREEN)
        WIN.blit(armor_label, (WIDTH / 2 - armor_label.get_width() / 2, 850))
    WIN.blit(lives_label, (10, 10))
    WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
    WIN.blit(player_name, (WIDTH / 2 - player_name.get_width() / 2, 10))
    WIN.blit(player_score, (10, 850))
    WIN.blit(player_health, (WIDTH - player_health.get_width() - 10, 850))
    for enemy in enemies:
        enemy.draw(WIN)
    for buff in buffs:
        buff.draw(WIN)
    player.draw(WIN)
    pygame.display.update()


def spawn_enemies():
    colors = ["red", "blue", "green"]
    list = []
    for i in range(30, WIDTH - 40, 70):
        enemy = Enemy(i, 30, colors[0])
        list.append(enemy)
    for i in range(30, WIDTH - 40, 70):
        enemy = Enemy(i, 100, colors[1])
        list.append(enemy)
    for i in range(30, WIDTH - 40, 70):
        enemy = Enemy(i, 170, colors[2])
        list.append(enemy)
    return list

def game():
    name, run = new_game()
    if name == "" or all(x == " " for x in name):
        name = 'Unknown'
    FPS = 60
    level = 0
    main_font = pygame.font.Font(F_PATH, 30)
    player = Player(400, 650, name)
    player_vel = 5
    enemies = []
    enemy_vel_y = 1
    enemy_move_period = FPS / 2
    enemy_move_counter = 0

    laser_vel_player = 5
    laser_vel_enemy = 2
    win = False
    diff = 20
    buff_cooldown = 600
    buff_counter = buff_cooldown
    buffs = []
    leader = False

    while run:
        clock.tick(FPS)
        buff_counter -= 1

        if len(enemies) == 0:
            level += 1
            diff -= 1
            enemies = spawn_enemies()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                if pause_game():
                    run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel < WIDTH - player.get_width():  # right
            player.x += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()

        if enemy_move_counter == 0:
            enemy_move_counter = 1
        elif enemy_move_counter >= enemy_move_period:
            enemy_move_counter = 0
        elif enemy_move_counter > 0:
            enemy_move_counter += 1

        for enemy in enemies:
            if enemy_move_counter == 0:
                enemy.move_y(enemy_vel_y)

            enemy.move_lasers(laser_vel_enemy, player)

            if random.randrange(0, diff * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.decrease_health()
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                player.decrease_health()
                enemies.remove(enemy)

        for buff in buffs:
            buff.y += 3
            if collide(buff, player):
                player.absorb_buff(buff.type)
                buffs.remove(buff)
            if buff.y >= 850:
                buffs.remove(buff)

        if buff_counter == 0:
            buff_counter = buff_cooldown
            buffs.append(Buff())

        player.move_lasers(-laser_vel_player, enemies)

        if (level == 3 and len(enemies) == 0) or (player.lives == 0 and player.health == 0):
            if player.lives == 0 and player.health == 0:
                win = False
            else:
                win = True

            leader = True
            break

        redraw_window(level, name, player, enemies, buffs, main_font)

    if leader:
        show_leaderboard(True, (name, player.score + player.lives * (player.health + player.armor), win))

def pause_game():
    pause_manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path='./assets/theme.json')
    msg_font = pygame.font.Font(F_PATH, 40)
    msg = msg_font.render('PAUSED', True, (255, 255, 255))
    p1, p2 = pygame.rect.Rect(450 - 45, 300, 30, 80), pygame.rect.Rect(450 + 15, 300, 30, 80)
    resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH / 2 - 100, 500), (200, 50)),
                                                 text='RESUME',
                                                 manager=pause_manager)
    exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH / 2 - 100, 600), (200, 50)),
                                               text='EXIT TO MAIN MENU',
                                               manager=pause_manager)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH / 2 - 100, 700), (200, 50)),
                                               text='QUIT TO DESKTOP',
                                               manager=pause_manager)

    run = True
    while run:
        time_delta = clock.tick(60) / 1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == resume_button:
                        return False
                    elif event.ui_element == exit_button:
                        return True

                    elif event.ui_element == quit_button:
                        pygame.quit()
                        quit()

            pause_manager.process_events(event)

        dp_blit(False, BLACK_BG, [(msg, (WIDTH / 2 - msg.get_width() / 2, 150))])
        pygame.draw.rect(WIN, (255, 255, 255), p1)
        pygame.draw.rect(WIN, (255, 255, 255), p2)
        pause_manager.update(time_delta)
        pause_manager.draw_ui(WIN)
        pygame.display.update()


def show_leaderboard(_append, _playerstat):
    all_font = pygame.font.Font(F_PATH, 40)
    lb_data = []
    lb = pd.read_csv(LEADERBOARD)
    return_label = pygame.font.Font(F_PATH, 25).render('Press ESC to return to main menu', 1, MAIN_PINK)
    x0, x1, x2, x3 = 100, 250, 650, 830
    y = 50
    run = True
    if _append:
        if len(lb) == 10:
            lb.drop(axis=0, index=len(lb) - 1, inplace=True)
        playerstat = pd.DataFrame({'Name': [_playerstat[0]], 'Score': [_playerstat[1]], 'Boss': [_playerstat[2]]})
        lb = lb.append(playerstat, ignore_index=True)
        lb.sort_values(by='Score', axis=0, ascending=False, inplace=True, ignore_index=True)

    for index, row in lb.iterrows():

        if _append and _playerstat[0] == row["Name"] and _playerstat[1] == row["Score"]:
            name_label = all_font.render(f'{row["Name"]}', 1, MAIN_PINK)
            score_label = all_font.render(f'{row["Score"]}', 1, MAIN_PINK)
            pos_label = all_font.render(f'{index + 1}.', 1, MAIN_PINK)
        else:
            name_label = all_font.render(f'{row["Name"]}', 1, MAIN_BLUE)
            score_label = all_font.render(f'{row["Score"]}', 1, MAIN_BLUE)
            pos_label = all_font.render(f'{index + 1}.', 1, MAIN_BLUE)

        lb_data.append((pos_label, (x0, y)))
        lb_data.append((name_label, (x1, y)))
        lb_data.append((score_label, (x2, y)))

        if row['Boss'] == 1:
            lb_data.append((WIN_MARK, (x3, y - 5)))

        y += 80
    lb_data.append((return_label, (WIDTH / 2 - return_label.get_width() / 2, 850)))
    dp_blit(False, BLACK_BG, lb_data)
    pygame.display.update()

    while run:
        clock.tick(10)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False
    if _append:
        lb.to_csv("./ldb.csv", index=False)


def new_game():
    msg_font = pygame.font.Font(F_PATH, 20)
    name_font = pygame.font.Font(F_PATH, 40)
    msg1 = msg_font.render('LEFT  CLICK  OR  HIT ENTER  TO  CONTINUE', True, (255, 255, 255))
    msg2 = msg_font.render('ENTER YOUR NICKNAME (MAX 10 CHARACTERS)', True, (255, 255, 255))
    labels = [(msg1, (WIDTH / 2 - msg1.get_width() / 2, 700)), (msg2, (WIDTH / 2 - msg2.get_width() / 2, 200))]
    text_manager = pygame_textinput.TextInputManager(validator=lambda inp: len(inp) <= 10)
    text_input = pygame_textinput.TextInputVisualizer(manager=text_manager, font_object=name_font, font_color=MAIN_PINK)
    text_input.antialias = True
    run = True
    continue_game = True
    while run:
        clock.tick(30)
        events = pygame.event.get()
        text_input.update(events)

        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                if pause_game():
                    run = False
                    continue_game = False
            elif event.type == pygame.MOUSEBUTTONDOWN or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                run = False

        dp_blit(False, BLACK_BG, labels + [(text_input.surface, (WIDTH / 2 - text_input.surface.get_width() / 2, 400))])
        pygame.display.update()

    if continue_game:
        run = True
        labels.remove(labels[1])
        tutorial = msg_font.render('HOW TO PLAY', True, (255, 255, 255))
        msg_esc = msg_font.render('Press ESCAPE or QUIT to pause the game', True, MAIN_PINK)
        msg_move = msg_font.render('Press A to move left and D to move right', True, MAIN_PINK)
        msg_shoot = msg_font.render('Press SPACE to shoot your laser', True, MAIN_PINK)
        msg_score = msg_font.render(
            'Your SCORE depends on everything you do!', True, MAIN_PINK)
        labels.append((tutorial, (WIDTH/2-tutorial.get_width()/2, 50)))
        labels.append((msg_esc, (WIDTH / 2 - msg_esc.get_width() / 2, 170)))
        labels.append((msg_move, (WIDTH / 2 - msg_move.get_width() / 2, 290)))
        labels.append((msg_shoot, (WIDTH / 2 - msg_shoot.get_width() / 2, 410)))
        labels.append((msg_score, (WIDTH / 2 - msg_score.get_width() / 2, 530)))
        dp_blit(False, BLACK_BG, labels)
        pygame.display.update()
        while run:
            clock.tick(10)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    if pause_game():
                        run = False
                        continue_game = False
                elif event.type == pygame.MOUSEBUTTONDOWN or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    run = False
            dp_blit(False, BLACK_BG, labels)
            pygame.display.update()

    return text_input.value, continue_game

def info():
    y = 150
    run = True
    rects = []
    return_label = pygame.font.Font(F_PATH, 25).render('Press ESC to return to main menu', 1, MAIN_PINK)
    labels = [(return_label, (WIDTH / 2 - return_label.get_width() / 2, 850))]
    msg_font = pygame.font.Font(F_PATH, 25)
    messages = ['Created by David K. in 2021:',
                "Made using pygame and it's extensions:",
                "Using assets and some code by Tech With Tim:",
                "Using Super-Legend-Boy font by Chequered Ink:",
                "Licensed under Apache 2.0:"
                ]
    links = ['github.com/edavidk7', "www.pygame.org/wiki/about",
             "www.youtube.com/c/TechWithTim/about", "chequered.ink/font-listing/",
             "www.apache.org/licenses/LICENSE-2.0"]

    rendered_messages = list(msg_font.render(f'{msg}', True, MAIN_GREEN) for msg in messages)
    rendered_links = list(msg_font.render(f'{link}', True, MAIN_GREEN) for link in links)

    for i in range(len(rendered_messages)):
        ycor = y * (i+1)
        labels.append((rendered_messages[i], (WIDTH/2-rendered_messages[i].get_width()/2, ycor-75)))
        labels.append((rendered_links[i], (WIDTH/2-rendered_links[i].get_width()/2, ycor)))
        rects.append(pygame.rect.Rect(WIDTH/2-rendered_links[i].get_width()/2, ycor, rendered_links[i].get_width(),rendered_links[i].get_height() ))

    dp_blit(False, BLACK_BG, labels)
    pygame.display.update()

    while run:
        clock.tick(10)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for rect in rects:
                    if rect.collidepoint(pos):
                        webbrowser.open(fr"https://{links[rects.index(rect)]}")

def main_menu():
    main_manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path='./assets/theme.json')
    new_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 350), (200, 50)),
                                              text='NEW GAME',
                                              manager=main_manager)
    leader_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 450), (200, 50)),
                                                 text='LEADERBOARD',
                                                 manager=main_manager)
    info_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 550), (200, 50)),
                                                   text='INFO & LICENSES',
                                                   manager=main_manager)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 650), (200, 50)),
                                               text='QUIT TO DESKTOP',
                                               manager=main_manager)
    title_font = pygame.font.Font(F_PATH, 70)
    title_label = title_font.render("Main Menu", 1, (255, 255, 255))
    main_ship = pygame.transform.scale(pygame.image.load(
        os.path.join("assets", "pixel_ship2.png")), (200, 180))
    squares = []
    rocks = []
    run = True
    while run:
        time_delta = clock.tick(60) / 1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == new_button:
                        squares = []
                        rocks = []
                        game()
                    elif event.ui_element == quit_button:
                        pygame.quit()
                        quit()
                    elif event.ui_element == leader_button:
                        squares = []
                        rocks = []
                        show_leaderboard(False, None)
                    elif event.ui_element == info_button:
                        squares = []
                        rocks = []
                        info()
            main_manager.process_events(event)

        dp_blit(True, None, [(title_label, (WIDTH / 2 - title_label.get_width() / 2, 100)), (main_ship, (500, 400))])

        if random.randint(0, 8) == 1:
            new_rect = pygame.rect.Rect((500 + main_ship.get_width()/2 + random.randint(-20, 0)), 580, 20, 20)
            squares.append(new_rect)


        if random.randint(0, 80) == 1:
            size = random.randint(10, 20)
            new_rock = pygame.rect.Rect(random.randint(500, 700), 200, size, 2*size)
            rocks.append(new_rock)


        for square in squares:
            square.move_ip(0, 1)
            if square.top > 700:
                squares.remove(square)
            else:
                pygame.draw.rect(WIN, (255, 115, 0), square)

        for rock in rocks:
            rock.move_ip(0, 3)
            if rock.top > 800:
                rocks.remove(rock)
            else:
                pygame.draw.rect(WIN, (99, 99, 99), rock)

        main_manager.update(time_delta)
        main_manager.draw_ui(WIN)
        pygame.display.update()


def intro():
    intro_font = pygame.font.Font(F_PATH, 60)
    msg_font = pygame.font.Font(F_PATH, 20)
    intro_label1 = intro_font.render('SPACE', True, MAIN_BLUE)
    intro_label2 = intro_font.render('EVADERS', True, MAIN_PINK)
    msg = msg_font.render('LEFT  CLICK  OR  HIT ENTER  TO  CONTINUE', True, (255, 255, 255))
    run = True
    cont = True
    aligned = False
    h1, h2 = 0, 900
    vel = 5
    while run:
        clock.tick(30)
        while not aligned:
            clock.tick(60)
            dp_blit(False, BLACK_BG, [(intro_label1, (WIDTH / 2 - 70 - intro_label1.get_width(), h1)),
                                      (intro_label2, (WIDTH / 2 - 10., h2))])
            if h1 == h2:
                aligned = True
            else:
                h1 += vel
                h2 -= vel
            pygame.event.clear()
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
                cont = False
            elif event.type == pygame.MOUSEBUTTONDOWN or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                run = False
                cont = True

        dp_blit(False, BLACK_BG,
                [(intro_label1, (WIDTH / 2 - 70 - intro_label1.get_width(), h1)), (intro_label2, (WIDTH / 2 - 10., h2)),
                 (msg, (WIDTH / 2 - msg.get_width() / 2, 700))])
        pygame.display.update()

    if not cont:
        pygame.quit()
        quit()


def main():
    intro()
    main_menu()


if __name__ == "__main__":
    main()

import pygame
import math

pygame.init()
pygame.display.set_caption("Shoot it")
fps = 60 
timer = pygame.time.Clock()
font = pygame.font.Font('assets/font/myFont.ttf', 32)
big_font = pygame.font.Font('assets/font/myFont.ttf', 64)
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
bgs = []
banners = []
guns = []
level = 0
points = 0
shot = False
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
one_coords = [[], [], []]
two_coords = [[], [], []]
three_coords = [[], [], [], []]
four_coords = [[], [], [], []]
five_coords = [[], [], [], [], []]
menu_img = pygame.image.load(f'assets/menus/menu.png')
game_over_img = pygame.image.load(f'assets/menus/gameover.png')
pause_img = pygame.image.load(f'assets/menus/pause.png')
total_shots = 0
# 0 = freeplay, 1 = accuracy, 2 = timed
mode = 0
ammo = 0
time_remaining = 0
time_passed = 0
counter = 1
best_freeplay = 0
best_ammo = 0
best_timed = 0
target_images = [[], [], [], [], []]
target_boxes = []
targets = {1: [10, 6, 4], 2: [10, 6, 4], 3: [9, 10, 6, 4], 4: [9, 10, 6, 4], 5: [9, 10, 6, 4, 1]}

for i in range(1, 6):
    bgs.append(pygame.image.load(f'assets/bgs/{i}.png'))
    banners.append(pygame.image.load(f'assets/banners/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (100, 100)))
    if i < 3:
        for j in range(1, 4):
            target_images[i - 1].append(pygame.transform.scale(pygame.image.load(f'assets/targets/{i}/{j}.png'),
                                                               (120 - (j*18), 80 - (j*12))))
    elif i == 3 or i == 4:
        for j in range(1, 5):
            target_images[i - 1].append(pygame.transform.scale(pygame.image.load(f'assets/targets/{i}/{j}.png'),
                                                               (120 - (j*18), 80 - (j*12))))
    else:
        for j in range(1, 6):
            target_images[i - 1].append(pygame.transform.scale(pygame.image.load(f'assets/targets/{i}/{j}.png'),
                                                               (120 - (j*18), 80 - (j*12))))

pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/background.mp3')
duck_sound = pygame.mixer.Sound('assets/sounds/Duck.mp3')
duck_sound.set_volume(.3)
slime_sound = pygame.mixer.Sound('assets/sounds/ball.mp3')
slime_sound.set_volume(.3)
laser_sound = pygame.mixer.Sound('assets/sounds/Laser Gun.wav')
laser_sound.set_volume(.4)
cat_sound = pygame.mixer.Sound('assets/sounds/cat.mp3')
cat_sound.set_volume(.3)
box_sound = pygame.mixer.Sound('assets/sounds/drop.mp3')
box_sound.set_volume(.3)
pygame.mixer.music.play()


def draw_score():
    points_text = font.render(f'Point : {points}', True, 'black')
    screen.blit(points_text, (320, 640))
    shots_text = font.render(f'Total Shots : {total_shots}', True, 'black')
    screen.blit(shots_text, (320, 667))
    time_text = font.render(f'Time Elapsed : {time_passed}', True, 'black')
    screen.blit(time_text, (320, 697))
    if mode == 0:
        mode_text = font.render(f'Freeplay!', True, 'black')
    if mode == 1:
        mode_text = font.render(f'Ammo Remaining : {ammo}', True, 'black')
    if mode == 2:
        mode_text = font.render(f'Time Remaining {time_remaining}', True, 'black')
    screen.blit(mode_text, (320, 727))
 

def draw_gun():
    mouse_pos = pygame.mouse.get_pos()
    gun_point = (WIDTH/2, HEIGHT - 200)
    lasers = ['brown', 'yellow', 'purple', 'blue', 'red']
    clicks = pygame.mouse.get_pressed()
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1])/(mouse_pos[0] - gun_point[0])
    else:
        slope = -10000
    angle = math.atan(slope)
    rotation = math.degrees(angle)
    if mouse_pos[0] < WIDTH/2:
        gun = pygame.transform.flip(guns[level - 1], True, False)
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH/2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
    else:
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH/2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)


def move_level(coords):
    if level == 1 or level == 2:
        max_val = 3
    elif level == 3 or level == 4:
        max_val = 4
    elif level == 5:
        max_val = 5
    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = WIDTH, my_coords[1]
            else:
                coords[i][j] = (my_coords[0] - 2**i, my_coords[1])
    return coords


def draw_level(coords):
    if level == 1 or level == 2:
        target_rects = [[], [], []]
    elif level == 3 or level == 4:
        target_rects = [[], [], [], []]
    elif level == 5:
        target_rects = [[], [], [], [], []]

    for i in range(len(coords)):
        for j in range(len(coords[i])):
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]),
                                                    (60 - i * 12, 60 - i * 12)))
            screen.blit(target_images[level - 1][i], coords[i][j])
    return target_rects


def check_shot(targets, coords):
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + 10 * (i**2)
                if level == 1:
                    duck_sound.play()
                elif level == 2:
                    slime_sound.play()
                elif level == 3:
                    laser_sound.play()
                elif level == 4:
                    cat_sound.play()
                elif level == 5:
                    box_sound.play()
    return coords


def draw_menu():
    global game_over, pause, mode, level, menu, time_passed, total_shots, points, ammo, time_remaining, best_ammo
    global best_freeplay, best_timed, write_values, clicked, new_coords
    game_over = False
    pause = False
    screen.blit(menu_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    freeplay_button = pygame.rect.Rect((50, 375), (300, 125))
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (265, 438))
    ammo_button = pygame.rect.Rect((532, 375), (300, 125))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (775, 438))
    timed_button = pygame.rect.Rect((50, 545), (300, 125))
    screen.blit(font.render(f'{best_timed}', True, 'black'), (295, 608))
    reset_button = pygame.rect.Rect((532, 545), (300, 125))
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0 
        level = 1 
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1 
        menu = False
        time_passed = 0
        ammo = 148
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2 
        level = 1 
        menu = False
        time_remaining = 70
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_timed = 0
        write_values = True
        clicked = True


def draw_game_over():
    global clicked, level, pause, game_over, menu, points, total_shots, time_passed, time_remaining
    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((170, 645), (260, 100))
    menu_button = pygame.rect.Rect((475, 645), (260, 100))
    screen.blit(big_font.render(f'{display_score}', True, 'black'), (600, 475))
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False


def draw_pause():
    global level, pause, menu, points, total_shots, time_passed, time_remaining, clicked, new_coords
    screen.blit(pause_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((50, 545), (300, 125))
    menu_button = pygame.rect.Rect((532, 545), (300, 125))
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
        clicked = True
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        pygame.mixer.music.play()
        level = 0
        pause = False
        menu = True
        new_coords = True
        clicked = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        

run = True
while run:
    timer.tick(fps)
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remaining -= 1

    if new_coords:
        one_coords = [[], [], []]
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]
        four_coords = [[], [], [], []]
        five_coords = [[], [], [], [], []]
        for i in range(3):
            my_list = targets[1]
            for j in range(my_list[i]):
                one_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(3):
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(4):
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
        for i in range(4):
            my_list = targets[4]
            for j in range(my_list[i]):
                four_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
        for i in range(5):
            my_list = targets[5]
            for j in range(my_list[i]):
                five_coords[i].append((WIDTH//(my_list[i]) * j, 300 - (i * 75) + 30 * (j % 2)))
        new_coords = False

    screen.fill('black')
    screen.blit(bgs[level - 1], (0, 0))
    screen.blit(banners[level - 1], (0, HEIGHT-200))
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()

    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False
    elif level == 4:
        target_boxes = draw_level(four_coords)
        four_coords = move_level(four_coords)
        if shot:
            four_coords = check_shot(target_boxes, four_coords)
            shot = False
    elif level == 5:
        target_boxes = draw_level(five_coords)
        five_coords = move_level(five_coords)
        if shot:
            five_coords = check_shot(target_boxes, five_coords)
            shot = False

    if level > 0:
        draw_gun()
        draw_score()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                shot = True
                total_shots += 1
                if mode == 1:
                   ammo -= 1
            if (750 < mouse_position[0] < 950) and (600 < mouse_position[1] < HEIGHT - 120):
                resume_level = level
                pause = True
                clicked = True
            if (750 < mouse_position[0] < 950) and (700 < mouse_position[1] < HEIGHT - 20):
                menu = True
                pygame.mixer.music.play()
                clicked = True
                new_coords = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level += 1
    if level > 2:
        if target_boxes == [[], [], [], []] and level < 5:
            level += 1
        if (level == 5 and target_boxes == [[], [], [], [], []]) or (mode == 1 and ammo == 0) or (
                mode == 2 and time_remaining == 0):
            new_coords = True
            pygame.mixer.music.play()
            if mode == 0:
                if time_passed < best_freeplay or best_freeplay == 0:
                    best_freeplay = time_passed
                    write_values = True
            if mode == 1:
                if points > best_ammo:
                    best_ammo = points
                    write_values = True
            if mode == 2:
                if points > best_timed:
                    best_timed = points
                    write_values = True
            game_over = True

    pygame.display.flip()
pygame.quit()

 
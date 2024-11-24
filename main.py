import pygame
import random
import json
import os

from objects import Bar, Dot, Player, Message, Particle, ScoreCard, Button

# Função para carregar e salvar o HighScore em um arquivo JSON
def load_highscore():
    if os.path.exists("highscore.json"):
        with open("highscore.json", "r") as f:
            data = json.load(f)
            return data.get("highscore", 0)
    else:
        return 0

def save_highscore(score):
    data = {"highscore": score}
    with open("highscore.json", "w") as f:
        json.dump(data, f)

# Inicializando o Pygame
pygame.init()
SCREEN = WIDTH, HEIGHT = 288, 512

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)

clock = pygame.time.Clock()
FPS = 30

bg = pygame.image.load(f'Assets/bg4.jpg')
bg = pygame.transform.scale(bg, SCREEN)

frame_height = 150
frame = pygame.image.load(f'Assets/bg3.jpg')
frame = pygame.transform.scale(frame, (WIDTH - 10, frame_height))
frameX, frameY = 5, HEIGHT//2 - frame_height//2

# Cores
BLACK = (0, 0, 32)
WHITE = (255, 255, 255)

# Sons
score_fx = pygame.mixer.Sound('Sounds/point.mp3')
dead_fx = pygame.mixer.Sound('Sounds/dead.mp3')
score_page_fx = pygame.mixer.Sound('Sounds/score_page.mp3')

pygame.mixer.music.load('Sounds/Chill Gaming.mp3')
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.5)

# Fontes
score_font = "Fonts/EvilEmpire-4BBVK.ttf"
final_score_font = "Fonts/ghostclanital.ttf"
title_font = "Fonts/dpcomic.ttf"

# Mensagens
dodgy = Message(WIDTH//2, HEIGHT//3, 80, "Dodgy", title_font, WHITE, win)
walls = Message(WIDTH//2, HEIGHT//2, 60, "Walls", title_font, WHITE, win)
tap_to_play = Message(WIDTH//2, HEIGHT-100, 20, "Tap To Play", None, WHITE, win)
new_high =  Message(WIDTH//2, 240, 20, "NEW HIGH", None, WHITE, win)

# Imagens de Botões
home_img = pygame.image.load('Assets/homeBtn.png')
replay_img = pygame.image.load('Assets/replay.png')
sound_off_img = pygame.image.load("Assets/soundOffBtn.png")
sound_on_img = pygame.image.load("Assets/soundOnBtn.png")

# Botões
home_btn = Button(home_img, (36, 36), WIDTH // 4 - 18, 320)
replay_btn = Button(replay_img, (44,44), WIDTH // 2 - 18, 315)
sound_btn = Button(sound_on_img, (36, 36), WIDTH - WIDTH // 4 - 18, 320)

# Grupos de Sprites
bar_group = pygame.sprite.Group()
dot_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()

score_msg = ScoreCard(WIDTH//2, 100, 50, score_font, WHITE, win)

p = Player(win)

# Variáveis
bar_frequency = 1400
bar_heights = [height for height in range(60, 100, 10)]
bar_speed = 3
pos = -1
pos_updater = 1
start_time = pygame.time.get_ticks()

clicked = False
score = 0
highscore = load_highscore()  # Carregar HighScore ao iniciar
player_alive = True
sound_on = True

home_page = True
game_page = False
score_page = False

running = True
while running:
    clicked = False
    win.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or \
                event.key == pygame.K_q:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN and home_page:
            home_page = False
            game_page = True
            score_page = False

            start_time = pygame.time.get_ticks()
            player_alive = True
            score = 0
            bar_speed = 3
            p = Player(win)

        if event.type == pygame.MOUSEBUTTONDOWN and game_page:
            if not clicked:
                clicked = True
        if event.type == pygame.MOUSEBUTTONUP and game_page:
            clicked = False

    if home_page:
        dodgy.update()
        walls.update()
        tap_to_play.update()

    if score_page:
        final_score = Message(WIDTH//2, 150, 100, f"{score}", score_font, WHITE, win)
        final_score.update()

        if score and score >= highscore:
            new_high.update()

        if home_btn.draw(win):
            home_page = True
            score_page = False
            game_page = False

        if replay_btn.draw(win):
            home_page = False
            score_page = False
            game_page = True

            start_time = pygame.time.get_ticks()
            player_alive = True
            score = 0
            bar_speed = 3
            p = Player(win)

        if sound_btn.draw(win):
            sound_on = not sound_on

            if sound_on:
                sound_btn.update_image(sound_on_img)
                pygame.mixer.music.play(loops=-1)
            else:
                sound_btn.update_image(sound_off_img)
                pygame.mixer.music.stop()

    if game_page:
        win.blit(frame, (frameX, frameY))

        if player_alive:
            current_time = pygame.time.get_ticks()
            if current_time - start_time >= bar_frequency:
                bar_height = random.choice(bar_heights)
                pos = pos * -1

                if pos == -1:
                    bar_y = frameY
                    dot_y = frameY + bar_height + 20
                elif pos == 1:
                    bar_y = frameY + frame_height - bar_height
                    dot_y = frameY + frame_height - bar_height - 20

                bar = Bar(WIDTH, bar_y, bar_height, BLACK, win)
                dot = Dot(WIDTH + 10, dot_y, win)
                bar_group.add(bar)
                dot_group.add(dot)

                start_time = current_time

            for dot in dot_group:
                if dot.rect.colliderect(p):
                    dot.kill()
                    score += 1
                    if highscore < score:
                        highscore = score
                        save_highscore(highscore)  # Salvar novo HighScore
                    score_fx.play()
                    score_msg.animate = True

            if pygame.sprite.spritecollide(p, bar_group, False):
                x, y = p.rect.center
                for i in range(10):
                    particle = Particle(x, y, WHITE, win)
                    particle_group.add(particle)
                player_alive = False
                dead_fx.play()
                bar_speed = 0

        bar_group.update(bar_speed)
        dot_group.update(bar_speed)
        p.update(player_alive, clicked)

        score_msg.update(score)
        particle_group.update()

        if not player_alive and len(particle_group) == 0:
            score_page = True
            game_page = False

        if score_page:
            bar_group.empty()
            dot_group.empty()
            score_page_fx.play()
            start_time = 0

    pygame.draw.rect(win, WHITE, (0, 0, WIDTH, HEIGHT), 5, border_radius=10)
    clock.tick(FPS)
    pygame.display.update()

pygame.quit()

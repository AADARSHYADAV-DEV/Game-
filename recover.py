import pygame
import random
import os
import math
from array import array

pygame.init()
pygame.mixer.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 640, 480
BLOCK = 20
BASE_SPEED = 8

# Nokia green theme
BG = (15, 56, 15)
GRID = (25, 90, 25)
SNAKE = (120, 255, 120)
FOOD = (255, 80, 80)
BONUS = (255, 215, 0)
TEXT = (200, 255, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nokia Snake Ultimate")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 24)
big_font = pygame.font.SysFont("consolas", 42)

# ---------------- SOUND ----------------
def make_beep(freq=600, duration_ms=120, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array("h")

    amplitude = int(32767 * volume)
    for s in range(n_samples):
        t = s / sample_rate
        buf.append(int(amplitude * math.sin(2 * math.pi * freq * t)))

    return pygame.mixer.Sound(buffer=buf)

eat_sound = make_beep(700, 100)
bonus_sound = make_beep(1000, 140)
gameover_sound = make_beep(250, 300)

# ---------------- HIGH SCORE ----------------
HS_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HS_FILE):
        with open(HS_FILE, "r") as f:
            return int(f.read() or 0)
    return 0

def save_highscore(score):
    with open(HS_FILE, "w") as f:
        f.write(str(score))

highscore = load_highscore()

# ---------------- FOOD ----------------
def random_pos():
    return (
        random.randrange(0, WIDTH, BLOCK),
        random.randrange(0, HEIGHT, BLOCK)
    )

def draw_text(text, y, big=False):
    surf = (big_font if big else font).render(text, True, TEXT)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)

# ---------------- MENUS ----------------
def start_menu():
    while True:
        screen.fill(BG)
        draw_text("NOKIA SNAKE", 120, True)
        draw_text("Press ENTER to Start", 220)
        draw_text("Arrow Keys = Move", 270)
        draw_text("P = Pause", 310)
        draw_text("High Score: " + str(highscore), 370)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def game_over(score):
    global highscore

    if score > highscore:
        highscore = score
        save_highscore(score)

    gameover_sound.play()

    while True:
        screen.fill(BG)
        draw_text("GAME OVER", 140, True)
        draw_text("Score: " + str(score), 240)
        draw_text("High Score: " + str(highscore), 290)
        draw_text("R = Restart", 360)
        draw_text("Q = Quit", 400)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

# ---------------- GAME ----------------
def game():
    x, y = WIDTH // 2, HEIGHT // 2
    dx, dy = BLOCK, 0

    snake = [(x, y)]
    length = 1

    food = random_pos()
    bonus = None
    bonus_timer = 0

    score = 0
    paused = False

    while True:
        level = score // 5 + 1
        speed = BASE_SPEED + (level - 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

                if not paused:
                    if event.key == pygame.K_LEFT and dx == 0:
                        dx, dy = -BLOCK, 0
                    elif event.key == pygame.K_RIGHT and dx == 0:
                        dx, dy = BLOCK, 0
                    elif event.key == pygame.K_UP and dy == 0:
                        dx, dy = 0, -BLOCK
                    elif event.key == pygame.K_DOWN and dy == 0:
                        dx, dy = 0, BLOCK

        if paused:
            draw_text("PAUSED", HEIGHT // 2, True)
            pygame.display.flip()
            clock.tick(5)
            continue

        # Move
        x += dx
        y += dy

        # Wrap mode
        x %= WIDTH
        y %= HEIGHT

        head = (x, y)
        snake.append(head)

        if len(snake) > length:
            snake.pop(0)

        # Self collision
        if head in snake[:-1]:
            game_over(score)
            return

        # Normal food
        if head == food:
            score += 1
            length += 1
            food = random_pos()
            eat_sound.play()

            # 25% chance bonus food
            if random.random() < 0.25:
                bonus = random_pos()
                bonus_timer = 120  # frames

        # Bonus food
        if bonus and head == bonus:
            score += 3
            length += 2
            bonus = None
            bonus_sound.play()

        # Bonus timer
        if bonus:
            bonus_timer -= 1
            if bonus_timer <= 0:
                bonus = None

        # Draw
        screen.fill(BG)

        # Grid
        for gx in range(0, WIDTH, BLOCK):
            pygame.draw.line(screen, GRID, (gx, 0), (gx, HEIGHT))
        for gy in range(0, HEIGHT, BLOCK):
            pygame.draw.line(screen, GRID, (0, gy), (WIDTH, gy))

        # Food
        pygame.draw.rect(screen, FOOD, (*food, BLOCK, BLOCK))

        # Bonus
        if bonus:
            pygame.draw.rect(screen, BONUS, (*bonus, BLOCK, BLOCK))

        # Snake
        for part in snake:
            pygame.draw.rect(screen, SNAKE, (*part, BLOCK, BLOCK))

        # HUD
        screen.blit(font.render(f"Score: {score}", True, TEXT), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, TEXT), (10, 40))
        screen.blit(font.render(f"High: {highscore}", True, TEXT), (10, 70))

        pygame.display.flip()
        clock.tick(speed)

# ---------------- MAIN LOOP ----------------
while True:
    start_menu()
    game()

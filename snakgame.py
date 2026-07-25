import math
import os
import random
from array import array

import pygame


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 720, 540
CELL = 20
HUD_HEIGHT = 80
PLAY_TOP = HUD_HEIGHT
PLAY_HEIGHT = HEIGHT - HUD_HEIGHT
BASE_SPEED = 9
HIGH_SCORE_FILE = "snake_highscore.txt"

BG = (12, 18, 30)
PANEL = (22, 32, 50)
GRID = (32, 45, 68)
TEXT = (224, 241, 255)
MUTED = (137, 158, 184)
ACCENT = (50, 215, 145)
SNAKE_HEAD = (70, 242, 166)
SNAKE_BODY = (38, 184, 132)
SNAKE_DARK = (21, 105, 82)
APPLE = (242, 76, 76)
APPLE_DARK = (150, 34, 47)
BONUS = (255, 209, 92)
BONUS_DARK = (176, 120, 36)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Arcade")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 22)
small_font = pygame.font.SysFont("consolas", 18)
big_font = pygame.font.SysFont("consolas", 46, bold=True)

play_rect = pygame.Rect(0, PLAY_TOP, WIDTH, PLAY_HEIGHT)


def make_beep(freq=600, duration_ms=120, volume=0.25):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array("h")
    amplitude = int(32767 * volume)

    for sample in range(n_samples):
        t = sample / sample_rate
        fade = 1 - sample / n_samples
        buf.append(int(amplitude * fade * math.sin(2 * math.pi * freq * t)))

    return pygame.mixer.Sound(buffer=buf)


eat_sound = make_beep(760, 90)
bonus_sound = make_beep(1080, 150)
gameover_sound = make_beep(210, 320)


def load_highscore():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_highscore(score):
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
        file.write(str(score))


def grid_pos():
    return (
        random.randrange(0, WIDTH, CELL),
        random.randrange(PLAY_TOP, HEIGHT, CELL),
    )


def random_empty_pos(snake, food=None, bonus=None):
    occupied = set(snake)
    if food:
        occupied.add(food)
    if bonus:
        occupied.add(bonus)

    while True:
        pos = grid_pos()
        if pos not in occupied:
            return pos


def draw_label(text, position, color=TEXT, use_small=False):
    label = (small_font if use_small else font).render(text, True, color)
    screen.blit(label, position)


def draw_center_text(text, y, color=TEXT, big=False):
    face = big_font if big else font
    shadow = face.render(text, True, BLACK)
    label = face.render(text, True, color)
    rect = label.get_rect(center=(WIDTH // 2, y))
    screen.blit(shadow, rect.move(3, 3))
    screen.blit(label, rect)


def draw_button(rect, text, fill=ACCENT):
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    label = small_font.render(text, True, BLACK)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_background():
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, ACCENT, (0, HUD_HEIGHT - 2), (WIDTH, HUD_HEIGHT - 2), 3)

    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRID, (x, PLAY_TOP), (x, HEIGHT))
    for y in range(PLAY_TOP, HEIGHT, CELL):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


def draw_food(position):
    x, y = position
    rect = pygame.Rect(x + 3, y + 3, CELL - 6, CELL - 6)
    pygame.draw.circle(screen, APPLE_DARK, rect.center, 9)
    pygame.draw.circle(screen, APPLE, (rect.centerx - 1, rect.centery - 1), 8)
    pygame.draw.rect(screen, ACCENT, (x + 11, y + 1, 5, 6), border_radius=2)


def draw_bonus(position, timer):
    x, y = position
    pulse = 2 if (timer // 8) % 2 == 0 else 0
    rect = pygame.Rect(x + 3 - pulse, y + 3 - pulse, CELL - 6 + pulse * 2, CELL - 6 + pulse * 2)
    pygame.draw.circle(screen, BONUS_DARK, rect.center, rect.width // 2)
    pygame.draw.circle(screen, BONUS, (rect.centerx - 1, rect.centery - 1), max(4, rect.width // 2 - 2))


def draw_snake(snake, direction):
    for index, part in enumerate(snake):
        x, y = part
        rect = pygame.Rect(x + 2, y + 2, CELL - 4, CELL - 4)
        color = SNAKE_HEAD if index == len(snake) - 1 else SNAKE_BODY
        pygame.draw.rect(screen, SNAKE_DARK, rect.inflate(2, 2), border_radius=7)
        pygame.draw.rect(screen, color, rect, border_radius=7)

    head = snake[-1]
    hx, hy = head
    eye_offset = {
        (CELL, 0): ((12, 6), (12, 14)),
        (-CELL, 0): ((6, 6), (6, 14)),
        (0, CELL): ((6, 12), (14, 12)),
        (0, -CELL): ((6, 6), (14, 6)),
    }[direction]

    for ox, oy in eye_offset:
        pygame.draw.circle(screen, WHITE, (hx + ox, hy + oy), 3)
        pygame.draw.circle(screen, BLACK, (hx + ox, hy + oy), 1)


def draw_hud(score, highscore, level, bonus_timer):
    draw_label(f"SCORE {score}", (18, 12))
    draw_label(f"BEST {highscore}", (18, 40), MUTED, use_small=True)
    draw_center_text(f"LEVEL {level}", 26, ACCENT)

    if bonus_timer > 0:
        width = int(140 * bonus_timer / 180)
        pygame.draw.rect(screen, GRID, (560, 20, 140, 12), border_radius=6)
        pygame.draw.rect(screen, BONUS, (560, 20, width, 12), border_radius=6)
        draw_label("BONUS", (596, 38), BONUS, use_small=True)


def draw_overlay(title, lines, buttons=None):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 145))
    screen.blit(shade, (0, 0))

    panel = pygame.Rect(110, 150, 500, 235)
    pygame.draw.rect(screen, PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, ACCENT, panel, 3, border_radius=14)
    draw_center_text(title, 202, ACCENT, big=True)

    y = 252
    for line in lines:
        draw_center_text(line, y, TEXT)
        y += 32

    if buttons:
        for rect, text, color in buttons:
            draw_button(rect, text, color)


def save_score_if_needed(score, highscore):
    if score > highscore:
        save_highscore(score)
        return score
    return highscore


def reset_game():
    start = (
        (WIDTH // CELL // 2) * CELL,
        PLAY_TOP + (PLAY_HEIGHT // CELL // 2) * CELL,
    )
    snake = [(start[0] - CELL * 2, start[1]), (start[0] - CELL, start[1]), start]
    return {
        "snake": snake,
        "direction": (CELL, 0),
        "next_direction": (CELL, 0),
        "food": random_empty_pos(snake),
        "bonus": None,
        "bonus_timer": 0,
        "score": 0,
        "paused": False,
        "game_over": False,
        "started": False,
    }


restart_button = pygame.Rect(214, 326, 130, 38)
quit_button = pygame.Rect(376, 326, 130, 38)

highscore = load_highscore()
state = reset_game()
running = True

while running:
    level = state["score"] // 6 + 1
    speed = BASE_SPEED + min(level - 1, 12)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and not state["started"]:
                state["started"] = True
            elif event.key == pygame.K_p and state["started"] and not state["game_over"]:
                state["paused"] = not state["paused"]
            elif event.key == pygame.K_r:
                state = reset_game()
                state["started"] = True
            elif event.key == pygame.K_q:
                running = False

            if state["started"] and not state["paused"] and not state["game_over"]:
                dx, dy = state["direction"]
                if event.key == pygame.K_LEFT and dx == 0:
                    state["next_direction"] = (-CELL, 0)
                elif event.key == pygame.K_RIGHT and dx == 0:
                    state["next_direction"] = (CELL, 0)
                elif event.key == pygame.K_UP and dy == 0:
                    state["next_direction"] = (0, -CELL)
                elif event.key == pygame.K_DOWN and dy == 0:
                    state["next_direction"] = (0, CELL)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if restart_button.collidepoint(event.pos):
                state = reset_game()
                state["started"] = True
            elif quit_button.collidepoint(event.pos):
                running = False

    if state["started"] and not state["paused"] and not state["game_over"]:
        state["direction"] = state["next_direction"]
        dx, dy = state["direction"]
        head_x, head_y = state["snake"][-1]
        new_head = ((head_x + dx) % WIDTH, PLAY_TOP + ((head_y + dy - PLAY_TOP) % PLAY_HEIGHT))
        state["snake"].append(new_head)

        ate_food = new_head == state["food"]
        ate_bonus = state["bonus"] and new_head == state["bonus"]

        if ate_food:
            state["score"] += 1
            state["food"] = random_empty_pos(state["snake"], bonus=state["bonus"])
            eat_sound.play()

            if not state["bonus"] and random.random() < 0.28:
                state["bonus"] = random_empty_pos(state["snake"], food=state["food"])
                state["bonus_timer"] = 180
        elif ate_bonus:
            state["score"] += 4
            state["bonus"] = None
            state["bonus_timer"] = 0
            bonus_sound.play()
        else:
            state["snake"].pop(0)

        if state["bonus"]:
            state["bonus_timer"] -= 1
            if state["bonus_timer"] <= 0:
                state["bonus"] = None

        if new_head in state["snake"][:-1]:
            state["game_over"] = True
            highscore = save_score_if_needed(state["score"], highscore)
            gameover_sound.play()

    draw_background()
    draw_hud(state["score"], highscore, level, state["bonus_timer"])
    draw_food(state["food"])

    if state["bonus"]:
        draw_bonus(state["bonus"], state["bonus_timer"])

    draw_snake(state["snake"], state["direction"])

    if not state["started"]:
        draw_overlay(
            "SNAKE ARCADE",
            ["ENTER or SPACE to start", "Arrow keys to move", "P pause  |  R restart  |  Q quit"],
        )
    elif state["paused"]:
        draw_overlay("PAUSED", ["Press P to continue", "R restart  |  Q quit"])
    elif state["game_over"]:
        draw_overlay(
            "GAME OVER",
            [f"Score: {state['score']}", f"Best: {highscore}"],
            [(restart_button, "Restart", ACCENT), (quit_button, "Quit", APPLE)],
        )

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()

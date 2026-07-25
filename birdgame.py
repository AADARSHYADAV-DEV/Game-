import os
import random
import sys

import pygame


pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bird Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (112, 197, 206)
CLOUD = (236, 249, 244)
GREEN = (115, 191, 46)
DARK_GREEN = (72, 143, 26)
PIPE_HIGHLIGHT = (164, 226, 64)
RED = (220, 60, 60)
YELLOW = (247, 212, 48)
LIGHT_YELLOW = (255, 238, 92)
WING_YELLOW = (236, 169, 35)
ORANGE = (232, 117, 36)
LIGHT_ORANGE = (255, 168, 57)
TAN = (222, 199, 117)
BROWN = (119, 85, 43)
CREAM = (255, 248, 210)
GRAY = (235, 235, 235)
DARK_GRAY = (65, 65, 65)

BIRD_X = 50
BIRD_RADIUS = 20
GRAVITY = 0.5
JUMP = -8
GROUND_HEIGHT = 72

PIPE_WIDTH = 60
PIPE_GAP = 200
PIPE_VEL = 5
HIGH_SCORE_FILE = "highscore.txt"

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 26)
clock = pygame.time.Clock()


def load_high_score():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_high_score(value):
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
        file.write(str(value))


def create_pipe():
    play_height = HEIGHT - GROUND_HEIGHT
    y = random.randint(110, play_height - 130)
    return {
        "x": WIDTH,
        "top": y - PIPE_GAP // 2,
        "bottom": y + PIPE_GAP // 2,
        "scored": False,
    }


def reset_game():
    return {
        "bird_y": HEIGHT // 2,
        "bird_vel": 0,
        "pipes": [],
        "score": 0,
        "frame": 0,
        "paused": False,
        "game_over": False,
        "show_high_score": False,
        "ground_x": 0,
    }


def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
    label = small_font.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_center_text(text, y, color=BLACK):
    shadow = font.render(text, True, WHITE)
    label = font.render(text, True, color)
    screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 2, y + 2)))
    screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))


def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    return high_score


def draw_background(frame):
    screen.fill(SKY_BLUE)

    cloud_offset = -(frame // 2) % WIDTH
    for x, y in ((70, 110), (260, 170), (430, 85)):
        draw_cloud(x + cloud_offset, y)
        draw_cloud(x + cloud_offset - WIDTH, y)


def draw_cloud(x, y):
    pygame.draw.circle(screen, CLOUD, (x, y), 18)
    pygame.draw.circle(screen, CLOUD, (x + 18, y - 8), 23)
    pygame.draw.circle(screen, CLOUD, (x + 42, y), 18)
    pygame.draw.rect(screen, CLOUD, (x - 4, y, 52, 18), border_radius=9)


def draw_pipe(pipe):
    x = int(pipe["x"])
    top_rect = pygame.Rect(x, 0, PIPE_WIDTH, pipe["top"])
    top_cap = pygame.Rect(x - 5, pipe["top"] - 25, PIPE_WIDTH + 10, 25)
    bottom_rect = pygame.Rect(x, pipe["bottom"], PIPE_WIDTH, HEIGHT - GROUND_HEIGHT - pipe["bottom"])
    bottom_cap = pygame.Rect(x - 5, pipe["bottom"], PIPE_WIDTH + 10, 25)

    for rect in (top_rect, top_cap, bottom_rect, bottom_cap):
        pygame.draw.rect(screen, GREEN, rect)
        pygame.draw.rect(screen, PIPE_HIGHLIGHT, (rect.x + 8, rect.y, 10, rect.height))
        pygame.draw.rect(screen, DARK_GREEN, rect, 3)


def draw_bird(y, velocity):
    tilt = max(-18, min(24, int(velocity * 2.5)))
    scale = 3
    bird = pygame.Surface((72 * scale, 56 * scale), pygame.SRCALPHA)

    def s_rect(x, y_pos, width, height):
        return (
            int(x * scale),
            int(y_pos * scale),
            int(width * scale),
            int(height * scale),
        )

    def s_point(point):
        return (int(point[0] * scale), int(point[1] * scale))

    def s_points(points):
        return [s_point(point) for point in points]

    pygame.draw.ellipse(bird, (35, 31, 24), s_rect(7, 10, 46, 34))
    pygame.draw.ellipse(bird, YELLOW, s_rect(9, 11, 42, 31))
    pygame.draw.ellipse(bird, LIGHT_YELLOW, s_rect(16, 13, 22, 12))
    pygame.draw.arc(bird, WHITE, s_rect(17, 14, 18, 10), 3.5, 5.8, 2 * scale)

    pygame.draw.ellipse(bird, (35, 31, 24), s_rect(15, 24, 27, 17))
    pygame.draw.ellipse(bird, WING_YELLOW, s_rect(17, 25, 23, 14))
    pygame.draw.arc(bird, (180, 116, 24), s_rect(20, 27, 15, 9), 0.2, 2.7, 2 * scale)

    pygame.draw.polygon(bird, (35, 31, 24), s_points([(47, 20), (68, 27), (47, 34)]))
    pygame.draw.polygon(bird, LIGHT_ORANGE, s_points([(49, 21), (65, 27), (49, 28)]))
    pygame.draw.polygon(bird, ORANGE, s_points([(49, 28), (65, 27), (49, 33)]))
    pygame.draw.line(bird, (139, 69, 29), s_point((50, 28)), s_point((64, 28)), 1 * scale)

    pygame.draw.circle(bird, (35, 31, 24), s_point((42, 19)), 10 * scale)
    pygame.draw.circle(bird, WHITE, s_point((42, 19)), 8 * scale)
    pygame.draw.circle(bird, BLACK, s_point((45, 20)), 3 * scale)
    pygame.draw.circle(bird, WHITE, s_point((46, 18)), 1 * scale)
    pygame.draw.arc(bird, (35, 31, 24), s_rect(35, 10, 16, 9), 3.4, 6.0, 1 * scale)

    body = pygame.transform.smoothscale(bird, (72, 56))
    rotated = pygame.transform.rotate(body, -tilt)
    screen.blit(rotated, rotated.get_rect(center=(BIRD_X, int(y))))


def draw_ground(ground_x):
    ground_y = HEIGHT - GROUND_HEIGHT
    pygame.draw.rect(screen, TAN, (0, ground_y, WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(screen, GREEN, (0, ground_y, WIDTH, 12))
    pygame.draw.line(screen, DARK_GREEN, (0, ground_y + 12), (WIDTH, ground_y + 12), 3)

    tile_width = 32
    for x in range(int(ground_x) - tile_width, WIDTH + tile_width, tile_width):
        pygame.draw.polygon(
            screen,
            BROWN,
            [(x, ground_y + 30), (x + 16, ground_y + 16), (x + 32, ground_y + 30)],
        )


def draw_score(score):
    text = font.render(str(score), True, WHITE)
    outline = font.render(str(score), True, BLACK)
    center = (WIDTH // 2, 46)

    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        screen.blit(outline, outline.get_rect(center=(center[0] + dx, center[1] + dy)))
    screen.blit(text, text.get_rect(center=center))


pause_button = pygame.Rect(8, 548, 74, 38)
restart_button = pygame.Rect(89, 548, 84, 38)
high_score_button = pygame.Rect(180, 548, 126, 38)
quit_button = pygame.Rect(313, 548, 78, 38)

state = reset_game()
high_score = load_high_score()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not state["paused"] and not state["game_over"]:
                state["bird_vel"] = JUMP
            elif event.key == pygame.K_p and not state["game_over"]:
                state["paused"] = not state["paused"]
            elif event.key == pygame.K_r:
                state = reset_game()
            elif event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_h:
                state["show_high_score"] = not state["show_high_score"]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pause_button.collidepoint(event.pos) and not state["game_over"]:
                state["paused"] = not state["paused"]
            elif restart_button.collidepoint(event.pos):
                state = reset_game()
            elif high_score_button.collidepoint(event.pos):
                state["show_high_score"] = not state["show_high_score"]
            elif quit_button.collidepoint(event.pos):
                running = False

    if not state["paused"] and not state["game_over"]:
        state["bird_vel"] += GRAVITY
        state["bird_y"] += state["bird_vel"]

        if state["frame"] % 90 == 0:
            state["pipes"].append(create_pipe())
        state["frame"] += 1

        for pipe in state["pipes"]:
            pipe["x"] -= PIPE_VEL

            if not pipe["scored"] and pipe["x"] + PIPE_WIDTH < BIRD_X:
                state["score"] += 1
                pipe["scored"] = True

        state["pipes"] = [
            pipe for pipe in state["pipes"] if pipe["x"] + PIPE_WIDTH > 0
        ]

        for pipe in state["pipes"]:
            hits_pipe_x = (
                BIRD_X + BIRD_RADIUS > pipe["x"]
                and BIRD_X - BIRD_RADIUS < pipe["x"] + PIPE_WIDTH
            )
            hits_pipe_y = (
                state["bird_y"] - BIRD_RADIUS < pipe["top"]
                or state["bird_y"] + BIRD_RADIUS > pipe["bottom"]
            )

            if hits_pipe_x and hits_pipe_y:
                state["game_over"] = True

        hits_screen_edge = (
            state["bird_y"] - BIRD_RADIUS < 0
            or state["bird_y"] + BIRD_RADIUS > HEIGHT - GROUND_HEIGHT
        )
        if hits_screen_edge:
            state["game_over"] = True

        if state["game_over"]:
            high_score = update_high_score(state["score"], high_score)

        state["ground_x"] = (state["ground_x"] - PIPE_VEL) % 32

    draw_background(state["frame"])
    for pipe in state["pipes"]:
        draw_pipe(pipe)

    draw_ground(state["ground_x"])
    draw_bird(state["bird_y"], state["bird_vel"])
    draw_score(state["score"])

    high_score_text = small_font.render(f"Best: {high_score}", True, BLACK)
    screen.blit(high_score_text, (10, 10))

    if state["show_high_score"]:
        draw_center_text(f"High Score: {high_score}", HEIGHT // 2 - 85)

    if state["paused"]:
        draw_center_text("Paused", HEIGHT // 2 - 20, BLACK)
        draw_center_text("Press P or Pause", HEIGHT // 2 + 20, DARK_GRAY)

    if state["game_over"]:
        draw_center_text("Game Over", HEIGHT // 2 - 40, RED)
        draw_center_text("Press R or Restart", HEIGHT // 2, DARK_GRAY)

    draw_button(pause_button, "Pause", YELLOW if not state["paused"] else GRAY)
    draw_button(restart_button, "Restart", CREAM)
    draw_button(high_score_button, "High Score", CREAM)
    draw_button(quit_button, "Quit", RED)

    pygame.display.flip()

pygame.quit()
sys.exit()

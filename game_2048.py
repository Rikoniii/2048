import random
import pygame
import sys
import os

# --- Настройки ---
WIDTH = 500
HEIGHT = 600
SIZE = 4
CELL_SIZE = 100
PADDING = 10

BACKGROUND_COLOR = (250, 248, 239)
BOARD_COLOR = (187, 173, 160)
TEXT_COLOR = (119, 110, 101)

CELL_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Deluxe 🧩")
font_big = pygame.font.SysFont("arial", 48, bold=True)
font_small = pygame.font.SysFont("arial", 28)
font_medium = pygame.font.SysFont("arial", 36, bold=True)

# --- Работа с рекордом ---
RECORD_FILE = "record.txt"


def load_record():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            return int(f.read().strip() or 0)
    return 0


def save_record(score):
    record = load_record()
    if score > record:
        with open(RECORD_FILE, "w") as f:
            f.write(str(score))


# --- Игровые функции ---
def new_tile(board):
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = random.choice([2, 4])


def draw_board(board, score, record):
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, BOARD_COLOR, (PADDING, 100, WIDTH - 2 * PADDING, WIDTH - 2 * PADDING), border_radius=10)

    # Текущий счёт и рекорд
    score_text = font_small.render(f"Счёт: {score}", True, TEXT_COLOR)
    record_text = font_small.render(f"Рекорд: {record}", True, TEXT_COLOR)
    screen.blit(score_text, (30, 40))
    screen.blit(record_text, (WIDTH - 180, 40))

    # Отрисовка ячеек
    for r in range(SIZE):
        for c in range(SIZE):
            value = board[r][c]
            color = CELL_COLORS.get(value, (60, 58, 50))
            rect = pygame.Rect(
                c * CELL_SIZE + PADDING * (c + 1),
                r * CELL_SIZE + 100 + PADDING * (r + 1),
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(screen, color, rect, border_radius=8)
            if value:
                font_size = 48 if value < 100 else 40 if value < 1000 else 32
                text = pygame.font.SysFont("arial", font_size, bold=True).render(str(value), True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    pygame.display.flip()


def compress(row):
    new_row = [i for i in row if i != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row


def merge(row):
    score = 0
    for i in range(SIZE - 1):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            score += row[i]
            row[i + 1] = 0
    return row, score


def move_left(board):
    new_board = []
    score = 0
    for row in board:
        compressed = compress(row)
        merged, gained = merge(compressed)
        compressed = compress(merged)
        new_board.append(compressed)
        score += gained
    return new_board, score


def rotate_board(board):
    return [list(row) for row in zip(*board[::-1])]


def can_move(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True
            if c < SIZE - 1 and board[r][c] == board[r][c + 1]:
                return True
            if r < SIZE - 1 and board[r][c] == board[r + 1][c]:
                return True
    return False


def game_over_screen(score, record):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((240, 240, 240))
    screen.blit(overlay, (0, 0))

    text = font_big.render("Ты проиграл", True, (80, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    screen.blit(text, text_rect)

    score_text = font_medium.render(f"Счёт: {score}", True, TEXT_COLOR)
    record_text = font_medium.render(f"Рекорд: {record}", True, TEXT_COLOR)
    screen.blit(score_text, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
    screen.blit(record_text, (WIDTH // 2 - 80, HEIGHT // 2 + 20))

    restart_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 80, 100, 50)
    quit_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 80, 100, 50)
    pygame.draw.rect(screen, (100, 180, 100), restart_btn, border_radius=10)
    pygame.draw.rect(screen, (200, 80, 80), quit_btn, border_radius=10)

    restart_text = font_small.render("Заново", True, (255, 255, 255))
    quit_text = font_small.render("Выход", True, (255, 255, 255))
    screen.blit(restart_text, restart_text.get_rect(center=restart_btn.center))
    screen.blit(quit_text, quit_text.get_rect(center=quit_btn.center))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(event.pos):
                    return True
                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def main():
    while True:
        board = [[0] * SIZE for _ in range(SIZE)]
        new_tile(board)
        new_tile(board)
        score = 0
        record = load_record()

        running = True
        while running:
            draw_board(board, score, record)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_record(score)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    moved = False
                    if event.key == pygame.K_LEFT:
                        new_board, gained = move_left(board)
                        moved = new_board != board
                        board = new_board
                    elif event.key == pygame.K_RIGHT:
                        board = rotate_board(rotate_board(board))
                        new_board, gained = move_left(board)
                        board = rotate_board(rotate_board(new_board))
                        moved = True
                    elif event.key == pygame.K_UP:
                        board = rotate_board(rotate_board(rotate_board(board)))
                        new_board, gained = move_left(board)
                        board = rotate_board(new_board)
                        moved = True
                    elif event.key == pygame.K_DOWN:
                        board = rotate_board(board)
                        new_board, gained = move_left(board)
                        board = rotate_board(rotate_board(rotate_board(new_board)))
                        moved = True
                    else:
                        gained = 0

                    if moved:
                        score += gained
                        new_tile(board)
                        record = max(record, score)

                    if not can_move(board):
                        save_record(score)
                        again = game_over_screen(score, record)
                        if again:
                            running = False
                        else:
                            pygame.quit()
                            sys.exit()


if __name__ == "__main__":
    main()

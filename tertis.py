#!/usr/bin/env python3
# TERTIS v3 - Terminal Tetris with Menu, Borders and English Default
# Run: python3 tertis.py

import curses, random, time

# Tetromino shapes
TETROMINOES = {
    'I': [[[1,1,1,1]], [[1],[1],[1],[1]]],
    'O': [[[1,1],[1,1]]],
    'T': [[[0,1,0],[1,1,1]], [[1,0],[1,1],[1,0]], [[1,1,1],[0,1,0]], [[0,1],[1,1],[0,1]]],
    'S': [[[0,1,1],[1,1,0]], [[1,0],[1,1],[0,1]]],
    'Z': [[[1,1,0],[0,1,1]], [[0,1],[1,1],[1,0]]],
    'J': [[[1,0,0],[1,1,1]], [[1,1],[1,0],[1,0]], [[1,1,1],[0,0,1]], [[0,1],[0,1],[1,1]]],
    'L': [[[0,0,1],[1,1,1]], [[1,0],[1,0],[1,1]], [[1,1,1],[1,0,0]], [[1,1],[0,1],[0,1]]]
}

WIDTH, HEIGHT = 10, 20
TICK_BASE = 0.6
BLOCK_STYLES = ["██", "▓▓", "▒▒", "░░", "##", "[]", "<>", "■■"]

# Language packs
LANG = {
    "en": {
        "start": "Start Game",
        "quit": "Quit",
        "lang": "Language",
        "style": "Block Style",
        "paused": "PAUSED",
        "game_over": "GAME OVER",
        "score": "Score",
        "level": "Level",
        "lines": "Lines",
        "next": "Next",
        "press_q": "Press Q to quit",
        "press_p": "Press P to resume",
        "title": "Tertis - Terminal Tetris",
    },
    "tr": {
        "start": "Oyunu Başlat",
        "quit": "Çıkış",
        "lang": "Dil",
        "style": "Kutu Stili",
        "paused": "DURDURULDU",
        "game_over": "OYUN BİTTİ",
        "score": "Puan",
        "level": "Seviye",
        "lines": "Satır",
        "next": "Sıradaki",
        "press_q": "Q: çıkış",
        "press_p": "P: devam",
        "title": "Tertis - Terminal Tetris",
    }
}

KEYS = {
    'left': [curses.KEY_LEFT, ord('a'), ord('A')],
    'right': [curses.KEY_RIGHT, ord('d'), ord('D')],
    'rotate': [curses.KEY_UP, ord('w'), ord('W')],
    'soft_drop': [curses.KEY_DOWN, ord('s'), ord('S')],
    'hard_drop': [ord(' ')],
    'pause': [ord('p'), ord('P')],
    'quit': [ord('q'), ord('Q')]
}

def rotate_shape(shape):
    return [list(row) for row in zip(*shape[::-1])]

class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.rotations = TETROMINOES[kind]
        self.rotation = 0
        self.shape = self.rotations[self.rotation]
        self.x = WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.rotations)
        self.shape = self.rotations[self.rotation]
    def undo_rotate(self):
        self.rotation = (self.rotation - 1) % len(self.rotations)
        self.shape = self.rotations[self.rotation]

def create_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def collides(board, piece, dx=0, dy=0):
    for r, row in enumerate(piece.shape):
        for c, val in enumerate(row):
            if not val: continue
            nx, ny = piece.x + c + dx, piece.y + r + dy
            if nx < 0 or nx >= WIDTH or ny >= HEIGHT: return True
            if ny >= 0 and board[ny][nx]: return True
    return False

def lock_piece(board, piece):
    for r, row in enumerate(piece.shape):
        for c, val in enumerate(row):
            if val:
                by, bx = piece.y + r, piece.x + c
                if 0 <= by < HEIGHT and 0 <= bx < WIDTH:
                    board[by][bx] = 1

def clear_lines(board):
    nb = [row for row in board if any(cell == 0 for cell in row)]
    cleared = HEIGHT - len(nb)
    while len(nb) < HEIGHT:
        nb.insert(0, [0] * WIDTH)
    return nb, cleared

def choose_piece(bag=None):
    if not bag:
        bag = list(TETROMINOES.keys())
        random.shuffle(bag)
    return Piece(bag.pop()), bag

def draw_box(win, y0, x0, h, w):
    win.addstr(y0, x0, "╔" + "═" * (w - 2) + "╗")
    for i in range(1, h - 1):
        win.addstr(y0 + i, x0, "║" + " " * (w - 2) + "║")
    win.addstr(y0 + h - 1, x0, "╚" + "═" * (w - 2) + "╝")

def draw_board(win, board, style, y0=1, x0=1):
    draw_box(win, y0 - 1, x0 - 2, HEIGHT + 2, WIDTH * 2 + 4)
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            ch = style if cell else "  "
            win.addstr(y0 + y, x0 + x * 2, ch)

def draw_piece(win, piece, style, y0=1, x0=1):
    for r, row in enumerate(piece.shape):
        for c, val in enumerate(row):
            if val:
                y = y0 + piece.y + r
                x = x0 + (piece.x + c) * 2
                if 0 <= y < y0 + HEIGHT:
                    win.addstr(y, x, style)

def draw_next(win, next_piece, style, y0, x0, lang):
    win.addstr(y0, x0, f"{lang['next']}:")
    for r, row in enumerate(next_piece.shape):
        for c, val in enumerate(row):
            ch = style if val else "  "
            win.addstr(y0 + 1 + r, x0 + c * 2, ch)

def menu_screen(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    lang_choice = "en"  # default language: English
    style_choice = BLOCK_STYLES[0]
    option = 0
    options = ["start", "lang", "style", "quit"]

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        title = "╔═══════════════════════╗\n║     TERTIS v3.0      ║\n╚═══════════════════════╝"
        for i, line in enumerate(title.splitlines()):
            stdscr.addstr(h // 2 - 6 + i, w // 2 - len(line) // 2, line)
        for i, opt in enumerate(options):
            prefix = "▶ " if i == option else "  "
            if opt == "start":
                text = LANG[lang_choice]["start"]
            elif opt == "quit":
                text = LANG[lang_choice]["quit"]
            elif opt == "lang":
                text = f"{LANG[lang_choice]['lang']}: {lang_choice.upper()}"
            elif opt == "style":
                text = f"{LANG[lang_choice]['style']}: {style_choice}"
            stdscr.addstr(h // 2 - 1 + i, w // 2 - len(text) // 2 - 2, prefix + text)

        stdscr.refresh()
        k = stdscr.getch()
        if k in [curses.KEY_UP, ord('w'), ord('W')]:
            option = (option - 1) % len(options)
        elif k in [curses.KEY_DOWN, ord('s'), ord('S')]:
            option = (option + 1) % len(options)
        elif k in [10, 13, ord(' ')]:  # Enter/space
            if options[option] == "start":
                return lang_choice, style_choice
            elif options[option] == "lang":
                lang_choice = "tr" if lang_choice == "en" else "en"
            elif options[option] == "style":
                idx = (BLOCK_STYLES.index(style_choice) + 1) % len(BLOCK_STYLES)
                style_choice = BLOCK_STYLES[idx]
            elif options[option] == "quit":
                exit()
        elif k in [ord('q'), ord('Q')]:
            exit()

def game(stdscr, lang, style):
    L = LANG[lang]
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    board = create_board()
    bag = []
    cur, bag = choose_piece(bag)
    nxt, bag = choose_piece(bag)
    score, level, lines = 0, 1, 0
    tick = TICK_BASE
    last = time.time()
    paused = False
    over = False

    while True:
        now = time.time()
        key = stdscr.getch()
        if key != -1:
            if key in KEYS['quit']:
                return
            if key in KEYS['pause']:
                paused = not paused
            if paused:
                continue
            if key in KEYS['left'] and not collides(board, cur, dx=-1):
                cur.x -= 1
            elif key in KEYS['right'] and not collides(board, cur, dx=1):
                cur.x += 1
            elif key in KEYS['rotate']:
                cur.rotate()
                if collides(board, cur):
                    cur.undo_rotate()
            elif key in KEYS['soft_drop'] and not collides(board, cur, dy=1):
                cur.y += 1
            elif key in KEYS['hard_drop']:
                while not collides(board, cur, dy=1):
                    cur.y += 1
                lock_piece(board, cur)
                board, clr = clear_lines(board)
                if clr:
                    score += [0, 100, 300, 500, 800][clr] * level
                    lines += clr
                    level = 1 + lines // 10
                    tick = max(0.05, TICK_BASE * (0.85 ** (level - 1)))
                cur, nxt = nxt, choose_piece(bag)[0]
                if collides(board, cur):
                    over = True

        if paused:
            stdscr.erase()
            stdscr.addstr(HEIGHT // 2, 10, L['paused'])
            stdscr.addstr(HEIGHT // 2 + 1, 10, L['press_p'])
            stdscr.refresh()
            time.sleep(0.1)
            continue
        if over:
            stdscr.erase()
            stdscr.addstr(HEIGHT // 2, 10, L['game_over'])
            stdscr.addstr(HEIGHT // 2 + 1, 10, f"{L['score']}: {score}")
            stdscr.addstr(HEIGHT // 2 + 2, 10, L['press_q'])
            stdscr.refresh()
            time.sleep(0.1)
            continue

        if now - last >= tick:
            last = now
            if not collides(board, cur, dy=1):
                cur.y += 1
            else:
                lock_piece(board, cur)
                board, clr = clear_lines(board)
                if clr:
                    score += [0, 100, 300, 500, 800][clr] * level
                    lines += clr
                    level = 1 + lines // 10
                    tick = max(0.05, TICK_BASE * (0.85 ** (level - 1)))
                cur, nxt = nxt, choose_piece(bag)[0]
                if collides(board, cur):
                    over = True

        stdscr.erase()
        stdscr.addstr(0, 2, L['title'])
        draw_board(stdscr, board, style, 2, 4)
        draw_piece(stdscr, cur, style, 2, 4)
        info_x = 4 + WIDTH * 2 + 6
        stdscr.addstr(2, info_x, f"{L['score']}: {score}")
        stdscr.addstr(3, info_x, f"{L['level']}: {level}")
        stdscr.addstr(4, info_x, f"{L['lines']}: {lines}")
        draw_next(stdscr, nxt, style, 6, info_x, L)
        stdscr.refresh()
        time.sleep(0.01)

def main():
    curses.wrapper(lambda stdscr: run_app(stdscr))

def run_app(stdscr):
    lang, style = menu_screen(stdscr)
    game(stdscr, lang, style)

if __name__ == "__main__":
    main()

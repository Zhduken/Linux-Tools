#!/usr/bin/env python3
import curses
import random
import sys

SNAKE_CHAR = "█"
MINE = "*"
FLAG = "⚑"
COVER = "#"
EMPTY = " "
MIN_W, MIN_H = 8, 8
MAX_W, MAX_H = 20, 20

# Dil sözlüğü
LANG = {}
def set_language(lang):
    global LANG
    if lang=="TR":
        LANG = {
            "title":"MAYIN TARLASI",
            "start":"Oyunu Başlat",
            "quit":"Çıkış",
            "controls":"Yön: oklar, Aç: Enter, Bayrak: F, Çıkış: Q",
            "boom":"BOOM! Oyun Bitti.",
            "win":"Tebrikler! Tüm mayınları buldunuz!",
            "small":"Terminal çok küçük. Lütfen büyültüp tekrar deneyin.",
            "prompt":"Çıkmak için Q, tekrar oynamak için herhangi bir tuşa basın",
            "difficulty":"Zorluk Seçin: 1-Kolay 2-Orta 3-Zor"
        }
    else:
        LANG = {
            "title":"MINESWEEPER",
            "start":"Start Game",
            "quit":"Quit",
            "controls":"Arrows: Move, Enter: Open, F: Flag, Q: Quit",
            "boom":"BOOM! Game Over.",
            "win":"Congratulations! You cleared all mines!",
            "small":"Terminal too small. Resize and try again.",
            "prompt":"Press Q to quit, any key to play again",
            "difficulty":"Select Difficulty: 1-Easy 2-Medium 3-Hard"
        }

def create_board(h,w,mines):
    board = [[0 for _ in range(w)] for _ in range(h)]
    positions = [(y,x) for y in range(h) for x in range(w)]
    random.shuffle(positions)
    for y,x in positions[:mines]:
        board[y][x] = MINE
    for y in range(h):
        for x in range(w):
            if board[y][x]==MINE:
                continue
            count=0
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    ny,nx = y+dy,x+dx
                    if 0<=ny<h and 0<=nx<w and board[ny][nx]==MINE:
                        count+=1
            board[y][x]=count
    return board

def draw_board(stdscr, top, left, board, revealed, flags, cursor, game_over=False):
    for y,row in enumerate(board):
        for x,val in enumerate(row):
            ch = COVER if not revealed[y][x] else (str(val) if val!=0 else EMPTY)
            color = curses.A_NORMAL
            if (y,x) in flags:
                ch = FLAG
            if game_over and val==MINE:
                ch = MINE
                color = curses.color_pair(1)
            if (y,x)==cursor:
                stdscr.addstr(top+y,left+x*2,ch,curses.A_REVERSE | color)
            else:
                stdscr.addstr(top+y,left+x*2,ch,color)

def reveal(board, revealed, y, x, h, w):
    if revealed[y][x]:
        return
    revealed[y][x]=True
    if board[y][x]==0:
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                ny,nx = y+dy,x+dx
                if 0<=ny<h and 0<=nx<w:
                    reveal(board,revealed,ny,nx,h,w)

def menu(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    title = LANG["title"]
    options = [LANG["start"], LANG["quit"]]
    selected=0
    while True:
        stdscr.erase()
        stdscr.border()
        stdscr.addstr(sh//2-5,(sw-len(title))//2,title,curses.A_BOLD)
        for i,opt in enumerate(options):
            x = sh//2-1+i*2
            text = f"[ {opt} ]" if i==selected else f"  {opt}  "
            style = curses.A_REVERSE if i==selected else curses.A_NORMAL
            stdscr.addstr(x,(sw-len(text))//2,text,style)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord('w'), ord('W')]:
            selected=(selected-1)%len(options)
        elif key in [curses.KEY_DOWN, ord('s'), ord('S')]:
            selected=(selected+1)%len(options)
        elif key in [curses.KEY_ENTER, ord('\n'), 10, 13]:
            return selected==0

def select_difficulty(stdscr):
    stdscr.clear()
    sh, sw = stdscr.getmaxyx()
    prompt = LANG["difficulty"]
    stdscr.addstr(sh//2, (sw-len(prompt))//2, prompt)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('1')]:
            return 10
        elif key in [ord('2')]:
            return 20
        elif key in [ord('3')]:
            return 35

def game(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1,curses.COLOR_RED,curses.COLOR_BLACK)
    stdscr.keypad(True)
    sh, sw = stdscr.getmaxyx()
    h,w = min(12,sh-6), min(12,sw//2-4)
    h,w = max(h, MIN_H), max(w, MIN_W)
    mines = select_difficulty(stdscr)
    board = create_board(h,w,mines)
    revealed=[[False]*w for _ in range(h)]
    flags=set()
    cursor=[0,0]
    top,left=(sh-h)//2,(sw-w*2)//2

    while True:
        stdscr.clear()
        draw_board(stdscr, top, left, board, revealed, flags, tuple(cursor))
        stdscr.addstr(top+h+1,left,LANG["controls"])
        stdscr.refresh()
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break
        elif key in [curses.KEY_UP, ord('w')]: cursor[0]=max(0,cursor[0]-1)
        elif key in [curses.KEY_DOWN, ord('s')]: cursor[0]=min(h-1,cursor[0]+1)
        elif key in [curses.KEY_LEFT, ord('a')]: cursor[1]=max(0,cursor[1]-1)
        elif key in [curses.KEY_RIGHT, ord('d')]: cursor[1]=min(w-1,cursor[1]+1)
        elif key in [ord('f'), ord('F')]:
            pos=tuple(cursor)
            if pos in flags: flags.remove(pos)
            else: flags.add(pos)
        elif key in [ord('\n'),10,13]:
            y,x=cursor
            if (y,x) in flags or revealed[y][x]: continue
            if board[y][x]==MINE:
                revealed[y][x]=True
                stdscr.clear()
                draw_board(stdscr, top, left, board, [[True]*w for _ in range(h)], flags, (-1,-1), game_over=True)
                stdscr.addstr(top+h+2,left,LANG["boom"])
                stdscr.refresh()
                stdscr.getch()
                break
            reveal(board,revealed,y,x,h,w)
        # kazanma kontrolü
        cells=sum(revealed[y][x] or (y,x) in flags for y in range(h) for x in range(w))
        if cells==h*w:
            stdscr.clear()
            draw_board(stdscr, top, left, board, [[True]*w for _ in range(h)], flags, (-1,-1))
            stdscr.addstr(top+h+2,left,LANG["win"])
            stdscr.refresh()
            stdscr.getch()
            break

def main(stdscr):
    # Dil seçimi
    curses.curs_set(0)
    stdscr.clear()
    sh, sw = stdscr.getmaxyx()
    prompt = "Dil / Language: 1-Türkçe 2-English"
    stdscr.addstr(sh//2, (sw-len(prompt))//2, prompt)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('1')]: set_language("TR"); break
        elif key in [ord('2')]: set_language("EN"); break

    while True:
        start = menu(stdscr)
        if not start: break
        game(stdscr)
        stdscr.clear()
        sh, sw = stdscr.getmaxyx()
        prompt = LANG["prompt"]
        stdscr.addstr(sh//2, max(0,(sw-len(prompt))//2), prompt)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break

if __name__=="__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)


#   ______                  _______               __                __ 
#  /      |                /       \             /  |              /  |
#  $$$$$$/  _______        $$$$$$$  |  ______   _$$ |_     ______  $$ |
##   $$ |  /       \       $$ |__$$ | /      \ / $$   |   /      \ $$ |
#    $$ |  $$$$$$$  |      $$    $$< /$$$$$$  |$$$$$$/    $$$$$$  |$$ |
#    $$ |  $$ |  $$ |      $$$$$$$  |$$    $$ |  $$ | __  /    $$ |$$/ 
#   _$$ |_ $$ |  $$ |      $$ |__$$ |$$$$$$$$/   $$ |/  |/$$$$$$$ | __ 
# /  $$   |$$ |  $$ |      $$    $$/ $$       |  $$  $$/ $$    $$ |/  |
# $$$$$$/ $$/   $$/       $$$$$$$/   $$$$$$$/    $$$$/   $$$$$$$/ $$/ 
                                                                    
      #Beta AŞAMASINDA! / İn Beta!                                                              
                                                                    

#!/usr/bin/env python3
import curses
import random
import time
import sys

SNAKE_CHAR = "█"
FOOD_CHAR = "@"
WALL_CHAR = "|"
CEIL_CHAR = "-"

MIN_W, MIN_H = 20, 10

def draw_border(win, top, left, h, w):
    for x in range(left, left + w):
        win.addch(top, x, CEIL_CHAR)
        win.addch(top + h -1, x, CEIL_CHAR)
    for y in range(top, top + h):
        win.addch(y, left, WALL_CHAR)
        win.addch(y, left + w -1, WALL_CHAR)

def place_food(top, left, h, w, snake):
    while True:
        fy = random.randint(top+1, top+h-2)
        fx = random.randint(left+1, left+w-2)
        if [fy, fx] not in snake:
            return [fy, fx]

def menu(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    title = "TERNAKE"
    options = ["Oyunu Başlat", "Çıkış"]
    selected = 0

    while True:
        stdscr.erase()
        stdscr.border()
        stdscr.addstr(sh//2 -5, (sw-len(title))//2, title, curses.A_BOLD)
        for i,opt in enumerate(options):
            x = sh//2 -1 + i*2
            text = f"[ {opt} ]" if i==selected else f"  {opt}  "
            style = curses.A_REVERSE if i==selected else curses.A_NORMAL
            stdscr.addstr(x, (sw - len(text))//2, text, style)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord('w'), ord('W')]:
            selected = (selected-1) % len(options)
        elif key in [curses.KEY_DOWN, ord('s'), ord('S')]:
            selected = (selected+1) % len(options)
        elif key in [curses.KEY_ENTER, ord('\n'), 10, 13]:
            return selected==0  # True = Başlat, False = Çıkış

def game(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    sh, sw = stdscr.getmaxyx()
    h, w = min(25, sh-6), min(60, sw-10)
    if h<MIN_H or w<MIN_W:
        stdscr.clear()
        msg = "Terminal çok küçük. Lütfen büyültüp tekrar deneyin."
        stdscr.addstr(sh//2, max(0,(sw-len(msg))//2), msg)
        stdscr.refresh()
        time.sleep(3)
        return
    top, left = (sh-h)//2, (sw-w)//2
    snake = [[top+h//2, left+w//2 + i] for i in range(3,0,-1)]
    direction = curses.KEY_RIGHT
    opposites = {curses.KEY_UP:curses.KEY_DOWN, curses.KEY_DOWN:curses.KEY_UP,
                 curses.KEY_LEFT:curses.KEY_RIGHT, curses.KEY_RIGHT:curses.KEY_LEFT}
    food = place_food(top, left, h, w, snake)
    score = 0
    speed = 120

    while True:
        stdscr.erase()
        draw_border(stdscr, top, left, h, w)
        # Yemek
        stdscr.addch(food[0], food[1], FOOD_CHAR)
        # Yılan
        for y,x in snake:
            stdscr.addch(y, x, SNAKE_CHAR)
        # Skor
        score_text = f"Puan: {score}"
        stdscr.addstr(top+h, max(0,left+(w-len(score_text))//2), score_text)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            if opposites.get(direction) != key:
                direction = key
        elif key in [ord('q'), ord('Q')]:
            break
        head = snake[0].copy()
        if direction==curses.KEY_UP:
            head[0]-=1
        elif direction==curses.KEY_DOWN:
            head[0]+=1
        elif direction==curses.KEY_LEFT:
            head[1]-=1
        elif direction==curses.KEY_RIGHT:
            head[1]+=1
        # Çarpışma
        if head in snake or head[0]<=top or head[0]>=top+h-1 or head[1]<=left or head[1]>=left+w-1:
            stdscr.addstr(top+h//2, left+w//2-5, "OYUN BİTTİ!")
            stdscr.addstr(top+h//2+2, left+w//2-10, f"Son Puan: {score}")
            stdscr.refresh()
            time.sleep(2)
            break
        snake.insert(0, head)
        if head==food:
            score+=1
            if score%5==0 and speed>40:
                speed=max(40,int(speed*0.9))
            food = place_food(top, left, h, w, snake)
        else:
            snake.pop()
        time.sleep(speed/1000)

def main(stdscr):
    curses.curs_set(0)
    while True:
        start = menu(stdscr)
        if not start:
            break
        game(stdscr)
        stdscr.clear()
        sh, sw = stdscr.getmaxyx()
        prompt = "Çıkmak için 'q', tekrar oynamak için herhangi bir tuşa basın"
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

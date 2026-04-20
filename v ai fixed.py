import tkinter as tk
import random

#CELL = 60
LINE = 3
#SIZE = CELL * 9
SIZE = 480   # 固定畫布
CELL = SIZE // 9

board = [["" for _ in range(9)] for _ in range(9)]
big_board = [["" for _ in range(3)] for _ in range(3)]
allowed_block = None

player = "O"
game_over = False
game_started = False

# ===== UI =====
root = tk.Tk()
root.title("Ultimate OX")

canvas = tk.Canvas(root, width=SIZE, height=SIZE)
canvas.pack()

label = tk.Label(root, text="Turn: O", font=("Arial",16))
label.pack()

score_label = tk.Label(root, text="O: 0   X: 0", font=("Arial",14))
score_label.pack()

mode_var = tk.StringVar(value="AI")
mode_menu = tk.OptionMenu(root, mode_var, "AI", "PVP")
mode_menu.pack()

difficulty_var = tk.StringVar(value="Medium")
difficulty_menu = tk.OptionMenu(root, difficulty_var, "Easy", "Medium", "Medium+", "Hard")
difficulty_menu.pack()

o_mode_var = tk.StringVar(value="Player")
o_menu = tk.OptionMenu(root, o_mode_var, "Player", "AI")
o_menu.pack()




# ===== 畫棋盤 =====
def draw_grid():
    canvas.delete("grid")
    for i in range(10):
        w = LINE if i % 3 == 0 else 1
        canvas.create_line(i*CELL, 0, i*CELL, SIZE, width=w, tags="grid")
        canvas.create_line(0, i*CELL, SIZE, i*CELL, width=w, tags="grid")

# ===== highlight =====
def highlight():
    canvas.delete("highlight")

    if game_over:
        return

    if allowed_block is None:
        for i in range(9):
            for j in range(9):
                if board[i][j] == "":
                    x1,y1 = j*CELL, i*CELL
                    canvas.create_rectangle(x1,y1,x1+CELL,y1+CELL,
                        fill="#fff7a8", outline="", tags="highlight")
    else:
        br, bc = allowed_block
        for i in range(3):
            for j in range(3):
                r = br*3+i
                c = bc*3+j
                if board[r][c] == "":
                    x1,y1 = c*CELL, r*CELL
                    canvas.create_rectangle(x1,y1,x1+CELL,y1+CELL,
                        fill="#fff7a8", outline="", tags="highlight")

    canvas.tag_lower("highlight")

# ===== 畫棋子 =====
def draw_pieces():
    canvas.delete("pieces")
    for i in range(9):
        for j in range(9):
            if board[i][j] != "":
                canvas.create_text(j*CELL+CELL//2, i*CELL+CELL//2,
                                   text=board[i][j], font=("Arial",24), tags="pieces")

# ===== 小格勝負 =====
def check_small_win(br, bc, b=None):
    if b is None: b = board
    sr, sc = br*3, bc*3

    for i in range(3):
        if b[sr+i][sc]==b[sr+i][sc+1]==b[sr+i][sc+2]!="":
            return b[sr+i][sc]
        if b[sr][sc+i]==b[sr+1][sc+i]==b[sr+2][sc+i]!="":
            return b[sr][sc+i]

    if b[sr][sc]==b[sr+1][sc+1]==b[sr+2][sc+2]!="":
        return b[sr][sc]
    if b[sr][sc+2]==b[sr+1][sc+1]==b[sr+2][sc]!="":
        return b[sr][sc+2]

    return None

# ===== 是否滿 =====
def is_block_full(br, bc):
    for i in range(3):
        for j in range(3):
            if board[br*3+i][bc*3+j] == "":
                return False
    return True

# ===== 分數 =====
def count_score():
    o = x = 0
    for br in range(3):
        for bc in range(3):
            sr, sc = br*3, bc*3

            for i in range(3):
                if board[sr+i][sc]==board[sr+i][sc+1]==board[sr+i][sc+2]!="":
                    if board[sr+i][sc]=="O": o+=1
                    else: x+=1
                if board[sr][sc+i]==board[sr+1][sc+i]==board[sr+2][sc+i]!="":
                    if board[sr][sc+i]=="O": o+=1
                    else: x+=1

            if board[sr][sc]==board[sr+1][sc+1]==board[sr+2][sc+2]!="":
                if board[sr][sc]=="O": o+=1
                else: x+=1
            if board[sr][sc+2]==board[sr+1][sc+1]==board[sr+2][sc]!="":
                if board[sr][sc+2]=="O": o+=1
                else: x+=1
    return o, x

# ===== Minimax 評分 =====
def evaluate(b):
    o,x = count_score(b)
    return x - o  # AI = X，越大越好

# ===== Minimax =====
def minimax(b, allowed, depth, maximizing):
    # 遊戲結束或深度
    o,x = count_score(b)
    if depth==0 or all(b[i][j]!="" for i in range(9) for j in range(9)):
        return evaluate(b), None

    moves=[]
    if allowed is None:
        moves=[(i,j) for i in range(9) for j in range(9) if b[i][j]==""]

    else:
        br, bc = allowed
        for i in range(3):
            for j in range(3):
                r,c = br*3+i, bc*3+j
                if b[r][c]=="": moves.append((r,c))
    if not moves: return evaluate(b), None

    best_move = None
    if maximizing:
        max_eval = -float("inf")
        for r,c in moves:
            b2 = copy.deepcopy(b)
            b2[r][c]="X"
            nr,nc = r%3,c%3
            next_allowed = None if is_block_full(nr,nc,b2) else (nr,nc)
            eval_score,_ = minimax(b2, next_allowed, depth-1, False)
            if eval_score>max_eval:
                max_eval=eval_score
                best_move=(r,c)
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for r,c in moves:
            b2 = copy.deepcopy(b)
            b2[r][c]="O"
            nr,nc = r%3,c%3
            next_allowed = None if is_block_full(nr,nc,b2) else (nr,nc)
            eval_score,_ = minimax(b2, next_allowed, depth-1, True)
            if eval_score<min_eval:
                min_eval=eval_score
                best_move=(r,c)
        return min_eval, best_move

# ===== 點擊 =====
def click(event):
    global player, allowed_block, game_over
    if not game_started or game_over: return
    c = event.x // CELL
    r = event.y // CELL
    if board[r][c] != "": return
    if allowed_block and (r//3, c//3) != allowed_block: return

    board[r][c] = player
    br, bc = r//3, c//3
    if big_board[br][bc] == "":
        winner = check_small_win(br, bc)
        if winner: big_board[br][bc] = winner
    nr,nc = r%3,c%3
    allowed_block = None if is_block_full(nr,nc) else (nr,nc)

    draw_pieces()
    o,x = count_score()
    score_label.config(text=f"O: {o}   X: {x}")

    full = all(board[i][j]!="" for i in range(9) for j in range(9))
    if full:
        game_over=True
        if o>x: label.config(text="O wins (more lines)")
        elif x>o: label.config(text="X wins (more lines)")
        else: label.config(text="Draw")
        highlight()
        return

    player="X" if player=="O" else "O"
    label.config(text="Turn: "+player)
    highlight()

    if player=="X" and mode_var.get()=="AI":
        root.after(100, ai_move)

# ===== AI =====
import copy

def ai_move():
    global player, allowed_block

    # 找可下位置
    moves=[]
    if allowed_block is None:
        moves=[(i,j) for i in range(9) for j in range(9) if board[i][j]==""]

    else:
        br, bc = allowed_block
        for i in range(3):
            for j in range(3):
                r,c = br*3+i, bc*3+j
                if board[r][c]=="": moves.append((r,c))
    if not moves: return

    diff = difficulty_var.get()
    
    if diff=="Hard":
        _, (r,c) = minimax(board, allowed_block, 2, True)  # Hard
    elif diff=="Medium":
        best_score = -float('inf')
        best_moves = []
        for r,c in moves:
            score = 0
            b_copy = copy.deepcopy(board)
            b_copy[r][c]="X"
            br, bc = r//3, c//3
            winner = check_small_win(br, bc, b_copy)
            if winner=="X":
                score += 10  # 自己贏
            # 阻止對手
            b_copy[r][c]="O"
            winner_o = check_small_win(br, bc, b_copy)
            if winner_o=="O":
                score += 7
            # 簡單評估形成連線的潛力
            # 橫
            sr, sc = br*3, bc*3
            for i in range(3):
                row = [b_copy[sr+i][sc+j] for j in range(3)]
                if row.count("X")==2 and row.count("")==1:
                    score += 8
                if row.count("O")==2 and row.count("")==1:
                    score += 5
            # 直
            for i in range(3):
                col = [b_copy[sr+j][sc+i] for j in range(3)]
                if col.count("X")==2 and col.count("")==1:
                    score += 8
                if col.count("O")==2 and col.count("")==1:
                    score += 5
            # 斜 ↘
            diag1 = [b_copy[sr+i][sc+i] for i in range(3)]
            if diag1.count("X")==2 and diag1.count("")==1:
                score += 8
            if diag1.count("O")==2 and diag1.count("")==1:
                score += 5
            # 斜 ↙
            diag2 = [b_copy[sr+i][sc+2-i] for i in range(3)]
            if diag2.count("X")==2 and diag2.count("")==1:
                score += 8
            if diag2.count("O")==2 and diag2.count("")==1:
                score += 5

            if score > best_score:
                best_score = score
                best_moves = [(r,c)]
            elif score == best_score:
                best_moves.append((r,c))

        r,c = random.choice(best_moves)  # 選其中一個最高分

    else:
        r,c = random.choice(moves)  # Easy 隨機
 # 落子
    board[r][c]="X"
    br, bc = r//3, c//3
    if big_board[br][bc]=="":
        winner=check_small_win(br, bc)
        if winner: big_board[br][bc]=winner
    nr,nc = r%3,c%3
    allowed_block = None if is_block_full(nr,nc) else (nr,nc)
    player="O"
    label.config(text="Turn: O")
    draw_pieces()
    highlight()

    # 落子
    board[r][c]="X"
    br, bc = r//3, c//3
    if big_board[br][bc]=="":
        winner=check_small_win(br, bc)
        if winner: big_board[br][bc]=winner
    nr,nc = r%3,c%3
    allowed_block = None if is_block_full(nr,nc) else (nr,nc)
    player="O"
    label.config(text="Turn: O")
    draw_pieces()
    highlight()
def ai_move_O():
    moves = get_moves()
    if not moves: return
    r,c = random.choice(moves)
    place(r,c)

# ===== 結束 =====
def end_game(o,x):
    global game_over
    game_over = True

    if o > x:
        label.config(text="O wins")
    elif x > o:
        label.config(text="X wins")
    else:
        label.config(text="Draw")

    canvas.delete("highlight")

    resign_btn.pack_forget()
    restart_btn.pack()

# ===== resign =====
def resign():
    global game_over
    game_over = True

    if player=="O":
        label.config(text="O resigns → X wins")
    else:
        label.config(text="X resigns → O wins")

    canvas.delete("highlight")

    resign_btn.pack_forget()
    restart_btn.pack()

# ===== 控制 =====
def start_game():
    global game_started, player

    game_started = True
    player = "O"

    draw_grid()
    highlight()

    label.config(text="Turn: O")

    # 🔒 鎖設定
    start_btn.config(state="disabled")
    mode_menu.config(state="disabled")
    difficulty_menu.config(state="disabled")
    o_menu.config(state="disabled")

    resign_btn.pack()
    restart_btn.pack_forget()

    if o_mode_var.get()=="AI":
        root.after(200, ai_move_O)

def reset():
    global board, allowed_block, player, game_over, game_started

    board = [["" for _ in range(9)] for _ in range(9)]
    allowed_block = None
    player = "O"
    game_over = False
    game_started = False

    draw_grid()
    draw_pieces()
    highlight()

    label.config(text="Turn: O")
    score_label.config(text="O: 0   X: 0")

    # 🔓 解鎖設定
    start_btn.config(state="normal")
    mode_menu.config(state="normal")
    difficulty_menu.config(state="normal")
    o_menu.config(state="normal")

    restart_btn.pack_forget()

# ===== 按鈕 =====
start_btn = tk.Button(root, text="Start", command=start_game)
start_btn.pack()

resign_btn = tk.Button(root, text="Resign", command=resign)
restart_btn = tk.Button(root, text="Restart", command=reset)

canvas.bind("<Button-1>", click)

draw_grid()
highlight()

root.mainloop()

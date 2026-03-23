import os
import time

ROWS = 6
COLS = 7

def clear_screen():
    """Clears the terminal screen for animation."""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_board():
    """Creates an empty 6x7 matrix."""
    return [[' ' for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board):
    """Prints the board to the terminal."""
    print("\n  1   2   3   4   5   6   7")
    print("|---|---|---|---|---|---|---|")
    for row in board:
        print("| " + " | ".join(row) + " |")
        print("|---|---|---|---|---|---|---|")
    print()

def get_board_state(board):
    """Returns an immutable tuple of the board to track history for Rule 3."""
    return tuple(tuple(row) for row in board)

def is_valid_location(board, col):
    """Checks if the chosen column has empty space for a drop."""
    return board[0][col] == ' '

def is_valid_pop(board, col, piece):
    """Checks if the player can pop a piece from the bottom of the column."""
    return board[ROWS - 1][col] == piece

def get_next_open_row(board, col):
    """Finds the lowest available row in the column."""
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == ' ':
            return r

def animate_drop(board, col, final_row, piece):
    """Animates the piece falling down the column."""
    for r in range(final_row):
        board[r][col] = piece
        clear_screen()
        print("Connect 4 - Dropping Piece...")
        print_board(board)
        time.sleep(0.1) 
        board[r][col] = ' '
    
    board[final_row][col] = piece
    clear_screen()
    print("Connect 4 - Game in Progress...")
    print_board(board)

def animate_pop(board, col):
    """Animates the popping of the bottom piece and the column falling down ONE by ONE."""
    board[ROWS - 1][col] = ' '
    clear_screen()
    print("Connect 4 - Popping Piece Out...")
    print_board(board)
    time.sleep(0.4) 
    
    for r in range(ROWS - 1, 0, -1):
        if board[r - 1][col] != ' ':
            board[r][col] = board[r - 1][col]
            board[r - 1][col] = ' ' 
            
            clear_screen()
            print("Connect 4 - Pieces Falling...")
            print_board(board)
            time.sleep(0.2) 
            
    clear_screen()
    print("Connect 4 - Pieces Settled!")
    print_board(board)
    time.sleep(0.2)

def check_win(board, piece):
    """Checks all possible winning combinations."""
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

def is_board_full(board):
    """Checks if the board is completely filled."""
    for c in range(COLS):
        if board[0][c] == ' ':
            return False
    return True

def play_game():
    board = create_board()
    game_over = False
    turn = 0
    # Modificado de dicionário para lista para criar uma janela deslizante de 6 posições
    state_history = [] 

    clear_screen()
    print("Welcome to Connect 4 (Pop Out Variant - Official Rules)!")
    print_board(board)

    while not game_over:
        piece = 'X' if turn == 0 else 'O'
        player_name = "Player 1 (X)" if turn == 0 else "Player 2 (O)"
        opponent_piece = 'O' if turn == 0 else 'X'
        opponent_name = "Player 2 (O)" if turn == 0 else "Player 1 (X)"

        # RULE 2: Board is full logic
        board_full = is_board_full(board)

        try:
            if board_full:
                choice = input(f"⚠️ BOARD FULL! {player_name}, type 'p1'-'p7' to pop, or 'draw' to end the game: ").strip().lower()
                if choice == 'draw':
                    print("Game declared a draw by mutual agreement!")
                    game_over = True
                    break
                if not choice.startswith('p'):
                    print("Invalid input. The board is full, you MUST pop or draw.")
                    continue
            else:
                choice = input(f"{player_name}, enter 1-7 to drop, or 'p1'-'p7' to pop: ").strip().lower()
            
            is_pop = choice.startswith('p')
            if is_pop:
                col = int(choice[1:]) - 1
            else:
                col = int(choice) - 1

        except ValueError:
            print("Invalid input. Please try again.")
            continue

        if col < 0 or col > 6:
            print("Invalid column. Choose a number between 1 and 7.")
            continue

        if is_pop:
            if is_valid_pop(board, col, piece):
                animate_pop(board, col)
                
                current_player_wins = check_win(board, piece)
                opponent_wins = check_win(board, opponent_piece)
                
                # RULE 1: Simultaneous four-in-rows
                if current_player_wins and opponent_wins:
                    print(f"Wow! Both aligned 4. By Rule 1, the popping player ({player_name}) is the winner!")
                    game_over = True
                elif current_player_wins:
                    print(f"🎉 Congratulations! {player_name} wins the game!")
                    game_over = True
                elif opponent_wins:
                    print(f"Oops! You helped {opponent_name} win!")
                    game_over = True
                
                turn += 1
                turn = turn % 2
            else:
                print("❌ Invalid pop. You can only pop your OWN piece from the VERY BOTTOM.")
                continue 
        
        else:
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                animate_drop(board, col, row, piece)

                if check_win(board, piece):
                    print(f"🎉 Congratulations! {player_name} wins the game!")
                    game_over = True

                turn += 1
                turn = turn % 2
            else:
                print("❌ This column is full. Please choose another one.")
                continue 
        
        # RULE 3: Threefold repetition handling (SLIDING WINDOW)
        if not game_over:
            current_state = get_board_state(board)
            state_history.append(current_state)
            
            # Limita o histórico a 6 estados máximos. Quando o 7º entra, remove o 1º (índice 0).
            if len(state_history) > 6:
                state_history.pop(0)
            
            # Conta quantas vezes o estado ATUAL aparece nos últimos 6 armazenados
            if state_history.count(current_state) >= 3:
                print("\n⚠️ THREEFOLD REPETITION DETECTED ⚠️")
                draw_choice = input("Either player can declare a draw. Type 'draw' to end, or press Enter to continue: ").strip().lower()
                if draw_choice == 'draw':
                    print("Game drawn due to threefold repetition!")
                    game_over = True
                # Se derem Enter, o jogo simplesmente volta ao topo do While Loop e continua!

if __name__ == "__main__":
    play_game()
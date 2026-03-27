# 04 - source/01 - game/ui.py
import os
import time

class UI:
    @staticmethod
    def clear_screen():
        """Limpa o ecrã do terminal para a animação."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_board(board):
        """Imprime o tabuleiro no terminal."""
        print("\n  1   2   3   4   5   6   7")
        print("|---|---|---|---|---|---|---|")
        for row in board.grid:
            print("| " + " | ".join(row) + " |")
            print("|---|---|---|---|---|---|---|") 
        print()

    @staticmethod
    def animate_drop(board, col, final_row, piece):
        """Anima a peça a cair pela coluna abaixo."""
        for r in range(final_row):
            board.grid[r][col] = piece
            UI.clear_screen()
            print("Connect 4 - Dropping Piece...")
            UI.print_board(board)
            time.sleep(0.1) 
            board.grid[r][col] = ' '
        
        # A peça assenta na sua posição final
        board.grid[final_row][col] = piece
        UI.clear_screen()
        print("Connect 4 - Game in Progress...")
        UI.print_board(board)

    @staticmethod
    def animate_pop(board, col):
        """Anima a remoção da peça da base e a queda das restantes."""
        board.grid[board.rows - 1][col] = ' '
        UI.clear_screen()
        print("Connect 4 - Popping Piece Out...")
        UI.print_board(board)
        time.sleep(0.4) 
        
        for r in range(board.rows - 1, 0, -1):
            if board.grid[r - 1][col] != ' ':
                board.grid[r][col] = board.grid[r - 1][col]
                board.grid[r - 1][col] = ' ' 
                
                UI.clear_screen()
                print("Connect 4 - Pieces Falling...")
                UI.print_board(board)
                time.sleep(0.2) 
                
        UI.clear_screen()
        print("Connect 4 - Pieces Settled!")
        UI.print_board(board)
        time.sleep(0.2)
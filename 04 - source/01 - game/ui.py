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
        """Anima a peça a cair pela coluna usando uma cópia visual temporária."""
        temp_board = board.copy() # Cria um clone apenas para a animação
        
        for r in range(final_row):
            temp_board.grid[r][col] = piece
            UI.clear_screen()
            print("Connect 4 - Dropping Piece...")
            UI.print_board(temp_board)
            time.sleep(0.1) 
            temp_board.grid[r][col] = ' '
            

    @staticmethod
    def animate_pop(board, col):
        """Anima a remoção da peça usando uma cópia visual temporária."""
        temp_board = board.copy() # Cria um clone apenas para a animação
        temp_board.grid[temp_board.rows - 1][col] = ' '
        
        UI.clear_screen()
        print("Connect 4 - Popping Piece Out...")
        UI.print_board(temp_board)
        time.sleep(0.4) 
        
        for r in range(temp_board.rows - 1, 0, -1):
            if temp_board.grid[r - 1][col] != ' ':
                temp_board.grid[r][col] = temp_board.grid[r - 1][col]
                temp_board.grid[r - 1][col] = ' ' 
                
                UI.clear_screen()
                print("Connect 4 - Pieces Falling...")
                UI.print_board(temp_board)
                time.sleep(0.2) 
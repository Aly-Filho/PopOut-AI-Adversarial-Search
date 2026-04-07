import os
import time

class UI:
    @staticmethod
    def clear_screen():
        """Limpa o ecrã do terminal."""
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
    def render(board, message="Connect 4 - Pop Out Variant."):
        """Centraliza a atualização do ecrã: limpa, mostra mensagem e imprime o tabuleiro."""
        UI.clear_screen()
        # Como o message agora tem um valor padrão, imprimimos sempre algo no topo.
        print(message)
        UI.print_board(board)

    @staticmethod
    def animate_drop(board, col, final_row, piece):
        """Anima a peça a cair pela coluna usando uma cópia visual temporária."""
        temp_board = board.copy() 
        
        for r in range(final_row):
            temp_board.grid[r][col] = piece
            UI.render(temp_board, "Connect 4 - Dropping Piece...")
            time.sleep(0.1) 
            temp_board.grid[r][col] = ' '
            
    @staticmethod
    def animate_pop(board, col):
        """Anima a remoção da peça usando uma cópia visual temporária."""
        temp_board = board.copy() 
        temp_board.grid[temp_board.rows - 1][col] = ' '
        
        UI.render(temp_board, "Connect 4 - Popping Piece Out...")
        time.sleep(0.4) 
        
        for r in range(temp_board.rows - 1, 0, -1):
            if temp_board.grid[r - 1][col] != ' ':
                temp_board.grid[r][col] = temp_board.grid[r - 1][col]
                temp_board.grid[r - 1][col] = ' ' 
                
                UI.render(temp_board, "Connect 4 - Pieces Falling...")
                time.sleep(0.2)
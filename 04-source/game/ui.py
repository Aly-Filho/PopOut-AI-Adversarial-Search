import os
import time

class UI:
    @staticmethod
    def clear_screen():
        """Limpa o ecrã do terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def wait_for_enter(message="\nPress Enter to return..."):
        """Pausa o jogo até o utilizador pressionar Enter."""
        input(message)

    @staticmethod
    def display_rules():
        UI.clear_screen()
        print("===============================================================")
        print("                      POPOUT - RULES                           ")
        print("===============================================================")
        print("1. Standard Connect 4 rules apply: get 4 pieces in a row")
        print("   (horizontal, vertical, or diagonal) to win.")
        print("2. DROP: On your turn, you can drop a piece into the top of")
        print("   any column that is not full.")
        print("3. POP OUT: Instead of dropping, you can choose to remove")
        print("   (pop) one of YOUR OWN pieces from the VERY BOTTOM of a")
        print("   column. The pieces above it will drop down one space.")
        print("4. SIMULTANEOUS WIN (Rule 1): If popping a piece creates a")
        print("   win for both players, the player who popped the piece wins!")
        print("5. FULL BOARD (Rule 2): If the board is completely full, the")
        print("   current player must either pop a piece or declare a draw.")
        print("6. THREEFOLD REPETITION (Rule 3): If the exact same board state")
        print("   occurs 3 times, either player can declare a draw.")
        print("===============================================================")

    @staticmethod
    def display_credits():
        UI.clear_screen()
        print("===============================================================")
        print("                        CREDITS                                ")
        print("===============================================================")
        print(" Game developed by: Aly, Rafael and Victor.")
        print(" Variant: PopOut (Official Rules)")
        print(" Course/Context: Artificial Intelligence & Data Science")
        print("===============================================================")

    @staticmethod
    def display_main_menu():
        UI.clear_screen()
        print("===================================")
        print("  Welcome to PopOut on terminal!   ")
        print("===================================")
        print(" 1 - Play")
        print(" 2 - Rules")
        print(" 3 - Credits")
        print(" 4 - Exit Game")
        print("===================================")

    @staticmethod
    def display_play_menu():
        UI.clear_screen()
        print("===================================")
        print("           SELECT MODE             ")
        print("===================================")
        print(" 1 - Human Vs Human")
        print(" 2 - Human vs AI")
        print(" 3 - AI vs AI")
        print(" 4 - Back")
        print("===================================")

    @staticmethod
    def display_ai_menu(player_label):
        print(f"\n===================================")
        print(f" Select Algorithm for {player_label} ")
        print(f"===================================")
        print(" 1 - MCTS Heuristic (With heuristics and optimizations)")
        print(" 2 - MCTS Vanilla (Standard)")
        print(" 3 - MCTS Multi-Expansion (N-Children)")
        print("===================================")

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


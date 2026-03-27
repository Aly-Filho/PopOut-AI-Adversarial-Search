# 04 - source/01 - game/main.py
from board import Board
from ui import UI
import sys
import time

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
    input("\nPress Enter to return to the main menu...")

def display_credits():
    UI.clear_screen()
    print("===============================================================")
    print("                        CREDITS                                ")
    print("===============================================================")
    print(" Game developed by: Aly, Rafael and Victor.")
    print(" Variant: PopOut (Official Rules)")
    print(" Course/Context: Artificial Intelligence & Data Science")
    print("===============================================================")
    input("\nPress Enter to return to the main menu...")

def play_menu():
    while True:
        UI.clear_screen()
        print("===================================")
        print("           SELECT MODE             ")
        print("===================================")
        print(" 1 - Human Vs Human")
        print(" 2 - Human vs AI")
        print(" 3 - AI vs AI")
        print(" 4 - Back")
        print("===================================")
        
        choice = input("Select an option (1-4): ").strip()

        if choice == '1':
            play_game() # Inicia o jogo normal
        elif choice == '2':
            print("\n🤖 AI integration is coming soon!")
            time.sleep(2)
        elif choice == '3':
            print("\n🤖 AI vs AI is coming soon!")
            time.sleep(2)
        elif choice == '4':
            break # Sai do loop e volta ao menu principal
        else:
            print("\n❌ Invalid choice! Please select 1, 2, 3, or 4.")
            time.sleep(1)

def main_menu():
    while True:
        UI.clear_screen()
        print("===================================")
        print("  Welcome to PopOut on terminal!   ")
        print("===================================")
        print(" 1 - Play")
        print(" 2 - Rules")
        print(" 3 - Credits")
        print(" 4 - Exit Game")
        print("===================================")
        
        choice = input("Select an option (1-4): ").strip()

        if choice == '1':
            play_menu()
        elif choice == '2':
            display_rules()
        elif choice == '3':
            display_credits()
        elif choice == '4':
            UI.clear_screen()
            print("Thanks for playing! Goodbye.\n")
            sys.exit()
        else:
            print("\n❌ Invalid choice! Please select 1, 2, 3, or 4.")
            time.sleep(1)

def play_game():
    """A função principal do jogo com a nova lógica de dicionário para empates."""
    board = Board()
    game_over = False
    turn = 0
    
    # 1. Inicializa o histórico como um dicionário
    state_history = {} 
    
    # 2. Registra o estado inicial (tabuleiro vazio) com valor 1
    initial_state = board.get_state()
    state_history[initial_state] = 1

    UI.clear_screen()
    print("Starting Match: Human vs Human!")
    UI.print_board(board)

    while not game_over:
        piece = 'X' if turn == 0 else 'O'
        player_name = "Player 1 (X)" if turn == 0 else "Player 2 (O)"
        opponent_piece = 'O' if turn == 0 else 'X'
        opponent_name = "Player 2 (O)" if turn == 0 else "Player 1 (X)"

        board_full = board.is_full()

        try:
            if board_full:
                choice = input(f"⚠️ BOARD FULL! {player_name}, type 'p1'-'p7' to pop, or 'draw' to end: ").strip().lower()
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
            if board.is_valid_pop(col, piece):
                UI.animate_pop(board, col)
                
                current_player_wins = board.check_win(piece)
                opponent_wins = board.check_win(opponent_piece)
                
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
            if board.is_valid_drop(col):
                row = board.get_next_open_row(col)
                UI.animate_drop(board, col, row, piece)

                if board.check_win(piece):
                    print(f"🎉 Congratulations! {player_name} wins the game!")
                    game_over = True

                turn += 1
                turn = turn % 2
            else:
                print("❌ This column is full. Please choose another one.")
                continue 
        
        # 3. Nova lógica de registro de estado no dicionário
        if not game_over:
            current_state = board.get_state()
            
            # Adiciona 1 à contagem deste estado específico. Se não existir, começa do 0 e soma 1.
            state_history[current_state] = state_history.get(current_state, 0) + 1
            
            # Se o estado atingiu 3 repetições
            if state_history[current_state] >= 3:
                print("\n⚠️ THREEFOLD REPETITION DETECTED ⚠️")
                draw_choice = input("Either player can declare a draw. Type 'draw' to end, or press Enter to continue: ").strip().lower()
                if draw_choice == 'draw':
                    print("Game drawn due to threefold repetition!")
                    game_over = True

    # Quando o jogo acaba, pede para pressionar Enter para voltar ao menu
    input("\nPress Enter to return to the play menu...")

if __name__ == "__main__":
    main_menu() # O ponto de entrada agora é o menu principal!
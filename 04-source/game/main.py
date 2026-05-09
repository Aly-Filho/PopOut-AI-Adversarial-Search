from board import Board
from ui import UI
import sys
import time
from models.mcts_heuristics import mcts_best_move
from models.mcts_vanilla import mcts_vanilla_best_move
from models.mcts_multi import mcts_multi_expansion_best_move

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

# ---- NOVO MENU DE SELEÇÃO DE IA ----
def select_ai_menu(player_label):
    while True:
        print(f"\n===================================")
        print(f" Select Algorithm for {player_label} ")
        print(f"===================================")
        print(" 1 - MCTS Heuristic (With heuristics and optimizations)")
        print(" 2 - MCTS Vanilla (Standard)")
        print(" 3 - MCTS Multi-Expansion (N-Children)")
        print("===================================")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == '1':
            return mcts_best_move, "MCTS Heuristic"
        elif choice == '2':
            return mcts_vanilla_best_move, "MCTS Vanilla"
        elif choice == '3':
            return mcts_multi_expansion_best_move, "MCTS Multi-Expansion"
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

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
            play_game("Human", "Human")
        elif choice == '2':
            # Pergunta qual IA vai jogar contra o Humano
            ai_func, ai_name = select_ai_menu("the AI")
            play_game("Human", "AI", p2_func=ai_func, p2_name=ai_name)
        elif choice == '3':
            # Pergunta qual IA será o Player 1 e qual será o Player 2
            UI.clear_screen()
            ai1_func, ai1_name = select_ai_menu("AI 1 (X)")
            ai2_func, ai2_name = select_ai_menu("AI 2 (O)")
            play_game("AI", "AI", p1_func=ai1_func, p1_name=ai1_name, p2_func=ai2_func, p2_name=ai2_name)
        elif choice == '4':
            break 
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

# ---- FUNÇÃO PLAY_GAME ADAPTADA PARA RECEBER AS FUNÇÕES DE IA ----
def play_game(player1_type, player2_type, p1_func=None, p1_name="Player 1", p2_func=None, p2_name="Player 2"):

    board = Board()
    game_over = False
    
    state_history = {} 
    initial_state = board.get_state()
    state_history[initial_state] = 1

    UI.clear_screen()
    
    # Formatação bonita dos nomes de quem vai jogar
    p1_display = "Human" if player1_type == "Human" else p1_name
    p2_display = "Human" if player2_type == "Human" else p2_name
    print(f"Starting Match: {p1_display} (X) vs {p2_display} (O)!")
    
    UI.render(board)

    while not game_over:
  
        piece = board.current_player
        opponent_piece = 'O' if piece == 'X' else 'X'
        
        # Define quem está a jogar neste momento
        if piece == 'X':
            current_player_type = player1_type
            current_player_display = f"{p1_display} (X)"
            current_ai_func = p1_func
        else:
            current_player_type = player2_type
            current_player_display = f"{p2_display} (O)"
            current_ai_func = p2_func

        opponent_display = f"{p2_display} (O)" if piece == 'X' else f"{p1_display} (X)"

        current_state = board.get_state()
        if state_history.get(current_state, 0) >= 3:
            print("\n⚠️ THREEFOLD REPETITION DETECTED ⚠️")
            if current_player_type == "Human":
                draw_choice = input(f"This board state has occurred 3 times. {current_player_display}, type 'draw' to end, or press Enter to play: ").strip().lower()
                if draw_choice == 'draw':
                    print("Game drawn due to threefold repetition!")
                    game_over = True
                    break
            else:
                # O computador reconhece a repetição (pode-se adicionar lógica heurística aqui depois)
                print(f"🤖 {current_player_display} noted the threefold repetition...")
                time.sleep(1.5)

        legal_moves = board.get_legal_moves()

        try:
            if current_player_type == "Human":
                if board.is_full():
                    choice = input(f"⚠️ BOARD FULL! {current_player_display}, type 'p1'-'p7' to pop, or 'draw' to end: ").strip().lower()
                    if choice == 'draw':
                        print(f"Game declared a draw by {current_player_display}!")
                        game_over = True
                        break
                    if not choice.startswith('p'):
                        print("Invalid input. The board is full, you MUST pop or draw.")
                        continue
                    
                    col = int(choice[1:]) - 1
                    move = ("pop", col)
                    
                else:
                    choice = input(f"{current_player_display}, enter 1-7 to drop, or 'p1'-'p7' to pop: ").strip().lower()
                    
                    if choice.startswith('p'):
                        col = int(choice[1:]) - 1
                        move = ("pop", col)
                    else:
                        col = int(choice) - 1
                        move = ("push", col)
                        
            else: 
                # ---- EXECUÇÃO DINÂMICA DA IA ESCOLHIDA ----
                UI.render(board, f"🤖 {current_player_display} is thinking...")
                
                # Chama o algoritmo exato que foi passado nos parâmetros
                move = current_ai_func(board) 
                col = move[1]

        except ValueError:
            print("Invalid input. Please try again.")
            continue
            
        if col < 0 or col > 6:
            print("Invalid column. Choose a number between 1 and 7.")
            continue
        if move not in legal_moves:
            print("❌ Invalid move! The column is full, or you don't own the bottom piece.")
            continue

        if move[0] == "pop":
            UI.animate_pop(board, col) 
            board.pop_piece(col) 
            UI.render(board)     
            
            current_player_wins = board.check_win(piece)
            opponent_wins = board.check_win(opponent_piece)
            
            if current_player_wins and opponent_wins:
                print(f"Wow! Both aligned 4. By Rule 1, the popping player ({current_player_display}) is the winner!")
                game_over = True
            elif current_player_wins:
                print(f"🎉 Congratulations! {current_player_display} wins the game!")
                game_over = True
            elif opponent_wins:
                print(f"Oops! You helped {opponent_display} win!")
                game_over = True

        elif move[0] == "push":
            row = board.get_next_open_row(col)
            UI.animate_drop(board, col, row, piece) 
            board.drop_piece(col, piece) 
            UI.render(board)             

            if board.check_win(piece):
                print(f"🎉 Congratulations! {current_player_display} wins the game!")
                game_over = True

        if not game_over:
            new_state = board.get_state()
            state_history[new_state] = state_history.get(new_state, 0) + 1
            
            board.switch_player()

    input("\nPress Enter to return to the play menu...")

if __name__ == "__main__":
    main_menu()
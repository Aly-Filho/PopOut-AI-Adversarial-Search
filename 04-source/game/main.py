from board import Board
from ui import UI
import sys
import time
from models.mcts import *

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
            play_game("Human", "Human")
        elif choice == '2':
            play_game("Human", "AI")
        elif choice == '3':
            play_game("AI", "AI")
        elif choice == '4':
            break #Goes back to the main menu.
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

def play_game(player1_type, player2_type):

    #1. Creation of the game.
    board = Board()
    game_over = False
    
    #2. Create the empty log of states.
    state_history = {} 
    
    #3. Register the initial state in the log of states.
    initial_state = board.get_state()
    state_history[initial_state] = 1

    #this part is only for the U.I
    UI.clear_screen()
    print(f"Starting Match: {player1_type} vs {player2_type}!")
    UI.render(board)

    while not game_over:
  
        # 4. The class board holds the current player.
        piece = board.current_player
        player_name = "Player 1 (X)" if piece == 'X' else "Player 2 (O)"
        opponent_piece = 'O' if piece == 'X' else 'X'
        opponent_name = "Player 2 (O)" if piece == 'X' else "Player 1 (X)"
        if piece == 'X':
            current_player = player1_type
        else:
            current_player = player2_type

        # 5. THE THREEFOLD REPETITION CHECK
        current_state = board.get_state()
        if state_history.get(current_state, 0) >= 3:
            print("\n⚠️ THREEFOLD REPETITION DETECTED ⚠️")
            if current_player == "Human":
                draw_choice = input(f"This board state has occurred 3 times. {player_name}, type 'draw' to end, or press Enter to play: ").strip().lower()
                if draw_choice == 'draw':
                    print("Game drawn due to threefold repetition!")
                    game_over = True
                    break
            else:
                ####É necessário verificar a heurística para nossa IA detectar um impate, não sei como mas iremos descobrir.###
                print(f"{player_name} (AI) noted the threefold repetition...")
                time.sleep(1.5)


        # Get the list of possible moves.
        legal_moves = board.get_legal_moves()

        try:
            if current_player == "Human": #Move by Human.
                if board.is_full():
                    choice = input(f"⚠️ BOARD FULL! {player_name}, type 'p1'-'p7' to pop, or 'draw' to end: ").strip().lower()
                    if choice == 'draw':
                        print(f"Game declared a draw by {player_name}!")
                        game_over = True
                        break
                    if not choice.startswith('p'):
                        print("Invalid input. The board is full, you MUST pop or draw.")
                        continue
                    
                    col = int(choice[1:]) - 1
                    move = ("pop", col)
                    
                else:
                    choice = input(f"{player_name}, enter 1-7 to drop, or 'p1'-'p7' to pop: ").strip().lower()
                    
                    if choice.startswith('p'):
                        col = int(choice[1:]) - 1
                        move = ("pop", col)
                    else:
                        col = int(choice) - 1
                        move = ("push", col)
                        
            else: #Move by AI.
                if player1_type == "AI" and player2_type == "AI":
                    ai_name = "AI 1" if piece == 'X' else "AI 2"
                else:
                    ai_name = "AI"
                
                UI.render(board, f"🤖 {ai_name} ({piece}) is thinking...")
                
                move = mcts_best_move(board) 
                col = move[1]

        #Error checks for invalid inputs by Human.
        except ValueError:
            print("Invalid input. Please try again.")
            continue
            
        if col < 0 or col > 6:
            print("Invalid column. Choose a number between 1 and 7.")
            continue
        if move not in legal_moves:
            print("❌ Invalid move! The column is full, or you don't own the bottom piece.")
            continue


        # Updating the board for POP.
        if move[0] == "pop":
            UI.animate_pop(board, col) #Call the UI function to animate de drop.
            board.pop_piece(col) # Actually update the state of the board.
            UI.render(board)     # Show the updated board on terminal.
            
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

        # Updating the board for PUSH.        
        elif move[0] == "push":
            row = board.get_next_open_row(col)
            UI.animate_drop(board, col, row, piece) #Call the UI function to animate de drop
            board.drop_piece(col, piece) # Actually update the state of the board.
            UI.render(board)             # Show the updated board on terminal.

            if board.check_win(piece):
                print(f"🎉 Congratulations! {player_name} wins the game!")
                game_over = True

        #Update our dictionary for the states of the game and move to the next player.
        if not game_over:
            new_state = board.get_state()
            state_history[new_state] = state_history.get(new_state, 0) + 1
            
            board.switch_player()

    input("\nPress Enter to return to the play menu...")


if __name__ == "__main__":
    main_menu()
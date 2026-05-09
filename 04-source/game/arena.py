from board import Board
import time
import csv

# Importe os seus modelos
from models.mcts_heuristics import mcts_best_move
from models.mcts_vanilla import mcts_vanilla_best_move
from models.mcts_multi import mcts_multi_expansion_best_move

# ==========================================
# 1. FUNÇÕES DE COMBATE (TESTE DE MODELOS)
# ==========================================

def simulate_match(p1_name, p1_func, p2_name, p2_func):
    board = Board()
    state_history = {board.get_state(): 1}
    
    while True:
        piece = board.current_player
        opponent_piece = 'O' if piece == 'X' else 'X'
        
        current_func = p1_func if piece == 'X' else p2_func
        current_name = p1_name if piece == 'X' else p2_name
        opponent_name = p2_name if piece == 'X' else p1_name

        current_state = board.get_state()
        if state_history.get(current_state, 0) >= 3:
            return "Draw"
            
        move = current_func(board)
        col = move[1]

        if move[0] == "pop":
            board.pop_piece(col)
            cw = board.check_win(piece)
            ow = board.check_win(opponent_piece)
            if cw and ow: return current_name 
            elif cw: return current_name
            elif ow: return opponent_name
        elif move[0] == "push":
            board.drop_piece(col, piece)
            if board.check_win(piece): return current_name

        new_state = board.get_state()
        state_history[new_state] = state_history.get(new_state, 0) + 1
        
        if not board.get_legal_moves():
            return "Draw"
            
        board.switch_player()

def run_combat_arena(num_games=10, iterations=500):
    heuristica = lambda b: mcts_best_move(b, iterations=iterations)
    vanilla = lambda b: mcts_vanilla_best_move(b, iterations=iterations)
    multi = lambda b: mcts_multi_expansion_best_move(b, iterations=iterations, n_children=3)

    matchups = [
        ("Vanilla", vanilla, "Heurística", heuristica),
        ("Heurística", heuristica, "Vanilla", vanilla),
        ("Heurística", heuristica, "Multi", multi)
    ]

    print(f"\n⚔️ A INICIAR COMBATES ({num_games} jogos / {iterations} iterações) ⚔️")
    results_table = []

    for p1_name, p1_func, p2_name, p2_func in matchups:
        print(f"A simular: [X] {p1_name} vs [O] {p2_name}...", end="", flush=True)
        start_time = time.time()
        p1_wins, p2_wins, draws = 0, 0, 0
        
        for i in range(num_games):
            winner = simulate_match(p1_name, p1_func, p2_name, p2_func)
            if winner == p1_name: p1_wins += 1
            elif winner == p2_name: p2_wins += 1
            else: draws += 1
                
        print(f" ({time.time() - start_time:.1f}s)")
        results_table.append({
            "Match": f"{p1_name} vs {p2_name}", "P1": p1_wins, "P2": p2_wins, "D": draws
        })

    print("\n--- RESULTADOS FINAIS ---")
    for res in results_table:
        print(f"{res['Match']} | Vitórias P1: {res['P1']} | Vitórias P2: {res['P2']} | Empates: {res['D']}")
    print("-------------------------\n")


# ==========================================
# 2. FUNÇÕES DE EXTRAÇÃO (GERAÇÃO DE DATASET)
# ==========================================

def get_flat_board(board):
    """Esmaga o tabuleiro numa lista linear de 42 strings ('X', 'O', 'V')."""
    flat = []
    for r in range(board.rows):
        for c in range(board.cols):
            piece = board.grid[r][c]
            if piece == ' ' or piece == 0 or piece is None:
                flat.append('V')
            else:
                flat.append(piece)
    return flat

def generate_dataset_winners_only(model_func, model_name, num_games=50, iterations=1000, filename="popout_dataset_winners.csv"):
    print(f"\n🧠 A gerar dataset de ALTA QUALIDADE usando {model_name} 🧠")
    print(f"-> Apenas as jogadas do jogador VENCEDOR serão guardadas.")
    print(f"Jogos a simular: {num_games} | Iterações: {iterations}")
    
    header = [f"c_{r}_{c}" for r in range(6) for c in range(7)]
    header.append("move")
    
    start_time = time.time()
    total_moves = 0
    jogos_uteis = 0
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        for i in range(num_games):
            board = Board()
            state_history = {board.get_state(): 1}
            game_over = False
            winner = None
            
            # Memória temporária do jogo atual: guarda tuplos (jogador_que_jogou, linha_do_csv)
            game_memory = [] 
            
            while not game_over:
                flat_state = get_flat_board(board)
                piece = board.current_player
                
                # Pede a jogada ao MCTS
                move = model_func(board, iterations=iterations)
                move_str = f"{move[0]}_{move[1]}"
                
                # Guarda na memória temporária em vez de escrever já no CSV
                game_memory.append((piece, flat_state + [move_str]))
                
                opponent_piece = 'O' if piece == 'X' else 'X'
                
                # Aplica a jogada
                if move[0] == "pop":
                    board.pop_piece(move[1])
                    cw, ow = board.check_win(piece), board.check_win(opponent_piece)
                    if cw and ow:
                        winner = piece
                        game_over = True
                    elif cw:
                        winner = piece
                        game_over = True
                    elif ow:
                        winner = opponent_piece
                        game_over = True
                else:
                    board.drop_piece(move[1], piece)
                    if board.check_win(piece):
                        winner = piece
                        game_over = True

                # Condições de Empate
                if not game_over:
                    new_state = board.get_state()
                    if state_history.get(new_state, 0) >= 3 or not board.get_legal_moves():
                        game_over = True # winner continua None (Empate)
                    state_history[new_state] = state_history.get(new_state, 0) + 1
                    board.switch_player()
            
            # FIM DO JOGO: O Filtro Mágico!
            if winner is not None:
                jogos_uteis += 1
                for player_who_moved, row_data in game_memory:
                    if player_who_moved == winner:
                        writer.writerow(row_data)
                        total_moves += 1
                    
            if (i + 1) % 5 == 0 or i == num_games - 1:
                print(f" -> Jogos processados: {i+1}/{num_games}... (Jogos com vencedor: {jogos_uteis})")

    elapsed = time.time() - start_time
    print(f"\n✅ Dataset '{filename}' gerado com sucesso!")
    print(f"📊 Total de jogadas VENCEDORAS gravadas: {total_moves}")
    print(f"⏱️ Tempo de processamento: {elapsed:.1f} segundos\n")


# ==========================================
# 3. MENU PRINCIPAL DA ARENA
# ==========================================

def main_menu():
    while True:
        print("===================================")
        print("         ARENA DO POPOUT           ")
        print("===================================")
        print(" 1 - Combater (Testar Modelos)")
        print(" 2 - Gerar Dataset (Self-Play)")
        print(" 3 - Sair")
        print("===================================")
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '1':
            jogos = int(input("Quantos jogos por confronto? (ex: 10): "))
            iters = int(input("Quantas iterações para o MCTS? (ex: 500): "))
            run_combat_arena(num_games=jogos, iterations=iters)
            
        elif choice == '2':
            print("\nQual modelo será o 'Professor' para gerar os dados?")
            print("1 - MCTS Heurístico (Recomendado)")
            print("2 - MCTS Vanilla")
            print("3 - MCTS Multi-Expansion")
            
            mod_choice = input("Escolha (1-3): ").strip()
            if mod_choice == '1':
                func, nome = mcts_best_move, "MCTS Heurístico"
            elif mod_choice == '2':
                func, nome = mcts_vanilla_best_move, "MCTS Vanilla"
            else:
                func, nome = mcts_multi_expansion_best_move, "MCTS Multi-Expansion" # Aqui podes ter de ajustar se o multi precisar do parâmetro extra
                
            jogos = int(input("Quantos jogos deseja gravar? (ex: 50): "))
            iters = int(input("Quantas iterações por jogada? (ex: 1000): "))
            
            # Chama a função de geração
            if mod_choice == '3':
                # Wrapper para garantir que o parametro n_children entra corretamente
                func_wrapper = lambda b, iterations: mcts_multi_expansion_best_move(b, iterations=iterations, n_children=3)
                generate_dataset_winners_only(func_wrapper, nome, num_games=jogos, iterations=iters)
            else:
                generate_dataset_winners_only(func, nome, num_games=jogos, iterations=iters)
            
        elif choice == '3':
            print("A sair da Arena...")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main_menu()
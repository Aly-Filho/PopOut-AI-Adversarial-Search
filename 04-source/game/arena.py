from board import Board
import time

# Importe os seus modelos
from models.mcts_heuristics import mcts_best_move
from models.mcts_vanilla import mcts_vanilla_best_move
from models.mcts_multi import mcts_multi_expansion_best_move

def simulate_match(p1_name, p1_func, p2_name, p2_func):
    """
    Simula uma única partida sem qualquer UI (Headless).
    Retorna o nome do vencedor ou 'Draw' em caso de empate.
    """
    board = Board()
    state_history = {board.get_state(): 1}
    
    while True:
        piece = board.current_player
        opponent_piece = 'O' if piece == 'X' else 'X'
        
        current_func = p1_func if piece == 'X' else p2_func
        current_name = p1_name if piece == 'X' else p2_name
        opponent_name = p2_name if piece == 'X' else p1_name

        # Verifica Empate por Repetição (Regra 3)
        current_state = board.get_state()
        if state_history.get(current_state, 0) >= 3:
            return "Draw"
            
        # Pede a jogada ao algoritmo
        # O MCTS já vai lidar com o tabuleiro cheio automaticamente nas suas legal_moves (só retorna pops)
        move = current_func(board)
        col = move[1]

        # Aplica a jogada e verifica as regras de vitória nativas do PopOut
        if move[0] == "pop":
            board.pop_piece(col)
            
            cw = board.check_win(piece)
            ow = board.check_win(opponent_piece)
            
            if cw and ow:
                return current_name # Regra 1: Quem faz o pop ganha se houver empate
            elif cw:
                return current_name
            elif ow:
                return opponent_name
                
        elif move[0] == "push":
            board.drop_piece(col, piece)
            if board.check_win(piece):
                return current_name

        # Regista o estado e passa a vez
        new_state = board.get_state()
        state_history[new_state] = state_history.get(new_state, 0) + 1
        board.switch_player()


def run_arena(num_games=10, iterations=500):
    """
    Gere os confrontos. 
    DICA: Baixe as 'iterations' para 500 ou 1000 durante os testes para não demorar horas.
    Quando for extrair os dados oficiais para o relatório, suba para 2000.
    """
    
    # Criamos wrappers (lambdas) para injetar o número de iterações facilmente
    # Nota: No multi_expansion estamos a forçar 3 filhos.
    heuristica = lambda b: mcts_best_move(b, iterations=iterations)
    vanilla = lambda b: mcts_vanilla_best_move(b, iterations=iterations)
    multi = lambda b: mcts_multi_expansion_best_move(b, iterations=iterations, n_children=3)

    matchups = [
        ("Vanilla", vanilla, "Heurística", heuristica),
        ("Heurística", heuristica, "Vanilla", vanilla),
        ("Heurística", heuristica, "Multi", multi),
        ("Multi", multi, "Heurística", heuristica),
        ("Vanilla", vanilla, "Multi", multi),
        ("Multi", multi, "Vanilla", vanilla)
    ]

    print(f"===============================================================")
    print(f" ⚔️ BEM-VINDO À ARENA POPOUT ⚔️")
    print(f" Iterações por jogada: {iterations} | Partidas por confronto: {num_games}")
    print(f"===============================================================\n")

    results_table = []

    for p1_name, p1_func, p2_name, p2_func in matchups:
        print(f"A simular: [X] {p1_name} vs [O] {p2_name}...", end="", flush=True)
        
        start_time = time.time()
        p1_wins = 0
        p2_wins = 0
        draws = 0
        
        for i in range(num_games):
            winner = simulate_match(p1_name, p1_func, p2_name, p2_func)
            if winner == p1_name:
                p1_wins += 1
            elif winner == p2_name:
                p2_wins += 1
            else:
                draws += 1
                
        elapsed_time = time.time() - start_time
        print(f" Concluído em {elapsed_time:.1f}s")
        
        results_table.append({
            "Match": f"{p1_name} (X) vs {p2_name} (O)",
            "P1_Wins": p1_wins,
            "P2_Wins": p2_wins,
            "Draws": draws
        })

    # Imprimir os resultados de forma legível
    print("\n===============================================================")
    print("                    RESULTADOS FINAIS                          ")
    print("===============================================================")
    for res in results_table:
        print(f"Confronto: {res['Match']}")
        print(f"  -> Vitórias P1 (X) : {res['P1_Wins']}")
        print(f"  -> Vitórias P2 (O) : {res['P2_Wins']}")
        print(f"  -> Empates         : {res['Draws']}")
        print("---------------------------------------------------------------")


if __name__ == "__main__":
    # Para testar se o script funciona rápido, corre apenas 5 jogos com 500 iterações.
    # Quando fores dormir, podes pôr run_arena(num_games=50, iterations=2000) e deixá-lo correr a noite toda!
    run_arena(num_games=5, iterations=500)
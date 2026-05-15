import time
import csv
import multiprocessing
from datetime import datetime, timedelta
from board import Board

# Importe os seus modelos (Garante que os caminhos estão corretos no teu projeto)
try:
    from models.mcts_heuristics import mcts_best_move
    from models.mcts_vanilla import mcts_vanilla_best_move
    from models.mcts_multi import mcts_multi_expansion_best_move
except ImportError:
    print("Erro: Certifica-te que as pastas 'models' e os ficheiros .py estão no diretório correto.")

# ==========================================
# FUNÇÕES DE UTILIDADE
# ==========================================

def get_flat_board(board):
    """Transforma o tabuleiro numa lista para o dataset."""
    flat = []
    for r in range(board.rows):
        for c in range(board.cols):
            piece = board.grid[r][c]
            flat.append('V' if piece in [' ', 0, None] else piece)
    return flat

# ==========================================
# TRABALHADOR PARALELO (WORKER)
# ==========================================

def worker_generate_data(worker_id, model_func, iterations, end_time, filename):
    """Loop de geração de jogos que roda até atingir o tempo limite."""
    jogos_concluidos = 0
    moves_gravados = 0
    
    # Cada worker abre o ficheiro em modo 'append' (a)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        while time.time() < end_time:
            board = Board()
            state_history = {board.get_state(): 1}
            game_over = False
            winner = None
            game_memory = [] # Guarda (jogador, estado+jogada)
            
            while not game_over:
                flat_state = get_flat_board(board)
                piece = board.current_player
                
                # Executa a lógica do modelo
                move = model_func(board, iterations=iterations)
                move_str = f"{move[0]}_{move[1]}"
                
                # Regista a jogada na memória temporária
                game_memory.append((piece, flat_state + [move_str]))
                
                opponent_piece = 'O' if piece == 'X' else 'X'
                
                if move[0] == "pop":
                    board.pop_piece(move[1])
                    cw, ow = board.check_win(piece), board.check_win(opponent_piece)
                    if cw and ow: winner = piece; game_over = True
                    elif cw: winner = piece; game_over = True
                    elif ow: winner = opponent_piece; game_over = True
                else:
                    board.drop_piece(move[1], piece)
                    if board.check_win(piece):
                        winner = piece
                        game_over = True

                if not game_over:
                    # Verifica empate por repetição ou falta de movimentos
                    new_state = board.get_state()
                    if state_history.get(new_state, 0) >= 3 or not board.get_legal_moves():
                        game_over = True
                    state_history[new_state] = state_history.get(new_state, 0) + 1
                    board.switch_player()
            
            # Só grava se houver um vencedor (Filtro de Qualidade)
            if winner is not None:
                jogos_concluidos += 1
                for player_who_moved, row_data in game_memory:
                    if player_who_moved == winner:
                        writer.writerow(row_data)
                        moves_gravados += 1
            
            # Log de progresso a cada 5 jogos por worker
            if jogos_concluidos % 5 == 0:
                restante = int(end_time - time.time())
                print(f"[Worker {worker_id}] Jogos: {jogos_concluidos} | Tempo restante: {restante//60} min")

    return jogos_concluidos, moves_gravados

# ==========================================
# ORQUESTRAÇÃO
# ==========================================

def run_parallel_session(model_func, model_name, hours, iterations, num_workers):
    start_time = time.time()
    end_timestamp = start_time + (hours * 3600)
    
    # Nome do ficheiro com timestamp para não sobrepor
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"dataset_{model_name.replace(' ', '_')}_{timestamp}.csv"
    
    # Criar o cabeçalho (Header)
    header = [f"c_{r}_{c}" for r in range(6) for c in range(7)] + ["move"]
    with open(filename, mode='w', newline='') as f:
        csv.writer(f).writerow(header)

    print(f"\n" + "="*40)
    print(f"🔥 SESSÃO DE TREINO PARALELA ATIVA 🔥")
    print(f"Modelo: {model_name}")
    print(f"Workers: {num_workers} | Duração: {hours}h")
    print(f"Final previsto: {datetime.now() + timedelta(hours=hours)}")
    print(f"Ficheiro: {filename}")
    print("="*40 + "\n")

    # Iniciar os processos
    pool = multiprocessing.Pool(processes=num_workers)
    results = []
    
    for i in range(num_workers):
        res = pool.apply_async(worker_generate_data, (i, model_func, iterations, end_timestamp, filename))
        results.append(res)
    
    pool.close()
    pool.join()
    
    # Balanço final
    total_jogos = sum(r.get()[0] for r in results)
    total_moves = sum(r.get()[1] for r in results)
    
    print("\n" + "✅" * 15)
    print("PROCESSAMENTO FINALIZADO")
    print(f"Total de jogos processados: {total_jogos}")
    print(f"Total de amostras gravadas: {total_moves}")
    print("✅" * 15)

def main():
    print("--- ARENA POPOUT: GERAÇÃO DE DADOS ---")
    print("1. MCTS Heurístico")
    print("2. MCTS Vanilla")
    print("3. MCTS Multi-Expansion")
    
    op = input("Escolha o modelo (1-3): ")
    if op == '1': func, nome = mcts_best_move, "Heuristico"
    elif op == '2': func, nome = mcts_vanilla_best_move, "Vanilla"
    else: func, nome = lambda b, iterations: mcts_multi_expansion_best_move(b, iterations=iterations, n_children=3), "MultiExpansion"
    
    h = float(input("Quantas horas de simulação? "))
    it = int(input("Iterações por jogada (ex: 800)? "))
    w = int(input(f"Número de workers (Sugestão: {multiprocessing.cpu_count()-1})? "))
    
    run_parallel_session(func, nome, h, it, w)

if __name__ == "__main__":
    # Necessário para Windows evitar recursividade de processos
    main()
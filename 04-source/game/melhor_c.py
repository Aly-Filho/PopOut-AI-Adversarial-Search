import math
import random
import multiprocessing


# ============================================================
# BOARD
# ============================================================

class Board:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.grid = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.current_player = 'X'

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_state(self):
        return tuple(tuple(row) for row in self.grid)

    def copy(self):
        new_board = Board(self.rows, self.cols)
        new_board.grid = [row[:] for row in self.grid]
        new_board.current_player = self.current_player
        return new_board

    def is_valid_drop(self, col):
        return self.grid[0][col] == ' '

    def is_valid_pop(self, col, piece):
        return self.grid[self.rows - 1][col] == piece

    def get_valid_moves(self):
        legal_moves = []
        for col in range(self.cols):
            if self.is_valid_drop(col):
                legal_moves.append(("push", col))
            if self.is_valid_pop(col, self.current_player):
                legal_moves.append(("pop", col))
        return legal_moves

    def get_next_open_row(self, col):
        for r in range(self.rows - 1, -1, -1):
            if self.grid[r][col] == ' ':
                return r
        return None

    def drop_piece(self, col, piece):
        row = self.get_next_open_row(col)
        if row is not None:
            self.grid[row][col] = piece
        return row

    def pop_piece(self, col):
        for r in range(self.rows - 1, 0, -1):
            self.grid[r][col] = self.grid[r - 1][col]
        self.grid[0][col] = ' '

    def apply_move(self, move):
        move_type, col = move
        if move_type == "push":
            self.drop_piece(col, self.current_player)
        elif move_type == "pop":
            self.pop_piece(col)
        self.switch_player()

    def check_win(self, piece):
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if (self.grid[r][c] == piece and self.grid[r][c+1] == piece and
                        self.grid[r][c+2] == piece and self.grid[r][c+3] == piece):
                    return True
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if (self.grid[r][c] == piece and self.grid[r+1][c] == piece and
                        self.grid[r+2][c] == piece and self.grid[r+3][c] == piece):
                    return True
        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if (self.grid[r][c] == piece and self.grid[r+1][c+1] == piece and
                        self.grid[r+2][c+2] == piece and self.grid[r+3][c+3] == piece):
                    return True
        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if (self.grid[r][c] == piece and self.grid[r-1][c+1] == piece and
                        self.grid[r-2][c+2] == piece and self.grid[r-3][c+3] == piece):
                    return True
        return False

    def is_full(self):
        for c in range(self.cols):
            if self.grid[0][c] == ' ':
                return False
        return True


# ============================================================
# MCTS NODE
# ============================================================

class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0
        self.untried_moves = board.get_valid_moves()
        self.player_who_just_moved = parent.board.current_player if parent else None

    def ucb1(self, c=1.414):
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def best_child(self, c=1.414):
        return max(self.children, key=lambda n: n.ucb1(c))

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return (self.board.check_win('X') or
                self.board.check_win('O') or
                not self.board.get_valid_moves())


# ============================================================
# HEURÍSTICAS
# ============================================================

def _find_winning_move(board):
    piece = board.current_player
    opponent = 'O' if piece == 'X' else 'X'
    for move in board.get_valid_moves():
        b = board.copy()
        b.apply_move(move)
        if move[0] == 'pop':
            if b.check_win(piece) and b.check_win(opponent):
                return move
            elif b.check_win(piece):
                return move
        else:
            if b.check_win(piece):
                return move
    return None


def _find_blocking_move(board):
    opponent = 'O' if board.current_player == 'X' else 'X'
    b_opp = board.copy()
    b_opp.current_player = opponent
    opp_win_move = _find_winning_move(b_opp)
    if opp_win_move and opp_win_move in board.get_valid_moves():
        return opp_win_move
    return None


def _weighted_random_move(moves, board):
    center = board.cols // 2
    weights = []
    for move_type, col in moves:
        if move_type == 'push':
            w = center - abs(col - center) + 1
        else:
            w = 1
        weights.append(w)
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for move, w in zip(moves, weights):
        cumulative += w
        if r <= cumulative:
            return move
    return moves[-1]


# ============================================================
# ROLLOUTS
# ============================================================

def _rollout_vanilla(board, ai_piece, max_depth=60):
    sim_board = board.copy()
    for _ in range(max_depth):
        legal_moves = sim_board.get_valid_moves()
        if not legal_moves:
            return 0.5
        move = random.choice(legal_moves)
        current_p = sim_board.current_player
        opponent_p = 'O' if current_p == 'X' else 'X'
        sim_board.apply_move(move)
        if move[0] == 'pop':
            cw = sim_board.check_win(current_p)
            ow = sim_board.check_win(opponent_p)
            if cw and ow:   return 1.0 if current_p == ai_piece else 0.0
            elif cw:        return 1.0 if current_p == ai_piece else 0.0
            elif ow:        return 0.0 if current_p == ai_piece else 1.0
        else:
            if sim_board.check_win(current_p):
                return 1.0 if current_p == ai_piece else 0.0
    return 0.5


def _rollout(board, ai_piece, max_depth=60):
    sim_board = board.copy()
    for _ in range(max_depth):
        legal_moves = sim_board.get_valid_moves()
        if not legal_moves:
            return 0.5
        win_move = _find_winning_move(sim_board)
        if win_move:
            return 1.0 if sim_board.current_player == ai_piece else 0.0
        block_move = _find_blocking_move(sim_board)
        move = block_move if block_move else _weighted_random_move(legal_moves, sim_board)
        current_p = sim_board.current_player
        opponent_p = 'O' if current_p == 'X' else 'X'
        sim_board.apply_move(move)
        if move[0] == 'pop':
            cw = sim_board.check_win(current_p)
            ow = sim_board.check_win(opponent_p)
            if cw and ow:   return 1.0 if current_p == ai_piece else 0.0
            elif cw:        return 1.0 if current_p == ai_piece else 0.0
            elif ow:        return 0.0 if current_p == ai_piece else 1.0
        else:
            if sim_board.check_win(current_p):
                return 1.0 if current_p == ai_piece else 0.0
    return 0.5


# ============================================================
# MCTS — FUNÇÕES PRINCIPAIS
# ============================================================

def mcts_vanilla_best_move(board, iterations=10000, c=1.414):
    ai_piece = board.current_player
    root = Node(board.copy())
    for _ in range(iterations):
        node = root
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(c)
        if not node.is_terminal() and node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            new_board = node.board.copy()
            new_board.apply_move(move)
            child = Node(new_board, parent=node, move=move)
            node.children.append(child)
            node = child
        result = _rollout_vanilla(node.board, ai_piece)
        backprop_node = node
        while backprop_node is not None:
            backprop_node.visits += 1
            if backprop_node.player_who_just_moved == ai_piece:
                backprop_node.wins += result
            elif backprop_node.player_who_just_moved is not None:
                backprop_node.wins += (1.0 - result)
            backprop_node = backprop_node.parent
    if not root.children:
        return board.get_valid_moves()[0]
    return max(root.children, key=lambda n: n.visits).move


def mcts_best_move(board, iterations=10000, c=1.414):
    ai_piece = board.current_player
    instant_win = _find_winning_move(board)
    if instant_win: return instant_win
    instant_block = _find_blocking_move(board)
    if instant_block: return instant_block
    root = Node(board.copy())
    for _ in range(iterations):
        node = root
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(c)
        if not node.is_terminal() and node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            new_board = node.board.copy()
            new_board.apply_move(move)
            child = Node(new_board, parent=node, move=move)
            node.children.append(child)
            node = child
        result = _rollout(node.board, ai_piece)
        backprop_node = node
        while backprop_node is not None:
            backprop_node.visits += 1
            if backprop_node.player_who_just_moved == ai_piece:
                backprop_node.wins += result
            elif backprop_node.player_who_just_moved is not None:
                backprop_node.wins += (1.0 - result)
            backprop_node = backprop_node.parent
    if not root.children:
        return board.get_valid_moves()[0]
    return max(root.children, key=lambda n: n.visits).move


# ============================================================
# ARENA
# ============================================================

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
            if cw and ow:   return current_name
            elif cw:        return current_name
            elif ow:        return opponent_name
        elif move[0] == "push":
            board.drop_piece(col, piece)
            if board.check_win(piece):
                return current_name
        new_state = board.get_state()
        state_history[new_state] = state_history.get(new_state, 0) + 1
        if not board.get_valid_moves():
            return "Draw"
        board.switch_player()


# ============================================================
# CALIBRAÇÃO DO C — MULTIPROCESSING
# ============================================================

def _jogar_uma_partida(args):
    nome_c1, c1, nome_c2, c2, iterations, c1_e_X = args
    f_c1 = lambda b: mcts_vanilla_best_move(b, iterations=iterations, c=c1)
    f_c2 = lambda b: mcts_vanilla_best_move(b, iterations=iterations, c=c2)
    if c1_e_X:
        vencedor = simulate_match(nome_c1, f_c1, nome_c2, f_c2)
    else:
        vencedor = simulate_match(nome_c2, f_c2, nome_c1, f_c1)
    if vencedor == nome_c1:
        return 'c1'
    elif vencedor == nome_c2:
        return 'c2'
    else:
        return 'empate'


def avaliar_confronto_c(c1, c2, num_jogos_por_lado=50, iterations=2000, num_cores=10):
    nome_c1 = f"MCTS_C_{c1:.4f}"
    nome_c2 = f"MCTS_C_{c2:.4f}"
    tarefas = []
    for _ in range(num_jogos_por_lado):
        tarefas.append((nome_c1, c1, nome_c2, c2, iterations, True))
    for _ in range(num_jogos_por_lado):
        tarefas.append((nome_c1, c1, nome_c2, c2, iterations, False))
    print(f"  -> {len(tarefas)} jogos no total ({num_cores} cores)...")
    with multiprocessing.Pool(processes=num_cores) as pool:
        resultados = pool.map(_jogar_uma_partida, tarefas)
    vitorias_c1 = sum(1 for r in resultados if r == 'c1')
    vitorias_c2 = sum(1 for r in resultados if r == 'c2')
    empates     = sum(1 for r in resultados if r == 'empate')
    print(f"  Resultados: {nome_c1}: {vitorias_c1} | {nome_c2}: {vitorias_c2} | Empates: {empates}")
    if vitorias_c2 != vitorias_c1:
        return vitorias_c2 > vitorias_c1
    else:
        return abs(c2 - 1.414) <= abs(c1 - 1.414)


def otimizar_c_busca_binaria(low=1.0, high=2.0, max_passos=5, iterations=2000, num_jogos_por_lado=50, num_cores=10):
    print(f"====== INICIANDO BUSCA DO VALOR IDEAL DE C NO INTERVALO [{low}, {high}] ======")
    print(f"       {num_jogos_por_lado*2} jogos/passo | {iterations} iterações | {num_cores} cores\n")
    for passo in range(1, max_passos + 1):
        meio  = (low + high) / 2
        delta = (high - low) * 0.1
        c1    = meio - delta
        c2    = meio + delta
        print(f"Passo {passo}/{max_passos}: Intervalo atual [{low:.4f}, {high:.4f}]")
        print(f"Testando C1 = {c1:.4f} vs C2 = {c2:.4f}")
        if avaliar_confronto_c(c1, c2, num_jogos_por_lado=num_jogos_por_lado,
                                iterations=iterations, num_cores=num_cores):
            print(f"👉 C2 venceu. Ajustando limite inferior para {meio:.4f}\n")
            low = meio
        else:
            print(f"👉 C1 venceu. Ajustando limite superior para {meio:.4f}\n")
            high = meio
    c_final = (low + high) / 2
    print(f"====== BUSCA CONCLUÍDA ======")
    print(f"O valor aproximado para o C ideal é: {c_final:.4f}")
    return c_final

import multiprocessing
multiprocessing.set_start_method('fork', force=True)

def grid_search_c(candidatos, num_jogos_por_lado=30, iterations=2000, num_cores=10):
    """
    Testa todos os candidatos entre si (par a par adjacente) para identificar
    em que intervalo está o pico real de performance.
    Retorna o intervalo (low, high) com maior potencial.
    """
    print(f"====== GRID SEARCH EM {len(candidatos)} PONTOS ======\n")
    scores = {c: 0 for c in candidatos}

    for i in range(len(candidatos) - 1):
        c1 = candidatos[i]
        c2 = candidatos[i + 1]
        print(f"Confronto: C={c1:.4f} vs C={c2:.4f}")
        c2_venceu = avaliar_confronto_c(c1, c2,
                                        num_jogos_por_lado=num_jogos_por_lado,
                                        iterations=iterations,
                                        num_cores=num_cores)
        if c2_venceu:
            scores[c2] += 1
            print(f"  → Vencedor: C={c2:.4f}\n")
        else:
            scores[c1] += 1
            print(f"  → Vencedor: C={c1:.4f}\n")

    print("Scores finais do grid search:")
    for c, s in sorted(scores.items()):
        print(f"  C={c:.4f} → {s} vitórias")

    # Identificar o melhor candidato e definir intervalo em torno dele
    melhor = max(scores, key=scores.get)
    idx = candidatos.index(melhor)
    low  = candidatos[max(0, idx - 1)]
    high = candidatos[min(len(candidatos) - 1, idx + 1)]

    print(f"\n→ Melhor zona identificada: [{low:.4f}, {high:.4f}] (pico em C={melhor:.4f})\n")
    return low, high


def busca_robusta_c(iterations=2000, num_jogos_por_lado_grid=30,
                    num_jogos_por_lado_binaria=50, max_passos=5, num_cores=10):
    """
    Cenário ideal:
      1. Grid search grosso para identificar a zona de pico global.
      2. Três buscas binárias com intervalos ligeiramente diferentes dentro dessa zona.
      3. Mediana dos três resultados como estimativa final robusta.
    """

    # --- FASE 1: Grid Search ---
    candidatos = [1.0, 1.2, 1.414, 1.6, 1.8, 2.0]
    low, high = grid_search_c(candidatos,
                               num_jogos_por_lado=num_jogos_por_lado_grid,
                               iterations=iterations,
                               num_cores=num_cores)

    # Garantir que o intervalo tem largura mínima para a busca binária ser útil
    if high - low < 0.1:
        margem = 0.1
        low  = max(1.0, low  - margem)
        high = min(2.0, high + margem)
        print(f"  (Intervalo alargado para [{low:.4f}, {high:.4f}] por ser muito estreito)\n")

    # --- FASE 2: Três Buscas Binárias com intervalos ligeiramente deslocados ---
    print(f"====== BUSCAS BINÁRIAS (3x) NO INTERVALO [{low:.4f}, {high:.4f}] ======\n")
    largura = high - low
    offsets = [0, -largura * 0.1, largura * 0.1]  # centro, deslocado à esquerda, à direita
    resultados = []

    for i, offset in enumerate(offsets, 1):
        l = max(1.0, low  + offset)
        h = min(2.0, high + offset)
        print(f"Busca {i}/3: intervalo [{l:.4f}, {h:.4f}]")
        c = otimizar_c_busca_binaria(low=l, high=h,
                                     max_passos=max_passos,
                                     iterations=iterations,
                                     num_jogos_por_lado=num_jogos_por_lado_binaria,
                                     num_cores=num_cores)
        resultados.append(c)
        print(f"  → Busca {i} convergiu para C={c:.4f}\n")

    # --- FASE 3: Mediana como estimativa final ---
    resultados_sorted = sorted(resultados)
    c_final = resultados_sorted[len(resultados_sorted) // 2]

    print(f"====== RESULTADO FINAL ======")
    print(f"  Buscas individuais: {[f'{c:.4f}' for c in resultados]}")
    print(f"  Mediana (estimativa robusta): C = {c_final:.4f}")

    if max(resultados) - min(resultados) > 0.15:
        print(f"  ⚠️  Alta divergência entre buscas ({max(resultados)-min(resultados):.4f})")
        print(f"      Considera aumentar num_jogos_por_lado para mais precisão.")
    else:
        print(f"  ✅ Buscas convergentes — resultado confiável.")

    return c_final


# --- CHAMADA ---
melhor_c = busca_robusta_c(
    iterations=10000,
    num_jogos_por_lado_grid=30,
    num_jogos_por_lado_binaria=50,
    max_passos=5,
    num_cores=10
)
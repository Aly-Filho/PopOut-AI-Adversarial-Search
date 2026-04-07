import math
import random

# ──────────────────────────────────────────────
# Nó da árvore MCTS
# ──────────────────────────────────────────────
class Node:
    def __init__(self, board, parent=None, move=None):
        """
        board  : cópia do Board neste estado
        parent : nó pai (None na raiz)
        move   : tuplo ('push'/'pop', col) que gerou este nó
        """
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0

        # Usa o método nativo do board.py para os movimentos não testados
        self.untried_moves = self.board.get_legal_moves()
        
        # Regista quem fez a jogada para chegar a este estado
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
        # O jogo termina se alguém ganhou ou se não há mais movimentos legais
        return (self.board.check_win('X') or 
                self.board.check_win('O') or 
                not self.board.get_legal_moves())

# ──────────────────────────────────────────────
# Funções Heurísticas (Heavy Playouts)
# ──────────────────────────────────────────────
def _find_winning_move(board):
    """Procura se o jogador atual tem algum movimento de vitória imediata."""
    piece = board.current_player
    opponent = 'O' if piece == 'X' else 'X'
    
    for move in board.get_legal_moves():
        b = board.copy()
        b.apply_move(move) # Aplica a jogada e passa a vez nativamente
        
        if move[0] == 'pop':
            # Regra simultânea: Se for pop e ambos ganharem, o jogador que deu o pop ganha
            if b.check_win(piece) and b.check_win(opponent):
                return move
            elif b.check_win(piece):
                return move
        else:
            if b.check_win(piece):
                return move
    return None

def _find_blocking_move(board):
    """Verifica se o oponente vai ganhar na próxima jogada e tenta bloquear."""
    opponent = 'O' if board.current_player == 'X' else 'X'
    
    # Simula o turno do oponente
    b_opp = board.copy()
    b_opp.current_player = opponent 
    
    opp_win_move = _find_winning_move(b_opp)
    
    # Se o oponente tem um movimento vencedor, verificamos se o podemos executar (para bloquear)
    if opp_win_move and opp_win_move in board.get_legal_moves():
        return opp_win_move
    return None

def _weighted_random_move(moves, board):
    """Dá mais peso a colunas centrais na hora de escolher um movimento aleatório."""
    center = board.cols // 2
    weights = []
    
    for move_type, col in moves:
        if move_type == 'push':
            # Quanto mais perto do centro, maior o peso
            w = center - abs(col - center) + 1
        else:
            w = 1 # Pops têm peso padrão
        weights.append(w)

    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for move, w in zip(moves, weights):
        cumulative += w
        if r <= cumulative:
            return move
    return moves[-1]

# ──────────────────────────────────────────────
# Rollout Inteligente
# ──────────────────────────────────────────────
def _rollout(board, ai_piece, max_depth=60):
    sim_board = board.copy()

    for _ in range(max_depth):
        legal_moves = sim_board.get_legal_moves()
        if not legal_moves:
            return 0.5 # Empate por tabuleiro cheio ou bloqueio

        # 1. Jogada vencedora imediata
        win_move = _find_winning_move(sim_board)
        if win_move:
            return 1.0 if sim_board.current_player == ai_piece else 0.0

        # 2. Bloqueia vitória imediata do oponente
        block_move = _find_blocking_move(sim_board)
        if block_move:
            move = block_move
        else:
            # 3. Movimento aleatório pesado (foco no centro)
            move = _weighted_random_move(legal_moves, sim_board)

        # Guarda quem está a fazer o movimento para verificar a regra do Pop
        current_p = sim_board.current_player
        opponent_p = 'O' if current_p == 'X' else 'X'
        
        sim_board.apply_move(move)

        if move[0] == 'pop':
            cw = sim_board.check_win(current_p)
            ow = sim_board.check_win(opponent_p)
            if cw and ow:
                return 1.0 if current_p == ai_piece else 0.0
            elif cw:
                return 1.0 if current_p == ai_piece else 0.0
            elif ow:
                return 0.0 if current_p == ai_piece else 1.0
        else:
            if sim_board.check_win(current_p):
                return 1.0 if current_p == ai_piece else 0.0

    return 0.5 # Se atingir a profundidade máxima, assume empate

# ──────────────────────────────────────────────
# Algoritmo Principal MCTS
# ──────────────────────────────────────────────
def mcts_best_move(board, iterations=2000, c=1.414):
    ai_piece = board.current_player
    
    # ── OTIMIZAÇÃO DE TOPO ──
    # Se a IA pode ganhar agora, não perde tempo a simular!
    instant_win = _find_winning_move(board)
    if instant_win:
        return instant_win
        
    # Se precisa de bloquear agora, bloqueia!
    instant_block = _find_blocking_move(board)
    if instant_block:
        return instant_block

    root = Node(board.copy())

    for _ in range(iterations):
        node = root
        
        # ── 1. SELECTION ──
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(c)

        # ── 2. EXPANSION ──
        if not node.is_terminal() and node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            
            new_board = node.board.copy()
            new_board.apply_move(move)
            
            child = Node(new_board, parent=node, move=move)
            node.children.append(child)
            node = child

        # ── 3. SIMULATION ──
        result = _rollout(node.board, ai_piece)

        # ── 4. BACKPROPAGATION ──
        backprop_node = node
        while backprop_node is not None:
            backprop_node.visits += 1
            if backprop_node.player_who_just_moved == ai_piece:
                backprop_node.wins += result
            elif backprop_node.player_who_just_moved is not None:
                backprop_node.wins += (1.0 - result)
            backprop_node = backprop_node.parent

    # Retorno de segurança caso não haja filhos (muito raro)
    if not root.children:
        return board.get_legal_moves()[0]

    # Escolhe o nó mais robusto (mais visitado)
    best_move_node = max(root.children, key=lambda n: n.visits)
    return best_move_node.move
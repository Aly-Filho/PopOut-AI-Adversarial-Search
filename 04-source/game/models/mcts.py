import math
import random

# ==========================================
# 1. CLASSE BASE (Usada por todos os MCTS)
# ==========================================
class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0

        self.untried_moves = self.board.get_legal_moves()
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
                not self.board.get_legal_moves())

# ==========================================
# 2. FUNÇÕES AUXILIARES / HEURÍSTICAS
# ==========================================
def _find_winning_move(board):
    piece = board.current_player
    opponent = 'O' if piece == 'X' else 'X'
    
    for move in board.get_legal_moves():
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
    
    if opp_win_move and opp_win_move in board.get_legal_moves():
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

# ==========================================
# 3. FUNÇÕES DE ROLLOUT (SIMULAÇÃO)
# ==========================================
def _rollout_vanilla(board, ai_piece, max_depth=60):
    """Rollout 100% aleatório sem inteligência."""
    sim_board = board.copy()

    for _ in range(max_depth):
        legal_moves = sim_board.get_legal_moves()
        if not legal_moves:
            return 0.5 

        move = random.choice(legal_moves)
        current_p = sim_board.current_player
        opponent_p = 'O' if current_p == 'X' else 'X'
        sim_board.apply_move(move)

        if move[0] == 'pop':
            cw = sim_board.check_win(current_p)
            ow = sim_board.check_win(opponent_p)
            if cw and ow: return 1.0 if current_p == ai_piece else 0.0
            elif cw: return 1.0 if current_p == ai_piece else 0.0
            elif ow: return 0.0 if current_p == ai_piece else 1.0
        else:
            if sim_board.check_win(current_p):
                return 1.0 if current_p == ai_piece else 0.0
    return 0.5 

def _rollout(board, ai_piece, max_depth=60):
    """Rollout inteligente com heurísticas (Heavy Playouts)."""
    sim_board = board.copy()

    for _ in range(max_depth):
        legal_moves = sim_board.get_legal_moves()
        if not legal_moves:
            return 0.5

        win_move = _find_winning_move(sim_board)
        if win_move: return 1.0 if sim_board.current_player == ai_piece else 0.0

        block_move = _find_blocking_move(sim_board)
        if block_move:
            move = block_move
        else:
            move = _weighted_random_move(legal_moves, sim_board)

        current_p = sim_board.current_player
        opponent_p = 'O' if current_p == 'X' else 'X'
        sim_board.apply_move(move)

        if move[0] == 'pop':
            cw = sim_board.check_win(current_p)
            ow = sim_board.check_win(opponent_p)
            if cw and ow: return 1.0 if current_p == ai_piece else 0.0
            elif cw: return 1.0 if current_p == ai_piece else 0.0
            elif ow: return 0.0 if current_p == ai_piece else 1.0
        else:
            if sim_board.check_win(current_p):
                return 1.0 if current_p == ai_piece else 0.0
    return 0.5

# ==========================================
# 4. OS TRÊS ALGORITMOS PRINCIPAIS MCTS
# ==========================================

def mcts_vanilla_best_move(board, iterations=2000, c=1.414):
    """MCTS Padrão: Sem heurísticas de vitória imediata e simulações aleatórias."""
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

    if not root.children: return board.get_legal_moves()[0]
    return max(root.children, key=lambda n: n.visits).move


def mcts_best_move(board, iterations=2000, c=1.414):
    """MCTS Heurístico: Verificações imediatas e simulações pesadas."""
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

    if not root.children: return board.get_legal_moves()[0]
    return max(root.children, key=lambda n: n.visits).move


def mcts_multi_expansion_best_move(board, iterations=2000, c=1.414, n_children=3):
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

        expanded_nodes = []
        if not node.is_terminal() and node.untried_moves:
            num_to_expand = min(n_children, len(node.untried_moves))
            for _ in range(num_to_expand):
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)
                new_board = node.board.copy()
                new_board.apply_move(move)
                child = Node(new_board, parent=node, move=move)
                node.children.append(child)
                expanded_nodes.append(child)
            
            node = random.choice(expanded_nodes)

        result = _rollout(node.board, ai_piece)

        backprop_node = node
        while backprop_node is not None:
            backprop_node.visits += 1
            if backprop_node.player_who_just_moved == ai_piece:
                backprop_node.wins += result
            elif backprop_node.player_who_just_moved is not None:
                backprop_node.wins += (1.0 - result)
            backprop_node = backprop_node.parent

    if not root.children: return board.get_legal_moves()[0]
    return max(root.children, key=lambda n: n.visits).move
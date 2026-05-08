import math
import random

# MCTS algorithm need a class "node" to store the data that will be used on the interations inside the algorithm
class Node:
    def __init__(self, board, parent=None, move=None):

        self.board = board #Copy of the board on this current state.
        self.parent = parent #Parent node.
        self.move = move #Move that originated this node.
        self.children = []
        self.wins = 0.0 #Number of times this node was used to achive a win.
        self.visits = 0 #Number of times this node got explored.

        #Our class Board has a method that get the legal moves and stores it in itself.
        self.untried_moves = self.board.get_legal_moves()
        
        # Regista quem fez a jogada para chegar a este estado
        self.player_who_just_moved = parent.board.current_player if parent else None

    #classic Upper Confidence Bound, standard value of c.
    def ucb1(self, c=1.414):
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    # Uses the UCB1 to choose the best child node.
    def best_child(self, c=1.414):
        return max(self.children, key=lambda n: n.ucb1(c))


    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return (self.board.check_win('X') or 
                self.board.check_win('O') or 
                not self.board.get_legal_moves())


## Heuristics Functions (Heavy Playouts) ##

# There's a move that give us a win? POP logic already solved (RULE 1)
def _find_winning_move(board):
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

# Opponent is gonna win? What move is he going to do?
def _find_blocking_move(board):
    opponent = 'O' if board.current_player == 'X' else 'X'
    
    b_opp = board.copy()
    b_opp.current_player = opponent 
    
    opp_win_move = _find_winning_move(b_opp)
    
    if opp_win_move and opp_win_move in board.get_legal_moves():
        return opp_win_move
    return None

#Priotizes central columms (more involved on Wins)
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


## Roll Out, current with depth of 60 plays from a certain state ##
def _rollout(board, ai_piece, max_depth=60):
    sim_board = board.copy()

    for _ in range(max_depth):
        legal_moves = sim_board.get_legal_moves()
        if not legal_moves:
            return 0.5

        win_move = _find_winning_move(sim_board)
        if win_move:
            return 1.0 if sim_board.current_player == ai_piece else 0.0

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
            if cw and ow:
                return 1.0 if current_p == ai_piece else 0.0
            elif cw:
                return 1.0 if current_p == ai_piece else 0.0
            elif ow:
                return 0.0 if current_p == ai_piece else 1.0
        else:
            if sim_board.check_win(current_p):
                return 1.0 if current_p == ai_piece else 0.0

    return 0.5

# Main MCTS, it's called on the main file ##
def mcts_best_move(board, iterations=2000, c=1.414):
    ai_piece = board.current_player
    
    #1. First check if theres a winning move at the door!
    instant_win = _find_winning_move(board)
    if instant_win:
        return instant_win
        
    #2. Check if theres a losing possibility at the door and there's a way to escape it!
    instant_block = _find_blocking_move(board)
    if instant_block:
        return instant_block

    #3. Start the cycle of MCTS.
    root = Node(board.copy())

    for _ in range(iterations):
        node = root
        
        # 1. SELECTION
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(c)

        # 2. EXPANSION
        if not node.is_terminal() and node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            
            new_board = node.board.copy()
            new_board.apply_move(move)
            
            child = Node(new_board, parent=node, move=move)
            node.children.append(child)
            node = child

        # 3. SIMULATION
        result = _rollout(node.board, ai_piece)

        # 4. BACKPROPAGATION
        backprop_node = node
        while backprop_node is not None:
            backprop_node.visits += 1
            if backprop_node.player_who_just_moved == ai_piece:
                backprop_node.wins += result
            elif backprop_node.player_who_just_moved is not None:
                backprop_node.wins += (1.0 - result)
            backprop_node = backprop_node.parent

    # Safety return if there's no children.
    if not root.children:
        return board.get_legal_moves()[0]

    # Choose the node with more visits.
    best_move_node = max(root.children, key=lambda n: n.visits)
    return best_move_node.move
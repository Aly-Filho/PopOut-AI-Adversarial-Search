import math
import random

# A classe Node mantém-se exatamente igual
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


## Rollout Vanilla (Sem heurísticas, 100% aleatório) ##
def _rollout_vanilla(board, ai_piece, max_depth=60):
    sim_board = board.copy()

    for _ in range(max_depth):
        legal_moves = sim_board.get_legal_moves()
        if not legal_moves:
            return 0.5 # Empate

        # Escolha de jogada puramente aleatória (sem pesos ou bloqueios)
        move = random.choice(legal_moves)

        current_p = sim_board.current_player
        opponent_p = 'O' if current_p == 'X' else 'X'
        
        sim_board.apply_move(move)

        # Verificação de vitória com a regra de 'pop' do PopOut
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

    return 0.5 # Empate se atingir o limite de profundidade


## Main MCTS Vanilla ##
def mcts_vanilla_best_move(board, iterations=2000, c=1.414):
    ai_piece = board.current_player
    
    # Repara que removemos as validações instantâneas de vitória/bloqueio aqui na raiz
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

        # 3. SIMULATION (Chamando o nosso novo rollout vanilla)
        result = _rollout_vanilla(node.board, ai_piece)

        # 4. BACKPROPAGATION
        backprop_node = node
        while backprop_node is not None:
            backprop_node.visits += 1
            if backprop_node.player_who_just_moved == ai_piece:
                backprop_node.wins += result
            elif backprop_node.player_who_just_moved is not None:
                backprop_node.wins += (1.0 - result)
            backprop_node = backprop_node.parent

    # Safety return
    if not root.children:
        return board.get_legal_moves()[0]

    # Escolhe a jogada mais visitada
    best_move_node = max(root.children, key=lambda n: n.visits)
    return best_move_node.move
class Board:
    def __init__(self, rows=6, cols=7):
        """Inicializa o tabuleiro vazio com as dimensões especificadas."""
        self.rows = rows
        self.cols = cols
        self.grid = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.current_player = 'X'

    def switch_player(self):
        """Alterna o jogador atual."""
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_state(self):
        """Retorna uma tupla imutável do tabuleiro (ótimo para a Regra 3 e para a IA)."""
        return tuple(tuple(row) for row in self.grid)

    def is_valid_drop(self, col):
        """Verifica se a coluna tem espaço para uma nova peça."""
        return self.grid[0][col] == ' '

    def is_valid_pop(self, col, piece):
        """Verifica se o jogador pode remover a peça da base da coluna."""
        return self.grid[self.rows - 1][col] == piece

    def get_next_open_row(self, col):
        """Encontra a linha vazia mais baixa na coluna."""
        for r in range(self.rows - 1, -1, -1):
            if self.grid[r][col] == ' ':
                return r
        return None

    def drop_piece(self, col, piece):
        """Aplica a queda da peça na matriz instantaneamente."""
        row = self.get_next_open_row(col)
        if row is not None:
            self.grid[row][col] = piece
        return row # Retorna a linha onde caiu (útil para a UI depois)

    def pop_piece(self, col):
        """Remove a peça da base e faz as outras caírem instantaneamente."""
        # Puxa as peças de cima para baixo
        for r in range(self.rows - 1, 0, -1):
            self.grid[r][col] = self.grid[r - 1][col]
        # A posição mais alta da coluna fica vazia
        self.grid[0][col] = ' '

    def check_win(self, piece):
        """Verifica todas as combinações de vitória para a peça dada."""
        # Horizontal
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if (self.grid[r][c] == piece and self.grid[r][c+1] == piece and 
                    self.grid[r][c+2] == piece and self.grid[r][c+3] == piece):
                    return True
        # Vertical
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if (self.grid[r][c] == piece and self.grid[r+1][c] == piece and 
                    self.grid[r+2][c] == piece and self.grid[r+3][c] == piece):
                    return True
        # Diagonal Positiva
        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if (self.grid[r][c] == piece and self.grid[r+1][c+1] == piece and 
                    self.grid[r+2][c+2] == piece and self.grid[r+3][c+3] == piece):
                    return True
        # Diagonal Negativa
        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if (self.grid[r][c] == piece and self.grid[r-1][c+1] == piece and 
                    self.grid[r-2][c+2] == piece and self.grid[r-3][c+3] == piece):
                    return True
        return False

    def is_full(self):
        """Verifica se o tabuleiro está completamente cheio."""
        for c in range(self.cols):
            if self.grid[0][c] == ' ':
                return False
        return True
    
    def copy(self):
        """Cria uma cópia profunda do tabuleiro. Essencial para a árvore do MCTS simular jogadas."""
        new_board = Board(self.rows, self.cols)
        # Copia a matriz de forma rápida
        new_board.grid = [row[:] for row in self.grid]
        # Copia também o estado de quem é a vez na simulação
        new_board.current_player = self.current_player 
        return new_board
    
    def get_legal_moves(self):
        """Retorna uma lista de movimentos legais no formato ('push', col) ou ('pop', col)."""
        legal_moves = []
        for col in range(self.cols):
            # Verifica se pode fazer DROP (push)
            if self.is_valid_drop(col):
                legal_moves.append(("push", col))
            
            # Verifica se pode fazer POP com a peça do jogador atual
            if self.is_valid_pop(col, self.current_player):
                legal_moves.append(("pop", col))
        
        return legal_moves

    def apply_move(self, move):
        """Executa um movimento ('push' ou 'pop') e já passa a vez para o próximo."""
        move_type, col = move
        
        if move_type == "push":
            self.drop_piece(col, self.current_player)
        elif move_type == "pop":
            self.pop_piece(col)
            
        # Troca o turno automaticamente após aplicar a jogada
        self.switch_player()
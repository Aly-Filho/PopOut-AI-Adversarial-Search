import time
from IPython.display import clear_output
from board import Board
from ui import UI

def criar_tabuleiro_vazio(linhas=6, colunas=7):
    """
    Cria uma instância de um tabuleiro completamente vazio.
    """
    return Board(rows=linhas, cols=colunas)

def jupyter_render(board, message=""):
    """
    Renderizador Exclusivo para o Jupyter Notebook.
    Limpa a célula sem piscar e desenha o tabuleiro usando a UI base.
    """
    clear_output(wait=True)
    if message:
        print(message)
    # Reutilizamos a lógica de desenho do ui.py, mas contornamos o limpa-ecrãs do terminal
    UI.print_board(board)

def jupyter_animate_drop(board, col, final_row, piece):
    """Animação de queda fluida nativa para o Jupyter Notebook."""
    temp_board = board.copy() 
    for r in range(final_row + 1):
        temp_board.grid[r][col] = piece
        jupyter_render(temp_board, "A simular: Dropping Piece...")
        time.sleep(0.1) 
        if r != final_row:
            temp_board.grid[r][col] = ' '

def jupyter_animate_pop(board, col):
    """Animação de remoção e gravidade fluida nativa para o Jupyter Notebook."""
    temp_board = board.copy() 
    temp_board.grid[temp_board.rows - 1][col] = ' '
    
    jupyter_render(temp_board, "A simular: Popping Piece Out...")
    time.sleep(0.4) 
    
    # Anima a gravidade a puxar o resto das peças para baixo
    for r in range(temp_board.rows - 1, 0, -1):
        if temp_board.grid[r - 1][col] != ' ':
            temp_board.grid[r][col] = temp_board.grid[r - 1][col]
            temp_board.grid[r - 1][col] = ' '
            jupyter_render(temp_board, "A simular: Popping Piece Out...")
            time.sleep(0.1)

def simular_stack_e_pop(board, coluna=3, num_pecas=4):
    """
    Simula o empilhamento de peças alternadas ('X' e 'O') numa coluna,
    seguido do 'pop' de TODAS as peças sequencialmente até esvaziar a coluna.
    """
    pecas = ['X', 'O']
    
    jupyter_render(board, f"A iniciar demonstração: Empilhar {num_pecas} peças na coluna {coluna}...")
    time.sleep(1.5)

    # 1. FASE DE EMPILHAMENTO (DROP)
    for i in range(num_pecas):
        peca_atual = pecas[i % 2] # Alterna entre 'X' (0) e 'O' (1)
        
        jupyter_render(board, f"A preparar Drop da peça '{peca_atual}'...")
        time.sleep(0.5)
        
        if board.is_valid_drop(coluna):
            linha_queda = board.get_next_open_row(coluna)
            
            # Anima e efetiva a jogada
            jupyter_animate_drop(board, coluna, linha_queda, peca_atual)
            board.drop_piece(coluna, peca_atual)
            
            jupyter_render(board, f"Drop da peça '{peca_atual}' concluído.")
            time.sleep(0.8)
            
    jupyter_render(board, f"Pilha completa! A iniciar sequência de {num_pecas} Pops...")
    time.sleep(2)
            
    # 2. FASE DE ESVAZIAMENTO (POP)
    for i in range(num_pecas):
        # Como as peças foram alternadas na entrada, sairão alternadas na mesma ordem
        peca_base = pecas[i % 2]
        
        jupyter_render(board, f"A preparar Pop da peça base '{peca_base}' (Pop {i+1} de {num_pecas})...")
        time.sleep(1) # Pausa antes de cada pop
        
        # O PopOut só permite fazer pop das nossas próprias peças, 
        # mas como estamos a prever a alternância exata, será sempre válido.
        if board.is_valid_pop(coluna, peca_base):
            jupyter_animate_pop(board, coluna)
            board.pop_piece(coluna)
            jupyter_render(board, f"Pop {i+1} ('{peca_base}') concluído! Repare no deslize.")
        else:
            # Fallback de segurança visual (caso o estado fosse alterado externamente)
            jupyter_render(board, f"A forçar Pop demonstrativo...")
            jupyter_animate_pop(board, coluna)
            board.pop_piece(coluna)
            
        time.sleep(1.2) # Pausa para apreciar a gravidade a atuar
        
    jupyter_render(board, "Demonstração finalizada! A coluna está totalmente limpa.")


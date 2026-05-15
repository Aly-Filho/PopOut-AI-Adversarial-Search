import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

# ==========================================
# 1. FUNÇÕES MATEMÁTICAS (ENTROPIA E GANHO)
# ==========================================

def calculate_entropy(y):
    class_counts = Counter(y)
    total_samples = len(y)
    entropy = 0.0
    for count in class_counts.values():
        probability = count / total_samples
        if probability > 0:
            entropy -= probability * np.log2(probability)
    return entropy

def calculate_information_gain(df, feature_name, target_name):
    total_entropy = calculate_entropy(df[target_name])
    unique_values = df[feature_name].unique()
    total_samples = len(df)
    
    weighted_entropy = 0.0
    for value in unique_values:
        subset = df[df[feature_name] == value]
        subset_weight = len(subset) / total_samples
        subset_entropy = calculate_entropy(subset[target_name])
        weighted_entropy += subset_weight * subset_entropy
        
    information_gain = total_entropy - weighted_entropy
    return information_gain

# ==========================================
# 2. ALGORITMO ID3 (MOTOR PRINCIPAL)
# ==========================================

def build_id3_tree(df, features, target_name, current_depth=0, max_depth=None):
    unique_classes = df[target_name].unique()
    
    if len(unique_classes) == 1:
        return unique_classes[0]
    
    if len(features) == 0:
        return df[target_name].mode()[0]
        
    if max_depth is not None and current_depth >= max_depth:
        return df[target_name].mode()[0]
    
    best_feature = None
    max_gain = -1
    
    for feature in features:
        gain = calculate_information_gain(df, feature, target_name)
        if gain > max_gain:
            max_gain = gain
            best_feature = feature
            
    if max_gain <= 0:
         return df[target_name].mode()[0]
            
    tree = {best_feature: {}}
    remaining_features = [f for f in features if f != best_feature]
    
    for value in df[best_feature].unique():
        subset = df[df[best_feature] == value]
        if len(subset) == 0:
            tree[best_feature][value] = df[target_name].mode()[0]
        else:
            tree[best_feature][value] = build_id3_tree(
                subset, remaining_features, target_name, current_depth + 1, max_depth
            )
            
    return tree

def predict_sample(tree, sample, default_class="Desconhecido"):
    if not isinstance(tree, dict):
        return tree 
    
    root_node = next(iter(tree))
    feature_value = sample[root_node]
    
    if feature_value in tree[root_node]:
        return predict_sample(tree[root_node][feature_value], sample, default_class)
    else:
        return default_class

# ==========================================
# FUNÇÕES DE VISUALIZAÇÃO DA ÁRVORE
# ==========================================

def _get_tree_depth(tree):
    """Calculates the maximum depth of the tree for plotting dimensions."""
    if not isinstance(tree, dict): return 1
    return 1 + max(_get_tree_depth(v) for v in next(iter(tree.values())).values())

def _get_tree_width(tree):
    """Calculates the number of leaf nodes to determine plotting width."""
    if not isinstance(tree, dict): return 1
    return sum(_get_tree_width(v) for v in next(iter(tree.values())).values())

def _draw_node(ax, text, center, parent, edge_label):
    """Draws a single node and its connecting edge."""
    # Styling for feature nodes vs prediction leaf nodes
    if "Previsão:" in text:
        bbox_props = dict(boxstyle="round,pad=0.4", fc="#d9f2d9", ec="#006600", lw=1.5)
    else:
        bbox_props = dict(boxstyle="round,pad=0.4", fc="#e6f2ff", ec="#004d99", lw=1.5)
        
    ax.text(center[0], center[1], text, ha="center", va="center", bbox=bbox_props, zorder=3, fontsize=10)
    
    # Draw edge and label if it's not the root node
    if parent is not None:
        ax.plot([parent[0], center[0]], [parent[1], center[1]], color="#666666", lw=1.5, zorder=1)
        mid_x = (parent[0] + center[0]) / 2
        mid_y = (parent[1] + center[1]) / 2
        ax.text(mid_x, mid_y, edge_label, ha="center", va="center", 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), zorder=2, fontsize=9, color="#cc0000")

def _draw_tree_recursive(ax, tree, center, parent, edge_label, width, depth_step):
    """Recursively traverses the tree to draw nodes at calculated coordinates."""
    if not isinstance(tree, dict):
        _draw_node(ax, f"Previsão:\n{tree}", center, parent, edge_label)
        return
    
    root_node = next(iter(tree))
    _draw_node(ax, root_node, center, parent, edge_label)
    
    branches = tree[root_node]
    num_branches = len(branches)
    
    child_y = center[1] - depth_step
    start_x = center[0] - width / 2
    
    current_x = start_x
    for val, subtree in branches.items():
        # Apportion width based on the size of each subtree
        child_width = _get_tree_width(subtree) * (width / _get_tree_width(tree)) if _get_tree_width(tree) > 0 else width / num_branches
        child_x = current_x + child_width / 2
        _draw_tree_recursive(ax, subtree, (child_x, child_y), center, str(val), child_width, depth_step)
        current_x += child_width

def _plot_tree_graph(tree):
    """Sets up the matplotlib figure and triggers the recursive drawing."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    
    depth = _get_tree_depth(tree)
    depth_step = 1.0 / depth if depth > 1 else 0.5
    
    _draw_tree_recursive(ax, tree, center=(0.5, 1.0), parent=None, edge_label="", width=1.0, depth_step=depth_step)
    
    plt.tight_layout()
    plt.show()

def print_tree_terminal(tree, indent=""):
    """Original function to print the tree in the terminal."""
    if not isinstance(tree, dict):
        print(f"-> Previsão: {tree}")
        return
    
    root_node = next(iter(tree))
    print(f"[{root_node}]")
    
    branches = tree[root_node]
    for i, (value, subtree) in enumerate(branches.items()):
        is_last = (i == len(branches) - 1)
        prefix = "└── " if is_last else "├── "
        print(f"{indent}{prefix}{value} ", end="")
        
        next_indent = indent + ("    " if is_last else "│   ")
        print_tree_terminal(subtree, next_indent)

def display_tree(tree, mode="terminal"):
    """
    Main controller for displaying the tree.
    :param mode: 'terminal', 'plot', or 'both'
    """
    if mode in ["terminal", "both"]:
        print_tree_terminal(tree)
    
    if mode in ["plot", "both"]:
        _plot_tree_graph(tree)

# ==========================================
# 3. FUNÇÕES UTILITÁRIAS & INTERATIVIDADE
# ==========================================

def custom_train_test_split(df, test_size=0.3):
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    split_index = int(len(df_shuffled) * (1 - test_size))
    return df_shuffled.iloc[:split_index], df_shuffled.iloc[split_index:]

def calculate_accuracy(y_true, y_pred):
    correct = sum(1 for true, pred in zip(y_true, y_pred) if true == pred)
    return correct / len(y_true) if len(y_true) > 0 else 0

def parse_depths(depth_str):
    """Converte uma string '2,4,None' numa lista [2, 4, None]"""
    depths = []
    for d in depth_str.split(','):
        d = d.strip()
        if d.lower() == 'none' or d == '':
            depths.append(None)
        else:
            try:
                depths.append(int(d))
            except ValueError:
                print(f"Aviso: Valor inválido ignorado -> {d}")
    return depths

# ==========================================
# 4. MOTOR DE TREINO EM MASSA
# ==========================================

def train_and_evaluate(dataset_name, train_df, test_df, features, target, depths_to_test, display_mode):
    most_common = train_df[target].mode()[0]
    y_true_train = train_df[target].tolist()
    y_true_test = test_df[target].tolist()
    
    print(f"\n{'='*50}")
    print(f" INICIANDO AVALIAÇÃO - DATASET {dataset_name}")
    print(f"{'='*50}")
    
    for depth in depths_to_test:
        depth_label = depth if depth is not None else "Sem Limite (None)"
        print(f"\n⚙️ A treinar árvore com max_depth = {depth_label}...")
        
        tree = build_id3_tree(train_df, features, target, max_depth=depth)
        
        if display_mode != 'none':
            print(f"\n--- ESTRUTURA DA ÁRVORE (Profundidade: {depth_label}) ---")
            display_tree(tree, mode=display_mode)
            print("-" * 50)
        
        # Evaluate Train
        y_pred_train = [predict_sample(tree, row, most_common) for _, row in train_df.iterrows()]
        acc_train = calculate_accuracy(y_true_train, y_pred_train)
        
        # Evaluate Test
        y_pred_test = [predict_sample(tree, row, most_common) for _, row in test_df.iterrows()]
        acc_test = calculate_accuracy(y_true_test, y_pred_test)
        
        print(f"🎯 RESULTADOS (Max Depth: {depth_label}):")
        print(f"  -> Accuracy no Treino: {acc_train * 100:.2f}%")
        print(f"  -> Accuracy no Teste:  {acc_test * 100:.2f}%")

# ==========================================
# 5. LÓGICA DE EXECUÇÃO DOS MODELOS
# ==========================================

def execute_model(dataset_name, df, features, target):
    # Data Split (70/30 for Iris, 80/20 for Popout)
    test_size = 0.3 if dataset_name == "IRIS" else 0.2
    train_df, test_df = custom_train_test_split(df, test_size=test_size)
    
    print(f"\n📊 Distribuição dos Dados ({dataset_name}):")
    print(f"  -> Total de amostras: {len(df)}")
    print(f"  -> Treino: {len(train_df)} amostras")
    print(f"  -> Teste:  {len(test_df)} amostras\n")
    
    # INTERACTIVE QUESTIONS
    multi_response = input(f"Deseja testar múltiplas profundidades para o {dataset_name}? (s/n): ").strip().lower()
    
    if multi_response == 's':
        default_pattern = "2,4,6,8,10,14,18,24,30,40,50,None"
        depths_str = input(f"Introduza as profundidades separadas por vírgula\n(Pressione Enter para usar o padrão: {default_pattern}): ").strip()
        if not depths_str:
            depths_str = default_pattern
        depths_to_test = parse_depths(depths_str)
    else:
        depth_response = input("Introduza a profundidade única desejada (ou deixe em branco para 'None'): ").strip()
        depths_to_test = parse_depths(depth_response) if depth_response else [None]
        
    print("\nComo deseja visualizar a(s) árvore(s)?")
    print("[1] Apenas no Terminal")
    print("[2] Gráfico (Ideal para Notebooks)")
    print("[3] Ambos (Terminal e Gráfico)")
    print("[0] Não imprimir árvore")
    print_response = input("Escolha (0-3): ").strip()
    
    display_mode = 'none'
    if print_response == '1':
        display_mode = 'terminal'
    elif print_response == '2':
        display_mode = 'plot'
    elif print_response == '3':
        display_mode = 'both'
    
    # Call the main training and evaluation engine
    train_and_evaluate(dataset_name, train_df, test_df, features, target, depths_to_test, display_mode)

def load_iris_data():
    """Carrega, limpa e discretiza os dados do Iris numa só função."""
    df_iris = pd.read_csv('iris.csv')
    
    if 'ID' in df_iris.columns:
        df_iris = df_iris.drop(columns=['ID'])
        
    features_iris = ['sepallength', 'sepalwidth', 'petallength', 'petalwidth']
    target_iris = 'class'

    # Lógica de discretização embutida diretamente aqui
    print("\n--- Limites de Discretização (Valores de Corte) ---")
    for col in features_iris:
        df_iris[col], bins = pd.qcut(df_iris[col], q=3, labels=['Baixo', 'Médio', 'Alto'], retbins=True, duplicates='drop')
        print(f"Feature: '{col}' | Baixo: <= {bins[1]:.2f} | Médio: <= {bins[2]:.2f} | Alto: <= {bins[3]:.2f}")
    print("---------------------------------------------------")
    
    return df_iris, features_iris, target_iris

def load_popout_data():
    """Apenas carrega e devolve os dados do Popout."""
    df_popout = pd.read_csv('popout_dataset_winners.csv')
    features_popout = [f"c_{r}_{c}" for r in range(6) for c in range(7)]
    target_popout = 'move'

    return df_popout, features_popout, target_popout

# ==========================================
# 6. MENU PRINCIPAL
# ==========================================
if __name__ == "__main__":
    while True:
        print("\n=========================================")
        print("       MENU - ÁRVORES DE DECISÃO         ")
        print("=========================================")
        print("1. Executar Análise - IRIS")
        print("2. Executar Análise - POPOUT")
        print("3. Executar Ambos")
        print("0. Sair")
        print("=========================================")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            print("\n=== A PREPARAR DADOS IRIS ===")
            try:
                df, features, target = load_iris_data()
                execute_model("IRIS", df, features, target)
            except FileNotFoundError:
                print("❌ ERRO: Ficheiro 'iris.csv' não encontrado na pasta atual.")
                
        elif escolha == '2':
            print("\n=== A PREPARAR DADOS POPOUT ===")
            try:
                df, features, target = load_popout_data()
                execute_model("POPOUT", df, features, target)
            except FileNotFoundError:
                print("❌ ERRO: Ficheiro 'popout_dataset_winners.csv' não encontrado na pasta atual.")
                
        elif escolha == '3':
            print("\n=== A PREPARAR DADOS IRIS ===")
            try:
                df_iris, features_iris, target_iris = load_iris_data()
                execute_model("IRIS", df_iris, features_iris, target_iris)
            except FileNotFoundError:
                print("❌ ERRO: Ficheiro 'iris.csv' não encontrado.")
                
            print("\n=== A PREPARAR DADOS POPOUT ===")
            try:
                df_popout, features_popout, target_popout = load_popout_data()
                execute_model("POPOUT", df_popout, features_popout, target_popout)
            except FileNotFoundError:
                print("❌ ERRO: Ficheiro 'popout_dataset_winners.csv' não encontrado.")
                
        elif escolha == '0':
            print("A encerrar o programa...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.\n")
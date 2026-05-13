import pandas as pd
import numpy as np
from collections import Counter

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

def print_tree(tree, indent=""):
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
        print_tree(subtree, next_indent)

# ==========================================
# 3. FUNÇÕES UTILITÁRIAS & INTERATIVIDADE
# ==========================================

def discretize_features(df, features):
    df_discrete = df.copy()
    print("\n--- Limites de Discretização (Valores de Corte) ---")
    for col in features:
        df_discrete[col], bins = pd.qcut(df[col], q=3, labels=['Baixo', 'Médio', 'Alto'], retbins=True, duplicates='drop')
        print(f"Feature: '{col}' | Baixo: <= {bins[1]:.2f} | Médio: <= {bins[2]:.2f} | Alto: <= {bins[3]:.2f}")
    print("---------------------------------------------------")
    return df_discrete

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

def treinar_e_avaliar(nome_dataset, train_df, test_df, features, target, depths_to_test, print_trees):
    most_common = train_df[target].mode()[0]
    y_true_train = train_df[target].tolist()
    y_true_test = test_df[target].tolist()
    
    print(f"\n{'='*50}")
    print(f" INICIANDO AVALIAÇÃO - DATASET {nome_dataset}")
    print(f"{'='*50}")
    
    for prof in depths_to_test:
        label_prof = prof if prof is not None else "Sem Limite (None)"
        print(f"\n⚙️ A treinar árvore com max_depth = {label_prof}...")
        
        tree = build_id3_tree(train_df, features, target, max_depth=prof)
        
        if print_trees:
            print(f"\n--- ESTRUTURA DA ÁRVORE (Profundidade: {label_prof}) ---")
            print_tree(tree)
            print("-" * 50)
        
        # Avaliar Treino
        y_pred_train = [predict_sample(tree, row, most_common) for _, row in train_df.iterrows()]
        acc_train = calculate_accuracy(y_true_train, y_pred_train)
        
        # Avaliar Teste
        y_pred_test = [predict_sample(tree, row, most_common) for _, row in test_df.iterrows()]
        acc_test = calculate_accuracy(y_true_test, y_pred_test)
        
        print(f"🎯 RESULTADOS (Max Depth: {label_prof}):")
        print(f"  -> Accuracy no Treino: {acc_train * 100:.2f}%")
        print(f"  -> Accuracy no Teste:  {acc_test * 100:.2f}%")

# ==========================================
# 5. LÓGICA DE EXECUÇÃO DOS MODELOS
# ==========================================

def executar_modelo(nome_dataset, df, features, target):
    # Divisão de dados (70/30 para Iris, 80/20 para Popout)
    test_size = 0.3 if nome_dataset == "IRIS" else 0.2
    train_df, test_df = custom_train_test_split(df, test_size=test_size)
    
    print(f"\n📊 Distribuição dos Dados ({nome_dataset}):")
    print(f"  -> Total de amostras: {len(df)}")
    print(f"  -> Treino: {len(train_df)} amostras")
    print(f"  -> Teste:  {len(test_df)} amostras\n")
    
    # PERGUNTAS INTERATIVAS
    resp_multi = input(f"Deseja testar múltiplas profundidades para o {nome_dataset}? (s/n): ").strip().lower()
    
    if resp_multi == 's':
        padrao = "2,4,6,8,10,14,18,24,30,40,50,None"
        str_depths = input(f"Introduza as profundidades separadas por vírgula\n(Pressione Enter para usar o padrão: {padrao}): ").strip()
        if not str_depths:
            str_depths = padrao
        depths_to_test = parse_depths(str_depths)
    else:
        resp_prof = input("Introduza a profundidade única desejada (ou deixe em branco para 'None'): ").strip()
        depths_to_test = parse_depths(resp_prof) if resp_prof else [None]
        
    resp_print = input("Deseja imprimir a(s) árvore(s) gerada(s) no terminal? (s/n): ").strip().lower()
    print_trees = (resp_print == 's')
    
    # Chama o motor principal de treino e avaliação
    treinar_e_avaliar(nome_dataset, train_df, test_df, features, target, depths_to_test, print_trees)

def executar_iris():
    print("\n=== A PREPARAR MODELO IRIS ===")
    try:
        df_iris = pd.read_csv('iris.csv')
        if 'ID' in df_iris.columns:
            df_iris = df_iris.drop(columns=['ID'])
            
        features_iris = ['sepallength', 'sepalwidth', 'petallength', 'petalwidth']
        target_iris = 'class'

        df_iris_discrete = discretize_features(df_iris, features_iris)
        executar_modelo("IRIS", df_iris_discrete, features_iris, target_iris)
        
    except FileNotFoundError:
        print("❌ ERRO: Ficheiro 'iris.csv' não encontrado.")

def executar_popout():
    print("\n=== A PREPARAR MODELO POPOUT ===")
    try:
        df_popout = pd.read_csv('popout_dataset_winners.csv')
        features_popout = [f"c_{r}_{c}" for r in range(6) for c in range(7)]
        target_popout = 'move'

        executar_modelo("POPOUT", df_popout, features_popout, target_popout)
        
    except FileNotFoundError:
        print("❌ ERRO: Ficheiro 'popout_dataset_winners.csv' não encontrado.")

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
            executar_iris()
        elif escolha == '2':
            executar_popout()
        elif escolha == '3':
            executar_iris()
            executar_popout()
        elif escolha == '0':
            print("A encerrar o programa...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.\n")
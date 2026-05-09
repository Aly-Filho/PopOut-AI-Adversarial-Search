import pandas as pd
import numpy as np
from collections import Counter
import pprint

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
# 2. CONSTRUTOR DA ÁRVORE (ID3) 
# ==========================================
# Repare que a função de discretização desapareceu, pois o PopOut já é categórico!

def build_id3_tree(df, features, target_name):
    unique_classes = df[target_name].unique()
    if len(unique_classes) == 1:
        return unique_classes[0]
    
    if len(features) == 0:
        return df[target_name].mode()[0]
    
    best_feature = None
    max_gain = -1
    
    for feature in features:
        gain = calculate_information_gain(df, feature, target_name)
        if gain > max_gain:
            max_gain = gain
            best_feature = feature
            
    # Se o ganho máximo for 0, significa que nenhuma divisão ajuda mais. Retorna a classe mais comum.
    if max_gain <= 0:
         return df[target_name].mode()[0]
            
    tree = {best_feature: {}}
    remaining_features = [f for f in features if f != best_feature]
    
    for value in df[best_feature].unique():
        subset = df[df[best_feature] == value]
        if len(subset) == 0:
            tree[best_feature][value] = df[target_name].mode()[0]
        else:
            tree[best_feature][value] = build_id3_tree(subset, remaining_features, target_name)
            
    return tree

# ==========================================
# 3. FUNÇÃO DE PREVISÃO
# ==========================================

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
# 4. FUNÇÕES DE AVALIAÇÃO (SUBSTITUTAS DO SCIKIT-LEARN)
# ==========================================

def custom_train_test_split(df, test_size=0.3):
    """Embaralha e divide o dataset em treino e teste manualmente."""
    # O frac=1 com random_state baralha as linhas de forma reproduzível
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    split_index = int(len(df_shuffled) * (1 - test_size))
    
    train_df = df_shuffled.iloc[:split_index]
    test_df = df_shuffled.iloc[split_index:]
    
    return train_df, test_df

def calculate_accuracy(y_true, y_pred):
    """Calcula a percentagem de acertos manually."""
    correct = sum(1 for true, pred in zip(y_true, y_pred) if true == pred)
    return correct / len(y_true) if len(y_true) > 0 else 0


# ==========================================
# 5. EXECUÇÃO PRINCIPAL PARA O POPOUT
# ==========================================
if __name__ == "__main__":
    print("1. A carregar o dataset do PopOut...")
    try:
        # Quando gerar o ficheiro na arena, certifique-se que lhe dá este nome
        df_popout = pd.read_csv('popout_dataset_winners.csv')
    except FileNotFoundError:
        print("❌ ERRO: O ficheiro 'popout_dataset_winners.csv' não foi encontrado. Vá gerar o dataset primeiro!")
        exit()

    # O nosso tabuleiro tem 6 linhas e 7 colunas, logo as features são c_0_0 até c_5_6
    features = [f"c_{r}_{c}" for r in range(6) for c in range(7)]
    target = 'move' # A jogada sugerida pelo MCTS

    print("2. A dividir os dados em Treino (80%) e Teste (20%)...")
    # Para jogos, costuma ser melhor dar mais dados ao treino (ex: 80/20)
    train_df, test_df = custom_train_test_split(df_popout, test_size=0.2)

    print(f"  -> Tamanho do Treino: {len(train_df)} estados de tabuleiro")
    print(f"  -> Tamanho do Teste : {len(test_df)} estados de tabuleiro\n")

    print("3. A treinar a Árvore de Decisão ID3 (isto pode demorar um pouco mediante o tamanho do dataset)...")
    my_decision_tree = build_id3_tree(train_df, features, target)

    print("4. A fazer previsões para o conjunto de Teste...")
    most_common_move = train_df[target].mode()[0]
    
    y_true = test_df[target].tolist()
    y_pred = []
    
    for index, row in test_df.iterrows():
        prediction = predict_sample(my_decision_tree, row, default_class=most_common_move)
        y_pred.append(prediction)

    print("\n==========================================")
    print("          MÉTRICAS DE AVALIAÇÃO           ")
    print("==========================================\n")
    
    acc = calculate_accuracy(y_true, y_pred)
    print(f"🎯 Accuracy (Exatidão): {acc * 100:.2f}%\n")
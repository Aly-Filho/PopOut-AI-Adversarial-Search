import pandas as pd
import numpy as np
from collections import Counter
import pprint

# Importações do Scikit-Learn para a pipeline de avaliação
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

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
# 2. FUNÇÃO DE DISCRETIZAÇÃO
# ==========================================

def discretize_features(df, features):
    """
    Discretiza features contínuas dividindo-as em 3 categorias quantílicas
    e imprime os valores de fronteira para justificar as decisões no relatório.
    """
    df_discrete = df.copy()
    print("\n--- Limites de Discretização (Valores de Corte) ---")
    
    for col in features:
        # retbins=True devolve os valores numéricos onde os cortes foram feitos
        df_discrete[col], bins = pd.qcut(df[col], q=3, labels=['Baixo', 'Médio', 'Alto'], retbins=True, duplicates='drop')
        
        print(f"Feature: '{col}'")
        print(f"  - Baixo: valores entre {bins[0]:.2f} e {bins[1]:.2f}")
        print(f"  - Médio: valores maiores que {bins[1]:.2f} até {bins[2]:.2f}")
        print(f"  - Alto:  valores maiores que {bins[2]:.2f} até {bins[3]:.2f}\n")
        
    print("---------------------------------------------------")
    return df_discrete

# ==========================================
# 3. CONSTRUTOR DA ÁRVORE (ID3)
# ==========================================

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
# 4. FUNÇÃO DE PREVISÃO
# ==========================================

def predict_sample(tree, sample, default_class="Desconhecido"):
    """
    Navega a árvore. Adicionámos um default_class para o caso de no teste 
    aparecer uma combinação de atributos que a árvore nunca viu no treino.
    """
    if not isinstance(tree, dict):
        return tree 
    
    root_node = next(iter(tree))
    feature_value = sample[root_node]
    
    if feature_value in tree[root_node]:
        return predict_sample(tree[root_node][feature_value], sample, default_class)
    else:
        return default_class


# ==========================================
# 5. EXECUÇÃO PRINCIPAL COM SCIKIT-LEARN
# ==========================================
if __name__ == "__main__":
    print("1. A carregar o dataset iris.csv...")
    try:
        df_iris = pd.read_csv('iris.csv')
    except FileNotFoundError:
        print("❌ ERRO: O ficheiro 'iris.csv' não foi encontrado.")
        exit()

    if 'ID' in df_iris.columns:
        df_iris = df_iris.drop(columns=['ID'])

    features = ['sepallength', 'sepalwidth', 'petallength', 'petalwidth']
    target = 'class'

    print("2. A discretizar os dados contínuos...")
    df_discrete = discretize_features(df_iris, features)

    print("3. A dividir os dados em Treino (70%) e Teste (30%)...")
    # O random_state garante que os resultados são reproduzíveis
    train_df, test_df = train_test_split(df_discrete, test_size=0.3, random_state=42)

    print(f"  -> Tamanho do Treino: {len(train_df)} amostras")
    print(f"  -> Tamanho do Teste : {len(test_df)} amostras\n")

    print("4. A treinar a Árvore de Decisão ID3 apenas com os dados de Treino...")
    # A árvore só vai "ver" os dados de train_df
    my_decision_tree = build_id3_tree(train_df, features, target)

    print("5. A fazer previsões para o conjunto de Teste...")
    # Descobrimos a classe mais comum no treino para usar como fallback em casos "Desconhecidos"
    most_common_class = train_df[target].mode()[0]
    
    y_true = test_df[target].tolist()
    y_pred = []
    
    # Percorrer cada flor do dataset de teste e pedir à árvore para prever
    for index, row in test_df.iterrows():
        prediction = predict_sample(my_decision_tree, row, default_class=most_common_class)
        y_pred.append(prediction)

    print("\n==========================================")
    print("          MÉTRICAS DE AVALIAÇÃO           ")
    print("==========================================\n")
    
    # Calcular a Accuracy global
    acc = accuracy_score(y_true, y_pred)
    print(f"🎯 Accuracy (Exatidão): {acc * 100:.2f}%\n")
    
    print("📊 Relatório de Classificação Detalhado:")
    # O classification_report dá-nos o Precision, Recall e F1-Score para CADA tipo de flor
    print(classification_report(y_true, y_pred))
    
    print("Matriz de Confusão:")
    print(confusion_matrix(y_true, y_pred))
    print("==========================================\n")
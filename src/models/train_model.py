"""
Script de treinamento do modelo de classificação de notícias.
Pipeline completo: carregamento, processamento, treinamento e avaliação.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
<<<<<<< HEAD
import warnings

# CONFIGURAÇÃO DO PATH =====
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

print(f"📂 Diretório raiz do projeto: {ROOT_DIR}")
print(f"📂 Python path: {sys.path[:3]}")

# ===== IMPORTS DO PROJETO =====
try:
    from src.preprocessing.text_processor import TextProcessor
    from src.models.classifier import NewsClassifier
    print("✅ Módulos importados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print(f"📂 Verifique se está executando da raiz do projeto: {ROOT_DIR}")
    sys.exit(1)
=======
from sklearn.utils.class_weight import compute_class_weight
import warnings

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.preprocessing.text_processor import TextProcessor
from src.models.classifier import NewsClassifier
>>>>>>> 4147398bb0b3a4801dbe4414a0042c3f05c4caeb

warnings.filterwarnings('ignore')


def load_dataset(dataset_path: str) -> pd.DataFrame:
    """
    Carrega o dataset de notícias.
    
    Args:
        dataset_path (str): Caminho para o arquivo CSV
        
    Returns:
        pd.DataFrame: DataFrame com os dados carregados
    """
    print("📁 Carregando dataset...")
    
    try:
        df = pd.read_csv(dataset_path)
        print(f"✅ Dataset carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        return df
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {dataset_path}")
        print("📝 Coloque o dataset na pasta 'data/raw/' com o nome 'news_dataset.csv'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {str(e)}")
        sys.exit(1)


def prepare_data(df: pd.DataFrame, text_column: str = 'title', 
                category_column: str = 'category') -> tuple:
    """
    Prepara os dados para treinamento: limpeza e split.
    
    Args:
        df (pd.DataFrame): DataFrame original
        text_column (str): Nome da coluna de texto
        category_column (str): Nome da coluna de categoria
        
    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    print("\n🔄 Preparando dados para treinamento...")
    
    # Verificar colunas necessárias
    required_columns = [text_column, category_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Colunas não encontradas: {missing_columns}")
        print(f"📋 Colunas disponíveis: {list(df.columns)}")
        sys.exit(1)
    
    # Remover linhas com valores nulos nas colunas necessárias
    initial_len = len(df)
    df = df.dropna(subset=required_columns)
    print(f"🧹 Removidas {initial_len - len(df)} linhas com valores nulos")
    
    # Balanceamento básico: remover categorias com poucas amostras
    category_counts = df[category_column].value_counts()
    min_samples = 10  # Mínimo de amostras por categoria
    
    small_categories = category_counts[category_counts < min_samples].index
    if len(small_categories) > 0:
        print(f"⚖️ Removendo {len(small_categories)} categorias com menos de {min_samples} amostras")
        df = df[~df[category_column].isin(small_categories)]
    
    # Processar textos
    print("🔤 Processando textos...")
    processor = TextProcessor()
    X = processor.process_batch(df[text_column].values)
    y = df[category_column].values
    
    # Remover textos vazios após processamento
    valid_indices = [i for i, text in enumerate(X) if text.strip()]
    X = [X[i] for i in valid_indices]
    y = [y[i] for i in valid_indices]
    
    print(f"📊 Dados processados: {len(X)} amostras válidas")
    
    # Verificar balanceamento e aplicar estratificação
    unique_categories, counts = np.unique(y, return_counts=True)
    print(f"📚 Categorias finais: {len(unique_categories)}")
    
    # Split estratificado
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    
    print(f"✂️ Split realizado: {len(X_train)} treino, {len(X_test)} teste")
    
    return X_train, X_test, y_train, y_test


def train_and_evaluate(X_train, X_test, y_train, y_test):
    """
    Treina e avalia o modelo de classificação.
    
    Args:
        X_train, X_test, y_train, y_test: Dados de treino e teste
    """
    print("\n🚀 Treinando classificador...")
    
    # Criar e treinar modelo
    classifier = NewsClassifier()
    classifier.fit(X_train, y_train)
    
    # Avaliar modelo
    print("\n📊 Avaliando modelo...")
    metrics = classifier.evaluate(X_test, y_test)
    
    # Exibir resultados
    print("\n" + "="*50)
    print("📈 RESULTADOS DA AVALIAÇÃO")
    print("="*50)
    print(f"🎯 Acurácia: {metrics['accuracy']:.4f}")
    print(f"📊 F1-Score Macro: {metrics['macro_avg_f1']:.4f}")
    print(f"📊 F1-Score Ponderado: {metrics['weighted_avg_f1']:.4f}")
    print("="*50)
    
    # Mostrar top 5 e bottom 5 categorias por F1-score
    report = metrics['classification_report']
    categories_f1 = {
        cat: report[cat]['f1-score'] 
        for cat in report 
        if cat not in ['accuracy', 'macro avg', 'weighted avg']
    }
    
    sorted_categories = sorted(categories_f1.items(), key=lambda x: x[1], reverse=True)
    
    print("\n📈 TOP 5 Categorias (F1-Score):")
    for cat, f1 in sorted_categories[:5]:
        print(f"  ✅ {cat}: {f1:.4f}")
    
    print("\n📉 BOTTOM 5 Categorias (F1-Score):")
    for cat, f1 in sorted_categories[-5:]:
        print(f"  ⚠️ {cat}: {f1:.4f}")
    
    return classifier, metrics


<<<<<<< HEAD
def save_artifacts(classifier, metrics, output_dir: str = 'src/models'):
    """
    Salva o modelo treinado e métricas de avaliação.
    
    Argumentos:
=======
def save_artifacts(classifier, metrics, output_dir: str = 'models'):
    """
    Salva o modelo treinado e métricas de avaliação.
    
    Args:
>>>>>>> 4147398bb0b3a4801dbe4414a0042c3f05c4caeb
        classifier: Modelo treinado
        metrics: Métricas de avaliação
        output_dir (str): Diretório de saída
    """
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Salvar modelo
    model_path = os.path.join(output_dir, 'news_classifier.pkl')
    classifier.save(model_path)
    
    # Salvar métricas
    metrics_path = os.path.join(output_dir, 'model_metrics.txt')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        f.write(f"Acurácia: {metrics['accuracy']:.4f}\n")
        f.write(f"F1-Score Macro: {metrics['macro_avg_f1']:.4f}\n")
        f.write(f"F1-Score Ponderado: {metrics['weighted_avg_f1']:.4f}\n")
        f.write(f"\nCategorias suportadas: {len(classifier.classes_)}\n")
    
    print(f"\n💾 Artefatos salvos em: {output_dir}/")


def main():
    """Função principal do pipeline de treinamento."""
    
    print("🤖 CLASSIFICADOR DE NOTÍCIAS - TREINAMENTO")
    print("="*50)
    
    # Configurações
    DATASET_PATH = 'data/raw/news_dataset.csv'
    TEXT_COLUMN = 'title'
    CATEGORY_COLUMN = 'category'
    
    # Pipeline
    # 1. Carregar dados
    df = load_dataset(DATASET_PATH)
    
    # 2. Preparar dados
    X_train, X_test, y_train, y_test = prepare_data(
        df, 
        text_column=TEXT_COLUMN, 
        category_column=CATEGORY_COLUMN
    )
    
    # 3. Treinar e avaliar
    classifier, metrics = train_and_evaluate(X_train, X_test, y_train, y_test)
    
    # 4. Salvar artefatos
    save_artifacts(classifier, metrics)
    
    print("\n✅ Pipeline de treinamento concluído com sucesso!")


if __name__ == "__main__":
    main()
<<<<<<< HEAD
    
=======
  
>>>>>>> 4147398bb0b3a4801dbe4414a0042c3f05c4caeb

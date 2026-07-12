"""
Classificador de categorias de notícias.
Implementa o pipeline de classificação usando TF-IDF e Naive Bayes.
"""

import joblib
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix


class NewsClassifier:
    """
    Classificador de notícias usando TF-IDF + Naive Bayes.
    
    Características:
    - Pipeline integrado de vetorização e classificação
    - Suporte a balanceamento de classes
    - Métricas detalhadas por categoria
    
    Attributes:
        pipeline (Pipeline): Pipeline sklearn completo
        classes_ (List[str]): Lista de categorias conhecidas
        vectorizer (TfidfVectorizer): Vetorizador TF-IDF
        classifier (MultinomialNB): Classificador Naive Bayes
    """
    
    def __init__(self):
        """Inicializa o pipeline de classificação."""
        self.pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.9,
                sublinear_tf=True
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        self.classes_ = None
        self.vectorizer = None
        self.classifier = None
        
    def fit(self, X: List[str], y: List[str]) -> 'NewsClassifier':
        """
        Treina o classificador.
        
        Args:
            X (List[str]): Lista de textos processados
            y (List[str]): Lista de categorias correspondentes
            
        Returns:
            NewsClassifier: Instância treinada do classificador
        """
        print("🎯 Iniciando treinamento do classificador...")
        print(f"📊 Amostras de treino: {len(X)}")
        print(f"📚 Categorias únicas: {len(set(y))}")
        
        # Treinar o pipeline
        self.pipeline.fit(X, y)
        
        # Extrair componentes para acesso direto
        self.vectorizer = self.pipeline.named_steps['vectorizer']
        self.classifier = self.pipeline.named_steps['classifier']
        self.classes_ = self.pipeline.classes_
        
        print("✅ Treinamento concluído com sucesso!")
        
        return self
    
    def predict(self, X: List[str]) -> np.ndarray:
        """
        Prediz categorias para novos textos.
        
        Args:
            X (List[str]): Lista de textos para classificar
            
        Returns:
            np.ndarray: Array com categorias preditas
        """
        return self.pipeline.predict(X)
    
    def predict_proba(self, X: List[str]) -> np.ndarray:
        """
        Retorna probabilidades de cada categoria.
        
        Args:
            X (List[str]): Lista de textos para classificar
            
        Returns:
            np.ndarray: Matriz de probabilidades por classe
        """
        return self.pipeline.predict_proba(X)
    
    def predict_with_confidence(self, text: str) -> Dict:
        """
        Prediz categoria com confiança e top 3 alternativas.
        
        Args:
            text (str): Texto para classificar
            
        Returns:
            Dict: Resultado com categoria principal, confiança e alternativas
        """
        # Predizer probabilidades
        probabilities = self.predict_proba([text])[0]
        
        # Ordenar por probabilidade decrescente
        top_indices = np.argsort(probabilities)[::-1]
        
        # Categoria principal
        main_category = self.classes_[top_indices[0]]
        confidence = float(probabilities[top_indices[0]])
        
        # Top 3 alternativas
        alternatives = [
            {
                "categoria": str(self.classes_[idx]),
                "probabilidade": float(probabilities[idx])
            }
            for idx in top_indices[:3]
        ]
        
        return {
            "categoria_principal": main_category,
            "confianca": round(confidence, 4),
            "alternativas": alternatives,
            "texto_analisado": text
        }
    
    def evaluate(self, X_test: List[str], y_test: List[str]) -> Dict:
        """
        Avalia o modelo com métricas detalhadas.
        
        Args:
            X_test (List[str]): Textos de teste
            y_test (List[str]): Categorias verdadeiras
            
        Returns:
            Dict: Dicionário com métricas de avaliação
        """
        # Predições
        y_pred = self.predict(X_test)
        
        # Métricas detalhadas
        report = classification_report(
            y_test, 
            y_pred, 
            target_names=self.classes_,
            output_dict=True
        )
        
        # Matriz de confusão
        cm = confusion_matrix(y_test, y_pred)
        
        # Métricas globais
        metrics = {
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "accuracy": report['accuracy'],
            "macro_avg_f1": report['macro avg']['f1-score'],
            "weighted_avg_f1": report['weighted avg']['f1-score']
        }
        
        return metrics
    
    def save(self, filepath: str) -> None:
        """
        Salva o modelo treinado em disco.
        
        Args:
            filepath (str): Caminho para salvar o modelo
        """
        model_data = {
            'pipeline': self.pipeline,
            'classes_': self.classes_,
            'metadata': {
                'type': 'NewsClassifier',
                'version': '1.0.0',
                'features': self.pipeline.named_steps['vectorizer'].max_features
            }
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Modelo salvo em: {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'NewsClassifier':
        """
        Carrega um modelo salvo do disco.
        
        Args:
            filepath (str): Caminho do modelo salvo
            
        Returns:
            NewsClassifier: Instância carregada do classificador
        """
        model_data = joblib.load(filepath)
        
        classifier = cls()
        classifier.pipeline = model_data['pipeline']
        classifier.classes_ = model_data['classes_']
        classifier.vectorizer = classifier.pipeline.named_steps['vectorizer']
        classifier.classifier = classifier.pipeline.named_steps['classifier']
        
        print(f"📂 Modelo carregado de: {filepath}")
        print(f"📚 Categorias suportadas: {len(classifier.classes_)}")
        
        return classifier

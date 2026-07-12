"""
Processador de texto para língua portuguesa.
Responsável pela limpeza e normalização dos títulos de notícias.
"""

import re
import unicodedata
from typing import List, Optional
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup


class TextProcessor:
    """
    Classe para processamento de texto em português brasileiro.
    
    Responsabilidades:
    - Remover HTML e caracteres especiais
    - Normalizar acentos e caracteres
    - Tokenizar e remover stopwords
    - Aplicar stemming para redução de dimensionalidade
    
    Attributes:
        stopwords_pt (set): Conjunto de stopwords em português
        stemmer (nltk.stem.RSLPStemmer): Stemmer para português
    """
    
    def __init__(self):
        """Inicializa o processador com recursos de NLP em português."""
        self._download_nltk_resources()
        
        # Stopwords em português
        self.stopwords_pt = set(stopwords.words('portuguese'))
        
        # Adicionar stopwords específicas do domínio jornalístico
        domain_stopwords = {'após', 'diz', 'segundo', 'nova', 'novo', 'dizem'}
        self.stopwords_pt.update(domain_stopwords)
        
        # Stemmer para português (opcional, pode ser substituído por lematização)
        try:
            self.stemmer = nltk.stem.RSLPStemmer()
        except:
            # Fallback para stemmer simples se RSLP não estiver disponível
            self.stemmer = None
    
    @staticmethod
    def _download_nltk_resources() -> None:
        """
        Baixa recursos necessários do NLTK de forma segura.
        """
        resources = ['stopwords', 'rslp', 'punkt']
        for resource in resources:
            try:
                nltk.data.find(f'corpora/{resource}')
            except LookupError:
                nltk.download(resource, quiet=True)
    
    def clean_text(self, text: str) -> str:
        """
        Limpa e normaliza o texto.
        
        Args:
            text (str): Texto bruto para processamento
            
        Returns:
            str: Texto limpo e normalizado
        """
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # Remover tags HTML
        text = BeautifulSoup(text, "html.parser").get_text()
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remover menções e hashtags
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Normalizar caracteres especiais e acentos
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        
        # Remover números, pontuação e caracteres especiais (mantendo espaços)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza o texto em palavras, removendo stopwords e palavras curtas.
        
        Args:
            text (str): Texto limpo para tokenização
            
        Returns:
            List[str]: Lista de tokens relevantes
        """
        if not text:
            return []
        
        # Tokenização simples por espaços
        tokens = text.split()
        
        # Filtrar stopwords e palavras muito curtas
        tokens = [
            token for token in tokens 
            if token not in self.stopwords_pt and len(token) > 2
        ]
        
        # Aplicar stemming se disponível
        if self.stemmer:
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def process(self, text: str, return_string: bool = True) -> str:
        """
        Pipeline completo de processamento de texto.
        
        Args:
            text (str): Texto original
            return_string (bool): Se True, retorna string; se False, retorna lista de tokens
            
        Returns:
            Union[str, List[str]]: Texto processado
        """
        # Limpar texto
        cleaned_text = self.clean_text(text)
        
        # Tokenizar
        tokens = self.tokenize(cleaned_text)
        
        if return_string:
            return ' '.join(tokens)
        return tokens
    
    def process_batch(self, texts: List[str]) -> List[str]:
        """
        Processa um lote de textos.
        
        Args:
            texts (List[str]): Lista de textos para processar
            
        Returns:
            List[str]: Lista de textos processados
        """
        return [self.process(text) for text in texts]

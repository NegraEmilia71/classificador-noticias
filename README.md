# 📰 Classificador de Categorias de Notícias

API inteligente para classificação automática de notícias brasileiras usando Machine Learning.

## 🎯 Visão Geral

Sistema completo de classificação de notícias que utiliza Processamento de Linguagem Natural (NLP) e Machine Learning para categorizar automaticamente notícias brasileiras baseado em seus títulos. O projeto inclui:

- **Pipeline de Treinamento**: Scripts para treinar e avaliar modelos
- **API REST**: Interface para classificação em tempo real
- **Containerização**: Docker para deploy simplificado
- **Documentação**: Swagger/OpenAPI integrado

## 📊 Dataset

O modelo foi treinado com o dataset [News of the site FolhaUOL](https://www.kaggle.com/datasets/marlesson/news-of-the-site-folhauol), que contém notícias do jornal Folha de São Paulo.

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**: Linguagem principal
- **Scikit-learn**: Pipeline de ML (TF-IDF + Naive Bayes)
- **NLTK & spaCy**: Processamento de linguagem natural
- **FastAPI**: Framework para API REST
- **Docker**: Containerização e deploy
- **Pytest**: Testes automatizados

## 📁 Estrutura do Projeto
classificador-noticias/
├── data/ # Dados do projeto
│ └── raw/ # Dataset original
├── notebooks/ # Análises exploratórias
│ └── eda.ipynb # Notebook de EDA
├── src/ # Código fonte
│ ├── preprocessing/ # Processamento de texto
│ │ └── text_processor.py # Limpeza e tokenização
│ ├── models/ # Modelos de ML
│ │ ├── classifier.py # Classificador principal
│ │ └── train_model.py # Script de treinamento
│ └── api/ # API REST
│ └── main.py # FastAPI application
├── tests/ # Testes unitários
│ └── test_api.py # Testes da API
├── Dockerfile # Container Docker
├── docker-compose.yml # Orquestração
├── requirements.txt # Dependências
└── README.md # Este arquivo

## 🚀 Quick Start

### Pré-requisitos
- Python 3.9+
- Docker e Docker Compose (opcional)
- Dataset na pasta `data/raw/`

### Instalação Local

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd classificador-noticias

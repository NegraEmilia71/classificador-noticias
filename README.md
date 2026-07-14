# 📰 Classificador de Categorias de Notícias

API inteligente para classificação automática de notícias brasileiras usando Machine Learning.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)

## 📋 Descrição

O sistema consiste em um classificador de notícias que utiliza técnicas de Processamento de Linguagem Natural (NLP) para categorizar títulos de notícias brasileiras em categorias como:
- Política
- Economia
- Esportes
- Tecnologia
- E outras categorias

## 🚀 Funcionalidades

- ✅ Classificação individual por título
- ✅ Classificação em lote (até 100 notícias)
- ✅ Informações do modelo em produção
- ✅ Health Check para monitoramento
- ✅ Documentação interativa via Swagger/ReDoc

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework para construção da API
- **Scikit-learn** - Modelagem e vetorização
- **NLTK** - Processamento de texto
- **Pandas** - Manipulação de dados
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validação de dados

## 🎯 Visão Geral

Sistema completo de classificação de notícias que utiliza Processamento de Linguagem Natural (NLP) e Machine Learning para categorizar automaticamente notícias brasileiras baseado em seus títulos. O projeto inclui:

- **Pipeline de Treinamento**: Scripts para treinar e avaliar modelos
- **API REST**: Interface para classificação em tempo real
- **Containerização**: Docker para deploy simplificado
- **Documentação**: Swagger/OpenAPI integrado

## 📊 Dataset

O modelo foi treinado com o dataset [News of the site FolhaUOL](https://www.kaggle.com/datasets/marlesson/news-of-the-site-folhauol), que contém notícias do jornal Folha de São Paulo.

## 📁 Estrutura do Projeto
```plaintext
classificador-noticias/
├── data/                              # Dados do projeto
│   └── raw/
│       └── new_dataset.csv            # Dataset original
├── notebooks/                         # Análises exploratórias
│   └── eda.ipynb                      # Notebook de EDA
├── src/                               # Código fonte
│   ├── preprocessing/                 # Processamento de texto
│   │   └── text_processor.py          # Limpeza e tokenização
│   ├── models/                        # Modelos de ML
│   │   ├── classifier.py              # Classificador principal
│   │   └── train_model.py             # Script de treinamento
│   └── api/                           # API REST
│       └── main.py                    # FastAPI application
├── tests/                             # Testes unitários
│   ├── test_api.py                    # Testes da API
│   ├── Include
│   ├── Lib
│   ├── Scripts
│   └── share
├── .gitignore
├── docker-compose.yml                 # Orquestração
├── Dockerfile                         # Container Docker
├── requirements.txt                   # Dependências
└── README.md                          # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**: Linguagem principal
- **Scikit-learn**: Pipeline de ML (TF-IDF + Naive Bayes)
- **NLTK & spaCy**: Processamento de linguagem natural
- **FastAPI**: Framework para API REST
- **Docker**: Containerização e deploy
- **Pytest**: Testes automatizados

## 🚀 Quick Start

### Pré-requisitos
- Python 3.9+
- Docker e Docker Compose (opcional)
- Dataset na pasta `data/raw/`

##📎 Links e Materiais
### 🔗 Acesso ao Repositório
- **URL do repositório:** [https:/github.com/NegraEmilia71/classificador-noticias] (https:/github.com/NegraEmilia71/classificador-noticias)
- **Clone via HTTPS:** 
  ```bash
  git clone https:/github.com/NegraEmilia71/classificador-noticias.git
  ```
- **Clone via SSH:**
  ```bash
  git clone git@github.com:NegraEmilia71/classificador-noticias.git
  ```

### 📊 Material de Apresentação
- **Slides da apresentação:** [Link para o Google Slides/PowerPoint/PDF]

### Instalação Local
```bash
1. 🎯 Clone o repositório
git clone <https://github.com/NegraEmilia71>
cd classificador-noticias

2. 📖 Documentação da API
Acesse a documentação interativa:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

Endpoints
Método	Endpoint	Descrição
GET	/	Rota raiz - boas-vindas
GET	/health	Health check da API
GET	/modelo/info	Informações do modelo
POST	/classificar	Classificar uma notícia
POST	/classificar/lote	Classificar em lote

3. 🧪 Exemplo de Uso
Classificar uma notícia
bash
curl -X POST "http://127.0.0.1:8000/classificar" \
     -H "Content-Type: application/json" \
     -d '{"titulo": "Governo anuncia novo pacote econômico"}'

Resposta:
json
{
  "categoria_principal": "economia",
  "confianca": 0.92,
  "alternativas": [
    {"categoria": "politica", "confianca": 0.05},
    {"categoria": "negocios", "confianca": 0.02}
  ],
  "texto_analisado": "Governo anuncia novo pacote econômico",
  "timestamp": "2026-07-13T17:30:00"
}
Classificação em Lote
bash
curl -X POST "http://127.0.0.1:8000/classificar/lote" \
     -H "Content-Type: application/json" \
     -d '{
       "noticias": [
         {"titulo": "Título da notícia 1"},
         {"titulo": "Título da notícia 2"}
       ]
     }'

4. 🐳 Dockerfile
Build da imagem
bash
docker build -t classificador-noticias .
Executar o container
bash
docker run -p 8000:8000 classificador-noticias

5. ✅ Testes
bash
pytest tests/

6. 📊 Performance do Modelo
Métrica	Valor
Acurácia	0.85
F1-Score Macro	0.83
F1-Score Ponderado	0.86
Categorias	10
Os resultados podem variar conforme o dataset utilizado.

7. 👩‍💻 Autora
Joyce Emília 
LinkedIn | GitHub

8. 📄 Licença
Este projeto está sob a licença MIT.

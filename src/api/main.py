"""
API REST para classificação de categorias de notícias.
Implementa endpoints para classificação e monitoramento.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.classifier import NewsClassifier
from src.preprocessing.text_processor import TextProcessor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização da API
app = FastAPI(
    title="Classificador de Notícias",
    description="""
    API para classificação automática de categorias de notícias brasileiras.
    
    ## Funcionalidades
    * **Classificação**: Classifica uma notícia com base no título
    * **Classificação em lote**: Classifica múltiplas notícias simultaneamente
    * **Métricas**: Informações sobre o modelo em produção
    * **Health Check**: Verificação de saúde da API
    
    ## Categorias Suportadas
    O modelo é treinado para classificar notícias em diversas categorias 
    como política, economia, esportes, tecnologia, entre outras.
    """,
    version="1.0.0",
    contact={
        "name": "Equipe de Dados",
        "email": "data@empresa.com.br"
    }
)

# Configuração CORS para permitir chamadas de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis globais para o modelo
classifier = None
text_processor = None

# Timestamp de inicialização da API
startup_time = None


class NewsInput(BaseModel):
    """
    Modelo de entrada para classificação de notícia individual.
    """
    titulo: str = Field(
        ..., 
        min_length=5,
        max_length=500,
        description="Título da notícia para classificação",
        example="Governo anuncia novo pacote de medidas econômicas"
    )
    
    @validator('titulo')
    def validate_titulo(cls, v):
        """Valida se o título não está vazio após limpeza."""
        if not v or not v.strip():
            raise ValueError('O título não pode estar vazio')
        return v.strip()


class BatchNewsInput(BaseModel):
    """
    Modelo de entrada para classificação em lote.
    """
    noticias: List[NewsInput] = Field(
        ..., 
        min_items=1,
        max_items=100,
        description="Lista de notícias para classificar (máximo 100)"
    )


class ClassificationResponse(BaseModel):
    """
    Modelo de resposta para classificação individual.
    """
    categoria_principal: str = Field(..., description="Categoria principal predita")
    confianca: float = Field(..., ge=0, le=1, description="Confiança da predição (0-1)")
    alternativas: List[Dict[str, Any]] = Field(..., description="Top 3 categorias alternativas")
    texto_analisado: str = Field(..., description="Texto original analisado")
    timestamp: str = Field(..., description="Timestamp da classificação")


class BatchClassificationResponse(BaseModel):
    """
    Modelo de resposta para classificação em lote.
    """
    resultados: List[ClassificationResponse]
    total_processado: int
    tempo_processamento: float


class ModelInfo(BaseModel):
    """
    Informações sobre o modelo em produção.
    """
    status: str
    categorias_suportadas: int
    lista_categorias: List[str]
    versao_modelo: str
    uptime: str


def load_model() -> bool:
    """
    Carrega o modelo treinado e inicializa o processador de texto.
    
    Returns:
        bool: True se o modelo foi carregado com sucesso, False caso contrário
    """
    global classifier, text_processor
    
    logger.info("🔄 Inicializando modelo e processador...")
    
    try:
        # Caminho do modelo (configurável via variável de ambiente)
        model_path = os.getenv('MODEL_PATH', 'models/news_classifier.pkl')
        
        if not os.path.exists(model_path):
            logger.error(f"❌ Modelo não encontrado em: {model_path}")
            logger.info("📝 Execute 'python src/models/train_model.py' para treinar o modelo")
            return False
        
        # Carregar classificador
        classifier = NewsClassifier.load(model_path)
        
        # Inicializar processador de texto
        text_processor = TextProcessor()
        
        logger.info(f"✅ Modelo carregado com sucesso! Categorias: {len(classifier.classes_)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo: {str(e)}")
        return False


@app.on_event("startup")
async def startup_event():
    """Executa ao iniciar a API."""
    global startup_time
    
    logger.info("🚀 Iniciando API de Classificação de Notícias")
    startup_time = datetime.now()
    
    if not load_model():
        logger.warning("⚠️ API iniciada sem modelo. Endpoints de classificação indisponíveis.")
    
    logger.info("✅ API pronta para receber requisições!")


@app.get("/", tags=["Início"])
async def root():
    """
    Rota raiz da API.
    
    Returns:
        dict: Mensagem de boas-vindas e instruções básicas
    """
    return {
        "mensagem": "Bem-vindo à API de Classificação de Notícias",
        "documentacao": "/docs",
        "versao": "1.0.0",
        "status": "online" if classifier else "modelo_indisponivel"
    }


@app.get("/health", tags=["Monitoramento"])
async def health_check():
    """
    Endpoint de verificação de saúde da API.
    Útil para monitoramento e balanceadores de carga.
    
    Returns:
        dict: Status da API e do modelo
    """
    health_status = {
        "api_status": "healthy",
        "modelo_status": "loaded" if classifier else "not_loaded",
        "timestamp": datetime.now().isoformat()
    }
    
    if not classifier:
        health_status["api_status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


@app.get("/modelo/info", 
         response_model=ModelInfo,
         tags=["Modelo"])
async def model_info():
    """
    Retorna informações sobre o modelo em produção.
    
    Returns:
        ModelInfo: Detalhes do modelo carregado
    
    Raises:
        HTTPException: Se o modelo não estiver carregado
    """
    if not classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo não carregado. Execute o treinamento primeiro."
        )
    
    # Calcular uptime
    uptime_str = "N/A"
    if startup_time:
        uptime_delta = datetime.now() - startup_time
        uptime_str = str(uptime_delta).split('.')[0]  # Remove microssegundos
    
    return ModelInfo(
        status="online",
        categorias_suportadas=len(classifier.classes_),
        lista_categorias=list(classifier.classes_),
        versao_modelo="1.0.0",
        uptime=uptime_str
    )


@app.post("/classificar", 
          response_model=ClassificationResponse,
          tags=["Classificação"])
async def classify_news(news: NewsInput):
    """
    Classifica uma notícia individual com base no título.
    
    Args:
        news (NewsInput): Título da notícia
        
    Returns:
        ClassificationResponse: Resultado da classificação com categoria e confiança
        
    Raises:
        HTTPException: Se o modelo não estiver carregado ou erro no processamento
        
    Example:
        ```json
        {
            "titulo": "Mercado financeiro reage positivamente a novas medidas"
        }

"""
if not classifier:
raise HTTPException(
status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
detail="Serviço de classificação indisponível. Modelo não carregado."
)

try:
logger.info(f"📝 Classificando: '{news.titulo}'")

Processar texto
processed_text = text_processor.process(news.titulo)

if not processed_text:
raise HTTPException(
status_code=status.HTTP_400_BAD_REQUEST,
detail="Não foi possível processar o texto. Verifique se o título é válido."
)

Classificar
result = classifier.predict_with_confidence(processed_text)

Criar resposta formatada
response = ClassificationResponse(
categoria_principal=result["categoria_principal"],
confianca=result["confianca"],
alternativas=result["alternativas"],
texto_analisado=news.titulo,
timestamp=datetime.now().isoformat()
)

logger.info(f"✅ Resultado: {response.categoria_principal} ({response.confianca:.2%})")

return response

except HTTPException:
raise
except Exception as e:
logger.error(f"❌ Erro na classificação: {str(e)}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail=f"Erro interno ao processar classificação: {str(e)}"
)

@app.post("/classificar/lote",
response_model=BatchClassificationResponse,
tags=["Classificação"])
async def classify_batch(batch: BatchNewsInput):
"""
Classifica múltiplas notícias em lote.

Args:
batch (BatchNewsInput): Lista de notícias para classificar

Returns:
BatchClassificationResponse: Resultados da classificação em lote

Raises:
HTTPException: Se o modelo não estiver carregado ou erro no processamento
"""
if not classifier:
raise HTTPException(
status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
detail="Serviço de classificação indisponível"
)

start_time = datetime.now()
resultados = []

try:
logger.info(f"📦 Processando lote de {len(batch.noticias)} notícias")

for i, news in enumerate(batch.noticias):
try:

Processar e classificar cada notícia
processed_text = text_processor.process(news.titulo)

if processed_text:
result = classifier.predict_with_confidence(processed_text)

resultados.append(ClassificationResponse(
categoria_principal=result["categoria_principal"],
confianca=result["confianca"],
alternativas=result["alternativas"],
texto_analisado=news.titulo,
timestamp=datetime.now().isoformat()
))
else:

Adicionar erro para textos inválidos
resultados.append(ClassificationResponse(
categoria_principal="erro_processamento",
confianca=0.0,
alternativas=[],
texto_analisado=news.titulo,
timestamp=datetime.now().isoformat()
))

except Exception as e:
logger.error(f"❌ Erro ao processar notícia {i}: {str(e)}")
resultados.append(ClassificationResponse(
categoria_principal="erro_processamento",
confianca=0.0,
alternativas=[],
texto_analisado=news.titulo,
timestamp=datetime.now().isoformat()
))

tempo_processamento = (datetime.now() - start_time).total_seconds()

logger.info(f"✅ Lote processado em {tempo_processamento:.2f}s")

return BatchClassificationResponse(
resultados=resultados,
total_processado=len(resultados),
tempo_processamento=round(tempo_processamento, 2)
)

except Exception as e:
logger.error(f"❌ Erro no processamento em lote: {str(e)}")
raise HTTPException(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
detail=f"Erro ao processar lote: {str(e)}"
)

if name == "main":
import uvicorn

Iniciar servidor
uvicorn.run(
"main:app",
host="0.0.0.0",
port=8000,
reload=True,
log_level="info"
)

"""
Testes unitários para a API de classificação de notícias.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.main import app, load_model, NewsInput, ClassificationResponse


# Configuração do cliente de teste
client = TestClient(app)


class TestAPIHealth:
    """Testes de saúde e disponibilidade da API."""
    
    def test_root_endpoint(self):
        """Testa se a rota raiz está respondendo."""
        response = client.get("/")
        assert response.status_code == 200
        assert "mensagem" in response.json()
    
    def test_health_check(self):
        """Testa o endpoint de health check."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # Pode estar sem modelo
    
    def test_documentation_available(self):
        """Testa se a documentação Swagger está disponível."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestValidation:
    """Testes de validação de entrada."""
    
    def test_valid_title(self):
        """Testa validação de título válido."""
        input_data = NewsInput(titulo="Notícia de teste válida")
        assert input_data.titulo == "Notícia de teste válida"
    
    def test_short_title(self):
        """Testa validação de título muito curto."""
        with pytest.raises(ValueError):
            NewsInput(titulo="Ab")  # Menos de 5 caracteres
    
    def test_empty_title(self):
        """Testa validação de título vazio."""
        with pytest.raises(ValueError):
            NewsInput(titulo="")
    
    def test_whitespace_title(self):
        """Testa validação de título apenas com espaços."""
        with pytest.raises(ValueError):
            NewsInput(titulo="     ")


class TestResponseFormat:
    """Testes de formato das respostas."""
    
    def test_classification_response_model(self):
        """Testa o modelo de resposta de classificação."""
        response = ClassificationResponse(
            categoria_principal="politica",
            confianca=0.95,
            alternativas=[
                {"categoria": "economia", "probabilidade": 0.03},
                {"categoria": "geral", "probabilidade": 0.02}
            ],
            texto_analisado="Teste",
            timestamp="2024-01-01T00:00:00"
        )
        
        assert response.categoria_principal == "politica"
        assert 0 <= response.confianca <= 1
        assert len(response.alternativas) == 2


class TestIntegration:
    """Testes de integração (requerem modelo carregado)."""
    
    @pytest.mark.skipif(not load_model(), reason="Modelo não encontrado")
    def test_classify_endpoint(self):
        """Testa o endpoint de classificação com modelo real."""
        input_data = {
            "titulo": "Governo anuncia novo pacote de medidas econômicas"
        }
        response = client.post("/classificar", json=input_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verificar estrutura da resposta
        assert "categoria_principal" in result
        assert "confianca" in result
        assert "alternativas" in result
        assert len(result["alternativas"]) == 3
        
        # Verificar valores
        assert isinstance(result["categoria_principal"], str)
        assert 0 <= result["confianca"] <= 1
        assert result["texto_analisado"] == input_data["titulo"]
    
    @pytest.mark.skipif(not load_model(), reason="Modelo não encontrado")
    def test_batch_classify(self):
        """Testa o endpoint de classificação em lote."""
        input_data = {
            "noticias": [
                {"titulo": "Seleção brasileira vence amistoso internacional"},
                {"titulo": "Bolsa de valores fecha em alta pelo terceiro dia"},
                {"titulo": "Nova tecnologia revoluciona mercado de smartphones"}
            ]
        }
        response = client.post("/classificar/lote", json=input_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert "resultados" in result
        assert len(result["resultados"]) == 3
        assert "total_processado" in result
        assert result["total_processado"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    
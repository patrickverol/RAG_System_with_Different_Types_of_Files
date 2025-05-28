# Projeto 10 - IA Generativa e RAG Para App de Sistema Inteligente de Busca em Documentos - Frontend
# Módulo de Inicialização da API

# Import
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializa a API
if __name__=="__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run(
        "api:app",
        host='0.0.0.0',
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )
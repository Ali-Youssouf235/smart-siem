from elasticsearch import Elasticsearch
import os

# Retour au HTTP classique sur le port 9200
ELASTICSEARCH_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
ELASTIC_USER = "elastic"
ELASTIC_PASSWORD = "siem2026"

try:
    es_client = Elasticsearch(
        ELASTICSEARCH_URL,
        basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
        request_timeout=5
    )
    print("⏳ Client Elasticsearch initialisé. Prêt pour les tests d'insertion.")
except Exception as e:
    print(f"⚠️ Erreur d'initialisation d'Elasticsearch : {e}")
    es_client = None

    
def save_log_to_elasticsearch(log_data: dict, index_name: str = "smart-siem-logs"):
    """
    Sauvegarde de manière définitive un log normalisé dans l'index Elasticsearch.
    """
    if es_client is None:
        print("⚠️ Impossible de sauvegarder le log : client Elasticsearch non connecté.")
        return False
    try:
        log_id = log_data.get("id")
        response = es_client.index(index=index_name, id=log_id, document=log_data)
        return response.get("result") in ["created", "updated"]
    except Exception as e:
        print(f"❌ Erreur lors de l'indexation du log dans Elasticsearch : {e}")
        return False
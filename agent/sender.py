import requests
import time
from typing import Dict, List
from .config_loader import ConfigLoader
from .logger import AgentLogger

class LogSender:
    """Envoie les logs vers le backend API avec gestion des retries et mémoire tampon"""
    
    def __init__(self, config: ConfigLoader, logger: AgentLogger):
        self.config = config
        self.logger = logger.get_logger()
        self.backend_url = config.get("backend", "url")
        self.timeout = config.get("backend", "timeout", default=10)
        self.retry_interval = config.get("backend", "retry_interval", default=5)
        self.max_retries = 3
        
        # Le retry_manager sera injecté après l'initialisation dans main.py
        self.retry_manager = None

    def send_instantly(self, log: Dict) -> bool:
        """
        Tente un envoi immédiat et unique d'un seul log (ou lot).
        Retourne True si l'API répond avec succès, False sinon.
        Utile pour le RetryManager pour tester la ligne réseau.
        """
        try:
            response = requests.post(
                self.backend_url,
                json=log, # Envoi direct du contrat requis par l'API de Rohan
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code in (200, 201)
        except requests.exceptions.RequestException:
            return False
    
    def send_logs(self, logs: List[Dict]) -> bool:
        """Envoie un batch de logs vers l'API. Bascule sur le cache si l'API est en panne."""
        if not logs:
            return True
        
        self.logger.info(f"Tentative d'envoi de {len(logs)} logs vers le backend...")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.backend_url,
                    json=logs,  # Note : Rohan attend un tableau de logs direct [{}, {}] ou un objet selon son API
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in (200, 201):
                    self.logger.info(f"✨ {len(logs)} logs envoyés avec succès")
                    return True
                else:
                    self.logger.warning(
                        f"Échec (status {response.status_code}), tentative {attempt+1}/{self.max_retries}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erreur de connexion (tentative {attempt+1}): {e}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_interval)
        
        # --- BASCULEMENT SUR LA RÉSILIENCE (RETRY QUEUE) ---
        self.logger.error(f" Échec définitif après {self.max_retries} tentatives. Transfert au tampon de résilience...")
        if self.retry_manager:
            for log in logs:
                self.retry_manager.add_to_buffer(log)
        else:
            self.logger.critical("Le gestionnaire de résilience (RetryManager) n'est pas configuré sur le Sender !")
            
        return False
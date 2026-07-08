import sys
import os
from agent.config_loader import ConfigLoader
from agent.logger import AgentLogger
from agent.sender import LogSender
from agent.retry import RetryManager
from agent.collector import CentralCollector

def main():
    print("==================================================")
    print("          DÉMARRAGE DE L'AGENT SMART-SIEM         ")
    print("==================================================")

    config_path = os.path.join("config", "config.yaml")
    if not os.path.exists(config_path):
        print(f"[❌ ERROR] Fichier de configuration introuvable : {config_path}")
        sys.exit(1)
        
    config = ConfigLoader(config_path)

    # Initialisation propre du Logger
    logger_instance = AgentLogger(config)
    logger = logger_instance.get_logger()
    logger.info("Configuration et système de journalisation initialisés.")

    # Configuration du Sender
    sender = LogSender(config, logger_instance)

    # Configuration de la résilience
    retry_max_size = config.get("agent", "buffer_max_size", default=5000)
    retry_manager = RetryManager(sender, logger_instance, max_buffer_size=retry_max_size)
    
    # Liaison bidirectionnelle
    sender.retry_manager = retry_manager
    logger.info("Gestionnaire de résilience (Retry Cache) actif.")

    # Lancement du moteur central
    try:
        collector = CentralCollector(config, logger_instance, sender)
        collector.run()
    except Exception as e:
        logger.critical(f"Erreur fatale lors de l'exécution de l'agent : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
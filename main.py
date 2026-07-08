import sys
import os
from agent.config_loader import ConfigLoader
from agent.logger import AgentLogger
from agent.sender import LogSender
from agent.retry import RetryManager
from agent.collector import CentralCollector

def launch_agent():
    """Lance l'agent principal de collecte"""
    print("\n" + "="*60)
    print("     DÉMARRAGE DE L'AGENT SMART-SIEM")
    print("="*60)
    
    config_path = os.path.join("config", "config.yaml")
    
    # Vérification de sécurité si le fichier n'existe pas
    if not os.path.exists(config_path):
        print(f"[ERREUR] Fichier de configuration introuvable : {config_path}")
        print("Veuillez d'abord exécuter installer.py")
        sys.exit(1)
    
    try:
        config = ConfigLoader(config_path)
        logger_instance = AgentLogger(config)
        logger = logger_instance.get_logger()
        
        logger.info("Agent démarré avec succès.")
        
        sender = LogSender(config, logger_instance)
        retry_manager = RetryManager(sender, logger_instance, 
                                    max_buffer_size=config.get("agent", "buffer_max_size", 5000))
        sender.retry_manager = retry_manager
        
        collector = CentralCollector(config, logger_instance, sender)
        collector.run()
        
    except Exception as e:
        print(f"[ERREUR FATALE] {e}")
        sys.exit(1)

if __name__ == "__main__":
    launch_agent()
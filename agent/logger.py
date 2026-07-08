import logging
import os
from .config_loader import ConfigLoader

class AgentLogger:
    """Gestionnaire de logs pour l'agent"""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger("smart_siem_agent")
        logger.setLevel(self.config.get("logging", "level", default="INFO"))
        
        if logger.handlers:
            logger.handlers.clear()
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        log_file = self.config.get("logging", "file", default="logs/agent.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_logger(self):
        return self.logger
import sys
import time
from .parser import LogParser

class CentralCollector:
    """Orchestrateur central de l'agent SIEM"""

    def __init__(self, config, logger, sender):
        self.config = config
        self.logger_instance = logger  # Wrapper complet AgentLogger
        self.logger = logger.get_logger()  # Logger natif Python
        self.sender = sender
        self.parser = LogParser(config)

        self.os_type = sys.platform
        self.sub_collector = self._init_sub_collector()

    def _init_sub_collector(self):
        """Instancie le collecteur adapté à l'OS"""
        if self.os_type.startswith("linux"):
            self.logger.info("Système Linux détecté. Chargement du LinuxLogCollector.")
            from .collectors.linux import LinuxLogCollector
            # Transmission du wrapper complet pour éviter tout conflit d'initialisation parente
            return LinuxLogCollector(self.config, self.logger_instance)
        elif self.os_type.startswith("win"):
            self.logger.info("Système Windows détecté. Chargement du WindowsLogCollector.")
            from .collectors.windows import WindowsLogCollector
            return WindowsLogCollector(self.config, self.logger_instance)
        else:
            self.logger.critical(f"Système d'exploitation non supporté : {self.os_type}")
            raise NotImplementedError("OS non supporté")

    def run(self):
        """Boucle principale d'exécution de l'agent"""
        self.logger.info("Démarrage de la boucle de collecte active...")
        interval = self.config.get("agent", "scan_interval", default=2)

        try:
            while True:
                for raw_data in self.sub_collector.collect():
                    # Ligne de Debug : Affiche immédiatement la capture brute sur l'écran
                    print(f"🔍 [COLLECTEUR DETECTÉ] -> {raw_data['raw_line'][:120]}")
                    
                    # Passage au parseur pour nettoyage / filtrage
                    formatted_log = self.parser.parse(raw_data)
                    
                    if formatted_log:
                        # Envoi sous forme de liste [dict] pour correspondre à send_logs
                        self.sender.send_logs([formatted_log])

                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Arrêt de l'agent demandé par l'utilisateur.")
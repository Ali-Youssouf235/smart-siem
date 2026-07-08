import queue
import time
import threading

class RetryManager:
    """Gère la mise en cache mémoire et les tentatives de réémission en cas de panne réseau"""

    def __init__(self, sender, logger, max_buffer_size=5000):
        self.sender = sender
        self.logger = logger.get_logger()
        self.buffer = queue.Queue(maxsize=max_buffer_size)
        self.is_running = True
        
        # Lancement d'un thread en arrière-plan dédié aux tentatives de réémission
        self.retry_thread = threading.Thread(target=self._retry_loop, daemon=True)
        self.retry_thread.start()

    def add_to_buffer(self, log_payload: dict):
        """Ajoute un log au tampon si le réseau est tombé"""
        try:
            if not self.buffer.full():
                self.buffer.put_nowait(log_payload)
                self.logger.warning(f"Log mis en mémoire tampon (Taille actuelle du cache : {self.buffer.qsize()})")
            else:
                self.logger.critical("Le tampon de mémoire de l'agent est PLEIN. Des logs vont être perdus !")
        except queue.Full:
            self.logger.critical("Le tampon de mémoire de l'agent est PLEIN. Des logs vont être perdus !")

    def _retry_loop(self):
        """Boucle d'arrière-plan qui tente de vider le cache dès que l'API de Rohan répond"""
        while self.is_running:
            if not self.buffer.empty():
                # On jette un œil au premier élément sans le retirer immédiatement
                log_payload = self.buffer.queue[0]
                
                # On tente un renvoi via le sender classique
                success = self.sender.send_instantly(log_payload)
                
                if success:
                    # Si ça marche, on le retire officiellement de la file
                    self.buffer.get()
                    self.buffer.task_done()
                    self.logger.info("Connexion rétablie : un log en cache a été transmis avec succès.")
                    time.sleep(0.1) # Pause ultra-courte pour dépiler rapidement
                else:
                    # Si l'API est toujours en panne, on attend avant de retenter pour ne pas saturer le CPU
                    self.logger.debug("Le backend est toujours injoignable, attente de 5 secondes...")
                    time.sleep(5)
            else:
                time.sleep(1) # Si la file est vide, on vérifie toutes les secondes

    def stop(self):
        self.is_running = False
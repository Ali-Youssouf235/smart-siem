from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class AlertBaseSchema(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'alerte générée.")
    timestamp: datetime = Field(..., description="Date et heure exactes de la levée de l'alerte.")
    niveau_criticite: str = Field(..., description="Niveau d'impact : 'INFO', 'WARNING', 'HIGH', 'CRITICAL'.")
    statut: str = Field(..., description="Cycle de vie : 'ouvert', 'en cours', 'résolu'.")
    regle_id: str = Field(..., description="Référence vers la règle de corrélation déclencheuse.")
    # Optionnel car au début, aucun analyste n'est encore assigné au ticket
    utilisateur_id: Optional[str] = Field(None, description="Analyste du SOC assigné au traitement.")

    # 🟢 CATÉGORISATION DE L'ALERTE
    # Avant ce correctif, une alerte ne portait que le champ technique `regle_id`
    # (ex: "MITRE-T1110-BRUTEFORCE"), illisible pour un analyste et invisible
    # dans le dashboard. Ces 4 champs rendent CLAIR ce qui a été détecté :
    # quelle catégorie d'attaque, dans quelle tactique/technique MITRE ATT&CK,
    # avec quelle description humaine, et à partir de quelles sources de logs.
    categorie: str = Field(
        default="Non catégorisé",
        description="Catégorie humaine et lisible de l'attaque détectée (ex: 'Brute Force SSH', 'Mouvement Latéral')."
    )
    tactique_mitre: Optional[str] = Field(
        default=None,
        description="Tactique MITRE ATT&CK associée (ex: 'TA0001 - Initial Access')."
    )
    technique_mitre: Optional[str] = Field(
        default=None,
        description="Technique MITRE ATT&CK associée (ex: 'T1110 - Brute Force')."
    )
    description: Optional[str] = Field(
        default=None,
        description="Explication claire et significative de l'événement détecté (hôte, IP, valeurs mesurées...)."
    )
    sources_correlees: List[str] = Field(
        default_factory=list,
        description="Types de logs combinés pour lever l'alerte (ex: ['auth', 'réseau']) — met en évidence la corrélation multi-source."
    )

    class Config:
        from_attributes = True
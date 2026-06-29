from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from app.services.report_service import generate_security_pdf
from datetime import datetime
import os

router = APIRouter(prefix="/api/v1/reports", tags=["Rapports de Sécurité"])

@router.get("/generate", response_class=FileResponse)
async def download_security_report():
    """
    Génère de manière dynamique un rapport d'activité PDF consolidé basé 
    sur les logs et alertes Elasticsearch des dernières 24 heures.
    """
    try:
        # Appel du service de génération
        pdf_path = generate_security_pdf()
        
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Le fichier PDF n'a pas pu être généré sur le serveur."
            )
            
        # On renvoie le PDF sous forme de fichier téléchargeable directement
        return FileResponse(
            path=pdf_path,
            filename=f"smart_siem_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création du rapport PDF : {str(e)}"
        )
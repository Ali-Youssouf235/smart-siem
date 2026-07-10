import { useState, useEffect } from 'react'
import { colors, severityConfig, roleConfig } from '../theme'
import { alertsApi } from '../api' // Importation de la connexion API centrale

export default function Alertes({ user }) {
  const [alertes, setAlertes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filtreStatus, setFiltreStatus] = useState('tous')
  const [filtreSeverity, setFiltreSeverity] = useState('tous')
  const [expandedId, setExpandedId] = useState(null)

  const isLecteur = user?.role === 'lecteur'

// 🔄 Chargement des alertes depuis Elasticsearch via FastAPI
  const fetchAlerts = async () => {
    setLoading(true)
    setError('')
    try {
      const params = {}
      if (filtreStatus !== 'tous') params.status = filtreStatus
      if (filtreSeverity !== 'tous') params.severity = filtreSeverity

      const data = await alertsApi.list(params)
      
      let rawAlerts = []
      // 1. Extraction sécurisée selon la structure renvoyée
      if (Array.isArray(data)) {
        rawAlerts = data
      } else if (data && data.alerts) {
        rawAlerts = data.alerts
      }

      // 2. 🟢 MAPPING : Traduction des champs Elasticsearch réels pour le rendu React
      const mappedAlerts = rawAlerts.map((item, index) => {
        // Normalisation de la sévérité (Elasticsearch renvoie souvent en MAJUSCULES : "CRITICAL")
        const rawSev = (item.niveau_criticite || item.severity || 'info').toLowerCase()
        // Ajustement pour faire correspondre "medium" avec ton filtre "warning"
        const finalSev = rawSev === 'medium' ? 'warning' : rawSev

        return {
          id: item.id || item._id || `ALERTE-${index}`,
          severity: finalSev,
          // 🟢 CORRECTIF : le backend renvoie 'description' (résumé humain généré
          // par le moteur de corrélation), pas 'message_brut' qui n'a jamais existé.
          message: item.description || item.message || "Événement de sécurité détecté",
          // Extraction propre de l'heure (HH:MM:SS) depuis le timestamp complet
          time: item.timestamp ? item.timestamp.substring(11, 19) : (item.time || 'En direct'),
          status: item.status || item.statut || 'nouveau',
          source: item.agent_id || item.source || 'Collecteur Local',
          ip: item.source_ip || item.ip || 'N/A',
          host: item.cible_host || item.host || 'N/A',
          // 🟢 CORRECTIF : 'categorie' est le champ réel posé par le moteur de
          // corrélation (app/core/categorization.py). L'ancien code retombait
          // systématiquement sur 'T1110 - Brute Force SSH' codé en dur, ce qui
          // affichait la même catégorie sur TOUTES les alertes sans exception.
          mitre: item.categorie || item.regle_id || 'Non catégorisé'
        }
      })

      setAlertes(mappedAlerts)

    } catch (err) {
      console.error("Erreur lors de la récupération des alertes:", err)
      setError("Impossible de joindre le cluster Elasticsearch ou l'API.")
    } finally {
      setLoading(false)
    }
  }

  // Se déclenche au chargement de la page ou quand un filtre change
  useEffect(() => {
    fetchAlerts()
  }, [filtreStatus, filtreSeverity])

  // 🛠️ Action de mise à jour du statut (SOAR / Traitement d'incident)
  const handleUpdateStatus = async (id, newStatus) => {
    try {
      await alertsApi.updateStatus(id, newStatus)
      // Rafraîchir instantanément la liste
      fetchAlerts()
    } catch (err) {
      console.error("Erreur lors du changement de statut:", err)
      alert("Erreur lors du traitement de la demande.")
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Flux des Alertes SOC</h1>
          <p style={styles.subtitle}>Gestion, corrélation et réponse aux incidents en temps réel</p>
        </div>
        <button style={styles.refreshBtn} onClick={fetchAlerts}>
          <i className="ti ti-refresh" /> Actualiser
        </button>
      </div>

      {/* Barre des Filtres */}
      <div style={styles.filtersBar}>
        <div style={styles.filterGroup}>
          <label style={styles.filterLabel}>Sévérité</label>
          <select 
            style={styles.select} 
            value={filtreSeverity} 
            onChange={(e) => setFiltreSeverity(e.target.value)}
          >
            <option value="tous">Toutes les sévérités</option>
            <option value="critical">Critique</option>
            <option value="high">Haute</option>
            <option value="warning">Moyenne</option>
            <option value="info">Basse / Info</option>
          </select>
        </div>

        <div style={styles.filterGroup}>
          <label style={styles.filterLabel}>Statut</label>
          <select 
            style={styles.select} 
            value={filtreStatus} 
            onChange={(e) => setFiltreStatus(e.target.value)}
          >
            <option value="tous">Tous les statuts</option>
            <option value="nouveau">Nouveau</option>
            <option value="en_cours">En cours</option>
            <option value="resolu">Résolu</option>
          </select>
        </div>
      </div>

      {/* Zone principale : Affichage des données ou États d'erreur/chargement */}
      {loading ? (
        <div style={styles.stateContainer}>
          <i className="ti ti-loader animate-spin" style={{ fontSize: 28, color: colors.primary }} />
          <p style={{ marginTop: 10, color: colors.textMuted }}>Interrogation de la base Elasticsearch...</p>
        </div>
      ) : error ? (
        <div style={styles.stateContainer}>
          <i className="ti ti-alert-triangle" style={{ fontSize: 32, color: colors.critical }} />
          <p style={{ marginTop: 10, color: colors.critical, fontWeight: 600 }}>{error}</p>
        </div>
      ) : alertes.length === 0 ? (
        <div style={styles.stateContainer}>
          <p style={{ color: colors.textFaint }}>Aucun incident de sécurité ne correspond à ces critères.</p>
        </div>
      ) : (
        <div style={styles.list}>
          {alertes.map((alerte) => {
            const sev = severityConfig[alerte.severity] || severityConfig.info
            const isExpanded = expandedId === alerte.id

            return (
              <div 
                key={alerte.id} 
                className="alert-item" 
                style={{ ...styles.item, borderLeft: `4px solid ${sev.color}` }}
              >
                <div style={styles.itemHeader} onClick={() => setExpandedId(isExpanded ? null : alerte.id)}>
                  <div style={styles.itemMainInfo}>
                    <span style={{ ...styles.badge, background: sev.bg, color: sev.color }}>
                      {sev.label}
                    </span>
                    <div style={styles.msgContainer}>
                      <span style={styles.message}>{alerte.message}</span>
                      <span style={styles.metaRow}>
                        <span><i className="ti ti-clock" /> {alerte.time}</span>
                        <span>•</span>
                        <span>ID: <strong>{alerte.id}</strong></span>
                        <span>•</span>
                        <span>Source: <strong>{alerte.source}</strong></span>
                      </span>
                    </div>
                  </div>

                  <div style={styles.itemActionsRight}>
                    <span style={{
                      ...styles.statusTag,
                      background: alerte.status === 'resolu' ? colors.successBg : alerte.status === 'en_cours' ? colors.warningBg : colors.neutralBg,
                      color: alerte.status === 'resolu' ? colors.success : alerte.status === 'en_cours' ? colors.warning : colors.textMuted
                    }}>
                      {alerte.status === 'resolu' ? 'Résolu' : alerte.status === 'en_cours' ? 'En cours' : 'Nouveau'}
                    </span>
                    <i className={`ti ti-chevron-${isExpanded ? 'up' : 'down'}`} style={{ color: colors.textFaint }} />
                  </div>
                </div>

                {isExpanded && (
                  <div style={styles.expanded}>
                    <div style={styles.detailsGrid}>
                      <div style={styles.expandedItem}>
                        <span style={styles.expandedLabel}>IP Source / Indicateur</span>
                        <span style={styles.expandedValue}>{alerte.ip || 'N/A'}</span>
                      </div>
                      <div style={styles.expandedItem}>
                        <span style={styles.expandedLabel}>Machine cible</span>
                        <span style={styles.expandedValue}>{alerte.host || 'N/A'}</span>
                      </div>
                      <div style={styles.expandedItem}>
                        <span style={styles.expandedLabel}>Classification MITRE ATT&CK</span>
                        <span style={{ ...styles.expandedValue, color: colors.primary, fontWeight: 600 }}>{alerte.mitre || 'Non classifié'}</span>
                      </div>
                    </div>

                    <div style={styles.actionsBlock}>
                      {isLecteur ? (
                        <div style={styles.readOnlyNotice}>
                          <i className="ti ti-shield-check" /> Profil Lecteur : Actions de remédiation indisponibles.
                        </div>
                      ) : (
                        <div style={styles.actionButtons}>
                          {alerte.status !== 'en_cours' && alerte.status !== 'resolu' && (
                            <button 
                              style={styles.actionBtnInvestigate} 
                              onClick={() => handleUpdateStatus(alerte.id, 'en_cours')}
                            >
                              <i className="ti ti-shield" /> Prendre en charge (Investiguer)
                            </button>
                          )}
                          {alerte.status !== 'resolu' && (
                            <button 
                              style={styles.actionBtnPrimary} 
                              onClick={() => handleUpdateStatus(alerte.id, 'resolu')}
                            >
                              <i className="ti ti-check" /> Marquer comme résolu (Fermer)
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// Styles inchangés de ton maquettage d'origine pour conserver le design exact
const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  header: { display: 'flex', justifyContent: 'spaceBetween', alignItems: 'center' },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  refreshBtn: { display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', background: '#fff', border: `1px solid ${colors.border}`, borderRadius: 8, fontSize: 13, fontWeight: 600, color: colors.text, cursor: 'pointer' },
  filtersBar: { display: 'flex', gap: 16, background: '#fff', padding: 16, borderRadius: 12, border: `1px solid ${colors.border}` },
  filterGroup: { display: 'flex', flexDirection: 'column', gap: 6 },
  filterLabel: { fontSize: 11, fontWeight: 700, color: colors.textFaint, textTransform: 'uppercase', letterSpacing: '0.03em' },
  select: { padding: '8px 12px', borderRadius: 8, border: `1px solid ${colors.border}`, fontSize: 13, minWidth: 160, background: '#fff', color: colors.text },
  stateContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}` },
  list: { display: 'flex', flexDirection: 'column', gap: 10 },
  item: { background: '#fff', borderRadius: 10, border: `1px solid ${colors.border}`, overflow: 'hidden', transition: 'all 0.15s' },
  itemHeader: { padding: '14px 18px', display: 'flex', justifyContent: 'spaceBetween', alignItems: 'center', cursor: 'pointer' },
  itemMainInfo: { display: 'flex', alignItems: 'flex-start', gap: 14, flex: 1 },
  badge: { padding: '4px 8px', borderRadius: 6, fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.03em', minWidth: 70, textAlign: 'center' },
  msgContainer: { display: 'flex', flexDirection: 'column', gap: 4 },
  message: { fontSize: 14, fontWeight: 600, color: colors.text },
  metaRow: { display: 'flex', gap: 12, fontSize: 11, color: colors.textFaint },
  itemActionsRight: { display: 'flex', alignItems: 'center', gap: 14 },
  statusTag: { padding: '4px 9px', borderRadius: 6, fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.02em' },
  expanded: { padding: '16px 18px', background: colors.neutralBg, borderTop: `1px solid ${colors.borderLight}` },
  detailsGrid: { display: 'flex', gap: 32, flexWrap: 'wrap', marginBottom: 16 },
  expandedItem: { display: 'flex', flexDirection: 'column', gap: 3 },
  expandedLabel: { fontSize: 10, color: colors.textFaint, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 },
  expandedValue: { fontSize: 13, color: colors.text, fontWeight: 500 },
  actionsBlock: { borderTop: `1px solid ${colors.borderLight}`, paddingTop: 14 },
  actionButtons: { display: 'flex', gap: 10, flexWrap: 'wrap' },
  actionBtnPrimary: { display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', background: colors.success, border: 'none', borderRadius: 7, fontSize: 12, fontWeight: 600, color: '#fff', cursor: 'pointer' },
  actionBtnInvestigate: { display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', background: colors.primaryBg, border: `1px solid ${colors.primaryBorder}`, borderRadius: 7, fontSize: 12, fontWeight: 600, color: colors.primary, cursor: 'pointer' },
  readOnlyNotice: { display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', background: colors.primaryBg, borderRadius: 8, color: colors.primary, fontSize: 12, fontWeight: 500 }
}
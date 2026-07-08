import { useState, useEffect } from 'react'
import { colors, severityConfig } from '../theme'
import { agentApi } from '../api' // Raccordement avec le service d'agents comportementaux
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts'

export default function UEBA({ user }) {
  const [analysedUsers, setAnalysedUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Données de structure par défaut pour les graphiques de l'utilisateur sélectionné
  const behaviorScores = [
    { subject: 'Connexions', A: selectedUser?.metrics?.connections ?? 85, fullMark: 100 },
    { subject: 'Accès fichiers', A: selectedUser?.metrics?.files ?? 72, fullMark: 100 },
    { subject: 'Heures actives', A: selectedUser?.metrics?.hours ?? 90, fullMark: 100 },
    { subject: 'Localisation', A: selectedUser?.metrics?.geo ?? 95, fullMark: 100 },
    { subject: 'Appareils', A: selectedUser?.metrics?.devices ?? 88, fullMark: 100 },
    { subject: 'Volume données', A: selectedUser?.metrics?.volume ?? 78, fullMark: 100 },
  ]

  const hourlyActivity = selectedUser?.hourlyActivity ?? [
    { hour: '00', activity: 5 },
    { hour: '04', activity: 2 },
    { hour: '08', activity: 35 },
    { hour: '12', activity: 60 },
    { hour: '16', activity: 45 },
    { hour: '20', activity: 15 },
  ]

  // 🔄 Chargement des profils d'agents et utilisateurs suivis par l'UEBA
  const fetchUebaData = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await agentApi.list()
      
      // Sécurité sur la structure de tableau attendue
      const list = Array.isArray(data) ? data : data?.agents || []
      setAnalysedUsers(list)

      // Sélectionner automatiquement le premier utilisateur de la liste s'il y en a un
      if (list.length > 0) {
        setSelectedUser(list[0])
      }
    } catch (err) {
      console.error("Erreur de récupération UEBA:", err)
      setError("Impossible de récupérer les profils de risques utilisateurs.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUebaData()
  }, [])

  return (
    <div style={styles.container}>
      <div>
        <h1 style={styles.title}>Analyse Comportementale (UEBA)</h1>
        <p style={styles.subtitle}>Détection des déviations de profils et calcul du score de risque utilisateur</p>
      </div>

      {loading ? (
        <div style={styles.stateContainer}>
          <i className="ti ti-loader animate-spin" style={{ fontSize: 28, color: colors.primary }} />
          <p style={{ marginTop: 10, color: colors.textMuted }}>Modélisation des profils comportementaux...</p>
        </div>
      ) : error ? (
        <div style={styles.stateContainer}>
          <i className="ti ti-alert-triangle" style={{ fontSize: 32, color: colors.critical }} />
          <p style={{ marginTop: 10, color: colors.critical, fontWeight: 600 }}>{error}</p>
        </div>
      ) : (
        <div style={styles.layoutGrid}>
          {/* Colonne de Gauche : Liste des identités surveillées */}
          <div style={styles.sidebarCard}>
            <h3 style={styles.sectionTitle}>Identités à Risque</h3>
            <div style={styles.userList}>
              {analysedUsers.map((u) => {
                const isSelected = selectedUser?.id === u.id
                let statusColor = colors.success
                if (u.riskScore > 80) statusColor = colors.critical
                else if (u.riskScore > 50) statusColor = colors.high

                return (
                  <div
                    key={u.id}
                    onClick={() => setSelectedUser(u)}
                    style={{
                      ...styles.userItem,
                      background: isSelected ? colors.primaryBg : '#fff',
                      borderColor: isSelected ? colors.primaryBorder : colors.border,
                    }}
                  >
                    <div style={styles.userInfoBlock}>
                      <span style={styles.userName}>{u.name}</span>
                      <span style={styles.userDept}>{u.department} · {u.email}</span>
                    </div>
                    <span style={{ ...styles.scoreBadge, color: statusColor, background: `${statusColor}15` }}>
                      {u.riskScore}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Colonne de Droite : Tableau de bord de l'utilisateur sélectionné */}
          {selectedUser && (
            <div style={styles.mainAnalysisArea}>
              {/* Carte d'en-tête de l'identité */}
              <div style={styles.profileHeaderCard}>
                <div style={styles.profileMain}>
                  <div style={styles.avatar}>
  {selectedUser?.name ? selectedUser.name.charAt(0) : '?'}
</div>
                  <div>
                    <h2 style={styles.profileTitle}>{selectedUser?.name || "Utilisateur Anonyme"}</h2>
<p style={styles.profileSub}>{selectedUser?.email || ""} · Département {selectedUser?.department || ""}</p>
                  </div>
                </div>
                <div style={styles.riskScoreBigBlock}>
                  <span style={styles.riskLabel}>Score de Risque</span>
                  <span style={{ 
                    ...styles.riskVal, 
                    color: selectedUser.riskScore > 80 ? colors.critical : selectedUser.riskScore > 50 ? colors.high : colors.success 
                  }}>
                    {selectedUser.riskScore}/100
                  </span>
                </div>
              </div>

              {/* Graphiques Recharts */}
              <div style={styles.chartsGrid}>
                {/* Radar comportemental */}
                <div style={styles.chartCard}>
                  <h4 style={styles.chartTitle}>Empreinte Comportementale Globale</h4>
                  <div style={{ height: 220 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="75%" data={behaviorScores}>
                        <PolarGrid stroke={colors.borderLight} />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: colors.textMuted, fontSize: 11 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 9 }} />
                        <Radar name={selectedUser.name} dataKey="A" stroke={colors.primary} fill={colors.primary} fillOpacity={0.2} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Activité horaire suspecte */}
                <div style={styles.chartCard}>
                  <h4 style={styles.chartTitle}>Activité sur les dernières 24 heures</h4>
                  <div style={{ height: 220 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={hourlyActivity} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={colors.borderLight} />
                        <XAxis dataKey="hour" stroke={colors.textFaint} style={{ fontSize: 11 }} />
                        <YAxis stroke={colors.textFaint} style={{ fontSize: 11 }} />
                        <Tooltip />
                        <Line type="monotone" dataKey="activity" stroke={colors.high} strokeWidth={2.5} dot={{ r: 4 }} name="Volume d'actions" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Journal des anomalies de l'utilisateur */}
              <div style={styles.anomaliesCard}>
                <h4 style={styles.chartTitle}>Dernières Anomalies Détectées (Machine Learning Engine)</h4>
                <div style={styles.anomaliesList}>
                  {selectedUser.anomalies && selectedUser.anomalies.length > 0 ? (
                    selectedUser.anomalies.map((anom, i) => (
                      <div key={i} style={styles.anomalyItem}>
                        <i className="ti ti-alert-circle" style={{ color: colors.high, fontSize: 16 }} />
                        <span>{anom}</span>
                      </div>
                    ))
                  ) : (
                    <div style={styles.noAnomaly}>
                      <i className="ti ti-circle-check" style={{ color: colors.success, fontSize: 18 }} />
                      <span>Aucun écart comportemental critique détecté sur la période.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  stateContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}` },
  layoutGrid: { display: 'grid', gridTemplateColumns: '300px 1fr', gap: 20 },
  sidebarCard: { background: '#fff', borderRadius: 12, padding: 16, border: `1px solid ${colors.border}`, display: 'flex', flexDirection: 'column', gap: 14 },
  sectionTitle: { fontSize: 14, fontWeight: 700, color: colors.text },
  userList: { display: 'flex', flexDirection: 'column', gap: 8 },
  userItem: { padding: '12px 14px', borderRadius: 10, border: '1px solid', display: 'flex', justifyContent: 'spaceBetween', alignItems: 'center', cursor: 'pointer', transition: 'all 0.15s' },
  userInfoBlock: { display: 'flex', flexDirection: 'column', gap: 3, overflow: 'hidden' },
  userName: { fontSize: 13, fontWeight: 600, color: colors.text },
  userDept: { fontSize: 11, color: colors.textFaint, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  scoreBadge: { padding: '4px 8px', borderRadius: 6, fontSize: 12, fontWeight: 700, minWidth: 28, textAlign: 'center' },
  mainAnalysisArea: { display: 'flex', flexDirection: 'column', gap: 16 },
  profileHeaderCard: { background: '#fff', borderRadius: 12, padding: 20, border: `1px solid ${colors.border}`, display: 'flex', justifyContent: 'spaceBetween', alignItems: 'center' },
  profileMain: { display: 'flex', alignItems: 'center', gap: 16 },
  avatar: { width: 44, height: 44, borderRadius: '50%', background: colors.primaryBg, color: colors.primary, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, fontWeight: 700 },
  profileTitle: { fontSize: 16, fontWeight: 800, color: colors.text },
  profileSub: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  riskScoreBigBlock: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 2 },
  riskLabel: { fontSize: 11, fontWeight: 600, color: colors.textFaint, textTransform: 'uppercase' },
  riskVal: { fontSize: 22, fontWeight: 800 },
  chartsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 },
  chartCard: { background: '#fff', borderRadius: 12, padding: 18, border: `1px solid ${colors.border}` },
  chartTitle: { fontSize: 13, fontWeight: 700, color: colors.text, marginBottom: 14 },
  anomaliesCard: { background: '#fff', borderRadius: 12, padding: 18, border: `1px solid ${colors.border}` },
  anomaliesList: { display: 'flex', flexDirection: 'column', gap: 10 },
  anomalyItem: { display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: colors.text, padding: '10px 12px', background: colors.neutralBg, borderRadius: 8 },
  noAnomaly: { display: 'flex', alignItems: 'center', gap: 10, color: colors.success, fontSize: 13, fontWeight: 500, padding: '6px 0' }
}
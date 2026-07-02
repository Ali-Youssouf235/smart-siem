import { useState, useEffect } from 'react'
import { colors, severityConfig } from '../theme'
import { alertsApi, logsApi } from '../api' // Connexion aux endpoints d'alertes et de logs
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'

export default function Dashboard({ user, onNavigate }) {
  const [stats, setStats] = useState({
    totalAlerts: 0,
    criticalCount: 0,
    highCount: 0,
    activeAgents: 0,
    graphTimeline: [],
    severityData: [],
    sourceData: []
  })
  const [recentLogs, setRecentLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // 🔄 Chargement des statistiques et des logs en direct depuis le Backend (Elasticsearch)
const loadDashboardData = async () => {
    setLoading(true)
    setError('')
    try {
      // 1. Récupération des stats globales du moteur d'alertes
      const statsRes = await alertsApi.getStats()
      
      // 2. Récupération des derniers logs (flux terminal en direct)
      const logsRes = await logsApi.search('')
      
      const realTotal = statsRes?.total_alerts ?? 0
      const realCritical = statsRes?.by_severity?.CRITICAL ?? 0
      const realHigh = statsRes?.by_severity?.HIGH ?? 0
      const realMedium = statsRes?.by_severity?.MEDIUM ?? 0
      const realLow = statsRes?.by_severity?.LOW ?? 0
      const liveAgents = statsRes?.active_agents ?? 0

      setStats({
        totalAlerts: realTotal,
        criticalCount: realCritical,
        highCount: realHigh,
        activeAgents: liveAgents,
        totalAgents: statsRes?.total_agents ?? (liveAgents > 0 ? 1 : 0),
        
        // 🟢 On récupère le vrai historique temporel calculé par Elasticsearch !
        graphTimeline: statsRes?.graph_timeline ?? [{"time": "Aucun log", "alerts": 0, "resolved": 0}],
        
        severityData: [
          { name: 'Critique', value: realCritical, color: colors.critical },
          { name: 'Haute', value: realHigh, color: colors.high },
          { name: 'Moyenne', value: realMedium, color: colors.warning },
          { name: 'Basse', value: realLow, color: colors.success },
        ].filter(item => item.value > 0),
        sourceData: []
      })

      if (Array.isArray(logsRes)) {
        setRecentLogs(logsRes.slice(0, 8))
      } else if (logsRes?.logs) {
        setRecentLogs(logsRes.logs.slice(0, 8))
      }
    } catch (err) {
      console.error("Erreur lors de la synchronisation du Dashboard:", err)
      setError("Erreur de liaison avec FastAPI.")
    } finally {
      setLoading(false)
    }
  }

  // Polling automatique : rafraîchit le dashboard toutes les 5 secondes pour la démo !
  useEffect(() => {
    loadDashboardData()
    const interval = setInterval(loadDashboardData, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={styles.container}>
      {error && (
        <div style={styles.errorBanner}>
          <i className="ti ti-activity animate-pulse" style={{ fontSize: 18 }} />
          <span>{error}</span>
        </div>
      )}

      {/* En-tête de bienvenue */}
      <div style={styles.welcomeRow}>
        <div>
          <h1 style={styles.title}>Supervision Globale du SOC</h1>
          <p style={styles.subtitle}>Bonjour, <strong>{user?.name || 'Analyste'}</strong> · Rôle : <span style={{ color: colors.primary, fontWeight: 600 }}>{user?.role?.toUpperCase()}</span></p>
        </div>
        <div style={styles.pulseContainer}>
          <div style={styles.pulseDot}></div>
          <span style={styles.pulseText}>Moteur de corrélation actif</span>
        </div>
      </div>

      {/* 4 Cartes de KPIS Métriques de l'infrastructure */}
      <div style={styles.kpiGrid}>
        <div style={styles.kpiCard} onClick={() => onNavigate('recherche')}>
          <div style={styles.kpiLeft}>
            <span style={styles.kpiLabel}>Volume total de Télémétrie</span>
            <span style={styles.kpiValue}>{stats.totalAlerts.toLocaleString()} logs</span>
          </div>
          <div style={{ ...styles.kpiIcon, background: colors.primaryBg, color: colors.primary }}>
            <i className="ti ti-database" style={{ fontSize: 22 }} />
          </div>
        </div>

        <div style={styles.kpiCard} onClick={() => onNavigate('recherche')}>
          <div style={styles.kpiLeft}>
            <span style={styles.kpiLabel}>Incidents Critiques</span>
            <span style={{ ...styles.kpiValue, color: colors.critical }}>{stats.criticalCount}</span>
          </div>
          <div style={{ ...styles.kpiIcon, background: colors.criticalBg, color: colors.critical }}>
            <i className="ti ti-shield-alert" style={{ fontSize: 22 }} />
          </div>
        </div>

        <div style={styles.kpiCard} onClick={() => onNavigate('recherche')}>
          <div style={styles.kpiLeft}>
            <span style={styles.kpiLabel}>Priorités Hautes / Moyennes</span>
            <span style={{ ...styles.kpiValue, color: colors.high }}>{stats.highCount}</span>
          </div>
          <div style={{ ...styles.kpiIcon, background: colors.warningBg, color: colors.high }}>
            <i className="ti ti-alert-octagon" style={{ fontSize: 22 }} />
          </div>
        </div>

        <div style={styles.kpiCard} onClick={() => onNavigate('ueba')}>
          <div style={styles.kpiLeft}>
            <span style={styles.kpiLabel}>Collecteurs Actifs (Agents)</span>
            <span style={{ ...styles.kpiValue, color: stats.activeAgents === stats.totalAgents ? colors.success : colors.high }}>
              {stats.activeAgents} / {stats.totalAgents} Online
            </span>
          </div>
          <div style={{ ...styles.kpiIcon, background: colors.successBg, color: colors.success }}>
            <i className="ti ti-cpu" style={{ fontSize: 22 }} />
          </div>
        </div>
      </div>

      {/* Graphique principal d'Évolution temporelle */}
      <div style={styles.chartRowFull}>
        <div style={styles.cardHeader}>
          <h3 style={styles.cardTitle}>Analyse du trafic et détection des anomalies</h3>
          <span style={styles.cardSub}>Flux d'événements par seconde calculé en direct</span>
        </div>
        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats.graphTimeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colAlerts" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.primary} stopOpacity={0.2}/>
                  <stop offset="95%" stopColor={colors.primary} stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="colResolved" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.success} stopOpacity={0.2}/>
                  <stop offset="95%" stopColor={colors.success} stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={colors.borderLight} />
              <XAxis dataKey="time" stroke={colors.textFaint} style={{ fontSize: 11 }} />
              <YAxis stroke={colors.textFaint} style={{ fontSize: 11 }} />
              <Tooltip />
              <Area type="monotone" dataKey="alerts" stroke={colors.primary} strokeWidth={2} fillOpacity={1} fill="url(#colAlerts)" name="Événements ingérés" />
              <Area type="monotone" dataKey="resolved" stroke={colors.success} strokeWidth={2} fillOpacity={1} fill="url(#colResolved)" name="Événements analysés" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ligne du bas : Répartition Sévérité + Flux Terminal de Logs */}
      <div style={styles.bottomRowGrid}>
        <div style={styles.gridCard}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>Distribution par Sévérité</h3>
            <span style={styles.cardSub}>Proportions calculées de l'index analytique</span>
          </div>
          <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats.severityData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={4} dataKey="value">
                  {stats.severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div style={styles.pieLegend}>
              {stats.severityData.map((item, i) => (
                <div key={i} style={styles.legendItem}>
                  <div style={{ ...styles.legendDot, background: item.color }} />
                  <span style={styles.legendName}>{item.name}</span>
                  <span style={styles.legendVal}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Console connectée à Elasticsearch pour prouver le lien réel */}
        <div style={styles.gridCard}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>Console Ingestion d'Événements (Elasticsearch Live Feed)</h3>
            <span style={styles.cardSub}>Derniers événements bruts indexés dans smart-siem-logs</span>
          </div>
          <div style={styles.terminal}>
            {recentLogs.length === 0 ? (
              <span style={{ color: '#5fffbd', opacity: 0.6 }}>[✓] Connexion au cluster établie. En attente de télémétrie locale...</span>
            ) : (
              recentLogs.map((log, index) => {
                const messageAFFICHE = log.raw_message && log.raw_message.trim() !== "\u0000" 
                  ? log.raw_message 
                  : `Événement sur l'hôte [${log.host || 'unknown-device'}] (ID: ${log.id || 'N/A'})`;

                return (
                  <div key={index} style={styles.terminalLine}>
                    <span style={styles.termTime}>[{log.timestamp ? log.timestamp.substring(11, 19) : 'LIVE'}]</span>
                    <span style={{ color: log.severity === 'HIGH' || log.severity === 'CRITICAL' ? colors.critical : '#5fffbd' }}>
                      {messageAFFICHE}
                    </span>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Styles consolidés
const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  errorBanner: { background: colors.primaryBg, color: colors.primary, border: `1px solid ${colors.primary}`, padding: '12px 16px', borderRadius: 10, display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, fontWeight: 600 },
  welcomeRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  pulseContainer: { display: 'flex', alignItems: 'center', gap: 8, background: '#fff', padding: '6px 12px', borderRadius: 20, border: `1px solid ${colors.border}` },
  pulseDot: { width: 8, height: 8, borderRadius: '50%', background: colors.success, boxShadow: `0 0 8px ${colors.success}` },
  pulseText: { fontSize: 12, fontWeight: 600, color: colors.textMuted },
  kpiGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 },
  kpiCard: { background: '#fff', borderRadius: 12, padding: 18, border: `1px solid ${colors.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', transition: 'all 0.15s' },
  kpiLeft: { display: 'flex', flexDirection: 'column', gap: 4 },
  kpiLabel: { fontSize: 12, color: colors.textFaint, fontWeight: 600 },
  kpiValue: { fontSize: 24, fontWeight: 800, color: colors.text },
  kpiIcon: { width: 44, height: 44, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  chartRowFull: { background: '#fff', borderRadius: 14, padding: 20, border: `1px solid ${colors.border}` },
  cardHeader: { marginBottom: 16 },
  cardTitle: { fontSize: 15, fontWeight: 700, color: colors.text },
  cardSub: { fontSize: 12, color: colors.textFaint, marginTop: 1 },
  bottomRowGrid: { display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 16, flexWrap: 'wrap' },
  gridCard: { background: '#fff', borderRadius: 14, padding: 20, border: `1px solid ${colors.border}`, display: 'flex', flexDirection: 'column' },
  pieLegend: { display: 'flex', flexDirection: 'column', gap: 8, minWidth: 110, paddingLeft: 10 },
  legendItem: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 },
  legendDot: { width: 8, height: 8, borderRadius: '50%' },
  legendName: { color: colors.textMuted, flex: 1 },
  legendVal: { fontWeight: 700, color: colors.text },
  terminal: { flex: 1, background: '#0a0f1d', borderRadius: 10, padding: 14, fontFamily: 'monospace', fontSize: 12, lineHeight: 1.6, overflowY: 'auto', maxHeight: 200, display: 'flex', flexDirection: 'column', gap: 6 },
  terminalLine: { display: 'flex', gap: 8, wordBreak: 'break-word' },
  termTime: { color: colors.textFaint }
}
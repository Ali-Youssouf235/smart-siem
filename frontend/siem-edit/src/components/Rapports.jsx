import { useState, useEffect } from 'react'
import { colors } from '../theme'
import { reportsApi, exportApi } from '../api'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'

const monthlyTrends = [
  { month: 'Jan', alertes: 245, resolues: 220, menaces: 45 },
  { month: 'Fév', alertes: 280, resolues: 265, menaces: 52 },
  { month: 'Mar', alertes: 220, resolues: 200, menaces: 38 },
  { month: 'Avr', alertes: 310, resolues: 290, menaces: 61 },
  { month: 'Mai', alertes: 275, resolues: 260, menaces: 48 },
  { month: 'Juin', alertes: 166, resolues: 155, menaces: 32 },
]

const threatCategories = [
  { name: 'Malware', value: 28, color: colors.critical },
  { name: 'Phishing', value: 35, color: colors.high },
  { name: 'Accès non autorisé', value: 22, color: colors.warning },
  { name: 'DDoS', value: 12, color: colors.primary },
  { name: 'Autres', value: 3, color: colors.textFaint },
]

const FREQUENCY_LABELS = { daily: 'Quotidien', weekly: 'Hebdomadaire', disabled: 'Désactivé' }
const TYPE_LABELS = { manuel: 'Manuel', auto_quotidien: 'Auto (quotidien)', auto_hebdomadaire: 'Auto (hebdomadaire)' }

export default function Rapports({ user }) {
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')

  // Historique réel des rapports déjà générés
  const [archive, setArchive] = useState([])
  const [archiveLoading, setArchiveLoading] = useState(true)

  // Planification automatique
  const [schedule, setSchedule] = useState(null)
  const [frequency, setFrequency] = useState('disabled')
  const [hour, setHour] = useState(7)
  const [savingSchedule, setSavingSchedule] = useState(false)
  const [scheduleMsg, setScheduleMsg] = useState('')

  // Export des alertes
  const [exporting, setExporting] = useState('')

  const isAdmin = user?.role === 'admin'

  const fetchArchive = async () => {
    setArchiveLoading(true)
    try {
      const data = await reportsApi.listArchive(20)
      setArchive(data.reports || [])
    } catch (err) {
      console.error("Erreur historique rapports:", err)
    } finally {
      setArchiveLoading(false)
    }
  }

  const fetchSchedule = async () => {
    try {
      const data = await reportsApi.getSchedule()
      setSchedule(data)
      setFrequency(data.frequency || 'disabled')
      setHour(data.hour ?? 7)
    } catch (err) {
      console.error("Erreur planification rapports:", err)
    }
  }

  useEffect(() => {
    fetchArchive()
    fetchSchedule()
  }, [])

  // 🔄 Téléchargement du rapport PDF Cyber en direct depuis FastAPI (archive automatiquement côté serveur)
  const handleDownloadReport = async () => {
    setDownloading(true)
    setError('')
    try {
      const blobData = await reportsApi.downloadPdf()
      const url = window.URL.createObjectURL(new Blob([blobData], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Smart_SIEM_Rapport_Securite_${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(url)
      fetchArchive() // Le nouveau rapport vient d'être archivé côté serveur : on rafraîchit la liste
    } catch (err) {
      console.error("Erreur d'export PDF:", err)
      setError("Erreur lors de la génération du PDF. Vérifiez votre backend FastAPI.")
    } finally {
      setDownloading(false)
    }
  }

  const handleDownloadArchived = async (report) => {
    try {
      const blobData = await reportsApi.downloadArchived(report.id)
      const url = window.URL.createObjectURL(new Blob([blobData], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', report.filename || 'rapport.pdf')
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert("Erreur lors du téléchargement du rapport archivé.")
    }
  }

  const handleSaveSchedule = async () => {
    setSavingSchedule(true)
    setScheduleMsg('')
    try {
      const result = await reportsApi.setSchedule(frequency, parseInt(hour, 10))
      setSchedule(result.schedule)
      setScheduleMsg(
        frequency === 'disabled'
          ? 'Génération automatique désactivée.'
          : `Génération automatique activée : ${FREQUENCY_LABELS[frequency].toLowerCase()}, vers ${hour}h00 (UTC).`
      )
    } catch (err) {
      setScheduleMsg("Erreur lors de l'enregistrement de la planification.")
    } finally {
      setSavingSchedule(false)
    }
  }

  const handleExportAlerts = async (format) => {
    setExporting(format)
    try {
      await exportApi.exportAlerts(format)
    } catch (err) {
      alert("Erreur lors de l'export des alertes.")
    } finally {
      setExporting('')
    }
  }

  return (
    <div style={styles.container}>
      {/* En-tête de la page */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Rapports & Gouvernance RSSI</h1>
          <p style={styles.subtitle}>Générez des extractions analytiques pour les audits de conformité et de gouvernance</p>
        </div>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button onClick={() => handleExportAlerts('csv')} disabled={exporting !== ''} style={styles.secondaryBtn}>
            {exporting === 'csv' ? <i className="ti ti-loader animate-spin" /> : <><i className="ti ti-file-type-csv" /> Alertes CSV</>}
          </button>
          <button onClick={() => handleExportAlerts('xlsx')} disabled={exporting !== ''} style={styles.secondaryBtn}>
            {exporting === 'xlsx' ? <i className="ti ti-loader animate-spin" /> : <><i className="ti ti-file-spreadsheet" /> Alertes Excel</>}
          </button>
          <button style={styles.downloadBtn} onClick={handleDownloadReport} disabled={downloading}>
            {downloading ? (
              <><i className="ti ti-loader animate-spin" /> Compilation du PDF...</>
            ) : (
              <><i className="ti ti-file-download" /> Exporter le Rapport (PDF)</>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ color: colors.critical, background: colors.criticalBg, padding: 12, borderRadius: 8, fontSize: 13, fontWeight: 600 }}>
          <i className="ti ti-alert-triangle" /> {error}
        </div>
      )}

      {/* Planification automatique — réservée aux admins */}
      {isAdmin && (
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Génération Automatique des Rapports</h3>
          <p style={{ fontSize: 12, color: colors.textMuted, marginTop: -10, marginBottom: 14 }}>
            Un rapport PDF sera généré et archivé tout seul, sans action manuelle, selon la fréquence choisie.
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <select value={frequency} onChange={(e) => setFrequency(e.target.value)} style={styles.select}>
              <option value="disabled">Désactivé</option>
              <option value="daily">Quotidien</option>
              <option value="weekly">Hebdomadaire (tous les 7 jours)</option>
            </select>
            {frequency !== 'disabled' && (
              <>
                <span style={{ fontSize: 12, color: colors.textMuted }}>vers</span>
                <select value={hour} onChange={(e) => setHour(e.target.value)} style={styles.select}>
                  {Array.from({ length: 24 }, (_, h) => (
                    <option key={h} value={h}>{String(h).padStart(2, '0')}h00 (UTC)</option>
                  ))}
                </select>
              </>
            )}
            <button onClick={handleSaveSchedule} disabled={savingSchedule} style={styles.secondaryBtn}>
              {savingSchedule ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </div>
          {schedule?.last_run && (
            <p style={{ fontSize: 12, color: colors.textFaint, marginTop: 10 }}>
              Dernière génération automatique : {new Date(schedule.last_run).toLocaleString('fr-FR')}
            </p>
          )}
          {scheduleMsg && <p style={{ fontSize: 12, color: colors.textMuted, marginTop: 8 }}>{scheduleMsg}</p>}
        </div>
      )}

      {/* Reste de la maquette visuelle avec les graphiques Recharts d'origine */}
      <div style={styles.topRow}>
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Tendances Semestrielles des Incidents</h3>
          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyTrends} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.borderLight} />
                <XAxis dataKey="month" stroke={colors.textFaint} style={{ fontSize: 11 }} />
                <YAxis stroke={colors.textFaint} style={{ fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="alertes" stroke={colors.primary} fill={colors.primaryBg} strokeWidth={2} name="Alertes cumulées" />
                <Area type="monotone" dataKey="resolues" stroke={colors.success} fill={colors.successBg} strokeWidth={2} name="Résolues" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Vecteurs d'Attaque Prédominants</h3>
          <div style={{ height: 220, display: 'flex', alignItems: 'center' }}>
            <ResponsiveContainer width="60%" height="100%">
              <PieChart>
                <Pie data={threatCategories} cx="50%" cy="50%" innerRadius={50} outerRadius={70} dataKey="value">
                  {threatCategories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div style={styles.pieLegend}>
              {threatCategories.map((item, i) => (
                <div key={i} style={styles.pieLegendItem}>
                  <div style={{ ...styles.legendColor, background: item.color }} />
                  <span style={styles.legendName}>{item.name}</span>
                  <span style={styles.legendValue}>{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={styles.bottomRow}>
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Historique des Livrables Générés</h3>
          {archiveLoading ? (
            <p style={{ fontSize: 13, color: colors.textMuted }}>Chargement de l'historique...</p>
          ) : archive.length === 0 ? (
            <p style={{ fontSize: 13, color: colors.textMuted }}>Aucun rapport généré pour le moment. Cliquez sur "Exporter le Rapport (PDF)" pour créer le premier.</p>
          ) : (
            <div style={styles.reportList}>
              {archive.map((report) => (
                <div key={report.id} style={styles.reportItem}>
                  <div style={styles.reportIcon}>
                    <i className="ti ti-file-analytics" style={{ color: report.type === 'manuel' ? colors.primary : colors.success }} />
                  </div>
                  <div style={styles.reportContent}>
                    <span style={styles.reportName}>{TYPE_LABELS[report.type] || report.type} — {new Date(report.generated_at).toLocaleString('fr-FR')}</span>
                    <span style={styles.reportMeta}>Format PDF · {((report.size_bytes || 0) / 1024).toFixed(0)} Ko</span>
                  </div>
                  <button style={styles.viewAllBtn} onClick={() => handleDownloadArchived(report)}><i className="ti ti-download" /></button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  downloadBtn: { display: 'flex', alignItems: 'center', gap: 8, padding: '12px 20px', background: colors.primary, border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 14px rgba(24,95,165,0.2)' },
  secondaryBtn: { display: 'flex', alignItems: 'center', gap: 8, padding: '10px 16px', background: '#fff', border: `1px solid ${colors.border}`, borderRadius: 10, color: colors.text, fontSize: 13, fontWeight: 600, cursor: 'pointer' },
  select: { padding: '8px 12px', borderRadius: 8, border: `1px solid ${colors.border}`, fontSize: 13, background: '#fff', color: colors.text, cursor: 'pointer' },
  topRow: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, flexWrap: 'wrap' },
  chartCard: { background: '#fff', borderRadius: 14, padding: 20, border: `1px solid ${colors.border}`, display: 'flex', flexDirection: 'column' },
  chartTitle: { fontSize: 14, fontWeight: 700, color: colors.text, marginBottom: 16 },
  pieLegend: { display: 'flex', flexDirection: 'column', gap: 10, flex: 1, paddingLeft: 10 },
  pieLegendItem: { display: 'flex', alignItems: 'center', gap: 8 },
  legendColor: { width: 10, height: 10, borderRadius: 3 },
  legendName: { fontSize: 12, color: colors.textMuted, flex: 1 },
  legendValue: { fontSize: 12, fontWeight: 700, color: colors.text },
  bottomRow: { display: 'grid', gridTemplateColumns: '1fr', gap: 16 },
  viewAllBtn: { background: 'none', border: 'none', color: colors.primary, fontSize: 14, cursor: 'pointer' },
  reportList: { display: 'flex', flexDirection: 'column', gap: 10 },
  reportItem: { display: 'flex', alignItems: 'center', gap: 12, padding: '11px 12px', background: colors.neutralBg, borderRadius: 8, border: `1px solid ${colors.borderLight}` },
  reportIcon: { width: 38, height: 38, borderRadius: 8, background: colors.primaryBg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  reportContent: { flex: 1, display: 'flex', flexDirection: 'column', gap: 3, minWidth: 0 },
  reportName: { fontSize: 13, fontWeight: 600, color: colors.text, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  reportMeta: { fontSize: 11, color: colors.textFaint }
}

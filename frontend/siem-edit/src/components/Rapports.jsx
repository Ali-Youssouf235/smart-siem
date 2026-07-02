import { useState } from 'react'
import { colors } from '../theme'
import { reportsApi } from '../api' // Raccordement au service d'exportation de fichiers PDF
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

export default function Rapports({ user }) {
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')

  // 🔄 Téléchargement du rapport PDF Cyber en direct depuis FastAPI
  const handleDownloadReport = async () => {
    setDownloading(true)
    setError('')
    try {
      const blobData = await reportsApi.downloadPdf()
      
      // Technique standard pour forcer le navigateur à télécharger le flux binaire PDF
      const url = window.URL.createObjectURL(new Blob([blobData], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Smart_SIEM_Rapport_Securite_${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      
      // Nettoyage de la mémoire du navigateur
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error("Erreur d'export PDF:", err)
      setError("Erreur lors de la génération du PDF. Vérifiez votre backend FastAPI.")
    } finally {
      setDownloading(false)
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
        
        {/* Le gros bouton d'action connecté à ton backend */}
        <button 
          style={styles.downloadBtn} 
          onClick={handleDownloadReport} 
          disabled={downloading}
        >
          {downloading ? (
            <>
              <i className="ti ti-loader animate-spin" /> Compilation du PDF...
            </>
          ) : (
            <>
              <i className="ti ti-file-download" /> Exporter le Rapport Mensuel (PDF)
            </>
          )}
        </button>
      </div>

      {error && (
        <div style={{ color: colors.critical, background: colors.criticalBg, padding: 12, borderRadius: 8, fontSize: 13, fontWeight: 600 }}>
          <i className="ti ti-alert-triangle" /> {error}
        </div>
      )}

      {/* Reste de la maquette visuelle avec tes graphiques Recharts d'origine */}
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
          <div style={styles.reportList}>
            <div style={styles.reportItem}>
              <div style={styles.reportIcon}><i className="ti ti-file-analytics" style={{ color: colors.primary }} /></div>
              <div style={styles.reportContent}>
                <span style={styles.reportName}>Rapport trimestriel d'Audit Interne</span>
                <span style={styles.reportMeta}>Généré par system · Format PDF · 4.2 MB</span>
              </div>
              <button style={styles.viewAllBtn} onClick={handleDownloadReport}><i className="ti ti-download" /></button>
            </div>
            <div style={styles.reportItem}>
              <div style={styles.reportIcon}><i className="ti ti-file-text" style={{ color: colors.success }} /></div>
              <div style={styles.reportContent}>
                <span style={styles.reportName}>Synthèse de Conformité ANSSI / ISO 27001</span>
                <span style={styles.reportMeta}>Généré par system · Format PDF · 1.8 MB</span>
              </div>
              <button style={styles.viewAllBtn} onClick={handleDownloadReport}><i className="ti ti-download" /></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  header: { display: 'flex', justifyContent: 'spaceBetween', alignItems: 'center', flexWrap: 'wrap', gap: 16 },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  downloadBtn: { display: 'flex', alignItems: 'center', gap: 8, padding: '12px 20px', background: colors.primary, border: 'none', borderRadius: 10, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 14px rgba(24,95,165,0.2)' },
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
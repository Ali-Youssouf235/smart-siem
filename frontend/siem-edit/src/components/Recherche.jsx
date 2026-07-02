import { useState } from 'react'
import { colors, severityConfig } from '../theme'
import { logsApi } from '../api'

export default function Recherche({ user }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [hasSearched, setHasSearched] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  const handleSearch = async (e) => {
    if (e) e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setHasSearched(true)
    setExpandedId(null)

    try {
      const data = await logsApi.search(query)
      
      // On s'adapte à la structure de l'API : soit un tableau, soit un objet contenant { logs: [...] }
      if (Array.isArray(data)) {
        setResults(data)
      } else if (data && data.logs) {
        setResults(data.logs)
      } else {
        setResults([])
      }
    } catch (err) {
      console.error("Erreur de Threat Hunting:", err)
      setError("Impossible d'interroger les index de logs Elasticsearch.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div>
        <h1 style={styles.title}>Threat Hunting & Investigation</h1>
        <p style={styles.subtitle}>Fouillez l'index Elasticsearch global pour corréler les indicateurs de compromission</p>
      </div>

      <form onSubmit={handleSearch} style={styles.searchBar}>
        <div style={styles.inputWrapper}>
          <i className="ti ti-search" style={styles.searchIcon} />
          <input
            type="text"
            placeholder="Entrez un identifiant de log, une sévérité ou un nom d'hôte (ex: unknown-device)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={styles.input}
          />
        </div>
        <button type="submit" style={styles.searchBtn} disabled={loading}>
          {loading ? <i className="ti ti-loader animate-spin" /> : <><i className="ti ti-terminal" /> Chasser</>}
        </button>
      </form>

      {loading ? (
        <div style={styles.stateContainer}>
          <i className="ti ti-loader animate-spin" style={{ fontSize: 28, color: colors.primary }} />
          <p style={{ marginTop: 10, color: colors.textMuted }}>Scan des clusters Elasticsearch...</p>
        </div>
      ) : error ? (
        <div style={styles.stateContainer}>
          <i className="ti ti-alert-triangle" style={{ fontSize: 32, color: colors.critical }} />
          <p style={{ marginTop: 10, color: colors.critical, fontWeight: 600 }}>{error}</p>
        </div>
      ) : !hasSearched ? (
        <div style={styles.welcomeState}>
          <div style={styles.welcomeIcon}>
            <i className="ti ti-database-search" style={{ fontSize: 32, color: colors.primary }} />
          </div>
          <h3 style={styles.welcomeTitle}>Moteur de Recherche Prêt</h3>
          <p style={styles.welcomeText}>Saisissez un indicateur ou un mot-clé pour extraire la télémétrie de la base.</p>
        </div>
      ) : results.length === 0 ? (
        <div style={styles.emptyState}>
          <i className="ti ti-zoom-cancel" style={{ fontSize: 32, color: colors.textFaint }} />
          <span style={styles.emptyText}>Aucun log correspondant trouvé (252 Bytes retournés)</span>
          <span style={styles.emptyHint}>Vérifiez que le mot-clé existe exactement dans un document Elasticsearch.</span>
        </div>
      ) : (
        <div style={styles.resultsList}>
          <div style={styles.resultsCount}>
            📊 <strong>{results.length}</strong> entrées de télémétrie extraites pour : <code>"{query}"</code>
          </div>

          {results.map((item) => {
            const currentId = item.id || item._id || Math.random().toString();
            const sev = severityConfig[item.severity] || severityConfig.info
            const isExpanded = expandedId === currentId

            return (
              <div key={currentId} style={styles.resultItem}>
                <div style={styles.itemHeader} onClick={() => setExpandedId(isExpanded ? null : currentId)}>
                  <div style={styles.itemLeft}>
                    <span style={{ ...styles.typeBadge, background: colors.neutralBg, color: colors.textMuted }}>
                      <i className="ti ti-file-text" /> {(item.log_type || 'LOG').toUpperCase()}
                    </span>
                    <div style={styles.titleBlock}>
                      <span style={styles.itemTitle}>
                        {item.raw_message && item.raw_message.trim() !== "\u0000" ? item.raw_message : `Événement ID: ${item.id}`}
                      </span>
                      <span style={styles.itemMeta}>
                        <span><i className="ti ti-clock" /> {item.timestamp}</span>
                        <span>•</span>
                        <span>Machine: <strong>{item.host || 'unknown'}</strong></span>
                      </span>
                    </div>
                  </div>
                  <div style={styles.itemRight}>
                    <span style={{ ...styles.sevBadge, background: sev.bg, color: sev.color }}>
                      {item.severity || 'LOW'}
                    </span>
                    <i className={`ti ti-chevron-${isExpanded ? 'up' : 'down'}`} style={{ color: colors.textFaint }} />
                  </div>
                </div>

                {isExpanded && (
                  <div style={styles.expandedContent}>
                    <div style={styles.divider} />
                    <div style={styles.detailsGrid}>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>ID Log</span>
                        <span style={styles.detailValue}><code>{item.id}</code></span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>Périmètre</span>
                        <span style={styles.detailValue}><code>{item.perimetre_id || 'N/A'}</code></span>
                      </div>
                      <div style={styles.detailItem}>
                        <span style={styles.detailLabel}>IP Source</span>
                        <span style={styles.detailValue}><code>{item.source_ip || 'null'}</code></span>
                      </div>
                    </div>
                    <div style={styles.rawLogBlock}>
                      <div style={styles.rawLogTitle}>Payload JSON original (Elasticsearch)</div>
                      <pre style={styles.jsonBlock}>{JSON.stringify(item, null, 2)}</pre>
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

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  searchBar: { display: 'flex', gap: 12, background: '#fff', padding: 12, borderRadius: 12, border: `1px solid ${colors.border}` },
  inputWrapper: { flex: 1, display: 'flex', alignItems: 'center', gap: 10, background: colors.neutralBg, padding: '0 14px', borderRadius: 8 },
  searchIcon: { color: colors.textFaint, fontSize: 16 },
  input: { flex: 1, background: 'transparent', border: 'none', padding: '12px 0', fontSize: 14, color: colors.text, outline: 'none', fontFamily: 'monospace' },
  searchBtn: { display: 'flex', alignItems: 'center', gap: 8, padding: '0 20px', background: colors.primary, border: 'none', borderRadius: 8, color: '#fff', fontSize: 14, fontWeight: 600, cursor: 'pointer' },
  stateContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '60px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}` },
  welcomeState: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '64px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}`, gap: 14, textAlign: 'center' },
  welcomeIcon: { width: 64, height: 64, borderRadius: 16, background: colors.primaryBg, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  welcomeTitle: { fontSize: 16, fontWeight: 700, color: colors.text },
  welcomeText: { fontSize: 13, color: colors.textMuted, maxWidth: 400 },
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '56px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}`, gap: 10, textAlign: 'center' },
  emptyText: { fontSize: 15, fontWeight: 600, color: colors.text },
  emptyHint: { fontSize: 13, color: colors.textMuted },
  resultsList: { display: 'flex', flexDirection: 'column', gap: 12 },
  resultsCount: { fontSize: 13, color: colors.textMuted },
  resultItem: { background: '#fff', borderRadius: 10, border: `1px solid ${colors.border}`, padding: '14px 16px' },
  itemHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' },
  itemLeft: { display: 'flex', gap: 14, alignItems: 'flex-start', flex: 1 },
  typeBadge: { display: 'flex', alignItems: 'center', gap: 4, padding: '4px 8px', borderRadius: 6, fontSize: 11, fontWeight: 700 },
  titleBlock: { display: 'flex', flexDirection: 'column', gap: 4 },
  itemTitle: { fontSize: 14, fontWeight: 600, color: colors.text },
  itemMeta: { display: 'flex', gap: 12, fontSize: 11, color: colors.textFaint },
  itemRight: { display: 'flex', alignItems: 'center', gap: 14 },
  sevBadge: { padding: '3px 8px', borderRadius: 5, fontSize: 10, fontWeight: 700, textTransform: 'uppercase' },
  expandedContent: { marginTop: 12 },
  divider: { height: 1, background: colors.borderLight, marginBottom: 12 },
  detailsGrid: { display: 'flex', gap: 32, flexWrap: 'wrap', marginBottom: 14 },
  detailItem: { display: 'flex', flexDirection: 'column', gap: 3 },
  detailLabel: { fontSize: 10, color: colors.textFaint, textTransform: 'uppercase', fontWeight: 600 },
  detailValue: { fontSize: 13, color: colors.text },
  rawLogBlock: { marginTop: 12, background: '#0a0f1d', borderRadius: 8, padding: 12 },
  rawLogTitle: { fontSize: 11, color: '#5fffbd', fontWeight: 700, marginBottom: 8, textTransform: 'uppercase', fontFamily: 'monospace' },
  jsonBlock: { margin: 0, padding: 0, fontFamily: 'monospace', fontSize: 12, color: '#e2eaf4', overflowX: 'auto', whiteSpace: 'pre-wrap' }
}
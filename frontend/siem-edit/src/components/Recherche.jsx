import { useState } from 'react'
import { colors, severityConfig } from '../theme'
import { logsApi, exportApi } from '../api'

export default function Recherche({ user }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [hasSearched, setHasSearched] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)
  const [exporting, setExporting] = useState('')

  // Contexte du pivot en cours (ex: "IP Source: 41.202.19.3") pour affichage clair
  const [activeContext, setActiveContext] = useState(null)

  // Marquage des événements suspects (investigation collaborative)
  const [suspectMap, setSuspectMap] = useState({}) // { [logId]: bool }
  const [suspectSaving, setSuspectSaving] = useState(null)

  // Timeline forensique d'un indicateur
  const [timelineTarget, setTimelineTarget] = useState(null) // { label, source_ip, host }
  const [timelineData, setTimelineData] = useState([])
  const [timelineLoading, setTimelineLoading] = useState(false)

  const applyResults = (data) => {
    let logs = []
    if (Array.isArray(data)) logs = data
    else if (data && data.logs) logs = data.logs
    setResults(logs)
    // Initialise l'état de marquage suspect à partir de ce que renvoie l'API
    const initial = {}
    logs.forEach((l) => { if (l.id) initial[l.id] = !!l.is_suspect })
    setSuspectMap((prev) => ({ ...initial, ...prev }))
  }

  const handleSearch = async (e) => {
    if (e) e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setHasSearched(true)
    setExpandedId(null)
    setActiveContext(null)
    setTimelineTarget(null)

    try {
      const data = await logsApi.search(query)
      applyResults(data)
    } catch (err) {
      console.error("Erreur de Threat Hunting:", err)
      setError("Impossible d'interroger les index de logs Elasticsearch.")
    } finally {
      setLoading(false)
    }
  }

  // 🎯 Pivot sur un indicateur précis (IP source, machine, utilisateur) : relance
  // une recherche exacte sur ce champ, pour suivre la piste d'un indicateur
  // de compromission d'un log à l'autre (exigence 4.6).
  const handlePivot = async (field, value, label) => {
    if (!value) return
    setLoading(true)
    setError('')
    setHasSearched(true)
    setExpandedId(null)
    setTimelineTarget(null)
    setQuery(value)
    setActiveContext(`${label} : ${value}`)

    try {
      const data = await logsApi.searchByField({ [field]: value })
      applyResults(data)
    } catch (err) {
      console.error('Erreur de pivot:', err)
      setError("Impossible de pivoter sur cet indicateur.")
    } finally {
      setLoading(false)
    }
  }

  // 🕒 Timeline forensique chronologique d'un indicateur
  const handleShowTimeline = async (item) => {
    const label = item.source_ip ? `IP ${item.source_ip}` : `Machine ${item.host}`
    setTimelineTarget({ label, source_ip: item.source_ip, host: item.host })
    setTimelineLoading(true)
    try {
      const data = await logsApi.getTimeline(
        item.source_ip ? { source_ip: item.source_ip } : { host: item.host }
      )
      setTimelineData(data.timeline || [])
    } catch (err) {
      console.error('Erreur timeline:', err)
      setTimelineData([])
    } finally {
      setTimelineLoading(false)
    }
  }

  // 🚩 Marquer / démarquer un événement comme suspect
  const handleToggleSuspect = async (item) => {
    if (!item.id) return
    const newValue = !suspectMap[item.id]
    setSuspectSaving(item.id)
    try {
      await logsApi.toggleSuspect(item.id, newValue)
      setSuspectMap((prev) => ({ ...prev, [item.id]: newValue }))
    } catch (err) {
      alert("Erreur lors du marquage de l'événement.")
    } finally {
      setSuspectSaving(null)
    }
  }

  // 🚩 Vue collaborative : tous les événements marqués suspects par l'équipe,
  // toutes recherches confondues (exigence 4.6 : investigation collaborative)
  const handleShowAllSuspects = async () => {
    setLoading(true)
    setError('')
    setHasSearched(true)
    setExpandedId(null)
    setTimelineTarget(null)
    setQuery('')
    setActiveContext('🚩 Événements marqués suspects par l\'équipe')

    try {
      const data = await logsApi.listSuspects(200)
      applyResults(data)
    } catch (err) {
      console.error('Erreur chargement suspects:', err)
      setError("Impossible de charger les événements marqués suspects.")
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format) => {
    setExporting(format)
    try {
      await exportApi.exportLogs(format, { keyword: query })
    } catch (err) {
      console.error("Erreur d'export:", err)
      alert("Erreur lors de l'export des résultats.")
    } finally {
      setExporting('')
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
            onChange={(e) => { setQuery(e.target.value); setActiveContext(null) }}
            style={styles.input}
          />
        </div>
        <button type="submit" style={styles.searchBtn} disabled={loading}>
          {loading ? <i className="ti ti-loader animate-spin" /> : <><i className="ti ti-terminal" /> Chasser</>}
        </button>
        <button type="button" onClick={handleShowAllSuspects} disabled={loading} style={styles.suspectsBtn}>
          <i className="ti ti-flag" /> Suspects de l'équipe
        </button>
      </form>

      {activeContext && (
        <div style={styles.pivotBanner}>
          <i className="ti ti-git-fork" /> Pivot actif sur <strong>{activeContext}</strong>
          <button onClick={() => setActiveContext(null)} style={styles.pivotClearBtn}>Effacer</button>
        </div>
      )}

      {/* 🕒 Panneau Timeline forensique */}
      {timelineTarget && (
        <div style={styles.timelinePanel}>
          <div style={styles.timelineHeader}>
            <h3 style={styles.timelineTitle}><i className="ti ti-history" /> Timeline — {timelineTarget.label}</h3>
            <button onClick={() => setTimelineTarget(null)} style={styles.pivotClearBtn}>Fermer</button>
          </div>
          {timelineLoading ? (
            <p style={{ fontSize: 13, color: colors.textMuted }}>Reconstruction de la chronologie...</p>
          ) : timelineData.length === 0 ? (
            <p style={{ fontSize: 13, color: colors.textMuted }}>Aucun événement chronologique trouvé pour cet indicateur.</p>
          ) : (
            <div style={styles.timelineList}>
              {timelineData.map((ev, i) => (
                <div key={ev.id || i} style={styles.timelineRow}>
                  <div style={styles.timelineDot} />
                  <div style={styles.timelineContent}>
                    <div style={styles.timelineRowTop}>
                      <span style={styles.timelineTime}>{ev.timestamp}</span>
                      {ev.delta_seconds !== undefined && (
                        <span style={styles.timelineDelta}>+{ev.delta_seconds}s</span>
                      )}
                    </div>
                    <span style={styles.timelineMsg}>{ev.raw_message || ev.log_type || 'Événement'} · {ev.host}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

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
          <span style={styles.emptyText}>Aucun log correspondant trouvé</span>
          <span style={styles.emptyHint}>Vérifiez que le mot-clé existe exactement dans un document Elasticsearch.</span>
        </div>
      ) : (
        <div style={styles.resultsList}>
          <div style={styles.resultsCount}>
            <span>📊 <strong>{results.length}</strong> entrées de télémétrie extraites pour : <code>"{query}"</code></span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => handleExport('csv')} disabled={exporting !== ''} style={styles.exportBtn}>
                {exporting === 'csv' ? <i className="ti ti-loader animate-spin" /> : <><i className="ti ti-file-type-csv" /> CSV</>}
              </button>
              <button onClick={() => handleExport('xlsx')} disabled={exporting !== ''} style={styles.exportBtn}>
                {exporting === 'xlsx' ? <i className="ti ti-loader animate-spin" /> : <><i className="ti ti-file-spreadsheet" /> Excel</>}
              </button>
            </div>
          </div>

          {results.map((item) => {
            const currentId = item.id || item._id || Math.random().toString();
            const sev = severityConfig[item.severity] || severityConfig.info
            const isExpanded = expandedId === currentId
            const isSuspect = !!suspectMap[item.id]

            return (
              <div key={currentId} style={{ ...styles.resultItem, borderColor: isSuspect ? colors.critical : colors.border }}>
                <div style={styles.itemHeader} onClick={() => setExpandedId(isExpanded ? null : currentId)}>
                  <div style={styles.itemLeft}>
                    <span style={{ ...styles.typeBadge, background: colors.neutralBg, color: colors.textMuted }}>
                      <i className="ti ti-file-text" /> {(item.log_type || 'LOG').toUpperCase()}
                    </span>
                    <div style={styles.titleBlock}>
                      <span style={styles.itemTitle}>
                        {item.raw_message && item.raw_message.trim() !== "\u0000" ? item.raw_message : `Événement ID: ${item.id}`}
                        {isSuspect && <span style={styles.suspectTag}>SUSPECT</span>}
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

                    {/* 🎯 Actions d'investigation : pivot, timeline, marquage suspect */}
                    <div style={styles.actionRow}>
                      {item.source_ip && (
                        <button style={styles.actionBtn} onClick={() => handlePivot('source_ip', item.source_ip, 'IP Source')}>
                          <i className="ti ti-git-fork" /> Pivoter sur l'IP
                        </button>
                      )}
                      {item.host && (
                        <button style={styles.actionBtn} onClick={() => handlePivot('host', item.host, 'Machine')}>
                          <i className="ti ti-git-fork" /> Pivoter sur la machine
                        </button>
                      )}
                      {item.username && (
                        <button style={styles.actionBtn} onClick={() => handlePivot('username', item.username, 'Utilisateur')}>
                          <i className="ti ti-git-fork" /> Pivoter sur l'utilisateur
                        </button>
                      )}
                      {(item.source_ip || item.host) && (
                        <button style={styles.actionBtn} onClick={() => handleShowTimeline(item)}>
                          <i className="ti ti-history" /> Voir la timeline
                        </button>
                      )}
                      <button
                        style={{ ...styles.actionBtn, color: isSuspect ? colors.critical : colors.text, borderColor: isSuspect ? colors.critical : colors.border }}
                        onClick={() => handleToggleSuspect(item)}
                        disabled={suspectSaving === item.id}
                      >
                        {suspectSaving === item.id ? (
                          <i className="ti ti-loader animate-spin" />
                        ) : (
                          <><i className="ti ti-flag" /> {isSuspect ? 'Démarquer' : 'Marquer suspect'}</>
                        )}
                      </button>
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
  suspectsBtn: { display: 'flex', alignItems: 'center', gap: 8, padding: '0 18px', background: '#fff', border: `1px solid ${colors.critical}`, borderRadius: 8, color: colors.critical, fontSize: 13, fontWeight: 700, cursor: 'pointer' },
  pivotBanner: { display: 'flex', alignItems: 'center', gap: 10, background: colors.primaryBg, color: colors.primary, padding: '10px 14px', borderRadius: 8, fontSize: 13, fontWeight: 600 },
  pivotClearBtn: { marginLeft: 'auto', background: 'none', border: 'none', color: 'inherit', textDecoration: 'underline', cursor: 'pointer', fontSize: 12, fontWeight: 600 },
  stateContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '60px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}` },
  welcomeState: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '64px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}`, gap: 14, textAlign: 'center' },
  welcomeIcon: { width: 64, height: 64, borderRadius: 16, background: colors.primaryBg, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  welcomeTitle: { fontSize: 16, fontWeight: 700, color: colors.text },
  welcomeText: { fontSize: 13, color: colors.textMuted, maxWidth: 400 },
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '56px 24px', background: '#fff', borderRadius: 12, border: `1px solid ${colors.border}`, gap: 10, textAlign: 'center' },
  emptyText: { fontSize: 15, fontWeight: 600, color: colors.text },
  emptyHint: { fontSize: 13, color: colors.textMuted },
  resultsList: { display: 'flex', flexDirection: 'column', gap: 12 },
  resultsCount: { fontSize: 13, color: colors.textMuted, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 },
  exportBtn: { display: 'flex', alignItems: 'center', gap: 6, background: '#fff', border: `1px solid ${colors.border}`, borderRadius: 8, padding: '6px 12px', fontSize: 12, fontWeight: 600, color: colors.text, cursor: 'pointer' },
  resultItem: { background: '#fff', borderRadius: 10, border: '1px solid', padding: '14px 16px' },
  itemHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' },
  itemLeft: { display: 'flex', gap: 14, alignItems: 'flex-start', flex: 1 },
  typeBadge: { display: 'flex', alignItems: 'center', gap: 4, padding: '4px 8px', borderRadius: 6, fontSize: 11, fontWeight: 700 },
  titleBlock: { display: 'flex', flexDirection: 'column', gap: 4 },
  itemTitle: { fontSize: 14, fontWeight: 600, color: colors.text, display: 'flex', alignItems: 'center', gap: 8 },
  suspectTag: { fontSize: 10, fontWeight: 800, color: '#fff', background: colors.critical, padding: '2px 6px', borderRadius: 4 },
  itemMeta: { display: 'flex', gap: 12, fontSize: 11, color: colors.textFaint },
  itemRight: { display: 'flex', alignItems: 'center', gap: 14 },
  sevBadge: { padding: '3px 8px', borderRadius: 5, fontSize: 10, fontWeight: 700, textTransform: 'uppercase' },
  expandedContent: { marginTop: 12 },
  divider: { height: 1, background: colors.borderLight, marginBottom: 12 },
  detailsGrid: { display: 'flex', gap: 32, flexWrap: 'wrap', marginBottom: 14 },
  detailItem: { display: 'flex', flexDirection: 'column', gap: 3 },
  detailLabel: { fontSize: 10, color: colors.textFaint, textTransform: 'uppercase', fontWeight: 600 },
  detailValue: { fontSize: 13, color: colors.text },
  actionRow: { display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 14 },
  actionBtn: { display: 'flex', alignItems: 'center', gap: 6, background: '#fff', border: `1px solid ${colors.border}`, borderRadius: 8, padding: '6px 12px', fontSize: 12, fontWeight: 600, cursor: 'pointer' },
  rawLogBlock: { marginTop: 12, background: '#0a0f1d', borderRadius: 8, padding: 12 },
  rawLogTitle: { fontSize: 11, color: '#5fffbd', fontWeight: 700, marginBottom: 8, textTransform: 'uppercase', fontFamily: 'monospace' },
  jsonBlock: { margin: 0, padding: 0, fontFamily: 'monospace', fontSize: 12, color: '#e2eaf4', overflowX: 'auto', whiteSpace: 'pre-wrap' },
  timelinePanel: { background: '#fff', border: `1px solid ${colors.border}`, borderRadius: 12, padding: 18 },
  timelineHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  timelineTitle: { fontSize: 15, fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: 8 },
  timelineList: { display: 'flex', flexDirection: 'column', gap: 0, maxHeight: 360, overflowY: 'auto', paddingLeft: 6 },
  timelineRow: { display: 'flex', gap: 12, borderLeft: `2px solid ${colors.border}`, paddingLeft: 14, paddingBottom: 14, position: 'relative' },
  timelineDot: { position: 'absolute', left: -6, top: 2, width: 10, height: 10, borderRadius: '50%', background: colors.primary },
  timelineContent: { display: 'flex', flexDirection: 'column', gap: 2 },
  timelineRowTop: { display: 'flex', gap: 10, alignItems: 'center' },
  timelineTime: { fontSize: 12, fontWeight: 700, color: colors.text, fontFamily: 'monospace' },
  timelineDelta: { fontSize: 11, color: colors.textFaint, background: colors.neutralBg, padding: '1px 6px', borderRadius: 4 },
  timelineMsg: { fontSize: 12, color: colors.textMuted },
}

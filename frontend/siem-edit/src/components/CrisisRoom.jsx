import { useState, useEffect, useCallback } from 'react';
import { colors } from '../theme';
import { alertsApi, logsApi } from '../api';

const REFRESH_MS = 5000; // Exigence 4.5 du cahier des charges : rafraîchissement toutes les 5 secondes

export default function CrisisRoom({ onExit }) {
  const [stats, setStats] = useState(null);
  const [criticalAlerts, setCriticalAlerts] = useState([]);
  const [liveLogs, setLiveLogs] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [clock, setClock] = useState(new Date());
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    try {
      const [statsRes, criticalRes, logsRes] = await Promise.all([
        alertsApi.getStats(),
        alertsApi.list({ severity: 'critical' }),
        logsApi.search(''),
      ]);
      setStats(statsRes);
      setCriticalAlerts(Array.isArray(criticalRes) ? criticalRes.slice(0, 8) : []);
      const logs = logsRes?.logs ?? (Array.isArray(logsRes) ? logsRes : []);
      setLiveLogs(logs.slice(0, 10));
      setLastUpdate(new Date());
      setError('');
    } catch (err) {
      console.error('Erreur Crisis Room:', err);
      setError('Liaison perdue avec le backend FastAPI — nouvelle tentative dans 5s...');
    }
  }, []);

  useEffect(() => {
    loadData();
    const dataInterval = setInterval(loadData, REFRESH_MS);
    const clockInterval = setInterval(() => setClock(new Date()), 1000);
    return () => {
      clearInterval(dataInterval);
      clearInterval(clockInterval);
    };
  }, [loadData]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  const total = stats?.total_alerts ?? 0;
  const critical = stats?.by_severity?.CRITICAL ?? 0;
  const high = stats?.by_severity?.HIGH ?? 0;
  const activeAgents = stats?.active_agents ?? 0;

  return (
    <div style={styles.root}>
      <div style={styles.topBar}>
        <div style={styles.brand}>
          <i className="ti ti-shield-lock" style={{ fontSize: 26, color: colors.critical }} />
          <span style={styles.brandText}>SMART SIEM — CRISIS ROOM</span>
        </div>
        <div style={styles.rightBar}>
          <span style={styles.clock}>{clock.toLocaleTimeString('fr-FR')}</span>
          <span style={styles.refreshTag}>
            <i className="ti ti-refresh" /> maj {Math.max(0, Math.round((new Date() - lastUpdate) / 1000))}s
          </span>
          <button onClick={toggleFullscreen} style={styles.iconBtn} title="Plein écran">
            <i className={`ti ${isFullscreen ? 'ti-minimize' : 'ti-maximize'}`} />
          </button>
          <button onClick={onExit} style={styles.exitBtn}>
            <i className="ti ti-x" /> Quitter
          </button>
        </div>
      </div>

      {error && <div style={styles.errorBanner}>{error}</div>}

      <div style={styles.kpiRow}>
        <KpiCard label="Alertes totales" value={total} color={colors.primary} icon="ti-bell" />
        <KpiCard label="Critiques" value={critical} color="#EF4444" icon="ti-alert-octagon" pulse={critical > 0} />
        <KpiCard label="Hautes" value={high} color="#F59E0B" icon="ti-alert-triangle" />
        <KpiCard label="Agents actifs" value={activeAgents} color="#10B981" icon="ti-antenna" />
      </div>

      <div style={styles.mainGrid}>
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}><i className="ti ti-flame" /> Alertes critiques en cours</h2>
          <div style={styles.alertList}>
            {criticalAlerts.length === 0 && <p style={styles.emptyText}>Aucune alerte critique active. Situation nominale.</p>}
            {criticalAlerts.map((a, i) => (
              <div key={a.id || i} style={styles.alertRow}>
                <span style={styles.alertBadge}>CRITICAL</span>
                <div style={styles.alertInfo}>
                  <strong style={styles.alertName}>{a.regle_nom || a.name || a.type || 'Alerte de sécurité'}</strong>
                  <span style={styles.alertMeta}>{a.source_ip || a.host || ''} {a.timestamp ? `· ${new Date(a.timestamp).toLocaleTimeString('fr-FR')}` : ''}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={styles.panel}>
          <h2 style={styles.panelTitle}><i className="ti ti-terminal-2" /> Flux d'événements en direct</h2>
          <div style={styles.logFeed}>
            {liveLogs.length === 0 && <p style={styles.emptyText}>Aucun événement récent.</p>}
            {liveLogs.map((log, i) => (
              <div key={log.id || i} style={styles.logRow}>
                <span style={styles.logTime}>{log.timestamp ? new Date(log.timestamp).toLocaleTimeString('fr-FR') : '--:--:--'}</span>
                <span style={styles.logHost}>{log.host || '—'}</span>
                <span style={styles.logMsg}>{(log.raw_message || log.message || '').slice(0, 90)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value, color, icon, pulse }) {
  return (
    <div style={{ ...styles.kpiCard, borderColor: color, animation: pulse ? 'pulseGlow 1.5s infinite' : 'none' }}>
      <i className={`ti ${icon}`} style={{ fontSize: 22, color }} />
      <span style={{ ...styles.kpiValue, color }}>{value}</span>
      <span style={styles.kpiLabel}>{label}</span>
    </div>
  );
}

const styles = {
  root: {
    position: 'fixed', inset: 0, background: '#0B1120', color: '#E5E7EB',
    zIndex: 9999, display: 'flex', flexDirection: 'column', padding: 24,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    overflow: 'auto',
  },
  topBar: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  brand: { display: 'flex', alignItems: 'center', gap: 10 },
  brandText: { fontSize: 18, fontWeight: 800, letterSpacing: '0.03em' },
  rightBar: { display: 'flex', alignItems: 'center', gap: 14 },
  clock: { fontSize: 20, fontWeight: 700, fontVariantNumeric: 'tabular-nums', color: '#93C5FD' },
  refreshTag: { fontSize: 12, color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: 4 },
  iconBtn: { background: '#1F2937', border: '1px solid #374151', color: '#E5E7EB', width: 36, height: 36, borderRadius: 8, cursor: 'pointer' },
  exitBtn: { display: 'flex', alignItems: 'center', gap: 6, background: '#DC2626', border: 'none', color: '#fff', padding: '8px 16px', borderRadius: 8, fontWeight: 700, cursor: 'pointer', fontSize: 13 },
  errorBanner: { background: '#7F1D1D', color: '#FCA5A5', padding: '10px 14px', borderRadius: 8, fontSize: 13, marginBottom: 16 },
  kpiRow: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 20 },
  kpiCard: { background: '#111827', border: '1px solid', borderRadius: 14, padding: 20, display: 'flex', flexDirection: 'column', gap: 6 },
  kpiValue: { fontSize: 40, fontWeight: 800, fontVariantNumeric: 'tabular-nums' },
  kpiLabel: { fontSize: 13, color: '#9CA3AF', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' },
  mainGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, flex: 1, minHeight: 0 },
  panel: { background: '#111827', border: '1px solid #1F2937', borderRadius: 14, padding: 20, display: 'flex', flexDirection: 'column', minHeight: 0 },
  panelTitle: { fontSize: 15, fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8, color: '#F3F4F6' },
  emptyText: { color: '#6B7280', fontSize: 13 },
  alertList: { display: 'flex', flexDirection: 'column', gap: 10, overflowY: 'auto' },
  alertRow: { display: 'flex', alignItems: 'center', gap: 12, background: '#1F2937', padding: '10px 12px', borderRadius: 8, borderLeft: '3px solid #EF4444' },
  alertBadge: { fontSize: 10, fontWeight: 800, color: '#EF4444', background: 'rgba(239,68,68,0.15)', padding: '3px 7px', borderRadius: 4 },
  alertInfo: { display: 'flex', flexDirection: 'column', gap: 2 },
  alertName: { fontSize: 13, color: '#F3F4F6' },
  alertMeta: { fontSize: 11, color: '#9CA3AF' },
  logFeed: { display: 'flex', flexDirection: 'column', gap: 6, overflowY: 'auto', fontFamily: "'JetBrains Mono', monospace" },
  logRow: { display: 'flex', gap: 10, fontSize: 12, padding: '6px 8px', borderRadius: 6, background: '#0F172A' },
  logTime: { color: '#6B7280', flexShrink: 0 },
  logHost: { color: '#60A5FA', flexShrink: 0, minWidth: 90 },
  logMsg: { color: '#D1D5DB', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
};

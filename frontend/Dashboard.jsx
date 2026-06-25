import React, { useState } from 'react'

const s = {
  body: { padding: '16px 20px 20px', background: '#F0F4F9', minHeight: 'calc(100vh - 92px)' },
  viewBar: {
    background: '#fff',
    borderBottom: '1px solid #E2EAF4',
    padding: '0 20px',
    display: 'flex',
    gap: '6px',
    alignItems: 'center',
    height: '40px',
  },
  vt: (active) => ({
    fontSize: '12px',
    padding: '4px 12px',
    borderRadius: '20px',
    border: `1px solid ${active ? '#185FA5' : '#E2EAF4'}`,
    color: active ? '#fff' : '#6B7A99',
    cursor: 'pointer',
    fontWeight: active ? 600 : 500,
    background: active ? '#185FA5' : 'transparent',
  }),
  kpiRow: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '14px' },
  kpi: {
    background: '#fff',
    borderRadius: '12px',
    padding: '14px 16px',
    border: '1px solid #E2EAF4',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
  },
  kpiHead: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' },
  kpiLbl: { fontSize: '11px', fontWeight: 600, color: '#8896B0', textTransform: 'uppercase', letterSpacing: '0.06em' },
  kpiIcon: (bg) => ({
    width: '28px',
    height: '28px',
    borderRadius: '7px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    background: bg,
  }),
  grid2: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' },
  grid2b: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' },
  card: {
    background: '#fff',
    borderRadius: '12px',
    padding: '14px 16px',
    border: '1px solid #E2EAF4',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
  },
  cardHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' },
  cardTitle: { fontSize: '12px', fontWeight: 700, color: '#1A2535', display: 'flex', alignItems: 'center', gap: '6px' },
  cardAction: { fontSize: '11px', color: '#185FA5', cursor: 'pointer', fontWeight: 600 },
  barsWrap: { display: 'flex', alignItems: 'flex-end', gap: '3px', height: '70px', marginBottom: '6px' },
  arow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '7px 0',
    borderBottom: '1px solid #F3F6FB',
    cursor: 'pointer',
  },
  sev: (bg, color) => ({
    fontSize: '10px',
    fontWeight: 700,
    borderRadius: '5px',
    padding: '2px 7px',
    background: bg,
    color: color,
    whiteSpace: 'nowrap',
  }),
  rrow: { display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 0' },
  rBarWrap: { flex: 2, height: '6px', background: '#F0F4F9', borderRadius: '99px', overflow: 'hidden' },
  mapPh: {
    background: '#F7F9FC',
    borderRadius: '10px',
    height: '92px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '5px',
    border: '1px dashed #D1DCEA',
  },
  quickRow: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginTop: '12px' },
  qbtn: {
    background: '#fff',
    border: '1px solid #E2EAF4',
    borderRadius: '10px',
    padding: '10px 14px',
    fontSize: '12px',
    fontWeight: 600,
    color: '#374151',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '7px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  },
  legend: { display: 'flex', gap: '12px', marginTop: '8px' },
  leg: { display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: '#8896B0' },
}

const bars = [22,28,18,24,20,32,26,22,40,54,88,100,63,36,32,40]
const barColors = ['#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#DC2626','#DC2626','#F59E0B','#D1E4F8','#D1E4F8','#D1E4F8']
const barLabels = ['14h','15h','16h','17h','18h','19h','20h','21h','22h','23h','00h','01h','02h','03h','04h','05h']

const alerts = [
  { sev: 'CRITICAL', bg: '#FEF2F2', col: '#DC2626', text: 'Exfiltration CTU-SVC-003', time: '06:14' },
  { sev: 'CRITICAL', bg: '#FEF2F2', col: '#DC2626', text: 'Compte dormant — zone CLASSIFIED', time: '03:05' },
  { sev: 'HIGH', bg: '#FFFBEB', col: '#D97706', text: 'Brute-force SSH réussi', time: '06:12' },
  { sev: 'HIGH', bg: '#FFFBEB', col: '#D97706', text: 'Accès hors horaires · B3', time: '02:47' },
  { sev: 'INFO', bg: '#F0FDF4', col: '#16A34A', text: "Jack Bauer · VPN établi", time: '06:14' },
]

const risks = [
  { name: 'Nina Myers', score: 94, color: '#DC2626' },
  { name: 'IP 178.43.x', score: 78, color: '#F59E0B' },
  { name: 'Jack Bauer', score: 12, color: '#16A34A' },
  { name: "Chloe O'Brian", score: 8, color: '#16A34A' },
]

export default function Dashboard({ onNav }) {
  const [activeView, setActiveView] = useState('analyste')
  const views = ['analyste', 'rssi', 'investigation', 'crisis']
  const viewLabels = { analyste: 'Vue Analyste', rssi: 'Vue RSSI', investigation: 'Investigation', crisis: '⚠ Crisis Room' }

  return (
    <>
      <div style={s.viewBar}>
        {views.map(v => (
          <span key={v} style={s.vt(activeView === v)} onClick={() => setActiveView(v)}>
            {viewLabels[v]}
          </span>
        ))}
      </div>

      <div style={s.body}>
        {/* KPIs */}
        <div style={s.kpiRow}>
          <div style={s.kpi}>
            <div style={s.kpiHead}>
              <span style={s.kpiLbl}>Alertes Critical</span>
              <div style={s.kpiIcon('#FEF2F2')}><i className="ti ti-alert-triangle" style={{ fontSize: '14px', color: '#DC2626' }} /></div>
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: '#DC2626', letterSpacing: '-0.5px' }}>3</div>
            <div style={{ fontSize: '11px', color: '#8896B0', marginTop: '3px' }}>+3 dernières 24h</div>
          </div>
          <div style={s.kpi}>
            <div style={s.kpiHead}>
              <span style={s.kpiLbl}>Logs / heure</span>
              <div style={s.kpiIcon('#EBF3FF')}><i className="ti ti-activity" style={{ fontSize: '14px', color: '#185FA5' }} /></div>
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: '#0F1D2E', letterSpacing: '-0.5px' }}>47 200</div>
            <div style={{ fontSize: '11px', color: '#8896B0', marginTop: '3px' }}>Normal : ~43 000</div>
          </div>
          <div style={s.kpi}>
            <div style={s.kpiHead}>
              <span style={s.kpiLbl}>Sources actives</span>
              <div style={s.kpiIcon('#F0FDF4')}><i className="ti ti-server" style={{ fontSize: '14px', color: '#16A34A' }} /></div>
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: '#0F1D2E', letterSpacing: '-0.5px' }}>23</div>
            <div style={{ fontSize: '11px', color: '#8896B0', marginTop: '3px' }}>Cisco, AD, VPN, AWS</div>
          </div>
          <div style={s.kpi}>
            <div style={s.kpiHead}>
              <span style={s.kpiLbl}>Playbooks SOAR</span>
              <div style={s.kpiIcon('#FFFBEB')}><i className="ti ti-player-play" style={{ fontSize: '14px', color: '#D97706' }} /></div>
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: '#0F1D2E', letterSpacing: '-0.5px' }}>2</div>
            <div style={{ fontSize: '11px', color: '#8896B0', marginTop: '3px' }}>En cours · Auto</div>
          </div>
        </div>

        {/* Grid 2 */}
        <div style={s.grid2}>
          {/* Volume de logs */}
          <div style={s.card}>
            <div style={s.cardHeader}>
              <span style={s.cardTitle}><i className="ti ti-chart-bar" style={{ color: '#185FA5' }} /> Volume de logs — 16h</span>
              <span style={s.cardAction}>Voir tout</span>
            </div>
            <div style={s.barsWrap}>
              {bars.map((h, i) => (
                <div key={i} style={{ flex: 1, borderRadius: '4px 4px 0 0', height: `${h}%`, background: barColors[i], minHeight: '4px' }} />
              ))}
            </div>
            <div style={{ display: 'flex', gap: '3px' }}>
              {barLabels.map((l, i) => (
                <span key={i} style={{ flex: 1, fontSize: '8.5px', color: '#B0BCCF', textAlign: 'center' }}>{l}</span>
              ))}
            </div>
            <div style={s.legend}>
              <div style={s.leg}><div style={{ width: '8px', height: '8px', borderRadius: '3px', background: '#D1E4F8' }}></div>Normal</div>
              <div style={s.leg}><div style={{ width: '8px', height: '8px', borderRadius: '3px', background: '#F59E0B' }}></div>Élevé</div>
              <div style={s.leg}><div style={{ width: '8px', height: '8px', borderRadius: '3px', background: '#DC2626' }}></div>Critical</div>
            </div>
          </div>

          {/* Dernières alertes */}
          <div style={s.card}>
            <div style={s.cardHeader}>
              <span style={s.cardTitle}><i className="ti ti-bell" style={{ color: '#185FA5' }} /> Dernières alertes</span>
              <span style={s.cardAction} onClick={() => onNav('alertes')}>Voir tout</span>
            </div>
            {alerts.map((a, i) => (
              <div key={i} style={{ ...s.arow, borderBottom: i < alerts.length - 1 ? '1px solid #F3F6FB' : 'none' }}>
                <span style={s.sev(a.bg, a.col)}>{a.sev}</span>
                <span style={{ flex: 1, fontSize: '12px', color: '#374151', fontWeight: 500 }}>{a.text}</span>
                <span style={{ fontSize: '10px', color: '#B0BCCF', fontFamily: "'JetBrains Mono', monospace" }}>{a.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Grid 2b */}
        <div style={s.grid2b}>
          <div style={s.card}>
            <div style={s.cardHeader}>
              <span style={s.cardTitle}><i className="ti ti-users" style={{ color: '#185FA5' }} /> Top risques UEBA</span>
              <span style={s.cardAction} onClick={() => onNav('ueba')}>Voir profils</span>
            </div>
            {risks.map((r, i) => (
              <div key={i} style={s.rrow}>
                <span style={{ fontSize: '12px', color: '#374151', fontWeight: 500, flex: 1 }}>{r.name}</span>
                <div style={s.rBarWrap}>
                  <div style={{ height: '100%', borderRadius: '99px', width: `${r.score}%`, background: r.color }} />
                </div>
                <span style={{ fontSize: '12px', fontWeight: 700, minWidth: '24px', textAlign: 'right', color: r.color }}>{r.score}</span>
              </div>
            ))}
          </div>
          <div style={s.card}>
            <div style={s.cardHeader}>
              <span style={s.cardTitle}><i className="ti ti-map-pin" style={{ color: '#185FA5' }} /> Sources d'attaques</span>
            </div>
            <div style={s.mapPh}>
              <i className="ti ti-world" style={{ fontSize: '26px', color: '#C5D9F2' }} />
              <span style={{ fontSize: '11px', color: '#8896B0', fontWeight: 500 }}>Douala · Los Angeles · Moscou</span>
              <span style={{ fontSize: '10px', color: '#B0BCCF' }}>Carte interactive — données temps réel</span>
            </div>
          </div>
        </div>

        {/* Quick actions */}
        <div style={s.quickRow}>
          <button style={s.qbtn} onClick={() => onNav('recherche')}>
            <i className="ti ti-search" style={{ fontSize: '14px', color: '#185FA5' }} /> Lancer une recherche
          </button>
          <button style={s.qbtn} onClick={() => onNav('alertes')}>
            <i className="ti ti-bell" style={{ fontSize: '14px', color: '#DC2626' }} /> Voir toutes les alertes
          </button>
          <button style={s.qbtn} onClick={() => onNav('ueba')}>
            <i className="ti ti-chart-radar" style={{ fontSize: '14px', color: '#8B5CF6' }} /> Analyse UEBA
          </button>
        </div>
      </div>
    </>
  )
}

import React, { useState } from 'react'

const s = {
  layout: {
    display: 'grid',
    gridTemplateColumns: '210px 1fr',
    minHeight: 'calc(100vh - 52px)',
    background: '#F0F4F9',
  },
  sidebar: {
    background: '#fff',
    borderRight: '1px solid #E2EAF4',
    padding: '16px 14px',
  },
  sg: { marginBottom: '18px' },
  sgTitle: {
    fontSize: '10px',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    color: '#A0AEBF',
    marginBottom: '8px',
  },
  fi: {
    display: 'flex',
    alignItems: 'center',
    gap: '7px',
    fontSize: '12px',
    color: '#374151',
    marginBottom: '5px',
    cursor: 'pointer',
    fontWeight: 500,
  },
  bc: (type) => ({
    marginLeft: 'auto',
    borderRadius: '20px',
    fontSize: '10px',
    padding: '1px 7px',
    fontWeight: 600,
    background: type === 'c' ? '#FEF2F2' : type === 'h' ? '#FFFBEB' : type === 'i' ? '#EBF3FF' : '#F3F6FB',
    color: type === 'c' ? '#DC2626' : type === 'h' ? '#D97706' : type === 'i' ? '#185FA5' : '#8896B0',
  }),
  main: { padding: '16px 20px' },
  searchWrap: {
    background: '#fff',
    borderRadius: '12px',
    padding: '14px 16px',
    border: '1px solid #E2EAF4',
    marginBottom: '12px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
  },
  searchBar: { display: 'flex', gap: '8px', marginBottom: '10px' },
  si: {
    flex: 1,
    background: '#F7F9FC',
    border: '1.5px solid #DDE5F0',
    borderRadius: '9px',
    padding: '10px 14px',
    fontSize: '13px',
    color: '#1A2535',
    fontFamily: "'JetBrains Mono', monospace",
    outline: 'none',
  },
  sbtn: {
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    color: '#fff',
    border: 'none',
    borderRadius: '9px',
    padding: '10px 18px',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  chips: { display: 'flex', gap: '6px', flexWrap: 'wrap' },
  chip: (active) => ({
    border: `1px solid ${active ? '#185FA5' : '#DDE5F0'}`,
    borderRadius: '20px',
    fontSize: '11px',
    padding: '4px 11px',
    color: active ? '#185FA5' : '#6B7A99',
    cursor: 'pointer',
    background: active ? '#EBF3FF' : '#F7F9FC',
    fontWeight: active ? 600 : 500,
  }),
  tlCard: {
    background: '#fff',
    borderRadius: '12px',
    padding: '14px 16px',
    border: '1px solid #E2EAF4',
    marginBottom: '12px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
  },
  cardTitle: { fontSize: '12px', fontWeight: 700, color: '#1A2535', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' },
  rrow: {
    background: '#fff',
    border: '1px solid #E2EAF4',
    borderRadius: '10px',
    padding: '10px 14px',
    marginBottom: '7px',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '10px',
    cursor: 'pointer',
    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  },
  sev: (type) => ({
    fontSize: '10px',
    fontWeight: 700,
    borderRadius: '5px',
    padding: '3px 7px',
    whiteSpace: 'nowrap',
    marginTop: '1px',
    background: type === 'c' ? '#FEF2F2' : type === 'h' ? '#FFFBEB' : '#F0FDF4',
    color: type === 'c' ? '#DC2626' : type === 'h' ? '#D97706' : '#16A34A',
  }),
  av: (bg, col) => ({
    width: '26px',
    height: '26px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '10px',
    fontWeight: 700,
    flexShrink: 0,
    marginTop: '1px',
    background: bg,
    color: col,
  }),
  pivotBtn: {
    fontSize: '10px',
    color: '#185FA5',
    background: '#EBF3FF',
    border: '1px solid #C5D9F2',
    borderRadius: '20px',
    padding: '3px 9px',
    cursor: 'pointer',
    marginTop: '4px',
    fontWeight: 600,
    whiteSpace: 'nowrap',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  actRow: { display: 'flex', gap: '7px', marginTop: '4px' },
  act: {
    fontSize: '11px',
    padding: '6px 12px',
    border: '1px solid #E2EAF4',
    borderRadius: '8px',
    background: '#fff',
    color: '#374151',
    cursor: 'pointer',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
  },
}

const tlBars = [14,18,10,24,16,12,21,28,44,54,85,100,57,27,16,20]
const tlColors = ['#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#D1E4F8','#F59E0B','#F59E0B','#DC2626','#DC2626','#F59E0B','#D1E4F8','#D1E4F8','#D1E4F8']
const tlLabels = ['23:00','','00:00','','01:00','','02:00','','03:00','','05:00','06:00','06:14','','','']

const results = [
  { sev: 'c', sevLabel: 'CRITICAL', avBg: '#FEE2E2', avCol: '#B91C1C', initials: 'NM',
    title: 'Compte CTU-SVC-003 — 47 fichiers classifiés en 90s',
    sub: 'src: 178.43.12.87 · user: nina.myers · host: SRV-ARCH-01 · MITRE: T1078',
    time: '06:14:37' },
  { sev: 'h', sevLabel: 'HIGH', avBg: '#FEF3C7', avCol: '#92400E', initials: '??',
    title: '5 tentatives SSH échouées → authentification réussie',
    sub: 'src: 178.43.12.87 · host: WIN-DC-01 · port: 22 · MITRE: T1110',
    time: '06:12:04' },
  { sev: 'c', sevLabel: 'CRITICAL', avBg: '#FEE2E2', avCol: '#B91C1C', initials: 'NM',
    title: 'Activation compte dormant — accès hors périmètre',
    sub: 'src: 10.0.4.22 (interne) · user: nina.myers · zone: CLASSIFIED',
    time: '03:05:11' },
  { sev: 'i', sevLabel: 'INFO', avBg: '#DBEAFE', avCol: '#1E40AF', initials: 'NM',
    title: 'Badge accès salle serveurs B3 — hors horaires',
    sub: 'user: nina.myers · zone: SERVER-ROOM-B3 · horaires normaux: 07:30–19:00',
    time: '02:47:19' },
]

const filterGroups = [
  {
    title: 'Criticité',
    items: [
      { label: 'Critical', badge: 'c', count: '12', checked: true },
      { label: 'High', badge: 'h', count: '34', checked: true },
      { label: 'Warning', badge: 'n', count: '128', checked: false },
      { label: 'Info', badge: 'i', count: '2.3k', checked: false },
    ],
  },
  {
    title: 'Type de log',
    items: [
      { label: 'Authentification', checked: true },
      { label: 'Réseau', checked: true },
      { label: 'Système', checked: false },
      { label: 'Accès physique', checked: false },
    ],
  },
  {
    title: 'Source',
    items: [
      { label: 'Active Directory', checked: true },
      { label: 'Pare-feu Cisco', checked: true },
      { label: 'Caméras CTU', checked: false },
      { label: 'VPN terrain', checked: false },
    ],
  },
  {
    title: 'MITRE ATT&CK',
    items: [
      { label: 'T1078 Valid Accounts', checked: true },
      { label: 'T1110 Brute Force', checked: false },
      { label: 'T1041 Exfiltration', checked: false },
    ],
  },
]

export default function Recherche() {
  const [activeChip, setActiveChip] = useState('custom')
  const chips = [
    { key: '30m', label: '30 min' },
    { key: '1h', label: '1h' },
    { key: '6h', label: '6h' },
    { key: 'custom', label: '14/03 23:00 → 15/03 06:14' },
    { key: '7d', label: '7 jours' },
    { key: 'custom2', label: '📅 Personnalisé' },
  ]

  return (
    <div style={s.layout}>
      <div style={s.sidebar}>
        {filterGroups.map((g, gi) => (
          <div key={gi} style={s.sg}>
            <p style={s.sgTitle}>{g.title}</p>
            {g.items.map((item, ii) => (
              <div key={ii} style={s.fi}>
                <input type="checkbox" defaultChecked={item.checked} style={{ accentColor: '#185FA5', cursor: 'pointer' }} />
                {item.label}
                {item.count && <span style={s.bc(item.badge)}>{item.count}</span>}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div style={s.main}>
        <div style={s.searchWrap}>
          <div style={s.searchBar}>
            <input
              style={s.si}
              type="text"
              defaultValue="source_ip:178.43.12.87 AND type:auth AND severity:critical"
            />
            <button style={s.sbtn}>
              <i className="ti ti-search" style={{ fontSize: '14px' }} /> Rechercher
            </button>
          </div>
          <div style={s.chips}>
            {chips.map(c => (
              <span key={c.key} style={s.chip(activeChip === c.key)} onClick={() => setActiveChip(c.key)}>
                {c.label}
              </span>
            ))}
          </div>
        </div>

        {/* Timeline */}
        <div style={s.tlCard}>
          <div style={{ ...s.cardTitle, justifyContent: 'space-between' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <i className="ti ti-timeline" style={{ color: '#185FA5' }} /> Distribution temporelle
            </span>
            <span style={{ fontSize: '11px', color: '#8896B0', fontWeight: 500 }}>46 événements trouvés</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '50px' }}>
            {tlBars.map((h, i) => (
              <div key={i} style={{ borderRadius: '4px 4px 0 0', flex: 1, minHeight: '4px', height: `${h}%`, background: tlColors[i] }} />
            ))}
          </div>
          <div style={{ display: 'flex', gap: '3px', marginTop: '4px' }}>
            {tlLabels.map((l, i) => (
              <span key={i} style={{ flex: 1, fontSize: '8.5px', color: '#B0BCCF', textAlign: 'center' }}>{l}</span>
            ))}
          </div>
        </div>

        {/* Results */}
        {results.map((r, i) => (
          <div key={i} style={s.rrow}>
            <span style={s.sev(r.sev)}>{r.sevLabel}</span>
            <div style={s.av(r.avBg, r.avCol)}>{r.initials}</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontSize: '13px', color: '#1A2535', fontWeight: 600, margin: '0 0 3px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {r.title}
              </p>
              <p style={{ fontSize: '11px', color: '#8896B0', margin: 0, fontFamily: "'JetBrains Mono', monospace", overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {r.sub}
              </p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
              <span style={{ fontSize: '10px', color: '#B0BCCF', fontFamily: "'JetBrains Mono', monospace" }}>{r.time}</span>
              <button style={s.pivotBtn}>
                <i className="ti ti-arrows-right-left" style={{ fontSize: '10px' }} /> Pivoter
              </button>
            </div>
          </div>
        ))}

        {/* Actions */}
        <div style={s.actRow}>
          <button style={s.act}><i className="ti ti-download" style={{ fontSize: '13px', color: '#185FA5' }} /> Export CSV</button>
          <button style={s.act}><i className="ti ti-file-type-pdf" style={{ fontSize: '13px', color: '#DC2626' }} /> Rapport PDF</button>
          <button style={s.act}><i className="ti ti-flag" style={{ fontSize: '13px', color: '#D97706' }} /> Escalader en alerte</button>
        </div>
      </div>
    </div>
  )
}

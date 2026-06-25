import React from 'react'

const s = {
  body: {
    padding: '16px 20px',
    background: '#F0F4F9',
    minHeight: 'calc(100vh - 52px)',
  },
  card: {
    background: '#fff',
    borderRadius: '12px',
    padding: '24px',
    border: '1px solid #E2EAF4',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    marginBottom: '12px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '16px',
  },
  title: { fontSize: '14px', fontWeight: 700, color: '#0F1D2E', display: 'flex', alignItems: 'center', gap: '8px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' },
  rCard: {
    background: '#F7F9FC',
    borderRadius: '10px',
    padding: '16px',
    border: '1px solid #EDF1F7',
    cursor: 'pointer',
  },
  btn: {
    fontSize: '12px',
    padding: '8px 16px',
    borderRadius: '8px',
    border: '1px solid #185FA5',
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  btnOutline: {
    fontSize: '12px',
    padding: '8px 16px',
    borderRadius: '8px',
    border: '1px solid #E2EAF4',
    background: '#fff',
    color: '#374151',
    cursor: 'pointer',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
}

const reports = [
  { icon: 'ti-file-text', color: '#185FA5', title: 'Rapport quotidien', desc: '14/03/2026', size: '248 Ko', format: 'PDF' },
  { icon: 'ti-file-spreadsheet', color: '#16A34A', title: 'Export audit S1', desc: '01/03 – 14/03/2026', size: '1.2 Mo', format: 'Excel' },
  { icon: 'ti-file-text', color: '#DC2626', title: 'Rapport incident S7', desc: 'Scénario Nina Myers', size: '87 Ko', format: 'PDF' },
  { icon: 'ti-file-text', color: '#185FA5', title: 'Rapport hebdomadaire', desc: 'Semaine 10/2026', size: '312 Ko', format: 'PDF' },
  { icon: 'ti-file-spreadsheet', color: '#16A34A', title: 'Export logs MITRE', desc: 'T1078 + T1110 + T1041', size: '3.4 Mo', format: 'CSV' },
  { icon: 'ti-certificate', color: '#D97706', title: 'Conformité ISO 27001', desc: 'Mars 2026', size: '156 Ko', format: 'PDF' },
]

export default function Rapports() {
  return (
    <div style={s.body}>
      <div style={s.card}>
        <div style={s.header}>
          <span style={s.title}>
            <i className="ti ti-file-text" style={{ color: '#185FA5', fontSize: '16px' }} />
            Rapports & Exports
          </span>
          <button style={s.btn}>
            <i className="ti ti-plus" style={{ fontSize: '13px' }} /> Générer un rapport
          </button>
        </div>

        <div style={s.grid}>
          {reports.map((r, i) => (
            <div key={i} style={s.rCard}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '9px', background: `${r.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <i className={`ti ${r.icon}`} style={{ fontSize: '18px', color: r.color }} />
                </div>
                <div>
                  <p style={{ fontSize: '13px', fontWeight: 600, color: '#0F1D2E' }}>{r.title}</p>
                  <p style={{ fontSize: '11px', color: '#8896B0', marginTop: '2px' }}>{r.desc}</p>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', background: '#EDF1F7', borderRadius: '5px', padding: '2px 8px', color: '#6B7A99', fontWeight: 600 }}>
                  {r.format} · {r.size}
                </span>
                <button style={{ ...s.btnOutline, padding: '4px 10px', fontSize: '11px' }}>
                  <i className="ti ti-download" style={{ fontSize: '11px', color: '#185FA5' }} /> Télécharger
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={s.card}>
        <div style={s.header}>
          <span style={s.title}>
            <i className="ti ti-settings-automation" style={{ color: '#185FA5', fontSize: '16px' }} />
            Génération automatique
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          {[
            { label: 'Rapport PDF quotidien', schedule: 'Tous les jours à 06:00', active: true },
            { label: 'Export CSV hebdomadaire', schedule: 'Chaque lundi à 08:00', active: true },
            { label: 'Rapport conformité mensuel', schedule: 'Le 1er de chaque mois', active: false },
            { label: 'Rapport incident immédiat', schedule: 'À chaque CRITICAL', active: true },
          ].map((item, i) => (
            <div key={i} style={{ background: '#F7F9FC', borderRadius: '10px', padding: '12px 14px', border: '1px solid #EDF1F7', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <p style={{ fontSize: '12px', fontWeight: 600, color: '#374151' }}>{item.label}</p>
                <p style={{ fontSize: '11px', color: '#8896B0', marginTop: '2px' }}>{item.schedule}</p>
              </div>
              <div style={{
                width: '36px', height: '20px', borderRadius: '10px',
                background: item.active ? '#185FA5' : '#E2EAF4',
                position: 'relative', cursor: 'pointer', flexShrink: 0,
              }}>
                <div style={{
                  position: 'absolute', top: '3px',
                  left: item.active ? '19px' : '3px',
                  width: '14px', height: '14px', borderRadius: '50%',
                  background: '#fff', transition: 'left 0.2s',
                }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

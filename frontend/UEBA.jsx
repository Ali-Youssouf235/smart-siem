import React from 'react'

const s = {
  body: {
    display: 'grid',
    gridTemplateColumns: '240px 1fr',
    gap: '14px',
    padding: '16px 20px',
    background: '#F0F4F9',
    minHeight: 'calc(100vh - 52px)',
  },
  colLeft: { display: 'flex', flexDirection: 'column', gap: '12px' },
  card: {
    background: '#fff',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid #E2EAF4',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
  },
  cardTitle: {
    fontSize: '12px',
    fontWeight: 700,
    color: '#1A2535',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '12px',
  },
  pfHead: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' },
  avBig: {
    width: '46px',
    height: '46px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #FEE2E2, #FECACA)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '15px',
    fontWeight: 700,
    color: '#B91C1C',
    flexShrink: 0,
    border: '2px solid #FCA5A5',
  },
  gaugeBox: {
    background: 'linear-gradient(135deg, #FEF2F2, #FFF5F5)',
    border: '1px solid #FECACA',
    borderRadius: '10px',
    padding: '12px',
    textAlign: 'center',
    marginBottom: '12px',
  },
  rrow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 0',
    borderBottom: '1px solid #F3F6FB',
    cursor: 'pointer',
  },
  ra: (bg, col) => ({
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '9px',
    fontWeight: 700,
    flexShrink: 0,
    background: bg,
    color: col,
  }),
  rb: { flex: 2, height: '6px', background: '#F0F4F9', borderRadius: '99px', overflow: 'hidden' },
  colRight: { display: 'flex', flexDirection: 'column', gap: '12px' },
  tlWrap: { display: 'flex', flexDirection: 'column', gap: 0 },
  tlEvent: (flagged) => ({
    display: 'flex',
    gap: '12px',
    padding: '10px 0 10px 16px',
    borderLeft: `2px solid ${flagged ? '#FECACA' : '#E2EAF4'}`,
    marginLeft: '8px',
    position: 'relative',
  }),
  tlTime: {
    fontSize: '11px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#8896B0',
    minWidth: '40px',
    fontWeight: 500,
    marginTop: '1px',
  },
  tlBadge: {
    fontSize: '10px',
    fontWeight: 700,
    background: '#FEF2F2',
    color: '#DC2626',
    borderRadius: '5px',
    padding: '2px 7px',
    whiteSpace: 'nowrap',
    marginTop: '2px',
    display: 'inline-block',
  },
  chartSection: {
    background: '#F7F9FC',
    borderRadius: '10px',
    padding: '12px',
    border: '1px solid #EDF1F7',
  },
  sbars: { display: 'flex', alignItems: 'flex-end', gap: '8px', height: '64px' },
  actRow: { display: 'flex', gap: '8px' },
  ab: (primary) => ({
    fontSize: '12px',
    padding: '8px 14px',
    border: primary ? '1px solid #185FA5' : '1px solid #E2EAF4',
    borderRadius: '8px',
    background: primary ? 'linear-gradient(135deg, #185FA5, #1474C4)' : '#fff',
    color: primary ? '#fff' : '#374151',
    cursor: 'pointer',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    boxShadow: primary ? '0 2px 8px rgba(24,95,165,0.2)' : '0 1px 3px rgba(0,0,0,0.04)',
  }),
}

const topRisks = [
  { initials: 'NM', bg: '#FEE2E2', col: '#B91C1C', name: 'Nina Myers', score: 94, barColor: '#DC2626' },
  { initials: '??', bg: '#FEF3C7', col: '#92400E', name: 'IP 178.43.x', score: 78, barColor: '#F59E0B' },
  { initials: 'JB', bg: '#DBEAFE', col: '#1E40AF', name: 'Jack Bauer', score: 12, barColor: '#16A34A' },
  { initials: 'CO', bg: '#D1FAE5', col: '#065F46', name: "Chloe O'Brian", score: 8, barColor: '#16A34A' },
  { initials: 'TA', bg: '#D1FAE5', col: '#065F46', name: 'Tony Almeida', score: 5, barColor: '#16A34A' },
]

const timeline = [
  {
    time: '02:47', flagged: false,
    title: 'Badge actif salle serveurs B3',
    sub: "Jamais avant 7h30 en 3 ans d'activité enregistrée",
    delta: '12 → 35',
    deltaRed: false,
  },
  {
    time: '02:53', flagged: true,
    title: 'Téléchargement de 840 fichiers classifiés',
    sub: '2.3 Go exfiltrés en 12 minutes · MITRE T1041',
    badge: 'Anomalie critique',
    delta: '35 → 47',
    deltaRed: true,
  },
  {
    time: '03:01', flagged: true,
    title: 'Tentative accès partition chiffrée',
    sub: 'Zone hors périmètre autorisé — accès refusé',
    badge: 'Hors périmètre',
    delta: '47 → 78',
    deltaRed: true,
  },
  {
    time: '03:05', flagged: true,
    title: 'Alerte CRITICAL générée automatiquement',
    sub: 'Moteur UEBA — seuil critique atteint · Chloe notifiée',
    badge: '🔴 CRITICAL',
    delta: '78 → 94',
    deltaRed: true,
  },
  {
    time: '03:08', flagged: false,
    title: 'Interception à la sortie du bâtiment',
    sub: 'Score final : 94 · Agent Jack Bauer',
    delta: 'Final 94',
    deltaRed: false,
  },
]

const scoreBars = [
  { height: '14%', color: '#D1E4F8' },
  { height: '37%', color: '#F59E0B' },
  { height: '50%', color: '#F59E0B' },
  { height: '83%', color: '#DC2626' },
  { height: '100%', color: '#DC2626' },
]
const scoreLabels = ['02:47', '02:53', '03:01', '03:05', '03:08']

export default function UEBA({ onNav }) {
  return (
    <div style={s.body}>
      <div style={s.colLeft}>
        {/* Profile card */}
        <div style={s.card}>
          <div style={s.pfHead}>
            <div style={s.avBig}>NM</div>
            <div>
              <p style={{ fontSize: '14px', fontWeight: 700, color: '#0F1D2E' }}>Nina Myers</p>
              <p style={{ fontSize: '11px', color: '#6B7A99', marginTop: '3px' }}>Analyste senior · 3 ans CTU</p>
            </div>
          </div>
          <div style={s.gaugeBox}>
            <div style={{ fontSize: '40px', fontWeight: 800, color: '#DC2626', letterSpacing: '-1px' }}>94</div>
            <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#F87171', fontWeight: 700, marginTop: '2px' }}>
              Score de risque
            </div>
          </div>
          <p style={{ fontSize: '11px', color: '#8896B0', lineHeight: 1.6 }}>
            Score stable à 12 depuis 3 ans. Bascule en 18 minutes suite à 3 comportements inédits détectés dans la nuit.
          </p>
        </div>

        {/* Top scores */}
        <div style={s.card}>
          <div style={s.cardTitle}>
            <i className="ti ti-users" style={{ color: '#185FA5' }} /> Top scores du jour
          </div>
          {topRisks.map((r, i) => (
            <div key={i} style={{ ...s.rrow, borderBottom: i < topRisks.length - 1 ? '1px solid #F3F6FB' : 'none' }}>
              <div style={s.ra(r.bg, r.col)}>{r.initials}</div>
              <span style={{ fontSize: '12px', color: '#374151', fontWeight: 600, flex: 1 }}>{r.name}</span>
              <div style={s.rb}>
                <div style={{ height: '100%', borderRadius: '99px', width: `${r.score}%`, background: r.barColor }} />
              </div>
              <span style={{ fontSize: '12px', fontWeight: 800, minWidth: '22px', textAlign: 'right', color: r.barColor }}>
                {r.score}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div style={s.colRight}>
        {/* Timeline card */}
        <div style={s.card}>
          <div style={s.cardTitle}>
            <i className="ti ti-timeline" style={{ color: '#185FA5' }} /> Reconstitution comportementale — Scénario S7
          </div>
          <div style={s.tlWrap}>
            {timeline.map((ev, i) => (
              <div key={i} style={s.tlEvent(ev.flagged)}>
                {/* Dot indicator */}
                <div style={{
                  position: 'absolute',
                  left: '-5px',
                  top: '14px',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: ev.flagged ? '#DC2626' : '#D1E4F8',
                  border: `1.5px solid ${ev.flagged ? '#FCA5A5' : '#E2EAF4'}`,
                }} />
                <span style={s.tlTime}>{ev.time}</span>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: '12px', color: '#374151', fontWeight: 600, margin: 0 }}>{ev.title}</p>
                  <p style={{ fontSize: '11px', color: '#8896B0', marginTop: '2px' }}>{ev.sub}</p>
                  {ev.badge && <span style={s.tlBadge}>{ev.badge}</span>}
                </div>
                <span style={{
                  fontSize: '11px',
                  fontFamily: "'JetBrains Mono', monospace",
                  color: ev.deltaRed ? '#DC2626' : '#8896B0',
                  fontWeight: ev.deltaRed ? 700 : 400,
                  whiteSpace: 'nowrap',
                }}>
                  {ev.delta}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Score chart */}
        <div style={s.card}>
          <div style={s.cardTitle}>
            <i className="ti ti-chart-bar" style={{ color: '#185FA5' }} /> Évolution du score — nuit du scénario
          </div>
          <div style={s.chartSection}>
            <div style={s.sbars}>
              {scoreBars.map((b, i) => (
                <div key={i} style={{ flex: 1, borderRadius: '5px 5px 0 0', height: b.height, background: b.color }} />
              ))}
            </div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '5px' }}>
              {scoreLabels.map((l, i) => (
                <span key={i} style={{ flex: 1, fontSize: '10px', color: '#8896B0', textAlign: 'center', fontFamily: "'JetBrains Mono', monospace" }}>
                  {l}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={s.actRow}>
          <button style={s.ab(true)} onClick={() => onNav('alertes')}>
            <i className="ti ti-bell" style={{ fontSize: '13px' }} /> Voir l'alerte liée
          </button>
          <button style={s.ab(false)} onClick={() => onNav('recherche')}>
            <i className="ti ti-search" style={{ fontSize: '13px', color: '#185FA5' }} /> Investiguer les logs bruts
          </button>
          <button style={s.ab(false)}>
            <i className="ti ti-file-type-pdf" style={{ fontSize: '13px', color: '#DC2626' }} /> Exporter le rapport
          </button>
        </div>
      </div>
    </div>
  )
}

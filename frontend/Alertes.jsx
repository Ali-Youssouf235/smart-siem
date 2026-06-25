import React from 'react'

const s = {
  body: { padding: '16px 20px', background: '#F0F4F9', minHeight: 'calc(100vh - 52px)' },
  acard: (type) => ({
    background: '#fff',
    borderRadius: '12px',
    padding: '16px 18px',
    marginBottom: '12px',
    border: '1px solid #E2EAF4',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    borderLeft: `4px solid ${type === 'crit' ? '#DC2626' : type === 'high' ? '#F59E0B' : '#E2EAF4'}`,
  }),
  acHead: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' },
  sev: (type) => ({
    fontSize: '10px',
    fontWeight: 700,
    borderRadius: '5px',
    padding: '3px 8px',
    whiteSpace: 'nowrap',
    background: type === 'crit' ? '#FEF2F2' : '#FFFBEB',
    color: type === 'crit' ? '#DC2626' : '#D97706',
  }),
  acTitle: { fontSize: '14px', fontWeight: 700, color: '#0F1D2E', flex: 1 },
  acTime: { fontSize: '11px', color: '#B0BCCF', fontFamily: "'JetBrains Mono', monospace" },
  acCorr: {
    fontSize: '12px',
    color: '#6B7A99',
    marginBottom: '10px',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontWeight: 500,
  },
  sigs: { display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '12px' },
  sig: {
    fontSize: '11px',
    background: '#F7F9FC',
    border: '1px solid #E2EAF4',
    borderRadius: '20px',
    padding: '4px 10px',
    color: '#374151',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
  },
  pbBox: {
    background: '#F7F9FC',
    borderRadius: '10px',
    padding: '10px 12px',
    marginBottom: '12px',
    border: '1px solid #EDF1F7',
  },
  pbHead: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' },
  pbTitle: { fontSize: '11px', fontWeight: 700, color: '#374151', textTransform: 'uppercase', letterSpacing: '0.06em' },
  modeA: {
    fontSize: '10px',
    padding: '2px 8px',
    borderRadius: '20px',
    fontWeight: 700,
    background: '#F0FDF4',
    color: '#16A34A',
    border: '1px solid #BBF7D0',
  },
  modeC: {
    fontSize: '10px',
    padding: '2px 8px',
    borderRadius: '20px',
    fontWeight: 700,
    background: '#FFFBEB',
    color: '#D97706',
    border: '1px solid #FDE68A',
  },
  pbStep: {
    display: 'flex',
    alignItems: 'center',
    gap: '9px',
    padding: '5px 0',
    borderBottom: '1px solid #EDF1F7',
  },
  stepDot: (type) => ({
    width: '22px',
    height: '22px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '11px',
    flexShrink: 0,
    background: type === 'done' ? '#F0FDF4' : type === 'run' ? '#EBF3FF' : '#FFFBEB',
    color: type === 'done' ? '#16A34A' : type === 'run' ? '#185FA5' : '#D97706',
    border: `1.5px solid ${type === 'done' ? '#BBF7D0' : type === 'run' ? '#C5D9F2' : '#FDE68A'}`,
  }),
  pbMeta: {
    fontSize: '10px',
    color: '#8896B0',
    fontFamily: "'JetBrains Mono', monospace",
    background: '#EDF1F7',
    borderRadius: '4px',
    padding: '1px 6px',
  },
  acActions: { display: 'flex', gap: '7px' },
  ab: (primary) => ({
    fontSize: '12px',
    padding: '7px 14px',
    border: primary ? '1px solid #185FA5' : '1px solid #E2EAF4',
    borderRadius: '8px',
    background: primary ? 'linear-gradient(135deg, #185FA5, #1474C4)' : '#fff',
    color: primary ? '#fff' : '#374151',
    cursor: 'pointer',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    boxShadow: primary ? '0 2px 8px rgba(24,95,165,0.2)' : 'none',
  }),
}

export default function Alertes({ onNav }) {
  return (
    <div style={s.body}>
      {/* Alert 1: CRITICAL coordinated attack */}
      <div style={s.acard('crit')}>
        <div style={s.acHead}>
          <span style={s.sev('crit')}>CRITICAL</span>
          <span style={s.acTitle}>Attaque coordonnée — 3 signaux corrélés</span>
          <span style={s.acTime}>06:14:37</span>
        </div>
        <p style={s.acCorr}>
          <i className="ti ti-git-merge" style={{ color: '#185FA5' }} />
          Corrélée automatiquement en 4 secondes à partir de 3 événements distincts
        </p>
        <div style={s.sigs}>
          <span style={s.sig}><i className="ti ti-world" style={{ fontSize: '12px', color: '#185FA5' }} /> Intrusion classifiée — IP Douala</span>
          <span style={s.sig}><i className="ti ti-upload" style={{ fontSize: '12px', color: '#DC2626' }} /> Exfiltration serveurs Pentagone</span>
          <span style={s.sig}><i className="ti ti-user-exclamation" style={{ fontSize: '12px', color: '#D97706' }} /> Compte dormant activé (interne)</span>
        </div>
        <div style={s.pbBox}>
          <div style={s.pbHead}>
            <span style={s.pbTitle}>Playbook SOAR — Blocage compromission</span>
            <span style={s.modeA}>AUTO</span>
          </div>
          <div style={{ ...s.pbStep }}>
            <div style={s.stepDot('done')}><i className="ti ti-check" /></div>
            <span style={{ fontSize: '12px', color: '#374151', flex: 1, fontWeight: 500 }}>Compte CTU-SVC-003 désactivé (Active Directory)</span>
            <span style={s.pbMeta}>3s</span>
          </div>
          <div style={{ ...s.pbStep }}>
            <div style={s.stepDot('done')}><i className="ti ti-check" /></div>
            <span style={{ fontSize: '12px', color: '#374151', flex: 1, fontWeight: 500 }}>IP 178.43.12.87 bloquée sur pare-feu Cisco</span>
            <span style={s.pbMeta}>7s</span>
          </div>
          <div style={{ ...s.pbStep, borderBottom: 'none' }}>
            <div style={s.stepDot('run')}><i className="ti ti-loader" /></div>
            <span style={{ fontSize: '12px', color: '#374151', flex: 1, fontWeight: 500 }}>Notification Jack Bauer — SMS + webhook Teams</span>
            <span style={s.pbMeta}>en cours</span>
          </div>
        </div>
        <div style={s.acActions}>
          <button style={s.ab(true)}><i className="ti ti-search" style={{ fontSize: '13px' }} /> Investiguer</button>
          <button style={s.ab(false)}>Acquitter</button>
          <button style={s.ab(false)}>Voir le détail</button>
        </div>
      </div>

      {/* Alert 2: HIGH - UEBA Nina Myers */}
      <div style={s.acard('high')}>
        <div style={s.acHead}>
          <span style={s.sev('high')}>HIGH</span>
          <span style={s.acTitle}>Comportement anormal — Nina Myers</span>
          <span style={s.acTime}>03:05:11</span>
        </div>
        <p style={s.acCorr}>
          <i className="ti ti-chart-radar" style={{ color: '#8B5CF6' }} />
          Détectée par le moteur UEBA — score de risque 94 / 100
        </p>
        <div style={s.sigs}>
          <span style={s.sig}><i className="ti ti-clock" style={{ fontSize: '12px', color: '#D97706' }} /> Connexion à 2h47 (jamais avant 7h30)</span>
          <span style={s.sig}><i className="ti ti-download" style={{ fontSize: '12px', color: '#DC2626' }} /> 840 fichiers en 12 min</span>
          <span style={s.sig}><i className="ti ti-lock" style={{ fontSize: '12px', color: '#DC2626' }} /> Accès partition chiffrée hors périmètre</span>
        </div>
        <div style={s.pbBox}>
          <div style={s.pbHead}>
            <span style={s.pbTitle}>Playbook SOAR — Confirmation requise</span>
            <span style={s.modeC}>CONFIRM</span>
          </div>
          <div style={{ ...s.pbStep, borderBottom: 'none' }}>
            <div style={s.stepDot('pend')}><i className="ti ti-clock" /></div>
            <span style={{ fontSize: '12px', color: '#374151', flex: 1, fontWeight: 500 }}>Isolation badge + compte — délai 60s avant action automatique</span>
            <span style={s.pbMeta}>en attente</span>
          </div>
        </div>
        <div style={s.acActions}>
          <button style={s.ab(true)} onClick={() => onNav('ueba')}>
            <i className="ti ti-chart-radar" style={{ fontSize: '13px' }} /> Voir profil UEBA
          </button>
          <button style={{ ...s.ab(false), background: '#FEF2F2', color: '#DC2626', border: '1px solid #FECACA' }}>Confirmer l'action</button>
          <button style={s.ab(false)}>Annuler</button>
        </div>
      </div>

      {/* Alert 3: HIGH - SSH brute force */}
      <div style={s.acard('high')}>
        <div style={s.acHead}>
          <span style={s.sev('high')}>HIGH</span>
          <span style={s.acTitle}>Brute-force SSH abouti — WIN-DC-01</span>
          <span style={s.acTime}>06:12:04</span>
        </div>
        <p style={s.acCorr}>
          <i className="ti ti-shield-x" style={{ color: '#DC2626' }} />
          MITRE T1110 — 5 échecs puis authentification réussie depuis IP externe
        </p>
        <div style={s.acActions}>
          <button style={s.ab(true)}><i className="ti ti-search" style={{ fontSize: '13px' }} /> Investiguer</button>
          <button style={s.ab(false)}>Acquitter</button>
        </div>
      </div>
    </div>
  )
}

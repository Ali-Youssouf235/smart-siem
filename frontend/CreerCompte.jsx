import React, { useState } from 'react'

const s = {
  body: {
    background: '#F0F4F9',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    fontFamily: "'Inter', sans-serif",
  },
  topBanner: {
    width: '100%',
    maxWidth: '480px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '1.25rem',
  },
  ucacLabel: { fontSize: '11px', fontWeight: 600, color: '#185FA5', letterSpacing: '0.08em', textTransform: 'uppercase' },
  versionTag: { fontSize: '10px', background: '#E8F1FC', color: '#185FA5', borderRadius: '20px', padding: '3px 10px', fontWeight: 500, border: '1px solid #C5D9F2' },
  card: {
    background: '#fff',
    borderRadius: '16px',
    padding: '2.25rem 2.5rem 2rem',
    width: '480px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.04), 0 12px 40px rgba(24,95,165,0.08)',
    border: '1px solid #E2EAF4',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
    marginBottom: '1.75rem',
    paddingBottom: '1.5rem',
    borderBottom: '1px solid #EDF1F7',
  },
  logoSq: {
    width: '46px',
    height: '46px',
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    borderRadius: '11px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 6px 18px rgba(24,95,165,0.22)',
    flexShrink: 0,
  },
  infoNote: {
    display: 'flex',
    gap: '10px',
    background: '#F0F6FF',
    border: '1px solid #C5D9F2',
    borderRadius: '10px',
    padding: '10px 12px',
    fontSize: '12px',
    color: '#3A5A8A',
    marginBottom: '1.5rem',
    lineHeight: 1.6,
  },
  sectionTitle: {
    fontSize: '11px',
    fontWeight: 600,
    color: '#8896B0',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginBottom: '10px',
  },
  inpGroup: { marginBottom: '1.1rem' },
  inpLabel: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#374151',
    marginBottom: '6px',
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
  },
  inp: {
    width: '100%',
    background: '#F7F9FC',
    border: '1.5px solid #DDE5F0',
    borderRadius: '9px',
    padding: '11px 14px',
    fontSize: '14px',
    color: '#1A2535',
    fontFamily: "'Inter', sans-serif",
    outline: 'none',
  },
  roleGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '1.5rem' },
  roleCard: (active) => ({
    border: `1.5px solid ${active ? '#185FA5' : '#E2EAF4'}`,
    borderRadius: '10px',
    padding: '11px 6px',
    textAlign: 'center',
    cursor: 'pointer',
    background: active ? 'linear-gradient(135deg, #EBF3FF, #F5F9FF)' : '#FAFBFD',
    boxShadow: active ? '0 2px 10px rgba(24,95,165,0.1)' : 'none',
  }),
  roleIcon: (active) => ({ fontSize: '20px', color: active ? '#185FA5' : '#A0AEBF', marginBottom: '4px' }),
  roleName: (active) => ({ fontSize: '12px', fontWeight: 600, color: active ? '#0D4A8A' : '#4A5A72' }),
  roleDesc: { fontSize: '10px', color: '#A0AEBF', marginTop: '2px' },
  dividerLabel: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1.1rem' },
  divLine: { flex: 1, height: '1px', background: '#EDF1F7' },
  divTxt: { fontSize: '11px', color: '#B0BCCF', fontWeight: 500 },
  strengthRow: { display: 'flex', gap: '4px', margin: '6px 0 4px' },
  sbar: (filled, warn) => ({
    flex: 1,
    height: '4px',
    borderRadius: '99px',
    background: filled ? (warn ? '#EF9F27' : '#2E9E4F') : '#E8EEF8',
  }),
  pwdHint: { fontSize: '11px', color: '#8896B0', marginBottom: '1.1rem' },
  checkRow: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '9px',
    fontSize: '12px',
    color: '#6B7A99',
    marginBottom: '1.5rem',
    lineHeight: 1.6,
  },
  btnPrimary: {
    width: '100%',
    padding: '13px',
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    border: 'none',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
    boxShadow: '0 4px 16px rgba(24,95,165,0.3)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
  linkRow: { textAlign: 'center', marginTop: '1rem', fontSize: '13px', color: '#6B7A99' },
  linkA: { color: '#185FA5', cursor: 'pointer', fontWeight: 600 },
}

const roles = [
  { key: 'lecteur', icon: 'ti-eye', name: 'Lecteur', desc: 'Consultation' },
  { key: 'analyste', icon: 'ti-search', name: 'Analyste', desc: 'Investigation' },
  { key: 'admin', icon: 'ti-settings', name: 'Admin', desc: 'Gestion' },
]

export default function CreerCompte({ onGoLogin }) {
  const [selectedRole, setSelectedRole] = useState('lecteur')
  const [checked, setChecked] = useState(false)

  return (
    <div style={s.body}>
      <div style={s.topBanner}>
        <span style={s.ucacLabel}>⬡ UCAC / ICAM — École d'Ingénieurs</span>
        <span style={s.versionTag}>Smart SIEM v3.0</span>
      </div>

      <div style={s.card}>
        <div style={s.header}>
          <div style={s.logoSq}>
            <i className="ti ti-user-plus" style={{ fontSize: '22px', color: '#fff' }} />
          </div>
          <div>
            <p style={{ fontSize: '18px', fontWeight: 700, color: '#0F1D2E', letterSpacing: '-0.3px' }}>Créer un compte</p>
            <p style={{ fontSize: '12px', color: '#6B7A99', marginTop: '3px' }}>Smart SIEM · Cellule Antiterroriste CTU</p>
          </div>
        </div>

        <div style={s.infoNote}>
          <i className="ti ti-info-circle" style={{ fontSize: '15px', flexShrink: 0, marginTop: '1px', color: '#185FA5' }} />
          <span>Votre compte sera soumis à validation par un administrateur avant activation (ségrégation RBAC).</span>
        </div>

        <p style={s.sectionTitle}>Informations personnelles</p>

        <div style={s.inpGroup}>
          <div style={s.inpLabel}>
            <i className="ti ti-user" style={{ fontSize: '13px', color: '#185FA5' }} />
            Nom complet
          </div>
          <input style={s.inp} type="text" placeholder="Ex : Nina Myers" />
        </div>

        <div style={s.inpGroup}>
          <div style={s.inpLabel}>
            <i className="ti ti-mail" style={{ fontSize: '13px', color: '#185FA5' }} />
            E-mail professionnel
          </div>
          <input style={s.inp} type="email" placeholder="nina.myers@ctu.gov" />
        </div>

        <p style={{ ...s.sectionTitle, marginTop: '0.5rem' }}>Rôle demandé</p>
        <div style={s.roleGrid}>
          {roles.map(r => (
            <div key={r.key} style={s.roleCard(selectedRole === r.key)} onClick={() => setSelectedRole(r.key)}>
              <div style={s.roleIcon(selectedRole === r.key)}>
                <i className={`ti ${r.icon}`} />
              </div>
              <div style={s.roleName(selectedRole === r.key)}>{r.name}</div>
              <div style={s.roleDesc}>{r.desc}</div>
            </div>
          ))}
        </div>

        <div style={s.dividerLabel}>
          <div style={s.divLine}></div>
          <span style={s.divTxt}>Sécurité du compte</span>
          <div style={s.divLine}></div>
        </div>

        <div style={s.inpGroup}>
          <div style={s.inpLabel}>
            <i className="ti ti-lock" style={{ fontSize: '13px', color: '#185FA5' }} />
            Mot de passe
          </div>
          <input style={{ ...s.inp, marginBottom: 0 }} type="password" placeholder="Minimum 12 caractères" />
          <div style={s.strengthRow}>
            <div style={s.sbar(true, false)}></div>
            <div style={s.sbar(true, false)}></div>
            <div style={s.sbar(true, true)}></div>
            <div style={s.sbar(false, false)}></div>
          </div>
          <p style={s.pwdHint}>Force : Moyenne — ajoutez un symbole pour améliorer</p>
        </div>

        <div style={s.inpGroup}>
          <div style={s.inpLabel}>
            <i className="ti ti-lock-check" style={{ fontSize: '13px', color: '#185FA5' }} />
            Confirmer le mot de passe
          </div>
          <input style={s.inp} type="password" placeholder="••••••••••••" />
        </div>

        <div style={s.checkRow}>
          <input
            type="checkbox"
            checked={checked}
            onChange={e => setChecked(e.target.checked)}
            style={{ marginTop: '3px', flexShrink: 0, accentColor: '#185FA5' }}
          />
          <span>J'accepte la <strong>charte d'utilisation du SIEM CTU</strong> et la politique de protection des données.</span>
        </div>

        <button style={s.btnPrimary}>
          <i className="ti ti-user-check" style={{ fontSize: '17px' }} />
          Soumettre la demande
        </button>

        <div style={s.linkRow}>
          Déjà un compte ?{' '}
          <span style={s.linkA} onClick={onGoLogin}>Se connecter</span>
        </div>
      </div>
    </div>
  )
}

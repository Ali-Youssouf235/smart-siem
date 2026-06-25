import React, { useState } from 'react'

const styles = {
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
    maxWidth: '460px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '1.25rem',
  },
  ucacLabel: {
    fontSize: '11px',
    fontWeight: 600,
    color: '#185FA5',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
  versionTag: {
    fontSize: '10px',
    background: '#E8F1FC',
    color: '#185FA5',
    borderRadius: '20px',
    padding: '3px 10px',
    fontWeight: 500,
    border: '1px solid #C5D9F2',
  },
  card: {
    background: '#FFFFFF',
    borderRadius: '16px',
    padding: '2.5rem 2.5rem 2rem',
    width: '460px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.04), 0 12px 40px rgba(24,95,165,0.08)',
    border: '1px solid #E2EAF4',
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem',
  },
  logoCircle: {
    width: '56px',
    height: '56px',
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    borderRadius: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 1rem',
    boxShadow: '0 8px 24px rgba(24,95,165,0.25)',
  },
  title: {
    fontSize: '20px',
    fontWeight: 700,
    color: '#0F1D2E',
    letterSpacing: '-0.4px',
  },
  subtitle: {
    fontSize: '13px',
    color: '#6B7A99',
    marginTop: '4px',
  },
  tlsPill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '5px',
    background: '#F0FBF0',
    border: '1px solid #C3E6C3',
    color: '#2E7D32',
    borderRadius: '20px',
    fontSize: '11px',
    padding: '4px 12px',
    fontWeight: 500,
    marginTop: '10px',
  },
  dotGreen: {
    width: '6px',
    height: '6px',
    background: '#4CAF50',
    borderRadius: '50%',
  },
  sectionTitle: {
    fontSize: '11px',
    fontWeight: 600,
    color: '#8896B0',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginBottom: '10px',
  },
  roleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '8px',
    marginBottom: '1.75rem',
  },
  roleCard: (active) => ({
    border: `1.5px solid ${active ? '#185FA5' : '#E2EAF4'}`,
    borderRadius: '10px',
    padding: '12px 8px',
    textAlign: 'center',
    cursor: 'pointer',
    background: active ? 'linear-gradient(135deg, #EBF3FF, #F5F9FF)' : '#FAFBFD',
    boxShadow: active ? '0 2px 12px rgba(24,95,165,0.12)' : 'none',
    transition: 'all 0.15s',
  }),
  roleIcon: (active) => ({
    fontSize: '22px',
    color: active ? '#185FA5' : '#A0AEBF',
    marginBottom: '6px',
  }),
  roleName: (active) => ({
    fontSize: '12px',
    fontWeight: 600,
    color: active ? '#0D4A8A' : '#4A5A72',
  }),
  roleDesc: (active) => ({
    fontSize: '10px',
    color: active ? '#5A87C5' : '#A0AEBF',
    marginTop: '2px',
  }),
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
  inpFooter: { display: 'flex', justifyContent: 'flex-end', marginTop: '5px' },
  forgot: { fontSize: '12px', color: '#185FA5', cursor: 'pointer', fontWeight: 500 },
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
    letterSpacing: '0.01em',
    boxShadow: '0 4px 16px rgba(24,95,165,0.3)',
    marginTop: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    margin: '1.25rem 0 1rem',
  },
  divLine: { flex: 1, height: '1px', background: '#EDF1F7' },
  divTxt: { fontSize: '11px', color: '#B0BCCF', fontWeight: 500 },
  linkRow: { textAlign: 'center', fontSize: '13px', color: '#6B7A99' },
  linkA: { color: '#185FA5', cursor: 'pointer', fontWeight: 600 },
  footerBar: {
    marginTop: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    fontSize: '11px',
    color: '#A0AEBF',
  },
}

const roles = [
  { key: 'lecteur', icon: 'ti-eye', name: 'Lecteur', desc: 'Consultation' },
  { key: 'analyste', icon: 'ti-search', name: 'Analyste', desc: 'Investigation' },
  { key: 'admin', icon: 'ti-settings', name: 'Admin', desc: 'Gestion' },
]

export default function Connexion({ onLogin, onGoCreate }) {
  const [selectedRole, setSelectedRole] = useState('analyste')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = () => {
    onLogin()
  }

  return (
    <div style={styles.body}>
      <div style={styles.topBanner}>
        <span style={styles.ucacLabel}>⬡ UCAC / ICAM — École d'Ingénieurs</span>
        <span style={styles.versionTag}>Smart SIEM v3.0</span>
      </div>

      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.logoCircle}>
            <i className="ti ti-shield-lock" style={{ fontSize: '24px', color: '#fff' }} />
          </div>
          <p style={styles.title}>Connexion au Smart SIEM</p>
          <p style={styles.subtitle}>Cellule Antiterroriste CTU — Accès restreint</p>
          <div style={styles.tlsPill}>
            <span style={styles.dotGreen}></span>
            Connexion sécurisée · TLS 1.3
          </div>
        </div>

        <p style={styles.sectionTitle}>Profil d'accès (RBAC)</p>
        <div style={styles.roleGrid}>
          {roles.map(r => (
            <div key={r.key} style={styles.roleCard(selectedRole === r.key)} onClick={() => setSelectedRole(r.key)}>
              <div style={styles.roleIcon(selectedRole === r.key)}>
                <i className={`ti ${r.icon}`} />
              </div>
              <div style={styles.roleName(selectedRole === r.key)}>{r.name}</div>
              <div style={styles.roleDesc(selectedRole === r.key)}>{r.desc}</div>
            </div>
          ))}
        </div>

        <div style={styles.inpGroup}>
          <div style={styles.inpLabel}>
            <i className="ti ti-user" style={{ fontSize: '13px', color: '#185FA5' }} />
            Identifiant
          </div>
          <input
            style={styles.inp}
            type="text"
            placeholder="chloe.obrian@ctu.gov"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </div>

        <div style={styles.inpGroup}>
          <div style={styles.inpLabel}>
            <i className="ti ti-lock" style={{ fontSize: '13px', color: '#185FA5' }} />
            Mot de passe
          </div>
          <input
            style={styles.inp}
            type="password"
            placeholder="••••••••••••"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
          <div style={styles.inpFooter}>
            <span style={styles.forgot}>Mot de passe oublié ?</span>
          </div>
        </div>

        <button style={styles.btnPrimary} onClick={handleSubmit}>
          <i className="ti ti-login" style={{ fontSize: '17px' }} />
          Se connecter
        </button>

        <div style={styles.divider}>
          <div style={styles.divLine}></div>
          <span style={styles.divTxt}>ou</span>
          <div style={styles.divLine}></div>
        </div>

        <div style={styles.linkRow}>
          Pas encore de compte ?{' '}
          <span style={styles.linkA} onClick={onGoCreate}>Créer un accès</span>
        </div>
      </div>

      <div style={styles.footerBar}>
        <i className="ti ti-lock" style={{ fontSize: '12px' }} />
        Smart SIEM · UCAC/ICAM · Projet CTU 2026
      </div>
    </div>
  )
}

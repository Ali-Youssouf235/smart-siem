import { useState } from 'react'
import { colors, roleConfig } from '../theme'
import { authApi } from '../api'

export default function Connexion({ onLogin, onSwitchToCreate }) {
  const [selectedRole, setSelectedRole] = useState('analyste')
  const [identifiant, setIdentifiant] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const roles = ['lecteur', 'analyste', 'admin']

  const handleSubmit = async (e) => {
  e.preventDefault()
  setError('')
  
  if (!identifiant || !password) {
    setError('Veuillez remplir tous les champs')
    return
  }
  
  setLoading(true)
  try {
    // Appel à ton FastAPI Swagger POST /auth/login
    const data = await authApi.login(identifiant, password)
    
    // On transmet les infos reçues du backend à App.jsx
    onLogin({
      name: data.username || identifiant.split('@')[0],
      email: identifiant,
      role: data.role || selectedRole, // Priorité au rôle retourné par la base
    })
  } catch (err) {
    console.error(err)
    setError(err.response?.data?.detail || "Échec d'authentification. Vérifiez vos identifiants.")
  } finally {
    setLoading(false)
  }
}

  return (
    <div style={styles.page}>
      <div style={styles.topBanner}>
        <span style={styles.ucacLabel}>⬡ UCAC / ICAM — École d'Ingénieurs</span>
        <span style={styles.versionTag}>Smart SIEM v3.0</span>
      </div>

      <div className="auth-card" style={styles.card}>
        <div style={styles.header}>
          <div style={styles.logoCircle}>
            <i className="ti ti-shield-lock" style={{ fontSize: 24, color: '#fff' }} />
          </div>
          <p style={styles.title}>Connexion au Smart SIEM</p>
          <p style={styles.subtitle}>Cellule Antiterroriste CTU — Accès restreint</p>
          <div style={styles.tlsPill}>
            <span className="live-dot" style={styles.dotGreen} />
            Connexion sécurisée · TLS 1.3
          </div>
        </div>

        <p style={styles.sectionTitle}>Profil d'accès (RBAC)</p>
        <div className="role-grid-3" style={styles.roleGrid}>
          {roles.map((role) => (
            <div
              key={role}
              onClick={() => setSelectedRole(role)}
              style={{
                ...styles.roleCard,
                ...(selectedRole === role ? styles.roleCardOn : {}),
              }}
            >
              <div style={styles.roleIcon}>
                <i className={`ti ${roleConfig[role].icon}`} style={{ fontSize: 22, color: selectedRole === role ? colors.primary : '#A0AEBF' }} />
              </div>
              <div style={{ ...styles.roleName, ...(selectedRole === role ? styles.roleNameOn : {}) }}>
                {roleConfig[role].label}
              </div>
              <div style={{ ...styles.roleDesc, ...(selectedRole === role ? styles.roleDescOn : {}) }}>
                {roleConfig[role].desc}
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div style={styles.error}>{error}</div>}

          <div style={styles.inpGroup}>
            <label style={styles.inpLabel}>
              <i className="ti ti-user" style={{ fontSize: 13, color: colors.primary }} />
              Identifiant
            </label>
            <input
              type="text"
              value={identifiant}
              onChange={(e) => setIdentifiant(e.target.value)}
              placeholder="chloe.obrian@ctu.gov"
              style={styles.inp}
            />
          </div>

          <div style={styles.inpGroup}>
            <label style={styles.inpLabel}>
              <i className="ti ti-lock" style={{ fontSize: 13, color: colors.primary }} />
              Mot de passe
            </label>
            <div style={styles.pwdWrapper}>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                style={{ ...styles.inp, paddingRight: 42 }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={styles.togglePwd}
              >
                <i className={`ti ${showPassword ? 'ti-eye-off' : 'ti-eye'}`} style={{ fontSize: 16, color: colors.textFaint }} />
              </button>
            </div>
            <div style={styles.inpFooter}>
              <span style={styles.forgot}>Mot de passe oublié ?</span>
            </div>
          </div>

          <button type="submit" style={{ ...styles.btnPrimary, opacity: loading ? 0.7 : 1 }} disabled={loading}>
            <i className="ti ti-login" style={{ fontSize: 17 }} />
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div style={styles.divider}>
          <div style={styles.divLine} />
          <span style={styles.divTxt}>ou</span>
          <div style={styles.divLine} />
        </div>

        <div style={styles.linkRow}>
          Pas encore de compte ? <a onClick={onSwitchToCreate} style={styles.link}>Créer un accès</a>
        </div>
      </div>

      <div style={styles.footerBar}>
        <i className="ti ti-lock" style={{ fontSize: 12 }} />
        Smart SIEM · UCAC/ICAM · Projet CTU 2026
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
  },
  topBanner: {
    width: '100%',
    maxWidth: 460,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '1.25rem',
  },
  ucacLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: colors.primary,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
  versionTag: {
    fontSize: 10,
    background: '#E8F1FC',
    color: colors.primary,
    borderRadius: 20,
    padding: '3px 10px',
    fontWeight: 500,
    border: `1px solid ${colors.primaryBorder}`,
  },
  card: {
    background: '#fff',
    borderRadius: 16,
    padding: '2.5rem 2.5rem 2rem',
    width: 460,
    boxShadow: '0 4px 6px rgba(0,0,0,0.04), 0 12px 40px rgba(24,95,165,0.08)',
    border: `1px solid ${colors.border}`,
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem',
  },
  logoCircle: {
    width: 56,
    height: 56,
    background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryLight})`,
    borderRadius: 14,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 1rem',
    boxShadow: '0 8px 24px rgba(24,95,165,0.25)',
  },
  title: {
    fontSize: 20,
    fontWeight: 700,
    color: colors.text,
    letterSpacing: '-0.4px',
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 4,
  },
  tlsPill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 5,
    background: '#F0FBF0',
    border: '1px solid #C3E6C3',
    color: '#2E7D32',
    borderRadius: 20,
    fontSize: 11,
    padding: '4px 12px',
    fontWeight: 500,
    marginTop: 10,
  },
  dotGreen: {
    width: 6,
    height: 6,
    background: '#4CAF50',
    borderRadius: '50%',
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: 600,
    color: colors.textFaint,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginBottom: 10,
  },
  roleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 8,
    marginBottom: '1.75rem',
  },
  roleCard: {
    border: `1.5px solid ${colors.border}`,
    borderRadius: 10,
    padding: '12px 8px',
    textAlign: 'center',
    cursor: 'pointer',
    background: '#FAFBFD',
    transition: 'all 0.15s',
  },
  roleCardOn: {
    borderColor: colors.primary,
    background: 'linear-gradient(135deg, #EBF3FF, #F5F9FF)',
    boxShadow: '0 2px 12px rgba(24,95,165,0.12)',
  },
  roleIcon: {
    marginBottom: 6,
  },
  roleName: {
    fontSize: 12,
    fontWeight: 600,
    color: '#4A5A72',
  },
  roleNameOn: {
    color: '#0D4A8A',
  },
  roleDesc: {
    fontSize: 10,
    color: '#A0AEBF',
    marginTop: 2,
  },
  roleDescOn: {
    color: '#5A87C5',
  },
  inpGroup: {
    marginBottom: '1.1rem',
  },
  inpLabel: {
    fontSize: 12,
    fontWeight: 600,
    color: colors.textBody,
    marginBottom: 6,
    display: 'flex',
    alignItems: 'center',
    gap: 5,
  },
  inp: {
    width: '100%',
    background: colors.neutralBg,
    border: `1.5px solid ${colors.neutralBorder}`,
    borderRadius: 9,
    padding: '11px 14px',
    fontSize: 14,
    color: colors.text,
    outline: 'none',
    transition: 'all 0.15s',
  },
  pwdWrapper: {
    position: 'relative',
  },
  togglePwd: {
    position: 'absolute',
    right: 12,
    top: '50%',
    transform: 'translateY(-50%)',
    background: 'none',
    border: 'none',
    padding: 4,
    display: 'flex',
    alignItems: 'center',
  },
  inpFooter: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginTop: 5,
  },
  forgot: {
    fontSize: 12,
    color: colors.primary,
    cursor: 'pointer',
    fontWeight: 500,
  },
  btnPrimary: {
    width: '100%',
    padding: 13,
    background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryLight})`,
    border: 'none',
    borderRadius: 10,
    color: '#fff',
    fontSize: 15,
    fontWeight: 600,
    boxShadow: '0 4px 16px rgba(24,95,165,0.3)',
    marginTop: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    transition: 'opacity 0.15s',
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    margin: '1.25rem 0 1rem',
  },
  divLine: {
    flex: 1,
    height: 1,
    background: colors.borderLight,
  },
  divTxt: {
    fontSize: 11,
    color: colors.textLight,
    fontWeight: 500,
  },
  linkRow: {
    textAlign: 'center',
    fontSize: 13,
    color: colors.textMuted,
  },
  link: {
    color: colors.primary,
    cursor: 'pointer',
    fontWeight: 600,
  },
  footerBar: {
    marginTop: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    fontSize: 11,
    color: '#A0AEBF',
  },
  error: {
    padding: '10px 12px',
    background: colors.criticalBg,
    border: `1px solid ${colors.criticalBorder}`,
    borderRadius: 8,
    color: colors.critical,
    fontSize: 13,
    marginBottom: '1rem',
  },
}

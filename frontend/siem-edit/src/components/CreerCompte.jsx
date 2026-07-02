import { useState } from 'react'
import { colors, roleConfig } from '../theme'

export default function CreerCompte({ onCreate, onSwitchToLogin, adminMode = false }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    password: '',
    confirmPassword: '',
  })
  const [selectedRole, setSelectedRole] = useState('lecteur')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const roles = ['lecteur', 'analyste', 'admin']

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value })
    setError('')
  }

  const passwordStrength = () => {
    const p = formData.password
    if (!p) return { score: 0, label: '', color: '#E2EAF4' }
    let score = 0
    if (p.length >= 6) score++
    if (p.length >= 10) score++
    if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
    if (/[0-9]/.test(p)) score++
    if (/[^A-Za-z0-9]/.test(p)) score++
    const config = [
      { label: 'Très faible', color: colors.critical },
      { label: 'Faible', color: colors.critical },
      { label: 'Moyen', color: colors.high },
      { label: 'Bon', color: colors.warning },
      { label: 'Fort', color: colors.success },
      { label: 'Excellent', color: colors.success },
    ]
    return { score, ...config[score] }
  }

  const strength = passwordStrength()

  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      if (!formData.name || !formData.email || !formData.password) {
        setError('Veuillez remplir tous les champs obligatoires')
        setLoading(false)
        return
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Les mots de passe ne correspondent pas')
        setLoading(false)
        return
      }
      if (formData.password.length < 6) {
        setError('Le mot de passe doit contenir au moins 6 caractères')
        setLoading(false)
        return
      }
      onCreate({
        id: `U-${Math.floor(Math.random() * 9000 + 1000)}`,
        name: formData.name,
        email: formData.email,
        company: formData.company,
        role: selectedRole,
        status: 'actif',
        lastLogin: '—',
      })
      setLoading(false)
    }, 700)
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
            <i className="ti ti-user-plus" style={{ fontSize: 24, color: '#fff' }} />
          </div>
          <p style={styles.title}>{adminMode ? 'Ajouter un utilisateur' : 'Créer un accès'}</p>
          <p style={styles.subtitle}>{adminMode ? 'Créer un nouveau compte pour la plateforme Smart SIEM' : 'Rejoignez la plateforme Smart SIEM'}</p>
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

          <div className="inp-row2" style={styles.inpRow2}>
            <div style={styles.inpGroup}>
              <label style={styles.inpLabel}>
                <i className="ti ti-user" style={{ fontSize: 13, color: colors.primary }} />
                Nom complet *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={handleChange('name')}
                placeholder="Jack Bauer"
                style={styles.inp}
                required
              />
            </div>
            <div style={styles.inpGroup}>
              <label style={styles.inpLabel}>
                <i className="ti ti-building" style={{ fontSize: 13, color: colors.primary }} />
                Organisation
              </label>
              <input
                type="text"
                value={formData.company}
                onChange={handleChange('company')}
                placeholder="CTU / UCAC-ICAM"
                style={styles.inp}
              />
            </div>
          </div>

          <div style={styles.inpGroup}>
            <label style={styles.inpLabel}>
              <i className="ti ti-mail" style={{ fontSize: 13, color: colors.primary }} />
              Adresse email *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              placeholder="jack.bauer@ctu.gov"
              style={styles.inp}
              required
            />
          </div>

          <div className="inp-row2" style={styles.inpRow2}>
            <div style={styles.inpGroup}>
              <label style={styles.inpLabel}>
                <i className="ti ti-lock" style={{ fontSize: 13, color: colors.primary }} />
                Mot de passe *
              </label>
              <div style={styles.pwdWrapper}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange('password')}
                  placeholder="Min. 6 caractères"
                  style={{ ...styles.inp, paddingRight: 42 }}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={styles.togglePwd}
                >
                  <i className={`ti ${showPassword ? 'ti-eye-off' : 'ti-eye'}`} style={{ fontSize: 16, color: colors.textFaint }} />
                </button>
              </div>
              {formData.password && (
                <div style={styles.strengthBar}>
                  <div style={{ ...styles.strengthFill, width: `${(strength.score / 5) * 100}%`, background: strength.color }} />
                  <span style={{ ...styles.strengthLabel, color: strength.color }}>{strength.label}</span>
                </div>
              )}
            </div>
            <div style={styles.inpGroup}>
              <label style={styles.inpLabel}>
                <i className="ti ti-lock-check" style={{ fontSize: 13, color: colors.primary }} />
                Confirmer *
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange('confirmPassword')}
                placeholder="Confirmer le mot de passe"
                style={styles.inp}
                required
              />
            </div>
          </div>

          <button type="submit" style={{ ...styles.btnPrimary, opacity: loading ? 0.7 : 1 }} disabled={loading}>
            <i className="ti ti-user-plus" style={{ fontSize: 17 }} />
            {loading ? 'Création...' : (adminMode ? 'Ajouter cet utilisateur' : 'Créer mon compte')}
          </button>
        </form>

        <div style={styles.divider}>
          <div style={styles.divLine} />
          <span style={styles.divTxt}>ou</span>
          <div style={styles.divLine} />
        </div>

        <div style={styles.linkRow}>
          {adminMode ? (
            <a onClick={onSwitchToLogin} style={styles.link}>← Annuler et retourner à Administration</a>
          ) : (
            <>Déjà un compte ? <a onClick={onSwitchToLogin} style={styles.link}>Se connecter</a></>
          )}
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
    maxWidth: 480,
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
    width: 480,
    boxShadow: '0 4px 6px rgba(0,0,0,0.04), 0 12px 40px rgba(24,95,165,0.08)',
    border: `1px solid ${colors.border}`,
  },
  header: {
    textAlign: 'center',
    marginBottom: '1.75rem',
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
    marginBottom: '1.5rem',
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
  inpRow2: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
  },
  inpGroup: {
    marginBottom: '1rem',
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
  strengthBar: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginTop: 6,
  },
  strengthFill: {
    height: 4,
    borderRadius: 2,
    transition: 'all 0.2s',
  },
  strengthLabel: {
    fontSize: 11,
    fontWeight: 600,
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

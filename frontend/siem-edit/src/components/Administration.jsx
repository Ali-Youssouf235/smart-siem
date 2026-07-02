import { useState, useEffect } from 'react'
import { colors, roleConfig } from '../theme'
import { authApi } from '../api' // Raccordement avec le contrôleur d'utilisateurs / gestion des comptes

export default function Administration({ user }) {
  const [analysts, setAnalysts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // États pour le formulaire d'ajout d'un nouvel analyste
  const [formData, setFormData] = useState({ name: '', email: '', role: 'lecteur', password: '' })
  const [submitting, setSubmitting] = useState(false)

  // 🔄 Chargement de la liste des analystes du SOC depuis le Backend
  const fetchAnalysts = async () => {
    setLoading(true)
    setError('')
    try {
      // On utilise le bon service de ton api.js !
      const data = await usersApi.list()
      // Ton api.js renvoie { total_users: X, users: [...] }, on cible donc 'data.users'
      setAnalysts(Array.isArray(data) ? data : data?.users || [])
    } catch (err) {
      console.error("Erreur de récupération des comptes:", err)
      setError("Impossible de synchroniser l'annuaire des analystes du SOC.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalysts()
  }, [])

  // ➕ Soumission du formulaire pour créer un nouvel utilisateur dans le SIEM
  const handleCreateUser = async (e) => {
    e.preventDefault()
    if (!formData.name || !formData.email || !formData.password) {
      alert("Veuillez remplir tous les champs obligatoires.")
      return
    }

    setSubmitting(true)
    try {
      // À l'intérieur de handleCreateUser, remplace 'await authApi.register(formData)' par :
  await usersApi.create(formData)
  
      // Réinitialiser le formulaire après succès
      setFormData({ name: '', email: '', role: 'lecteur', password: '' })
      
      // Rafraîchir instantanément le tableau des comptes
      fetchAnalysts()
      alert("Compte analyste créé avec succès sur le cluster !")
    } catch (err) {
      console.error("Erreur d'inscription:", err)
      alert("Erreur lors de la création du compte. Vérifiez si l'email n'est pas déjà pris.")
    } finally {
      setSubmitting(false)
    }
  }

  // Permet de modifier dynamiquement les champs du formulaire
  const handleInputChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value })
  }

  return (
    <div style={styles.container}>
      <div>
        <h1 style={styles.title}>Administration & Contrôle d'Accès</h1>
        <p style={styles.subtitle}>Gérez les habilitations de l'équipe SOC et auditez les privilèges d'accès (RBAC)</p>
      </div>

      <div style={styles.layoutGrid}>
        {/* Panneau de Gauche : Liste des comptes actifs */}
        <div style={styles.mainCard}>
          <h3 style={styles.sectionTitle}>Comptes Analystes Enregistrés</h3>
          
          {loading ? (
            <div style={styles.stateContainer}>
              <i className="ti ti-loader animate-spin" style={{ color: colors.primary }} />
              <p style={{ fontSize: 13, color: colors.textMuted, marginTop: 8 }}>Lecture de la table des utilisateurs...</p>
            </div>
          ) : error ? (
            <div style={styles.stateContainer}>
              <i className="ti ti-alert-triangle" style={{ color: colors.critical, fontSize: 24 }} />
              <p style={{ fontSize: 13, color: colors.critical, fontWeight: 600, marginTop: 8 }}>{error}</p>
            </div>
          ) : (
            <div style={styles.tableWrapper}>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.thRow}>
                    <th style={styles.th}>Analyste</th>
                    <th style={styles.th}>Privilège (RBAC)</th>
                    <th style={styles.th}>Statut</th>
                    <th style={styles.th}>Dernière session</th>
                  </tr>
                </thead>
                <tbody>
                  {analysts.map((analyst) => {
                    const cfg = roleConfig[analyst.role] || roleConfig.lecteur
                    const isActive = analyst.status !== 'suspendu'

                    return (
                      <tr key={analyst.id || analyst.email} style={styles.tr}>
                        <td style={styles.td}>
                          <div style={styles.userCell}>
                            <div style={styles.avatar}>{analyst.name.charAt(0)}</div>
                            <div style={styles.userMeta}>
                              <span style={styles.userName}>{analyst.name}</span>
                              <span style={styles.userEmail}>{analyst.email}</span>
                            </div>
                          </div>
                        </td>
                        <td style={styles.td}>
                          <span style={{ ...styles.roleBadge, background: cfg.bg, color: cfg.color }}>
                            {cfg.label}
                          </span>
                        </td>
                        <td style={styles.td}>
                          <span style={{
                            ...styles.statusBadge,
                            background: isActive ? colors.successBg : colors.criticalBg,
                            color: isActive ? colors.success : colors.critical
                          }}>
                            <div style={{ ...styles.statusDot, background: isActive ? colors.success : colors.critical }} />
                            {isActive ? 'Actif' : 'Suspendu'}
                          </span>
                        </td>
                        <td style={styles.td}>
                          <span style={styles.dateTxt}>{analyst.lastLogin || 'Nouveau compte'}</span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Panneau de Droite : Formulaire d'ajout rapide (Idéal pour la démo en direct devant le jury) */}
        <div style={styles.sidebarCard}>
          <h3 style={styles.sectionTitle}>Provisionner un Analyste</h3>
          <p style={{ fontSize: 12, color: colors.textMuted, marginBottom: 12 }}>
            Ajoutez instantanément un nouvel opérateur dans l'index de sécurité.
          </p>

          <form onSubmit={handleCreateUser} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>Nom complet</label>
              <input 
                type="text" 
                placeholder="Ex: John Doe" 
                value={formData.name} 
                onChange={handleInputChange('name')}
                style={styles.input} 
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Adresse Email</label>
              <input 
                type="email" 
                placeholder="analyste@ctu.gov" 
                value={formData.email} 
                onChange={handleInputChange('email')}
                style={styles.input} 
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Mot de passe initial</label>
              <input 
                type="password" 
                placeholder="••••••••••••" 
                value={formData.password} 
                onChange={handleInputChange('password')}
                style={styles.input} 
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Rôle & Droits d'accès</label>
              <select 
                value={formData.role} 
                onChange={handleInputChange('role')}
                style={styles.select}
              >
                <option value="lecteur">Lecteur (Lecture seule)</option>
                <option value="analyste">Analyste SOC (Remédiation)</option>
                <option value="admin">Administrateur (Gestion totale)</option>
              </select>
            </div>

            <button type="submit" style={styles.submitBtn} disabled={submitting}>
              {submitting ? (
                <i className="ti ti-loader animate-spin" />
              ) : (
                <>
                  <i className="ti ti-user-plus" /> Créer l'opérateur
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: { display: 'flex', flexDirection: 'column', gap: 20 },
  title: { fontSize: 22, fontWeight: 800, color: colors.text },
  subtitle: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  layoutGrid: { display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20, flexWrap: 'wrap' },
  mainCard: { background: '#fff', borderRadius: 14, padding: 20, border: `1px solid ${colors.border}`, display: 'flex', flexDirection: 'column', gap: 16 },
  sidebarCard: { background: '#fff', borderRadius: 14, padding: 20, border: `1px solid ${colors.border}`, height: 'max-content' },
  sectionTitle: { fontSize: 15, fontWeight: 700, color: colors.text },
  stateContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 0' },
  tableWrapper: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left' },
  thRow: { borderBottom: `2px solid ${colors.borderLight}` },
  th: { padding: '10px 12px', fontSize: 11, fontWeight: 700, color: colors.textFaint, textTransform: 'uppercase', letterSpacing: '0.03em' },
  tr: { borderBottom: `1px solid ${colors.borderLight}`, transition: 'background 0.1s' },
  td: { padding: '12px', verticalAlign: 'middle' },
  userCell: { display: 'flex', alignItems: 'center', gap: 12 },
  avatar: { width: 34, height: 34, borderRadius: '50%', background: colors.primaryBg, color: colors.primary, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700 },
  userMeta: { display: 'flex', flexDirection: 'column', gap: 2 },
  userName: { fontSize: 13, fontWeight: 600, color: colors.text },
  userEmail: { fontSize: 11, color: colors.textFaint },
  roleBadge: { padding: '4px 9px', borderRadius: 6, fontSize: 11, fontWeight: 600, display: 'inline-block' },
  statusBadge: { padding: '4px 9px', borderRadius: 6, fontSize: 11, fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 6 },
  statusDot: { width: 6, height: 6, borderRadius: '50%' },
  dateTxt: { fontSize: 12, color: colors.textMuted },
  form: { display: 'flex', flexDirection: 'column', gap: 14, marginTop: 10 },
  formGroup: { display: 'flex', flexDirection: 'column', gap: 6 },
  label: { fontSize: 11, fontWeight: 700, color: colors.textMuted, textTransform: 'uppercase' },
  input: { padding: '10px 12px', borderRadius: 8, border: `1px solid ${colors.border}`, fontSize: 13, background: '#fff', color: colors.text, outline: 'none' },
  select: { padding: '10px 12px', borderRadius: 8, border: `1px solid ${colors.border}`, fontSize: 13, background: '#fff', color: colors.text, cursor: 'pointer' },
  submitBtn: { display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center', padding: '12px', background: colors.primary, border: 'none', borderRadius: 8, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', marginTop: 6 }
}
import { useState } from 'react'
import Topbar from './components/Topbar'
import Dashboard from './components/Dashboard'
import Alertes from './components/Alertes'
import Rapports from './components/Rapports'
import Recherche from './components/Recherche'
import UEBA from './components/UEBA'
import Regles from './components/Regle'
import CrisisRoom from './components/CrisisRoom'
import Administration from './components/Administration'
import Connexion from './components/Connexion'
import CreerCompte from './components/CreerCompte'
import { roleConfig, colors } from './theme'

export default function App() {
  const [currentPage, setCurrentPage] = useState('connexion')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  // Mémorise la page d'où l'on vient quand on ouvre "Créer un compte"
  // depuis une page protégée (ex: Administration), pour pouvoir y revenir après création.
  const [returnTo, setReturnTo] = useState(null)
  // Liste des comptes créés par un admin depuis Administration, transmise à Administration.
  const [createdUsers, setCreatedUsers] = useState([])

  const handleLogin = (userData) => {
    setUser(userData)
    setIsAuthenticated(true)
    setCurrentPage('dashboard')
  }

  const handleLogout = () => {
    setUser(null)
    setIsAuthenticated(false)
    setCurrentPage('connexion')
  }

  // Ouvre la page Créer un compte SANS déconnecter l'utilisateur courant
  // (utilisé par le bouton "Ajouter un utilisateur" de la page Administration).
  const handleOpenCreateUser = () => {
    setReturnTo(currentPage)
    setCurrentPage('creerCompte')
  }

  // Quand un compte est créé pendant qu'un admin est déjà connecté,
  // on n'authentifie PAS ce nouveau compte : on l'ajoute juste à la liste
  // des utilisateurs et on revient sur la page d'origine (Administration).
  const handleUserCreated = (newUser) => {
    if (isAuthenticated) {
      setCreatedUsers((prev) => [...prev, newUser])
      setCurrentPage(returnTo || 'administration')
      setReturnTo(null)
    } else {
      // Comportement d'origine : création de compte en mode "auto-inscription"
      // (personne non connectée), on connecte directement le nouvel utilisateur.
      handleLogin(newUser)
    }
  }

  // Retour à la page d'origine sans créer de compte (bouton "Annuler" / "Se connecter").
  const handleCancelCreateUser = () => {
    if (isAuthenticated) {
      setCurrentPage(returnTo || 'administration')
      setReturnTo(null)
    } else {
      setCurrentPage('connexion')
    }
  }

  const canAccess = (page) => {
    if (!user) return false
    const role = user.role
    if (page === 'creerCompte') return true // accessible depuis Administration pour tous les rôles autorisés à y naviguer
    return roleConfig[role]?.pages.includes(page) || false
  }

  const renderPage = () => {
    if (!isAuthenticated) {
      switch (currentPage) {
        case 'connexion':
          return <Connexion onLogin={handleLogin} onSwitchToCreate={() => setCurrentPage('creerCompte')} />
        case 'creerCompte':
          return <CreerCompte onCreate={handleUserCreated} onSwitchToLogin={() => setCurrentPage('connexion')} />
        default:
          return <Connexion onLogin={handleLogin} onSwitchToCreate={() => setCurrentPage('creerCompte')} />
      }
    }

    // Cas particulier : un utilisateur déjà connecté (ex: Admin) ouvre la page
    // "Créer un compte" pour ajouter quelqu'un d'autre. On l'affiche en dehors
    // du switch protégé par rôle ci-dessous, sans changer la session active.
    if (currentPage === 'creerCompte') {
      return (
        <CreerCompte
          onCreate={handleUserCreated}
          onSwitchToLogin={handleCancelCreateUser}
          adminMode={roleConfig[user.role]?.canManageUsers || false}
        />
      )
    }

    if (!canAccess(currentPage)) {
      return (
        <div style={styles.accessDenied}>
          <div style={styles.adIcon}>
            <i className="ti ti-lock-access" style={{ fontSize: 36, color: colors.critical }} />
          </div>
          <h2 style={styles.adTitle}>Accès refusé</h2>
          <p style={styles.adText}>
            Votre profil <strong>{roleConfig[user.role]?.label}</strong> n'a pas accès à cette page.
          </p>
          <button style={styles.adBtn} onClick={() => setCurrentPage('dashboard')}>
            Retour au tableau de bord
          </button>
        </div>
      )
    }

    switch (currentPage) {
      case 'dashboard':
        return <Dashboard user={user} onNavigate={setCurrentPage} />
      case 'alertes':
        return <Alertes user={user} />
      case 'rapports':
        return <Rapports user={user} />
      case 'recherche':
        return <Recherche user={user} />
      case 'ueba':
        return <UEBA user={user} />
      case 'regles':
        return <Regles user={user} />
      case 'crisis':
        return <CrisisRoom onExit={() => setCurrentPage('dashboard')} />
      case 'administration':
        return <Administration user={user} onAddUser={handleOpenCreateUser} newUsers={createdUsers} />
      default:
        return <Dashboard user={user} onNavigate={setCurrentPage} />
    }
  }

  return (
    <div style={styles.app}>
      {isAuthenticated && (
        <Topbar
          currentPage={currentPage}
          onNavigate={setCurrentPage}
          user={user}
          onLogout={handleLogout}
        />
      )}
      <main style={isAuthenticated ? styles.main : styles.authMain}>
        {renderPage()}
      </main>
    </div>
  )
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: colors.bg,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  },
  main: {
    marginTop: 52,
    padding: 24,
    minHeight: 'calc(100vh - 52px)',
  },
  authMain: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  accessDenied: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '64px 24px',
    background: '#fff',
    borderRadius: 12,
    border: `1px solid ${colors.border}`,
    gap: 14,
    textAlign: 'center',
    maxWidth: 460,
    margin: '40px auto',
  },
  adIcon: {
    width: 72,
    height: 72,
    borderRadius: 18,
    background: colors.criticalBg,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  adTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: colors.text,
  },
  adText: {
    fontSize: 14,
    color: colors.textMuted,
    lineHeight: 1.6,
  },
  adBtn: {
    padding: '10px 20px',
    background: colors.primary,
    border: 'none',
    borderRadius: 8,
    color: '#fff',
    fontSize: 14,
    fontWeight: 600,
  },
}

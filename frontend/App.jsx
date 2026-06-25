import React, { useState } from 'react'
import Connexion from './components/Connexion'
import CreerCompte from './components/CreerCompte'
import Topbar from './components/Topbar'
import Dashboard from './components/Dashboard'
import Recherche from './components/Recherche'
import Alertes from './components/Alertes'
import UEBA from './components/UEBA'
import Rapports from './components/Rapports'

export default function App() {
  const [auth, setAuth] = useState(false)
  const [authView, setAuthView] = useState('login') // 'login' | 'register'
  const [page, setPage] = useState('dashboard')

  if (!auth) {
    if (authView === 'register') {
      return <CreerCompte onGoLogin={() => setAuthView('login')} />
    }
    return (
      <Connexion
        onLogin={() => setAuth(true)}
        onGoCreate={() => setAuthView('register')}
      />
    )
  }

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard onNav={setPage} />
      case 'recherche': return <Recherche />
      case 'alertes': return <Alertes onNav={setPage} />
      case 'ueba': return <UEBA onNav={setPage} />
      case 'rapports': return <Rapports />
      default: return <Dashboard onNav={setPage} />
    }
  }

  return (
    <div>
      <Topbar page={page} onNav={setPage} onLogout={() => setAuth(false)} />
      {renderPage()}
    </div>
  )
}

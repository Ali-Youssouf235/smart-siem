import { useState, useEffect } from 'react'
import { colors, roleConfig, navItems } from '../theme'
import { alertsApi } from '../api'

export default function Topbar({ currentPage, onNavigate, user, onLogout }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  // 🟢 Compteur réel d'alertes non résolues (remplace le badge "7" codé en dur)
  const [openAlertCount, setOpenAlertCount] = useState(null)

  const visibleItems = navItems.filter(item => !item.adminOnly || user?.role === 'admin')
  const role = user?.role || 'lecteur'
  const roleCfg = roleConfig[role]

  useEffect(() => {
    let cancelled = false

    const fetchOpenAlertsCount = async () => {
      try {
        const data = await alertsApi.list({})
        const rawAlerts = Array.isArray(data) ? data : (data?.alerts || [])
        // "Non résolu" = statut backend différent de 'résolu' (voir alert_schema.py)
        const openCount = rawAlerts.filter(a => (a.statut || a.status) !== 'résolu').length
        if (!cancelled) setOpenAlertCount(openCount)
      } catch (err) {
        // Pas d'alerte affichée plutôt qu'un chiffre inventé en cas d'échec réseau
        if (!cancelled) setOpenAlertCount(null)
      }
    }

    fetchOpenAlertsCount()
    // Rafraîchit le badge toutes les 30s pour rester représentatif en continu
    const interval = setInterval(fetchOpenAlertsCount, 30000)
    return () => { cancelled = true; clearInterval(interval) }
  }, [])

  return (
    <>
      <header style={styles.topbar}>
        <div style={styles.left}>
          <button className="mobile-menu-btn" style={styles.mobileBtn} onClick={() => setMobileOpen(!mobileOpen)}>
            <i className="ti ti-menu-2" style={{ fontSize: 20 }} />
          </button>

          <div style={styles.logo}>
            <div style={styles.logoIcon}>
              <i className="ti ti-shield-lock" style={{ fontSize: 18, color: '#fff' }} />
            </div>
            <div style={styles.logoText}>
              <span style={styles.logoName}>Smart SIEM</span>
              <span style={styles.logoSub}>CTU · UCAC/ICAM</span>
            </div>
          </div>

          <nav className={`topbar-nav ${mobileOpen ? 'open' : ''}`} style={styles.nav}>
            {visibleItems.map(item => {
              const active = currentPage === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => { onNavigate(item.id); setMobileOpen(false) }}
                  style={{
                    ...styles.navItem,
                    ...(active ? styles.navItemActive : {}),
                  }}
                >
                  <i className={`ti ${item.icon}`} style={{ fontSize: 16 }} />
                  <span>{item.label}</span>
                  {item.id === 'alertes' && openAlertCount > 0 && (
                    <span style={styles.navBadge}>{openAlertCount}</span>
                  )}
                </button>
              )
            })}
          </nav>
        </div>

        <div style={styles.right}>
          <div style={styles.searchBox}>
            <i className="ti ti-search" style={{ fontSize: 14, color: colors.textFaint }} />
            <input placeholder="Rechercher..." style={styles.searchInput} onFocus={() => onNavigate('recherche')} />
            <span style={styles.searchKbd}>⌘K</span>
          </div>

          <div style={styles.iconBtns}>
            <button style={styles.iconBtn} title="Statut système">
              <span className="live-dot" style={styles.dotGreen} />
              <i className="ti ti-activity" style={{ fontSize: 18 }} />
            </button>

            <div style={{ position: 'relative' }}>
              <button style={styles.iconBtn} onClick={() => setNotifOpen(!notifOpen)}>
                <i className="ti ti-bell" style={{ fontSize: 18 }} />
                <span style={styles.notifDot} />
              </button>
              {notifOpen && (
                <>
                  <div style={styles.overlay} onClick={() => setNotifOpen(false)} />
                  <div style={styles.notifPanel}>
                    <div style={styles.notifHeader}>
                      <span style={styles.notifTitle}>Notifications</span>
                      <span style={styles.notifCount}>3 nouvelles</span>
                    </div>
                    {[
                      { icon: 'ti-alert-triangle', color: colors.critical, text: 'Alerte critique — Tentative d\'escalade', time: 'Il y a 2 min' },
                      { icon: 'ti-user-x', color: colors.high, text: 'Comportement anormal — L. Petit', time: 'Il y a 8 min' },
                      { icon: 'ti-server', color: colors.primary, text: 'Pare-feu principal — Config modifiée', time: 'Il y a 15 min' },
                    ].map((n, i) => (
                      <div key={i} style={styles.notifItem}>
                        <div style={{ ...styles.notifIcon, background: `${n.color}15` }}>
                          <i className={`ti ${n.icon}`} style={{ fontSize: 16, color: n.color }} />
                        </div>
                        <div style={styles.notifContent}>
                          <span style={styles.notifText}>{n.text}</span>
                          <span style={styles.notifTime}>{n.time}</span>
                        </div>
                      </div>
                    ))}
                    <button style={styles.notifFooter} onClick={() => { onNavigate('alertes'); setNotifOpen(false) }}>
                      Voir toutes les alertes
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>

          <div style={{ position: 'relative' }}>
            <button style={styles.userPill} onClick={() => setUserMenuOpen(!userMenuOpen)}>
              <div style={styles.avatar}>
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div style={styles.userMeta}>
                <span style={styles.userName}>{user?.name || 'Utilisateur'}</span>
                <span style={styles.userRole}>
                  <i className={`ti ${roleCfg.icon}`} style={{ fontSize: 10 }} />
                  {roleCfg.label}
                </span>
              </div>
              <i className="ti ti-chevron-down" style={{ fontSize: 14, color: colors.textFaint }} />
            </button>
            {userMenuOpen && (
              <>
                <div style={styles.overlay} onClick={() => setUserMenuOpen(false)} />
                <div style={styles.userMenu}>
                  <div style={styles.userMenuHeader}>
                    <div style={styles.avatarLarge}>
                      {user?.name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <div>
                      <div style={styles.userMenuName}>{user?.name || 'Utilisateur'}</div>
                      <div style={styles.userMenuEmail}>{user?.email || ''}</div>
                    </div>
                  </div>
                  <div style={styles.userMenuRole}>
                    <i className={`ti ${roleCfg.icon}`} style={{ fontSize: 14, color: colors.primary }} />
                    Profil : <strong>{roleCfg.label}</strong>
                  </div>
                  <div style={styles.userMenuDivider} />
                  <button style={styles.userMenuItem}>
                    <i className="ti ti-user" style={{ fontSize: 16 }} />
                    Mon profil
                  </button>
                  <button style={styles.userMenuItem}>
                    <i className="ti ti-settings" style={{ fontSize: 16 }} />
                    Préférences
                  </button>
                  {role === 'admin' && (
                    <button style={styles.userMenuItem} onClick={() => { onNavigate('administration'); setUserMenuOpen(false) }}>
                      <i className="ti ti-users" style={{ fontSize: 16 }} />
                      Gestion utilisateurs
                    </button>
                  )}
                  <div style={styles.userMenuDivider} />
                  <button style={{ ...styles.userMenuItem, color: colors.critical }} onClick={onLogout}>
                    <i className="ti ti-logout" style={{ fontSize: 16 }} />
                    Déconnexion
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>
    </>
  )
}

const styles = {
  topbar: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: 52,
    background: '#fff',
    borderBottom: `1px solid ${colors.border}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 20px',
    zIndex: 200,
    boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    gap: 24,
    height: '100%',
  },
  mobileBtn: {
    display: 'none',
    background: 'none',
    border: 'none',
    padding: 6,
    color: colors.text,
    alignItems: 'center',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  logoIcon: {
    width: 32,
    height: 32,
    background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryLight})`,
    borderRadius: 8,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 2px 8px rgba(24,95,165,0.25)',
  },
  logoText: {
    display: 'flex',
    flexDirection: 'column',
    lineHeight: 1.1,
  },
  logoName: {
    fontSize: 14,
    fontWeight: 700,
    color: colors.text,
    letterSpacing: '-0.3px',
  },
  logoSub: {
    fontSize: 9,
    color: colors.textFaint,
    fontWeight: 500,
    letterSpacing: '0.05em',
  },
  nav: {
    display: 'flex',
    alignItems: 'center',
    gap: 2,
    height: '100%',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 7,
    padding: '7px 12px',
    background: 'none',
    border: 'none',
    borderRadius: 7,
    fontSize: 13,
    fontWeight: 500,
    color: colors.textMuted,
    transition: 'all 0.15s',
    position: 'relative',
  },
  navItemActive: {
    background: colors.primaryBg,
    color: colors.primary,
    fontWeight: 600,
  },
  navBadge: {
    background: colors.critical,
    color: '#fff',
    fontSize: 9,
    fontWeight: 700,
    borderRadius: 10,
    padding: '1px 5px',
    marginLeft: 2,
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: colors.neutralBg,
    border: `1px solid ${colors.neutralBorder}`,
    borderRadius: 8,
    padding: '6px 10px',
    width: 220,
  },
  searchInput: {
    border: 'none',
    background: 'none',
    outline: 'none',
    fontSize: 13,
    color: colors.text,
    flex: 1,
    width: '100%',
  },
  searchKbd: {
    fontSize: 10,
    color: colors.textLight,
    background: '#fff',
    border: `1px solid ${colors.border}`,
    borderRadius: 4,
    padding: '1px 5px',
    fontWeight: 500,
  },
  iconBtns: {
    display: 'flex',
    alignItems: 'center',
    gap: 4,
  },
  iconBtn: {
    position: 'relative',
    background: 'none',
    border: 'none',
    padding: 8,
    borderRadius: 8,
    color: colors.textMuted,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    transition: 'all 0.15s',
  },
  dotGreen: {
    width: 6,
    height: 6,
    background: '#4CAF50',
    borderRadius: '50%',
  },
  notifDot: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 7,
    height: 7,
    background: colors.critical,
    borderRadius: '50%',
    border: '1.5px solid #fff',
  },
  userPill: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: colors.neutralBg,
    border: `1px solid ${colors.neutralBorder}`,
    borderRadius: 20,
    padding: '3px 10px 3px 3px',
    transition: 'all 0.15s',
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: '50%',
    background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryLight})`,
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 12,
    fontWeight: 700,
    flexShrink: 0,
  },
  userMeta: {
    display: 'flex',
    flexDirection: 'column',
    lineHeight: 1.2,
    textAlign: 'left',
  },
  userName: {
    fontSize: 12,
    fontWeight: 600,
    color: colors.text,
  },
  userRole: {
    fontSize: 10,
    color: colors.textFaint,
    display: 'flex',
    alignItems: 'center',
    gap: 3,
  },
  overlay: {
    position: 'fixed',
    inset: 0,
    zIndex: 199,
  },
  notifPanel: {
    position: 'absolute',
    top: 44,
    right: 0,
    width: 340,
    background: '#fff',
    border: `1px solid ${colors.border}`,
    borderRadius: 12,
    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
    zIndex: 200,
    overflow: 'hidden',
  },
  notifHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 16px',
    borderBottom: `1px solid ${colors.borderLight}`,
  },
  notifTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: colors.text,
  },
  notifCount: {
    fontSize: 11,
    color: colors.primary,
    background: colors.primaryBg,
    borderRadius: 10,
    padding: '2px 8px',
    fontWeight: 600,
  },
  notifItem: {
    display: 'flex',
    gap: 12,
    padding: '12px 16px',
    borderBottom: `1px solid ${colors.borderLight}`,
    cursor: 'pointer',
    transition: 'background 0.15s',
  },
  notifIcon: {
    width: 36,
    height: 36,
    borderRadius: 8,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  notifContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  notifText: {
    fontSize: 13,
    color: colors.text,
    fontWeight: 500,
  },
  notifTime: {
    fontSize: 11,
    color: colors.textFaint,
  },
  notifFooter: {
    width: '100%',
    padding: '12px',
    background: colors.neutralBg,
    border: 'none',
    fontSize: 13,
    fontWeight: 600,
    color: colors.primary,
    textAlign: 'center',
  },
  userMenu: {
    position: 'absolute',
    top: 48,
    right: 0,
    width: 280,
    background: '#fff',
    border: `1px solid ${colors.border}`,
    borderRadius: 12,
    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
    zIndex: 200,
    overflow: 'hidden',
  },
  userMenuHeader: {
    display: 'flex',
    gap: 12,
    padding: '16px',
    alignItems: 'center',
  },
  avatarLarge: {
    width: 44,
    height: 44,
    borderRadius: '50%',
    background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryLight})`,
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 18,
    fontWeight: 700,
    flexShrink: 0,
  },
  userMenuName: {
    fontSize: 14,
    fontWeight: 700,
    color: colors.text,
  },
  userMenuEmail: {
    fontSize: 12,
    color: colors.textFaint,
    marginTop: 2,
  },
  userMenuRole: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '8px 16px',
    background: colors.primaryBg,
    fontSize: 12,
    color: colors.textBody,
    borderTop: `1px solid ${colors.borderLight}`,
    borderBottom: `1px solid ${colors.borderLight}`,
  },
  userMenuDivider: {
    height: 1,
    background: colors.borderLight,
  },
  userMenuItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    width: '100%',
    padding: '11px 16px',
    background: 'none',
    border: 'none',
    fontSize: 13,
    color: colors.textBody,
    textAlign: 'left',
    fontWeight: 500,
    transition: 'background 0.15s',
  },
}
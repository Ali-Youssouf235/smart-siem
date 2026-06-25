import React from 'react'

const s = {
  topbar: {
    background: '#fff',
    borderBottom: '1px solid #E2EAF4',
    padding: '0 20px',
    height: '52px',
    display: 'flex',
    alignItems: 'center',
    boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: '9px',
    marginRight: '28px',
  },
  logo: {
    width: '30px',
    height: '30px',
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    borderRadius: '7px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  nav: {
    display: 'flex',
    gap: '2px',
    flex: 1,
  },
  navItem: (active) => ({
    fontSize: '13px',
    padding: '6px 13px',
    borderRadius: '7px',
    color: active ? '#185FA5' : '#6B7A99',
    cursor: 'pointer',
    fontWeight: active ? 600 : 500,
    background: active ? '#EBF3FF' : 'transparent',
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
  }),
  right: {
    marginLeft: 'auto',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  liveBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    fontSize: '11px',
    color: '#2E9E4F',
    fontWeight: 600,
    background: '#F0FBF0',
    border: '1px solid #C3E6C3',
    borderRadius: '20px',
    padding: '3px 10px',
  },
  liveDot: {
    width: '6px',
    height: '6px',
    background: '#4CAF50',
    borderRadius: '50%',
  },
  notifBtn: {
    background: '#FEF2F2',
    border: '1px solid #FECACA',
    borderRadius: '8px',
    padding: '5px 10px',
    fontSize: '12px',
    fontWeight: 600,
    color: '#DC2626',
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    cursor: 'pointer',
  },
  userPill: {
    display: 'flex',
    alignItems: 'center',
    gap: '7px',
    background: '#F7F9FC',
    border: '1px solid #E2EAF4',
    borderRadius: '8px',
    padding: '5px 10px',
    cursor: 'pointer',
  },
  userAv: {
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #185FA5, #1474C4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '9px',
    fontWeight: 700,
    color: '#fff',
  },
}

const navItems = [
  { key: 'dashboard', label: 'Dashboard', icon: 'ti-layout-dashboard' },
  { key: 'recherche', label: 'Recherche', icon: 'ti-search' },
  { key: 'alertes', label: 'Alertes', icon: 'ti-bell' },
  { key: 'ueba', label: 'UEBA', icon: 'ti-chart-radar' },
  { key: 'rapports', label: 'Rapports', icon: 'ti-file-text' },
]

export default function Topbar({ page, onNav, onLogout }) {
  return (
    <div style={s.topbar}>
      <div style={s.brand}>
        <div style={s.logo}>
          <i className="ti ti-shield-lock" style={{ fontSize: '15px', color: '#fff' }} />
        </div>
        <span style={{ fontSize: '14px', fontWeight: 700, color: '#0F1D2E' }}>Smart SIEM</span>
      </div>

      <div style={s.nav}>
        {navItems.map(item => (
          <div
            key={item.key}
            style={s.navItem(page === item.key)}
            onClick={() => onNav(item.key)}
          >
            <i className={`ti ${item.icon}`} style={{ fontSize: '13px' }} />
            {item.label}
          </div>
        ))}
      </div>

      <div style={s.right}>
        <div style={s.liveBadge}>
          <span style={s.liveDot}></span>
          En direct
        </div>
        <div style={s.notifBtn}>
          <i className="ti ti-bell" style={{ fontSize: '13px' }} />
          3 CRITICAL
        </div>
        <div style={s.userPill}>
          <div style={s.userAv}>CO</div>
          <span style={{ fontSize: '12px', color: '#374151', fontWeight: 500 }}>Chloe O'Brian</span>
        </div>
        <span
          onClick={onLogout}
          style={{ fontSize: '12px', color: '#6B7A99', cursor: 'pointer', padding: '5px 8px', borderRadius: '7px', border: '1px solid #E2EAF4' }}
        >
          <i className="ti ti-logout" style={{ fontSize: '13px' }} />
        </span>
      </div>
    </div>
  )
}

export const colors = {
  bg: '#F0F4F9',
  cardBg: '#FFFFFF',
  border: '#E2EAF4',
  borderLight: '#EDF1F7',
  text: '#0F1D2E',
  textBody: '#374151',
  textMuted: '#6B7A99',
  textFaint: '#8896B0',
  textLight: '#B0BCCF',
  primary: '#185FA5',
  primaryLight: '#1474C4',
  primaryBg: '#EBF3FF',
  primaryBgLight: '#F0F6FF',
  primaryBorder: '#C5D9F2',

  critical: '#DC2626',
  criticalBg: '#FEF2F2',
  criticalBorder: '#FECACA',

  high: '#D97706',
  highBg: '#FFFBEB',
  highBorder: '#FDE68A',

  warning: '#F59E0B',
  warningBg: '#FFFBEB',

  success: '#16A34A',
  successBg: '#F0FDF4',
  successBorder: '#BBF7D0',

  info: '#185FA5',
  infoBg: '#EBF3FF',

  purple: '#8B5CF6',
  purpleBg: '#F5F3FF',

  neutralBg: '#F7F9FC',
  neutralBorder: '#DDE5F0',
  neutralLight: '#EDF1F7',
}

export const severityConfig = {
  critical: { label: 'CRITICAL', color: colors.critical, bg: colors.criticalBg, border: colors.criticalBorder },
  high: { label: 'HIGH', color: colors.high, bg: colors.highBg, border: colors.highBorder },
  warning: { label: 'WARNING', color: colors.warning, bg: colors.warningBg, border: colors.highBorder },
  info: { label: 'INFO', color: colors.success, bg: colors.successBg, border: colors.successBorder },
}

export const roleConfig = {
  lecteur: {
    label: 'Lecteur',
    desc: 'Consultation',
    icon: 'ti-eye',
    pages: ['dashboard', 'alertes', 'recherche', 'ueba', 'rapports', 'regles'],
    canExport: false,
    canAcknowledge: false,
    canInvestigate: false,
    canManageUsers: false,
  },
  analyste: {
    label: 'Analyste',
    desc: 'Investigation',
    icon: 'ti-search',
    pages: ['dashboard', 'alertes', 'recherche', 'ueba', 'rapports', 'regles', 'crisis'],
    canExport: true,
    canAcknowledge: true,
    canInvestigate: true,
    canManageUsers: false,
  },
  admin: {
    label: 'Admin',
    desc: 'Gestion',
    icon: 'ti-settings',
    pages: ['dashboard', 'alertes', 'recherche', 'ueba', 'rapports', 'regles', 'administration', 'crisis'],
    canExport: true,
    canAcknowledge: true,
    canInvestigate: true,
    canManageUsers: true,
  },
}

export const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'ti-layout-dashboard' },
  { id: 'recherche', label: 'Recherche', icon: 'ti-search' },
  { id: 'alertes', label: 'Alertes', icon: 'ti-bell' },
  { id: 'ueba', label: 'UEBA', icon: 'ti-users' },
  { id: 'regles', label: 'Règles', icon: 'ti-adjustments' },
  { id: 'rapports', label: 'Rapports', icon: 'ti-file-text' },
  { id: 'administration', label: 'Administration', icon: 'ti-settings', adminOnly: true },
]

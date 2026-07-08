import { useState, useEffect } from 'react';
import { colors } from '../theme';
import { rulesApi } from '../api';

const EMPTY_FORM = { id: '', name: '', description: '', severity: 'HIGH', threshold: 5, enabled: true };

export default function Regles({ user }) {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [newThreshold, setNewThreshold] = useState(3);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  const canManage = user?.role === 'admin' || user?.role === 'analyste';

  // Charger les règles depuis FastAPI
  const fetchRules = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await rulesApi.list();
      setRules(data.rules || []);
    } catch (err) {
      console.error("Erreur chargement règles:", err);
      setError("Impossible de récupérer les règles de corrélation depuis le moteur SIEM.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  // Sauvegarder la modification du seuil
  const handleSaveThreshold = async (id, currentRule) => {
    try {
      await rulesApi.update(id, {
        ...currentRule,
        threshold: parseInt(newThreshold, 10)
      });
      setEditingId(null);
      fetchRules();
    } catch (err) {
      alert("Erreur lors de la mise à jour de la règle.");
    }
  };

  // Activer / désactiver une règle sans changer le reste de sa configuration
  const handleToggleEnabled = async (rule) => {
    try {
      await rulesApi.update(rule.id, { ...rule, enabled: !rule.enabled });
      fetchRules();
    } catch (err) {
      alert("Erreur lors du changement d'état de la règle.");
    }
  };

  // Supprimer définitivement une règle du moteur de corrélation
  const handleDelete = async (rule) => {
    if (!window.confirm(`Supprimer définitivement la règle ${rule.id} - ${rule.name} ?`)) return;
    try {
      await rulesApi.delete(rule.id);
      fetchRules();
    } catch (err) {
      alert("Erreur lors de la suppression de la règle.");
    }
  };

  // Créer une nouvelle règle de corrélation
  const handleCreateRule = async (e) => {
    e.preventDefault();
    if (!formData.id || !formData.name) {
      alert("L'identifiant et le nom de la règle sont obligatoires.");
      return;
    }
    setSubmitting(true);
    try {
      await rulesApi.create({
        ...formData,
        threshold: formData.threshold ? parseInt(formData.threshold, 10) : null,
      });
      setFormData(EMPTY_FORM);
      setShowCreateForm(false);
      fetchRules();
    } catch (err) {
      alert("Erreur lors de la création de la règle (identifiant déjà utilisé ?).");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ padding: 20 }}>Chargement du moteur de corrélation...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: colors.text }}>Moteur de Corrélation & SIEM Rules</h1>
          <p style={{ fontSize: 13, color: colors.textMuted }}>Gestion des seuils de détection MITRE ATT&CK en temps réel</p>
        </div>
        {canManage && (
          <button
            onClick={() => setShowCreateForm((v) => !v)}
            style={{ background: colors.primary, color: '#fff', border: 'none', padding: '10px 16px', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <i className="ti ti-plus" /> Nouvelle règle
          </button>
        )}
      </div>

      {error && (
        <div style={{ background: colors.criticalBg, color: colors.critical, padding: 12, borderRadius: 8, fontSize: 13, fontWeight: 600 }}>
          {error}
        </div>
      )}

      {showCreateForm && (
        <form onSubmit={handleCreateRule} style={{ background: '#fff', padding: 18, borderRadius: 10, border: `1px solid ${colors.border}`, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <input placeholder="ID (ex: S7)" value={formData.id} onChange={(e) => setFormData({ ...formData, id: e.target.value })} style={inputStyle} />
          <input placeholder="Nom de la règle" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} style={inputStyle} />
          <input placeholder="Description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} style={{ ...inputStyle, gridColumn: '1 / -1' }} />
          <select value={formData.severity} onChange={(e) => setFormData({ ...formData, severity: e.target.value })} style={inputStyle}>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
          <input type="number" placeholder="Seuil (optionnel)" value={formData.threshold} onChange={(e) => setFormData({ ...formData, threshold: e.target.value })} style={inputStyle} />
          <div style={{ gridColumn: '1 / -1', display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button type="button" onClick={() => setShowCreateForm(false)} style={{ background: '#fff', border: `1px solid ${colors.border}`, padding: '8px 16px', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>Annuler</button>
            <button type="submit" disabled={submitting} style={{ background: colors.success, color: '#fff', border: 'none', padding: '8px 16px', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
              {submitting ? 'Création...' : 'Créer la règle'}
            </button>
          </div>
        </form>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {rules.length === 0 && !error && (
          <p style={{ color: colors.textMuted, fontSize: 13 }}>Aucune règle enregistrée pour le moment.</p>
        )}
        {rules.map((rule) => (
          <div key={rule.id} style={{ background: '#fff', padding: 18, borderRadius: 10, border: `1px solid ${colors.border}`, opacity: rule.enabled === false ? 0.55 : 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1, minWidth: 240 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontWeight: 700, color: colors.primary, background: colors.primaryBg, padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>{rule.id}</span>
                <strong style={{ color: colors.text }}>{rule.name}</strong>
                <span style={{ fontSize: 11, fontWeight: 600, color: rule.severity === 'CRITICAL' ? colors.critical : colors.high }}>
                  [{rule.severity}]
                </span>
                {rule.enabled === false && (
                  <span style={{ fontSize: 11, fontWeight: 700, color: colors.textFaint, border: `1px solid ${colors.border}`, padding: '1px 6px', borderRadius: 4 }}>DÉSACTIVÉE</span>
                )}
              </div>
              <p style={{ fontSize: 13, color: colors.textMuted, margin: 0 }}>{rule.description}</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              {rule.threshold !== undefined && rule.threshold !== null && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: colors.textFaint }}>SEUIL :</span>
                  {editingId === rule.id ? (
                    <input
                      type="number"
                      value={newThreshold}
                      onChange={(e) => setNewThreshold(e.target.value)}
                      style={{ width: 50, padding: 5, borderRadius: 6, border: `1px solid ${colors.border}` }}
                    />
                  ) : (
                    <strong style={{ color: colors.text }}>{rule.threshold} tentatives</strong>
                  )}
                </div>
              )}

              {editingId === rule.id ? (
                <button
                  onClick={() => handleSaveThreshold(rule.id, rule)}
                  style={{ background: colors.success, color: '#fff', border: 'none', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
                >
                  Valider
                </button>
              ) : (
                canManage && rule.threshold !== undefined && rule.threshold !== null && (
                  <button
                    onClick={() => { setEditingId(rule.id); setNewThreshold(rule.threshold || 3); }}
                    style={{ background: '#fff', border: `1px solid ${colors.border}`, padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12, color: colors.text }}
                  >
                    <i className="ti ti-edit" /> Modifier
                  </button>
                )
              )}

              {canManage && (
                <button
                  onClick={() => handleToggleEnabled(rule)}
                  style={{ background: '#fff', border: `1px solid ${colors.border}`, padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12, color: rule.enabled === false ? colors.success : colors.textMuted }}
                >
                  {rule.enabled === false ? 'Activer' : 'Désactiver'}
                </button>
              )}

              {user?.role === 'admin' && (
                <button
                  onClick={() => handleDelete(rule)}
                  style={{ background: colors.criticalBg, border: `1px solid ${colors.criticalBorder}`, padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12, color: colors.critical }}
                >
                  <i className="ti ti-trash" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const inputStyle = { padding: '10px 12px', borderRadius: 8, border: '1px solid #E2EAF4', fontSize: 13 };

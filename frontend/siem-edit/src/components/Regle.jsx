import { useState, useEffect } from 'react';
import { colors } from '../theme';
import { rulesApi } from '../api';

export default function Regles() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [newThreshold, setNewThreshold] = useState(3);

  // Charger les règles depuis FastAPI
  const fetchRules = async () => {
    try {
      setLoading(true);
      const data = await rulesApi.list();
      setRules(data.rules || []);
    } catch (err) {
      console.error("Erreur chargement règles:", err);
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
      alert(`Règle ${id} mise à jour dans le moteur de corrélation !`);
      setEditingId(null);
      fetchRules(); // Rafraîchir l'affichage
    } catch (err) {
      alert("Erreur lors de la mise à jour de la règle.");
    }
  };

  if (loading) return <div style={{ padding: 20 }}>Chargement du moteur de corrélation...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: colors.text }}>Moteur de Corrélation & SIEM Rules</h1>
        <p style={{ fontSize: 13, color: colors.textMuted }}>Gestion des seuils de détection MITRE ATT&CK en temps réel</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {rules.map((rule) => (
          <div key={rule.id} style={{ background: '#fff', padding: 18, borderRadius: 10, border: `1px solid ${colors.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontWeight: 700, color: colors.primary, background: colors.primaryBg, padding: '2px 6px', borderRadius: 4, fontSize: 12 }}>{rule.id}</span>
                <strong style={{ color: colors.text }}>{rule.name}</strong>
                <span style={{ fontSize: 11, fontWeight: 600, color: rule.severity === 'CRITICAL' ? colors.critical : colors.high }}>
                  [{rule.severity}]
                </span>
              </div>
              <p style={{ fontSize: 13, color: colors.textMuted, margin: 0 }}>{rule.description}</p>
            </div>

            {/* Ajustement du Seuil numérique */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {rule.threshold !== undefined && (
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

              {/* Actions Boutons */}
              {editingId === rule.id ? (
                <button 
                  onClick={() => handleSaveThreshold(rule.id, rule)}
                  style={{ background: colors.success, color: '#fff', border: 'none', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12 }}
                >
                  Valider
                </button>
              ) : (
                <button 
                  onClick={() => { setEditingId(rule.id); setNewThreshold(rule.threshold || 3); }}
                  style={{ background: '#fff', border: `1px solid ${colors.border}`, padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 12, color: colors.text }}
                >
                  <i className="ti ti-edit" /> Modifier
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
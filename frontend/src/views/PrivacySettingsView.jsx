import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { HiShieldCheck, HiArrowLeft, HiExclamationTriangle, HiCheckCircle } from 'react-icons/hi2';
import { useAuth } from '../context/AuthContext';

export const PrivacySettingsView = () => {
  const navigate = useNavigate();
  const { user, updateConsent, updatePrivacySettings, deleteAccount } = useAuth();
  const [loading, setLoading] = useState(false);
  const [privacySettings, setPrivacySettings] = useState({
    data_retention_days: 90,
    allow_analytics: false,
    allow_marketing: false,
    conversation_history_enabled: true
  });

  const handleConsentUpdate = async () => {
    setLoading(true);
    await updateConsent({ consent_given: true, consent_date: new Date().toISOString() });
    setLoading(false);
  };

  const handlePrivacyUpdate = async () => {
    setLoading(true);
    await updatePrivacySettings(privacySettings);
    setLoading(false);
  };

  const handleDeleteAccount = async () => {
    const success = await deleteAccount();
    if (success) navigate('/');
  };

  const Toggle = ({ active, onClick }) => (
    <button
      onClick={onClick}
      className={`relative w-12 h-6 rounded-full transition-colors shrink-0 ${
        active ? 'bg-primary-700' : 'bg-stone-300 dark:bg-primary-900/60'
      }`}
    >
      <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform shadow-sm ${active ? 'translate-x-6' : 'translate-x-0'}`} />
    </button>
  );

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate(-1)}
          className="p-2 text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200 rounded-xl hover:bg-stone-100 dark:hover:bg-primary-900/40 transition-colors"
        >
          <HiArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-serif font-semibold text-stone-900 dark:text-stone-100">Privacy Settings</h1>
          <p className="text-sm text-stone-600 dark:text-stone-400">Manage your data and privacy preferences</p>
        </div>
      </div>

      {/* Consent */}
      <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-2xl p-6 shadow-card border border-stone-200/80 dark:border-primary-900/50 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <HiShieldCheck className="w-6 h-6 text-primary-600 dark:text-accent-400" />
          <h2 className="text-lg font-serif font-semibold text-stone-900 dark:text-stone-100">Data Consent</h2>
        </div>
        <p className="text-sm text-stone-600 dark:text-stone-400 mb-4">
          By using AyurPedia, you agree to our data processing practices. We collect and process your data to provide legal intelligence services.
        </p>
        {user && !user.consent_given && (
          <button
            onClick={handleConsentUpdate}
            disabled={loading}
            className="px-4 py-2 btn-premium text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Accept Data Processing Consent'}
          </button>
        )}
        {user?.consent_given && (
          <div className="inline-flex items-center gap-1.5 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 text-sm rounded-xl">
            <HiCheckCircle className="w-4 h-4" /> Consent given
          </div>
        )}
      </div>

      {/* Preferences */}
      <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-2xl p-6 shadow-card border border-stone-200/80 dark:border-primary-900/50 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <HiShieldCheck className="w-6 h-6 text-primary-600 dark:text-accent-400" />
          <h2 className="text-lg font-serif font-semibold text-stone-900 dark:text-stone-100">Privacy Preferences</h2>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Data Retention Period (days)
            </label>
            <input
              type="number"
              value={privacySettings.data_retention_days}
              onChange={(e) => setPrivacySettings({ ...privacySettings, data_retention_days: parseInt(e.target.value) })}
              min={7}
              max={365}
              className="w-full px-4 py-2 bg-stone-50 dark:bg-primary-950/60 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500"
            />
            <p className="text-xs text-stone-500 mt-1">How long we keep your conversation history and data</p>
          </div>

          {[
            { key: 'allow_analytics', label: 'Allow Analytics', desc: 'Help us improve by sharing anonymous usage data' },
            { key: 'allow_marketing', label: 'Allow Marketing Communications', desc: 'Receive updates about new features and improvements' },
            { key: 'conversation_history_enabled', label: 'Save Conversation History', desc: 'Store your chat conversations for future reference' },
          ].map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between gap-4">
              <div>
                <label className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-1">{label}</label>
                <p className="text-xs text-stone-500">{desc}</p>
              </div>
              <Toggle
                active={privacySettings[key]}
                onClick={() => setPrivacySettings({ ...privacySettings, [key]: !privacySettings[key] })}
              />
            </div>
          ))}
        </div>

        <button
          onClick={handlePrivacyUpdate}
          disabled={loading}
          className="mt-6 w-full py-2.5 btn-premium text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save Privacy Settings'}
        </button>
      </div>

      {/* Danger Zone */}
      <div className="bg-clay-50 dark:bg-clay-900/20 rounded-2xl p-6 border border-clay-200 dark:border-clay-800/60">
        <div className="flex items-center gap-3 mb-4">
          <HiExclamationTriangle className="w-6 h-6 text-clay-600 dark:text-clay-400" />
          <h2 className="text-lg font-serif font-semibold text-clay-900 dark:text-clay-200">Danger Zone</h2>
        </div>
        <p className="text-sm text-clay-800 dark:text-clay-300 mb-4">These actions are irreversible. Please be certain.</p>
        <button
          onClick={handleDeleteAccount}
          className="px-4 py-2 bg-clay-600 hover:bg-clay-700 text-white text-sm font-semibold rounded-xl transition-colors"
        >
          Delete Account and All Data
        </button>
      </div>
    </div>
  );
};

export default PrivacySettingsView;

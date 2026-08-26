import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { HiLockClosed, HiEnvelope, HiUser, HiBuildingOffice2, HiArrowRight } from 'react-icons/hi2';
import { useAuth } from '../context/AuthContext';
import { AyurMark, Mandala, Sprig } from '../components/Common/Botanical';

export const RegisterView = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '', full_name: '', organization: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await register(formData);
    setLoading(false);
    if (success) navigate('/chat');
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const inputClass =
    'w-full pl-10 pr-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all';

  return (
    <div className="relative min-h-view flex items-center justify-center px-4 py-10 sm:py-12 overflow-hidden">
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <Mandala className="absolute -top-24 -left-20 w-80 h-80 text-primary-700/10 dark:text-primary-300/10" />
        <Sprig className="absolute bottom-4 right-0 w-40 h-40 text-accent-500/10 animate-sway" />
      </div>

      <div className="relative w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8 scale-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-800 text-accent-300 ring-1 ring-accent-400/25 rounded-2xl shadow-card mb-4">
            <AyurMark className="w-8 h-8" />
          </div>
          <h1 className="font-serif text-3xl font-semibold text-stone-900 dark:text-stone-100">
            Join AyurPedia
          </h1>
          <p className="text-stone-600 dark:text-stone-400 mt-2 text-sm">
            Create your account to access Ayurvedic IPR intelligence
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 shadow-card border border-stone-200/80 dark:border-primary-900/50">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="full_name" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">Full Name</label>
              <div className="relative">
                <HiUser className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" />
                <input type="text" id="full_name" name="full_name" value={formData.full_name} onChange={handleChange} placeholder="Dr. Anjali Sharma" className={inputClass} />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">Email Address</label>
              <div className="relative">
                <HiEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" />
                <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} required placeholder="you@example.com" className={inputClass} />
              </div>
            </div>

            <div>
              <label htmlFor="organization" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
                Organization <span className="text-stone-400 font-normal">(Optional)</span>
              </label>
              <div className="relative">
                <HiBuildingOffice2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" />
                <input type="text" id="organization" name="organization" value={formData.organization} onChange={handleChange} placeholder="Your institution or company" className={inputClass} />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">Password</label>
              <div className="relative">
                <HiLockClosed className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" />
                <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} required minLength={8} placeholder="••••••••" className={inputClass} />
              </div>
              <p className="text-xs text-stone-500 mt-1">Minimum 8 characters</p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 text-white btn-premium font-bold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <HiArrowRight className="w-5 h-5 text-accent-300" />
                </>
              )}
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-stone-200 dark:border-primary-900/50"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-[#fffdf8] dark:bg-[#0e1712] text-stone-500">Already have an account?</span>
            </div>
          </div>

          <Link
            to="/login"
            className="block w-full py-3 px-4 bg-stone-100 dark:bg-primary-900/40 hover:bg-stone-200 dark:hover:bg-primary-900/60 text-stone-700 dark:text-stone-200 font-semibold rounded-xl transition-all duration-300 text-center"
          >
            Sign In
          </Link>
        </div>

        <p className="text-xs text-stone-500 text-center mt-6">
          By creating an account, you agree to our{' '}
          <Link to="/terms" className="text-accent-700 dark:text-accent-400 hover:underline">Terms of Service</Link>
          {' '}and{' '}
          <Link to="/privacy" className="text-accent-700 dark:text-accent-400 hover:underline">Privacy Policy</Link>
        </p>

        <div className="text-center mt-4">
          <Link to="/" className="text-sm text-stone-500 hover:text-primary-700 dark:text-stone-400 dark:hover:text-accent-300 transition-colors">
            &larr; Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterView;

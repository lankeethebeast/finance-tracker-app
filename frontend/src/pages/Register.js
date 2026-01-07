import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Liquid Crystal Background Animation */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Animated Liquid Blobs */}
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-emerald-400/20 to-teal-500/20 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute bottom-3/4 left-1/4 w-80 h-80 bg-gradient-to-r from-indigo-400/20 to-purple-500/20 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute top-1/4 left-1/2 w-72 h-72 bg-gradient-to-r from-cyan-400/20 to-emerald-500/20 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>

        {/* Crystal Geometric Patterns */}
        <div className="absolute bottom-20 right-20 w-32 h-32 border border-emerald-400/30 rotate-45 animate-spin" style={{animationDuration: '20s'}}></div>
        <div className="absolute top-32 left-16 w-24 h-24 border border-indigo-400/30 rotate-12 animate-spin" style={{animationDuration: '15s', animationDirection: 'reverse'}}></div>
        <div className="absolute bottom-1/2 left-32 w-20 h-20 border border-teal-400/30 rotate-67 animate-spin" style={{animationDuration: '25s'}}></div>

        {/* Floating Particles */}
        <div className="absolute bottom-1/3 left-1/3 w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></div>
        <div className="absolute top-1/3 right-1/3 w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce animation-delay-1000"></div>
        <div className="absolute bottom-2/3 right-2/3 w-1 h-1 bg-teal-400 rounded-full animate-bounce animation-delay-2000"></div>
      </div>

      {/* Glass Morphism Card */}
      <div className="relative backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-2xl p-8 w-full max-w-md">
        {/* Inner glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-indigo-500/10 rounded-2xl"></div>

        <div className="relative z-10">
          <h1 className="text-4xl font-bold text-white mb-2 text-center bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
            Create Account
          </h1>
          <p className="text-emerald-100 text-center mb-8 text-lg">Start tracking your finances</p>

          {error && (
            <div className="backdrop-blur-sm bg-red-500/20 border border-red-400/30 text-red-100 px-4 py-3 rounded-xl mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-emerald-100 text-sm font-semibold mb-2" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                type="text"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-emerald-200 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent backdrop-blur-sm transition-all duration-300"
                placeholder="Choose a username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-emerald-100 text-sm font-semibold mb-2" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-emerald-200 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent backdrop-blur-sm transition-all duration-300"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-emerald-100 text-sm font-semibold mb-2" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-emerald-200 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent backdrop-blur-sm transition-all duration-300"
                placeholder="Create a strong password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-emerald-100 text-sm font-semibold mb-2" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-emerald-200 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent backdrop-blur-sm transition-all duration-300"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-emerald-500 to-indigo-600 hover:from-emerald-600 hover:to-indigo-700 text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Creating account...
                </div>
              ) : (
                'Register'
              )}
            </button>
          </form>

          <p className="text-center text-emerald-200 mt-8">
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-300 hover:text-white font-semibold transition-colors duration-300 hover:underline">
              Login
            </Link>
          </p>
        </div>
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animation-delay-1000 {
          animation-delay: 1s;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  );
};

export default Register;

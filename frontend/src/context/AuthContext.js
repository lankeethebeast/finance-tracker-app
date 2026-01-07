import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authAPI.getCurrentUser()
        .then(response => {
          setUser(response.data.user);
          setLoading(false);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    console.log('Login attempt with credentials:', credentials);
    const response = await authAPI.login(credentials);
    console.log('Login response:', response.data);
    console.log('Access token:', response.data.access_token);
    localStorage.setItem('token', response.data.access_token);
    console.log('Token saved to localStorage');

    // Verify it was actually saved
    const savedToken = localStorage.getItem('token');
    console.log('Verification - Token in localStorage:', savedToken ? 'Present' : 'FAILED TO SAVE');

    setUser(response.data.user);
    return response.data;
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const isAdmin = () => {
    return user && user.role === 'admin';
  };

  const hasRole = (role) => {
    return user && (user.role === role || user.role === 'admin');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, isAdmin, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

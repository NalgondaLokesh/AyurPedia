import React from 'react';
import { Navigate } from 'react-router-dom';
import LandingView from './views/LandingView';
import LoginView from './views/LoginView';
import RegisterView from './views/RegisterView';
import PrivacySettingsView from './views/PrivacySettingsView';
import ChatInterface from './components/Chat/ChatInterface';
import ClassifierFlow from './components/Classification/ClassifierFlow';
import GraphView from './views/GraphView';
import DisclaimerView from './views/DisclaimerView';
import PrivacyView from './views/PrivacyView';
import TermsView from './views/TermsView';
import { ProtectedRoute } from './components/Common/ProtectedRoute';
import { useAuth } from './context/AuthContext';

// Public route - redirects to chat if authenticated
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/chat" replace /> : children;
};

export const routes = [
  {
    path: '/',
    element: <PublicRoute><LandingView /></PublicRoute>,
    title: 'Home',
  },
  {
    path: '/login',
    element: <PublicRoute><LoginView /></PublicRoute>,
    title: 'Login',
  },
  {
    path: '/register',
    element: <PublicRoute><RegisterView /></PublicRoute>,
    title: 'Register',
  },
  {
    path: '/chat',
    element: <ProtectedRoute><ChatInterface /></ProtectedRoute>,
    title: 'Legal Chat',
  },
  {
    path: '/classify',
    element: <ProtectedRoute><ClassifierFlow /></ProtectedRoute>,
    title: 'Formulation Classifier',
  },
  {
    path: '/graph',
    element: <ProtectedRoute><GraphView /></ProtectedRoute>,
    title: 'Knowledge Graph',
  },
  {
    path: '/settings',
    element: <ProtectedRoute><PrivacySettingsView /></ProtectedRoute>,
    title: 'Privacy Settings',
  },
  {
    path: '/disclaimer',
    element: <DisclaimerView />,
    title: 'Disclaimer',
  },
  {
    path: '/privacy',
    element: <PrivacyView />,
    title: 'Privacy Policy',
  },
  {
    path: '/terms',
    element: <TermsView />,
    title: 'Terms of Use',
  },
];

export default routes;

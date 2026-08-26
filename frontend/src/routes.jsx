import React from 'react';
import LandingView from './views/LandingView';
import LoginView from './views/LoginView';
import RegisterView from './views/RegisterView';
import PrivacySettingsView from './views/PrivacySettingsView';
import ChatInterface from './components/Chat/ChatInterface';
import ClassifierFlow from './components/Classification/ClassifierFlow';
import DisclaimerView from './views/DisclaimerView';
import PrivacyView from './views/PrivacyView';
import TermsView from './views/TermsView';
import { ProtectedRoute } from './components/Common/ProtectedRoute';

export const routes = [
  {
    path: '/',
    element: <LandingView />,
    title: 'Home',
  },
  {
    path: '/login',
    element: <LoginView />,
    title: 'Login',
  },
  {
    path: '/register',
    element: <RegisterView />,
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

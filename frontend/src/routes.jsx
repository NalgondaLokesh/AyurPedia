import React from 'react';
import ChatInterface from './components/Chat/ChatInterface';
import ClassifierFlow from './components/Classification/ClassifierFlow';
import DisclaimerView from './views/DisclaimerView';
import PrivacyView from './views/PrivacyView';
import TermsView from './views/TermsView';

export const routes = [
  {
    path: '/',
    element: <ChatInterface />,
    title: 'Legal Chat',
  },
  {
    path: '/classify',
    element: <ClassifierFlow />,
    title: 'Formulation Classifier',
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

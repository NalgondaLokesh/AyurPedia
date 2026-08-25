import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AppProvider } from './context/AppContext';
import { ChatProvider } from './context/ChatContext';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import FacilitatorModal from './components/Common/FacilitatorModal';
import routes from './routes';
import './styles/App.css';
import './styles/Chat.css';

export const App = () => {
  return (
    <AppProvider>
      <ChatProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-gradient-to-br from-stone-50 via-emerald-50/25 to-stone-100 dark:from-stone-950 dark:via-stone-900 dark:to-stone-950 text-stone-800 dark:text-stone-100 transition-colors duration-200">
            {/* Toast notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#1a4d2e',
                  color: '#fff',
                  fontSize: '13px',
                  borderRadius: '14px',
                  boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
                },
                success: {
                  iconTheme: {
                    primary: '#52b788',
                    secondary: '#fff',
                  },
                },
                error: {
                  style: {
                    background: '#991b1b',
                  },
                },
              }}
            />

            {/* Global Header */}
            <Header />

            {/* Main Content Area */}
            <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
              <Routes>
                {routes.map((route, index) => (
                  <Route key={index} path={route.path} element={route.element} />
                ))}
              </Routes>
            </main>

            {/* Human Facilitator Escalation Modal */}
            <FacilitatorModal />

            {/* Global Footer */}
            <Footer />
          </div>
        </Router>
      </ChatProvider>
    </AppProvider>
  );
};

export default App;

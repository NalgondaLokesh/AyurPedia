import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AppProvider } from './context/AppContext';
import { ChatProvider } from './context/ChatContext';
import { AuthProvider } from './context/AuthContext';
import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import FacilitatorModal from './components/Common/FacilitatorModal';
import routes from './routes';
import './styles/App.css';
import './styles/Chat.css';

export const App = () => {
  return (
    <Router>
      <AuthProvider>
        <AppProvider>
          <ChatProvider>
            <div className="flex flex-col min-h-screen heritage-canvas paper-texture text-stone-800 dark:text-stone-100 transition-colors duration-300">
              {/* Toast notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#1f4133',
                    color: '#faf8f3',
                    fontSize: '13px',
                    borderRadius: '14px',
                    padding: '10px 14px',
                    border: '1px solid rgba(207, 143, 34, 0.35)',
                    boxShadow: '0 12px 30px -12px rgba(24, 51, 40, 0.5)',
                    fontFamily: 'Inter, system-ui, sans-serif',
                  },
                  success: {
                    iconTheme: {
                      primary: '#e0a93b',
                      secondary: '#12261e',
                    },
                  },
                  error: {
                    style: {
                      background: '#7a2d22',
                      border: '1px solid rgba(224, 169, 59, 0.3)',
                    },
                  },
                }}
              />

              {/* Global Header */}
              <Header />

              {/* Main Content Area */}
              <main className="flex-1 w-full">
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
          </ChatProvider>
        </AppProvider>
      </AuthProvider>
    </Router>
  );
};

export default App;

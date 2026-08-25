import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Simple Error Boundary to catch render issues gracefully
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[AyurPedia Render Error]:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-stone-100 p-6 text-center">
          <div className="max-w-md bg-white p-8 rounded-3xl border border-stone-200 shadow-xl">
            <div className="w-12 h-12 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl">
              ⚠️
            </div>
            <h2 className="text-lg font-bold text-stone-900 mb-2">Something went wrong</h2>
            <p className="text-xs text-stone-600 mb-6">
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-md"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import Home from './pages/Home';
import FeedPage from './pages/FeedPage';
import BriefingPage from './pages/BriefingPage';
import ArticlePage from './pages/ArticlePage';
import SignupPage from './pages/SignupPage';
import ScrollToTop from './components/ScrollToTop';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <ScrollToTop />
        <AuthProvider>
          <Routes>
            {/* Rota de Login (pública) */}
            <Route path="/login" element={<LoginPage />} />

            {/* Rota de Signup (pública) */}
            <Route path="/signup" element={<SignupPage />} />
            
            {/* Todas as outras rotas são protegidas */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Header />
                  <main className="min-h-screen bg-gray-50 dark:bg-slate-900">
                    <Routes>
                      <Route path="/" element={<Home />} />
                      <Route path="/feeds/:feedName" element={<FeedPage />} />
                      <Route path="/briefings/:id" element={<BriefingPage />} />
                      <Route path="/articles/:id" element={<ArticlePage />} />
                      
                      {/* Rota 404 */}
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </main>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
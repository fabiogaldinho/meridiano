// src/App.tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import FeedPage from './pages/FeedPage';
import BriefingPage from './pages/BriefingPage';
import ArticlePage from './pages/ArticlePage';

function App() {
    return (
        <BrowserRouter>
            <Header />
            <main className="min-h-screen bg-gray-50">
                <Routes>
                    {/* Rota da home */}
                    <Route path="/" element={<Home />} />
                
                    {/* Rota dinâmica para feeds */}
                    <Route path="/feeds/:feedName" element={<FeedPage />} />

                    {/* Rota dinâmica para briefings */}
                    <Route path="/briefings/:id" element={<BriefingPage />} />

                    {/* Rota dinâmica para articles */}
                    <Route path="/articles/:id" element={<ArticlePage />} />
          
                    {/* Rota 404 */}
                    <Route path="*" element={
                        <div className="max-w-7xl mx-auto px-4 py-8 text-center">
                        <h1 className="text-3xl font-bold text-gray-800 mb-4">Página não encontrada</h1>
                        <Link to="/" className="text-blue-600 hover:underline">Voltar para a home</Link>
                        </div>
                    } />
                </Routes>
            </main>
        </BrowserRouter>
    );
}

export default App;
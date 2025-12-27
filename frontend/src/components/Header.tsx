// src/components/Header.tsx
import { Link, useNavigate } from 'react-router-dom';
import Logo from './Logo';
import FeedsDropdown from './FeedsDropdown';
import ThemeToggle from './ThemeToggle';
import { useAuth } from '../contexts/AuthContext';

function Header() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 dark:from-slate-800 dark:via-slate-900 dark:to-slate-950 shadow-md">
      {/* Container com largura máxima e centralizado */}
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          
          {/* --- LOGO E NOME --- */}
          <Link 
            to="/" 
            className="
              flex items-center
              text-white text-xl font-bold
              hover:text-gray-100
              transition-colors duration-200
            "
          >
            <Logo />
            <span className="hidden sm:inline">Galdinho News</span>
          </Link>

          {/* --- NAVEGAÇÃO --- */}
          <nav className="flex items-center gap-8">
            {/* Link HOME */}
            <Link
              to="/"
              className="
                text-white font-medium
                hover:text-gray-200
                transition-colors duration-200
              "
            >
              HOME
            </Link>

            {/* Dropdown FEEDS */}
            <FeedsDropdown />

            {/* Área do Usuário */}
            <div className="flex items-center gap-4 border-l border-white/30 pl-4">
              {/* Nome do usuário */}
              <span className="text-white/90 text-sm">
                {user?.username}
              </span>

              {/* Dark mode */}
              <ThemeToggle />

              {/* Botão Logout */}
              <button
                onClick={handleLogout}
                className="
                  text-white/90 hover:text-white
                  transition-colors duration-200
                  text-sm font-medium
                "
                title="Sair"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </nav>
          {}

        </div>
      </div>
    </header>
  );
}

export default Header;
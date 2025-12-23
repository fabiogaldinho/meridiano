// src/components/Header.tsx
import { Link } from 'react-router-dom';
import Logo from './Logo';
import FeedsDropdown from './FeedsDropdown';

function Header() {
  return (
    <header className="sticky top-0 z-50 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 shadow-md">
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
            Galdinho News
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
          </nav>
          {}

        </div>
      </div>
    </header>
  );
}

export default Header;
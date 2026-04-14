// src/contexts/ThemeContext.tsx
import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
    document.body.style.backgroundColor = theme === 'dark' ? '#101628' : '#ECECEE';

    localStorage.setItem('theme', theme);

    // Atualiza meta theme-color
    const existingMeta = document.querySelector('meta[name="theme-color"]');
    if (existingMeta) {
        existingMeta.remove();
    }
    const newMeta = document.createElement('meta');
    newMeta.name = 'theme-color';
    newMeta.content = theme === 'dark' ? '#151823' : '#2563eb';
    document.head.appendChild(newMeta);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  
  if (!context) {
    throw new Error('useTheme deve ser usado dentro de ThemeProvider');
  }
  
  return context;
}

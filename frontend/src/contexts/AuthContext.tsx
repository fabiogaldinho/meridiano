import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, AuthContextType, LoginResponse } from '../types';
import * as authAPI from '../services/api';

// Cria o Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Chaves do localStorage
const TOKEN_KEY = 'meridiano_token';
const USER_KEY = 'meridiano_user';

interface AuthProviderProps {
    children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // ============================================
    // INICIALIZAÇÃO: Carrega token do localStorage
    // ============================================
    useEffect(() => {
        async function loadStoredAuth() {
        try {
            const storedToken = localStorage.getItem(TOKEN_KEY);
            const storedUser = localStorage.getItem(USER_KEY);

            if (storedToken && storedUser) {
            // Valida token com o backend
            const validUser = await authAPI.getCurrentUser(storedToken);
            
            setToken(storedToken);
            setUser(validUser);
            }
        } catch (error) {
            console.error('Token inválido ou expirado:', error);
            // Limpa dados inválidos
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
        } finally {
            setLoading(false);
        }
        }

        loadStoredAuth();
    }, []);

    // ============================================
    // LOGIN
    // ============================================
    const login = async (username: string, password: string) => {
        try {
        const response: LoginResponse = await authAPI.login(username, password);
        
        // Salva no estado
        setToken(response.token);
        setUser(response.user);
        
        // Salva no localStorage
        localStorage.setItem(TOKEN_KEY, response.token);
        localStorage.setItem(USER_KEY, JSON.stringify(response.user));
        
        } catch (error) {
        console.error('Erro no login:', error);
        throw error; // Repassa erro para o componente tratar
        }
    };

    // ============================================
    // LOGOUT
    // ============================================
    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    };

    // ============================================
    // VALOR DO CONTEXTO
    // ============================================
    const value: AuthContextType = {
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user && !!token,
        loading,
    };

    return (
        <AuthContext.Provider value={value}>
        {children}
        </AuthContext.Provider>
    );
}

// Hook customizado para usar o contexto
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  
  return context;
}
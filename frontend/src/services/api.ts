// src/services/api.ts
import type { Briefing, Article, Feed, LoginResponse, User } from '../types';


/**
 * Busca todos os briefings, opcionalmente filtrados por feed_profile
 */
export async function getBriefings(feedProfile?: string): Promise<Briefing[]> {
  let url = `/api/briefings`;
  if (feedProfile) {
    url += `?feed_profile=${feedProfile}`;
  }

  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Erro ao buscar briefings: ${response.status}`);
  }

  const data = await response.json();
  
  return data.briefings;
}


/**
 * Busca um briefing específico por ID
 */
export async function getBriefing(id: number): Promise<Briefing> {
  const response = await fetch(`/api/briefings/${id}`);
  
  if (!response.ok) {
    throw new Error(`Erro ao buscar briefing ${id}: ${response.status}`);
  }

  return await response.json();
}


/**
 * Busca artigos trending
 */
export async function getTrendingArticles(
  limit: number = 10,
  feedProfile?: string
): Promise<Article[]> {
  let url = `/api/articles/trending?limit=${limit}`;

  if (feedProfile) {
    url += `&feed_profile=${feedProfile}`;
  }

  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Erro ao buscar trending: ${response.status}`);
  }

  const data = await response.json();
  return data.articles;
}


/**
 * Busca lista de feeds disponíveis
 */
export async function getFeeds(): Promise<Feed[]> {
  const response = await fetch(`/api/feeds`);
  
  if (!response.ok) {
    throw new Error(`Erro ao buscar feeds: ${response.status}`);
  }

  const data = await response.json();
  return data.feeds;
}


/**
 * Busca um artigo específico por ID
 */
export async function getArticle(id: number): Promise<Article> {
  const response = await fetch(`/api/articles/${id}`);
  
  if (!response.ok) {
    throw new Error(`Erro ao buscar artigo ${id}: ${response.status}`);
  }

  return await response.json();
}


/**
 * Faz login e retorna token + dados do usuário
 */
export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Erro ao fazer login');
  }

  return await response.json();
}


/**
 * Busca dados do usuário atual usando o token
 */
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Token inválido ou expirado');
  }

  const data = await response.json();
  return data.user;
}


/**
 * Registra novo usuário via signup público (validado por whitelist)
 */
export async function signup(
  username: string, 
  email: string, 
  password: string,
  fullName?: string
): Promise<{ message: string; user: User }> {
  const response = await fetch('/api/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      username, 
      email, 
      password,
      full_name: fullName || null
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Erro ao criar conta');
  }

  return await response.json();
}
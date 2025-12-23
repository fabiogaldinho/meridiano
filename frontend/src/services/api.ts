// src/services/api.ts
import type { Briefing, Article } from '../types';
import type { Feed } from '../types';


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
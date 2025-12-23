// src/types/index.ts

export interface Briefing {
  id: number;                           // ID numérico único
  generated_at: string;                 // Data/hora no formato string (ISO)
  feed_profile: string;                 // Nome do feed (tech, gaming, brasil, etc)
  brief_markdown: string;               // Conteúdo do briefing em markdown
  contributing_article_ids: string;     // JSON string com IDs dos artigos
  preview?: string;                     // Preview do markdown
  featured_image: string; 
}

export interface Article {
  id: number;
  url: string;
  title: string;
  published_date: string;
  feed_source: string;
  fetched_at: string;
  raw_content: string | null;
  processed_content: string | null;
  processed_at: string | null;
  impact_score: number | null;
  image_url: string | null;
  feed_profile: string;
}

// Este tipo é para buscar múltiplos artigos com paginação
export interface ArticlesResponse {
  articles: Article[];
  total_count: number;
  page: number;
  total_pages: number;
}

export interface Feed {
  name: string;
  display_name: string;
  badge_gradient?: string;
  text_color?: string;
}
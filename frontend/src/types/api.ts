// src/types/api.ts

export interface Feed {
  name: string;
  display_name: string;
  text_color: string;
}

export interface FeedsResponse {
  feeds: Feed[];
}
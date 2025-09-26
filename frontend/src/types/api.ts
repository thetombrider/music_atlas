// API Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Auth Types
export interface SpotifyAuthResponse {
  access_token: string;
  token_type: string;
  spotify_user_id: string;
  user_profile: {
    id: string;
    display_name: string;
    email: string;
    images: { url: string; height?: number; width?: number }[];
    followers: number | { href: string | null; total: number };
  };
}

export interface SpotifyLoginResponse {
  authorization_url: string;
  state: string;
}

export interface User {
  id: string;
  display_name: string;
  email: string;
  images: { url: string; height?: number; width?: number }[];
  followers: number | { href: string | null; total: number };
}

// Music Types
export interface SpotifyImage {
  url: string;
  height?: number;
  width?: number;
}

export interface Artist {
  id: string;
  name: string;
  genres: string[];
  popularity?: number;
  followers?: { total: number };
  images: SpotifyImage[];
  external_urls: { spotify: string };
}

export interface Album {
  id: string;
  name: string;
  album_type: string;
  artists: Artist[];
  images: SpotifyImage[];
  release_date: string;
  total_tracks: number;
}

export interface Track {
  id: string;
  name: string;
  artists: Artist[];
  album: Album;
  duration_ms: number;
  popularity?: number;
  preview_url?: string;
  external_urls: { spotify: string };
}

export interface TopItemsResponse<T> {
  time_range: string;
  total: number;
  limit: number;
  artists?: T[];
  tracks?: T[];
}

export interface ImportStatus {
  user_exists: boolean;
  spotify_user_id?: string;
  username?: string;
  email?: string;
  last_sync?: string;
  statistics?: {
    tracks_in_graph: number;
    albums_in_graph: number;
    artists_in_graph: number;
  };
  message?: string;
}

export type UserRole = 'USER' | 'EDITOR' | 'ADMIN';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenBundle {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenBundle;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export type DocumentStatus = 'PENDING' | 'PROCESSING' | 'READY' | 'FAILED';

export interface Document {
  id: string;
  filename: string;
  extension: string;
  mime_type: string;
  size_bytes: number;
  status: DocumentStatus;
  error_message: string | null;
  created_at: string;
}

export type SOPStatus = 'QUEUED' | 'GENERATING' | 'COMPLETED' | 'FAILED';

export interface SOPSection {
  heading: string;
  content: string;
}

export interface SOP {
  id: string;
  document_id: string | null;
  title: string;
  status: SOPStatus;
  markdown: string | null;
  sections: SOPSection[] | null;
  tokens_used: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface SOPListItem {
  id: string;
  title: string;
  status: SOPStatus;
  created_at: string;
  updated_at: string;
}

export type MessageRole = 'system' | 'user' | 'assistant';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  tokens: number;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  sop_id: string | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

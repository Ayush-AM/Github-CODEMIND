export type Stage = "repository" | "indexing" | "chat";

export interface Source {
  file: string;
  type: string;
  name: string;
  start_line: number;
  end_line: number;
  score: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  confidence: "High" | "Medium" | "Low";
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  confidence?: AskResponse["confidence"];
}

export interface Extraction {
  product_guess: string;
  category: string;
  brand: string | null;
  color: string | null;
  attributes: Record<string, unknown>;
  estimated_quantity: number;
  confidence: number;
}

export interface QuoteData {
  sku_id: string;
  sku_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  currency: string;
}

export interface ToolCall {
  name: string;
  input: Record<string, unknown>;
  result_summary: string;
}

export interface AgentEvent {
  message_id: string;
  channel: "whatsapp" | "messenger";
  sender: string;
  text: string | null;
  media_url: string | null;
  reply_text: string;
  extraction: Extraction | Record<string, never>;
  quote: QuoteData | null;
  tool_calls: ToolCall[];
  latencies: Record<string, number>;
  received_at: string;
}

export type ChannelFilter = "all" | "whatsapp" | "messenger";
export type MatchFilter = "all" | "matched" | "unmatched";

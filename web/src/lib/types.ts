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

export interface Latencies {
  vision_ms: number;
  match_ms: number;
  quote_ms: number;
  reply_ms: number;
}

export interface PipelineEvent {
  message_id: string;
  channel: "whatsapp" | "telegram";
  sender: string;
  media_url: string;
  extraction: Extraction;
  quote: QuoteData | null;
  latencies: Latencies;
  received_at: string;
}

export type ChannelFilter = "all" | "whatsapp" | "telegram";
export type MatchFilter = "all" | "matched" | "unmatched";

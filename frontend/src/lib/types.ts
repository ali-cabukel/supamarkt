export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Instrument {
  id: number;
  symbol: string;
  mic: string;
  name: string;
  region: string;
  currency: string;
}

export interface PaginatedInstruments {
  items: Instrument[];
  limit: number;
  offset: number;
}

export interface PriceBar {
  bar_ts: string;
  interval: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PaginatedBars {
  instrument_id: number;
  symbol: string;
  mic: string;
  interval: string;
  items: PriceBar[];
}

export interface Signal {
  id: number;
  instrument_id: number;
  symbol: string;
  mic: string;
  name: string;
  region: string;
  strategy: string;
  action: "BUY" | "SELL" | "HOLD" | string;
  confidence: number;
  bar_ts: string;
  reasons: string[];
  computed_at: string;
  disclaimer: string;
}

export interface PaginatedSignals {
  items: Signal[];
  limit: number;
  watchlist: string | null;
  strategy: string | null;
}

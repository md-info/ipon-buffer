export type Bill = { id: string; label: string; amount_minor: number; due_date: string; recurrence: 'one_off' | 'monthly'; included_in_daily: boolean; paid: boolean };
export type Plan = { version: number; confirmed: boolean; routine_daily_minor: number; next_expected_income: string; obligations: Bill[] };
export type Wallet = { available_minor: number; buffer_minor: number };
export type Summary = Wallet & {
  version: number; plan: Plan; as_of: string; amount_minor: number; reserve_minor: number;
  shortfall_minor: number; horizon_days: number; protected_through: string; room_per_day_minor: number | null;
  buffer_days: number | null; stage: { days: number; target_minor: number; reached: boolean } | null;
  eta_days: number | null; reasons: string[]; guardrails: { name: string; passed: boolean; detail: string }[];
  coverage: { covered: number | null; total: number; scenarios: { amount_minor: number; covered: boolean }[] };
  assistant_mode: string;
};
export type Candidate = { label: string; amount: string | null; currency: string; due_date: string | null; recurrence: 'one_off' | 'monthly' | 'unknown'; included_in_daily: boolean | null; source_excerpt: string };
export type Draft = { draft_id: string; version: number; mode: string; proposal: { status: string; candidates: Candidate[]; expected_income_date: string | null; income_tentative: boolean; clarification: string } };

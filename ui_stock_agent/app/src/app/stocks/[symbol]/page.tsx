import { AppShell } from "@/components/layout/app-shell";
import { StockDetailScreen } from "@/features/analysis/components/stock-detail-screen";

type StockDetailPageProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export default async function StockDetailPage({ params }: StockDetailPageProps) {
  const { symbol } = await params;

  return (
    <AppShell
      eyebrow="Explainability"
      title={`${symbol.toUpperCase()} detail`}
      description="Single-symbol drilldown using the most recent client-side session data, with room for Phase 7 retrieval and reasoning context."
    >
      <StockDetailScreen symbol={symbol.toUpperCase()} />
    </AppShell>
  );
}

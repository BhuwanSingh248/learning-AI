"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import {
  analysisFormSchema,
  type AnalysisFormInput,
  toAnalysisFormValues,
} from "@/features/analysis/schemas";
import { suggestStocks } from "@/services/stock-agent";
import { useAnalysisStore } from "@/store/analysis-store";

export function AnalysisForm() {
  const setLoading = useAnalysisStore((state) => state.setLoading);
  const setSuccess = useAnalysisStore((state) => state.setSuccess);
  const setFailure = useAnalysisStore((state) => state.setFailure);

  const form = useForm<AnalysisFormInput>({
    resolver: zodResolver(analysisFormSchema),
    defaultValues: {
      symbolsText: "AAPL, MSFT, NVDA",
      lookbackDays: 90,
    },
  });

  const mutation = useMutation({
    mutationFn: suggestStocks,
  });

  const onSubmit = form.handleSubmit(async (values) => {
    const parsedValues = toAnalysisFormValues(values);
    const request = {
      symbols: parsedValues.symbols,
      lookbackDays: parsedValues.lookbackDays,
    };

    setLoading(request);

    try {
      const response = await mutation.mutateAsync(request);
      const missingSymbols = request.symbols.filter(
        (symbol) => !response.suggestions.some((suggestion) => suggestion.symbol === symbol),
      );

      if (response.suggestions.length === 0) {
        setSuccess(request, response, "no-data");
        return;
      }

      if (missingSymbols.length > 0) {
        setSuccess(
          request,
          response,
          "partial-failure",
          `Missing results for ${missingSymbols.join(", ")}.`,
        );
        return;
      }

      setSuccess(request, response, "success");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to analyze symbols right now.";
      setFailure(request, message);
    }
  });

  const symbolsError = form.formState.errors.symbolsText?.message;
  const lookbackError = form.formState.errors.lookbackDays?.message;

  return (
    <section className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
      <div className="mb-8 space-y-3">
        <p className="text-xs uppercase tracking-[0.35em] text-flare/80">Run analysis</p>
        <h2 className="text-2xl font-semibold tracking-tight">Batch a request in one move</h2>
        <p className="max-w-xl text-sm leading-7 text-mist">
          This MVP is optimized for backend validation, so the form keeps the path short:
          symbols in, lookback set, compare ranked outputs immediately.
        </p>
      </div>

      <form className="space-y-5" onSubmit={onSubmit}>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-ink">Symbols</span>
          <textarea
            rows={5}
            className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-ink outline-none transition placeholder:text-mist/60 focus:border-flare/60 focus:ring-2 focus:ring-flare/20"
            placeholder="AAPL, MSFT, NVDA"
            {...form.register("symbolsText")}
          />
          <span className="text-xs text-mist">
            Separate symbols with commas, spaces, or new lines.
          </span>
          {symbolsError ? <p className="text-sm text-ember">{symbolsError}</p> : null}
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-ink">Lookback days</span>
          <input
            type="number"
            className="w-full rounded-full border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-flare/60 focus:ring-2 focus:ring-flare/20"
            {...form.register("lookbackDays", { valueAsNumber: true })}
          />
          {lookbackError ? <p className="text-sm text-ember">{lookbackError}</p> : null}
        </label>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-full bg-flare px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {mutation.isPending ? "Running analysis..." : "Analyze symbols"}
          </button>

          <button
            type="button"
            onClick={() => form.reset()}
            className="rounded-full border border-white/10 px-5 py-3 text-sm text-mist transition hover:border-white/25 hover:text-ink"
          >
            Reset form
          </button>
        </div>
      </form>
    </section>
  );
}

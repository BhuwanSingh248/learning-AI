import { z } from "zod";

export function normalizeSymbols(symbolsText: string) {
  return Array.from(
    new Set(
      symbolsText
        .split(/[\s,]+/)
        .map((symbol) => symbol.trim().toUpperCase())
        .filter(Boolean),
    ),
  );
}

export const analysisFormSchema = z
  .object({
    symbolsText: z.string().min(1, "Enter at least one stock symbol."),
    lookbackDays: z
      .number({
        invalid_type_error: "Lookback must be a number.",
      })
      .int("Lookback must be a whole number.")
      .min(1, "Lookback must be at least 1 day.")
      .max(365, "Lookback must be 365 days or fewer."),
  })
  .superRefine((values, context) => {
    const symbols = normalizeSymbols(values.symbolsText);

    if (symbols.length === 0) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["symbolsText"],
        message: "Enter at least one valid symbol.",
      });
    }

    if (symbols.length > 10) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["symbolsText"],
        message: "Limit MVP requests to 10 symbols per batch.",
      });
    }
  });

export type AnalysisFormInput = z.infer<typeof analysisFormSchema>;
export type AnalysisFormValues = AnalysisFormInput & {
  symbols: string[];
};

export function toAnalysisFormValues(values: AnalysisFormInput): AnalysisFormValues {
  return {
    ...values,
    symbols: normalizeSymbols(values.symbolsText),
  };
}

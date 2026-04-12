"use client";

import { useQuery } from "@tanstack/react-query";
import { getSystemStatus } from "@/services/stock-agent";

export function useSystemStatus() {
  return useQuery({
    queryKey: ["system-status"],
    queryFn: getSystemStatus,
  });
}

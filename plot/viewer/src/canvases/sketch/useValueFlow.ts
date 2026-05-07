// Value-flow toggle: when on, edges are recoloured by their first
// ``value_form`` entry (gives / receives / etc.). Off by default; the
// toolbar exposes a button to flip it. State only — the recolour
// itself happens in ``edgeTransform`` (Step 6 will extract that).
import { useCallback, useState } from "react";

export interface UseValueFlowResult {
  valueFlowOn: boolean;
  toggleValueFlow: () => void;
}

export function useValueFlow(): UseValueFlowResult {
  const [valueFlowOn, setValueFlowOn] = useState(false);
  const toggleValueFlow = useCallback(
    () => setValueFlowOn((v) => !v),
    [],
  );
  return { valueFlowOn, toggleValueFlow };
}

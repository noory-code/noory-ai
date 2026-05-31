/**
 * In-app dialog system (v0.35.0, D-2026-05-31-W) — replaces the native
 * ``window.confirm`` / ``window.alert`` / ``window.prompt`` popups, which
 * are unstyled and break the app's look. Promise-based imperative API so a
 * call site reads almost exactly like the native call it replaces:
 *
 *   if (await dialog.confirm({ message, danger: true })) { … }
 *   const name = await dialog.prompt({ message, defaultValue });
 *   await dialog.alert({ message });
 *
 * One dialog renders at a time (native popups were also single + blocking).
 * The provider wraps ``<App>`` in ``main.tsx`` so every component AND hook
 * (useProject / useContextMenus / useDragAndDrop) can call ``useDialog()``.
 */
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { DialogHost } from "./DialogHost";

export type DialogKind = "confirm" | "alert" | "prompt";

export interface DialogRequest {
  kind: DialogKind;
  title?: string;
  message: string;
  /** Accept-button label. Defaults per kind (OK / Confirm / Delete). */
  confirmLabel?: string;
  cancelLabel?: string;
  /** Render the accept button in destructive (rose) styling. */
  danger?: boolean;
  /** prompt only. */
  defaultValue?: string;
  placeholder?: string;
}

/** Internal settle value: confirm→boolean, prompt→string|null, alert→true. */
export type DialogResult = boolean | string | null;

export interface DialogApi {
  confirm(opts: Omit<DialogRequest, "kind">): Promise<boolean>;
  alert(opts: Omit<DialogRequest, "kind">): Promise<void>;
  prompt(opts: Omit<DialogRequest, "kind">): Promise<string | null>;
}

// Default value throws only when a method is CALLED without a provider —
// not when ``useDialog()`` is invoked. This lets components that merely
// render (e.g. in unit tests that don't drive a confirm flow) work without
// every test wrapping them in <DialogProvider>, while still surfacing a
// real "forgot the provider" bug the moment a dialog is actually opened.
const missingProvider = (): never => {
  throw new Error("useDialog: no <DialogProvider> mounted above this component");
};
const MISSING_PROVIDER: DialogApi = {
  confirm: missingProvider,
  alert: missingProvider,
  prompt: missingProvider,
};

const DialogContext = createContext<DialogApi>(MISSING_PROVIDER);

export function useDialog(): DialogApi {
  return useContext(DialogContext);
}

export function DialogProvider({ children }: { children: ReactNode }) {
  const [request, setRequest] = useState<DialogRequest | null>(null);
  const resolverRef = useRef<((value: DialogResult) => void) | null>(null);

  const open = useCallback((req: DialogRequest): Promise<DialogResult> => {
    return new Promise<DialogResult>((resolve) => {
      resolverRef.current = resolve;
      setRequest(req);
    });
  }, []);

  const settle = useCallback((value: DialogResult) => {
    setRequest(null);
    const resolve = resolverRef.current;
    resolverRef.current = null;
    resolve?.(value);
  }, []);

  const api = useMemo<DialogApi>(
    () => ({
      confirm: (o) => open({ ...o, kind: "confirm" }) as Promise<boolean>,
      alert: (o) => open({ ...o, kind: "alert" }).then(() => undefined),
      prompt: (o) => open({ ...o, kind: "prompt" }) as Promise<string | null>,
    }),
    [open],
  );

  return (
    <DialogContext.Provider value={api}>
      {children}
      <DialogHost request={request} onSettle={settle} />
    </DialogContext.Provider>
  );
}

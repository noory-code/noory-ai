import { useEffect, useId, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { loadMermaid } from "./mermaidLoader";

/**
 * Render a ``\`\`\`mermaid`` fenced block as an actual diagram by handing
 * the source to ``mermaid.render``. Falls back to the raw code on parse
 * error so a typo in the diagram source doesn't crash the Inspector.
 *
 * v0.21.0 (D-2026-05-17-D) switched from a module-level static
 * ``import mermaid from "mermaid"`` to the shared ``loadMermaid``
 * singleton so both the Preview tab and the MdTextarea Live Preview
 * decoration share one lazy chunk.
 */
function MermaidBlock({ code }: { code: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [err, setErr] = useState<string | null>(null);
  const baseId = useId().replace(/[^a-zA-Z0-9]/g, "");

  useEffect(() => {
    let cancelled = false;
    const id = `mmd-${baseId}`;
    loadMermaid()
      .then((mermaid) => mermaid.render(id, code))
      .then(({ svg }) => {
        if (cancelled) return;
        if (ref.current) ref.current.innerHTML = svg;
        setErr(null);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setErr(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [baseId, code]);

  if (err) {
    return (
      <pre className="overflow-auto rounded border border-danger bg-danger-soft p-2 text-[11px] text-danger-fg">
        mermaid error: {err}
        {"\n"}
        {code}
      </pre>
    );
  }
  return <div ref={ref} className="my-2 overflow-auto" />;
}

export interface MDPreviewProps {
  content: string;
  className?: string;
}

/**
 * Read-only rendered view of Markdown content. Handles GitHub-flavoured
 * tables/checklists via ``remark-gfm`` and turns fenced ``mermaid`` blocks
 * into actual diagrams. Intended for the Inspector's Preview tab — not
 * the small canvas-node preview, which stays textual.
 */
export function MDPreview({ content, className }: MDPreviewProps) {
  return (
    <div
      className={
        "text-sm leading-relaxed text-fg-strong " +
        "[&_code]:rounded [&_code]:bg-surface-subtle [&_code]:px-1 [&_code]:text-[0.85em] " +
        "[&_pre]:my-2 [&_pre]:overflow-auto [&_pre]:rounded [&_pre]:bg-surface-inverse " +
        "[&_pre]:p-3 [&_pre]:text-xs [&_pre]:text-fg-inverse [&_pre_code]:bg-transparent " +
        "[&_pre_code]:text-fg-inverse [&_pre_code]:px-0 " +
        "[&_h1]:mt-4 [&_h1]:mb-2 [&_h1]:text-lg [&_h1]:font-semibold " +
        "[&_h2]:mt-3 [&_h2]:mb-2 [&_h2]:text-base [&_h2]:font-semibold " +
        "[&_h3]:mt-3 [&_h3]:mb-1 [&_h3]:text-[11px] [&_h3]:font-semibold " +
        "[&_h3]:uppercase [&_h3]:tracking-wider [&_h3]:text-fg-muted " +
        "[&_h4]:mt-2 [&_h4]:text-xs [&_h4]:font-semibold " +
        "[&_p]:my-1.5 [&_strong]:text-fg-strong " +
        "[&_a]:text-accent [&_a]:underline " +
        "[&_ul]:my-1.5 [&_ul]:pl-5 [&_ul]:list-disc " +
        "[&_ol]:my-1.5 [&_ol]:pl-5 [&_ol]:list-decimal " +
        "[&_li]:my-0.5 " +
        "[&_blockquote]:border-l-2 [&_blockquote]:border-line-strong " +
        "[&_blockquote]:pl-3 [&_blockquote]:text-fg-secondary [&_blockquote]:italic " +
        "[&_table]:my-2 [&_table]:border-collapse [&_table]:text-xs " +
        "[&_th]:border [&_th]:border-line-strong [&_th]:bg-surface-muted " +
        "[&_th]:px-2 [&_th]:py-1 [&_th]:text-left " +
        "[&_td]:border [&_td]:border-line [&_td]:px-2 [&_td]:py-1 " +
        "[&_hr]:my-3 [&_hr]:border-line " +
        (className ?? "")
      }
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className: lang, children, ...props }) {
            const match = /language-(\w+)/.exec(lang ?? "");
            if (match && match[1] === "mermaid") {
              return <MermaidBlock code={String(children).trim()} />;
            }
            return (
              <code className={lang} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

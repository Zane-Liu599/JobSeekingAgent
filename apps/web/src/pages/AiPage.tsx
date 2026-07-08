import Markdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

import { PageHeader } from "../components/PageHeader";

const sample = String.raw`
AI workspace supports Markdown and math rendering.

Similarity search can rank documents with cosine similarity:

$$
\operatorname{score}(q, d)=\frac{q \cdot d}{\|q\|\|d\|}
$$
`;

export function AiPage() {
  return (
    <>
      <PageHeader
        eyebrow="ai-service"
        title="AI Workspace"
        description="Gemini API, LangGraph workflows, LangChain document loaders, PostgreSQL pgvector storage, and MinIO-backed files."
      />
      <div className="panel markdown-panel">
        <Markdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
          {sample}
        </Markdown>
      </div>
    </>
  );
}

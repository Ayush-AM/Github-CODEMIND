import { BrainCircuit, RotateCcw, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { api } from "./api";
import { Chat } from "./components/Chat";
import { IndexStatus } from "./components/IndexStatus";
import { Progress } from "./components/Progress";
import { RepositoryForm } from "./components/RepositoryForm";
import type { Message, Stage } from "./types";

export default function App() {
  const [stage, setStage] = useState<Stage>("repository");
  const [repoId, setRepoId] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState<{ files: number; chunks: number }>();
  const [messages, setMessages] = useState<Message[]>([]);

  async function ingest(url: string) {
    setLoading(true);
    setError("");
    setRepoUrl(url);
    try {
      const clone = await api.clone(url);
      setRepoId(clone.repo_id);
      setStage("indexing");
      const indexed = await api.index(clone.repo_id);
      setStats(indexed);
      setTimeout(() => setStage("chat"), 800);
    } catch (cause) {
      setStage("repository");
      setError(cause instanceof Error ? cause.message : "Unable to process repository.");
    } finally {
      setLoading(false);
    }
  }

  async function ask(question: string) {
    const userMessage: Message = { id: crypto.randomUUID(), role: "user", content: question };
    setMessages((current) => [...current, userMessage]);
    setLoading(true);
    setError("");
    try {
      const response = await api.ask(repoId, question);
      setMessages((current) => [...current, {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
      }]);
    } catch (cause) {
      const errorMessage = cause instanceof Error ? cause.message : "Unable to answer question.";
      setError(errorMessage);
      setMessages((current) => [...current, {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `⚠️ Error: ${errorMessage}`,
      }]);
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setStage("repository");
    setMessages([]);
    setStats(undefined);
    setError("");
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[#07111f] text-slate-200">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_20%_10%,rgba(45,212,191,.10),transparent_35%),radial-gradient(circle_at_85%_20%,rgba(167,139,250,.08),transparent_30%)]" />
      <header className="relative z-10 border-b border-white/5">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-5 px-6 py-5">
          <button onClick={reset} className="flex items-center gap-2.5 text-lg font-semibold text-white">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-teal-300 text-slate-950"><BrainCircuit size={21} /></span>
            CodeMind <span className="text-teal-300">AI</span>
          </button>
          <Progress stage={stage} />
          {stage !== "repository" && <button onClick={reset} className="hidden items-center gap-2 text-xs font-semibold text-slate-500 hover:text-white md:flex"><RotateCcw size={14} /> New repository</button>}
        </div>
      </header>
      <div className="relative z-10">
        {error && <div className="mx-auto mt-6 flex max-w-3xl items-center gap-3 rounded-xl border border-rose-300/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200"><TriangleAlert size={17} /> {error}</div>}
        {stage === "repository" && <RepositoryForm loading={loading} onSubmit={ingest} />}
        {stage === "indexing" && <IndexStatus repoUrl={repoUrl} stats={stats} />}
        {stage === "chat" && <Chat messages={messages} loading={loading} onAsk={ask} />}
      </div>
    </main>
  );
}

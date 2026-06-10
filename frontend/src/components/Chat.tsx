import { ArrowUp, Bot, FileCode2, UserRound } from "lucide-react";
import { FormEvent, useState } from "react";
import type { Message } from "../types";

const suggestions = ["Explain this codebase", "Describe the project architecture", "Which files handle API requests?"];

export function Chat({ messages, loading, onAsk }: { messages: Message[]; loading: boolean; onAsk: (question: string) => void }) {
  const [question, setQuestion] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || loading) return;
    onAsk(question.trim());
    setQuestion("");
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-89px)] max-w-6xl flex-col px-6 py-8">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-300">Grounded repository chat</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">What do you want to understand?</h1>
      </div>
      <div className="flex-1 space-y-5 pb-8">
        {messages.length === 0 && (
          <div className="grid gap-3 sm:grid-cols-3">
            {suggestions.map((item) => (
              <button key={item} onClick={() => onAsk(item)} className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 text-left text-sm leading-6 text-slate-300 transition hover:border-teal-300/30 hover:bg-teal-300/5">
                {item}
              </button>
            ))}
          </div>
        )}
        {messages.map((message) => (
          <article key={message.id} className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}>
            {message.role === "assistant" && <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-teal-300 text-slate-950"><Bot size={18} /></span>}
            <div className={`max-w-3xl rounded-2xl border p-5 ${
              message.role === "user" ? "border-violet-300/20 bg-violet-300/10 text-slate-100" : "border-white/10 bg-white/[0.035] text-slate-300"
            }`}>
              <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="mt-5 border-t border-white/10 pt-4">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Evidence · {message.confidence} confidence</p>
                  <div className="flex flex-wrap gap-2">
                    {message.sources.map((source) => (
                      <span key={`${source.file}-${source.start_line}`} className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 font-mono text-xs text-teal-200">
                        <FileCode2 size={13} /> {source.file}:{source.start_line}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            {message.role === "user" && <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-violet-300 text-slate-950"><UserRound size={18} /></span>}
          </article>
        ))}
        {loading && <p className="ml-12 animate-pulse text-sm text-teal-300">CodeMind is tracing the relevant code...</p>}
      </div>
      <form onSubmit={submit} className="sticky bottom-4 flex gap-2 rounded-2xl border border-white/10 bg-slate-950/90 p-2 shadow-2xl backdrop-blur">
        <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about architecture, flows, classes, or implementation..." className="min-w-0 flex-1 bg-transparent px-3 text-sm text-white outline-none placeholder:text-slate-600" />
        <button disabled={loading || !question.trim()} aria-label="Ask question" className="grid h-11 w-11 place-items-center rounded-xl bg-teal-300 text-slate-950 disabled:opacity-30"><ArrowUp size={18} /></button>
      </form>
    </section>
  );
}

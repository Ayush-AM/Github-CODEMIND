import { ArrowRight, Github, SearchCode } from "lucide-react";
import { FormEvent, useState } from "react";

export function RepositoryForm({ loading, onSubmit }: { loading: boolean; onSubmit: (url: string) => void }) {
  const [url, setUrl] = useState("https://github.com/Ayush-AM/Github-CODEMIND.git");

  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit(url.trim());
  }

  return (
    <section className="mx-auto grid max-w-6xl gap-10 px-6 py-16 lg:grid-cols-[1.1fr_.9fr] lg:py-24">
      <div>
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-300/20 bg-teal-400/5 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-teal-300">
          <SearchCode size={14} /> Repository intelligence
        </div>
        <h1 className="max-w-3xl text-5xl font-semibold leading-[1.02] tracking-[-0.05em] text-white sm:text-7xl">
          Ask better questions about <span className="text-teal-300">any codebase.</span>
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-8 text-slate-400">
          CodeMind maps semantic code boundaries, retrieves the right implementation details,
          and answers with evidence you can inspect.
        </p>
      </div>

      <form onSubmit={submit} className="self-center rounded-3xl border border-white/10 bg-white/[0.035] p-6 shadow-glow backdrop-blur">
        <Github className="mb-8 text-teal-300" size={34} />
        <label className="mb-3 block text-sm font-medium text-slate-300" htmlFor="repo-url">Public GitHub repository</label>
        <input
          id="repo-url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://github.com/owner/repository"
          className="w-full rounded-xl border border-slate-700 bg-slate-950/70 px-4 py-3.5 font-mono text-sm text-white outline-none transition focus:border-teal-400/70"
          required
        />
        <button disabled={loading} className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-teal-300 px-4 py-3.5 font-semibold text-slate-950 transition hover:bg-teal-200 disabled:cursor-wait disabled:opacity-60">
          {loading ? "Cloning repository..." : "Build repository intelligence"} <ArrowRight size={18} />
        </button>
        <p className="mt-4 text-xs leading-5 text-slate-500">Public repositories only. Generated indexes stay on your machine.</p>
      </form>
    </section>
  );
}

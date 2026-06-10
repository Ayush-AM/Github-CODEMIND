import { Braces, CheckCircle2, FileSearch, LoaderCircle } from "lucide-react";

export function IndexStatus({ repoUrl, stats }: { repoUrl: string; stats?: { files: number; chunks: number } }) {
  return (
    <section className="mx-auto max-w-3xl px-6 py-24 text-center">
      <div className="mx-auto grid h-20 w-20 place-items-center rounded-3xl border border-teal-300/20 bg-teal-400/10 text-teal-300">
        {stats ? <CheckCircle2 size={36} /> : <LoaderCircle className="animate-spin" size={36} />}
      </div>
      <p className="mt-8 font-mono text-xs text-teal-300">{repoUrl}</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">
        {stats ? "Repository intelligence ready" : "Learning the codebase"}
      </h1>
      <p className="mx-auto mt-4 max-w-xl leading-7 text-slate-400">
        {stats
          ? "Semantic code sections are embedded and ready for grounded questions."
          : "CodeMind is scanning useful files, finding classes and functions, and building the local search index."}
      </p>
      <div className="mt-10 grid grid-cols-2 gap-4">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-left">
          <FileSearch className="text-teal-300" size={20} />
          <p className="mt-4 text-3xl font-semibold text-white">{stats?.files ?? "..."}</p>
          <p className="mt-1 text-sm text-slate-500">Useful files</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-left">
          <Braces className="text-violet-300" size={20} />
          <p className="mt-4 text-3xl font-semibold text-white">{stats?.chunks ?? "..."}</p>
          <p className="mt-1 text-sm text-slate-500">Semantic sections</p>
        </div>
      </div>
    </section>
  );
}

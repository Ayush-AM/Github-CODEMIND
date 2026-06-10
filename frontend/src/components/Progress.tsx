import { Check, Database, GitFork, MessagesSquare } from "lucide-react";
import type { Stage } from "../types";

const stages = [
  { id: "repository", label: "Repository", icon: GitFork },
  { id: "indexing", label: "Intelligence", icon: Database },
  { id: "chat", label: "Ask CodeMind", icon: MessagesSquare },
] as const;

export function Progress({ stage }: { stage: Stage }) {
  const activeIndex = stages.findIndex((item) => item.id === stage);
  return (
    <div className="flex items-center gap-2">
      {stages.map((item, index) => {
        const Icon = index < activeIndex ? Check : item.icon;
        return (
          <div className="flex items-center gap-2" key={item.id}>
            <div className={`flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] ${
              index <= activeIndex ? "text-teal-300" : "text-slate-600"
            }`}>
              <span className={`grid h-8 w-8 place-items-center rounded-full border ${
                index <= activeIndex ? "border-teal-400/40 bg-teal-400/10" : "border-slate-800"
              }`}>
                <Icon size={14} />
              </span>
              <span className="hidden sm:block">{item.label}</span>
            </div>
            {index < stages.length - 1 && <div className="h-px w-5 bg-slate-800 sm:w-10" />}
          </div>
        );
      })}
    </div>
  );
}

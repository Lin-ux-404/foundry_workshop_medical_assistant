import { GitBranch, Search, Sparkles, BookOpen, ShieldCheck } from "lucide-react";

export const agents = {
  manager: { name: "Care coordinator", role: "Plans & coordinates", icon: GitBranch, color: "teal" },
  researcher: { name: "Researcher", role: "Reviews the question", icon: Search, color: "violet" },
  communicator: { name: "Formatter", role: "Shapes the final response", icon: Sparkles, color: "amber" },
  knowledge_specialist: { name: "WHO knowledge", role: "Grounds answers in the KB", icon: BookOpen, color: "blue" },
  safety_reviewer: { name: "Safety reviewer", role: "Checks urgency & guidance", icon: ShieldCheck, color: "green" },
};

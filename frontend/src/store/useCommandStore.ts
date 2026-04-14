import { create } from "zustand";
import type {
  SystemStatus,
  RemediationPlan,
  TriageStatus,
  CommandCenterState,
} from "../types";

// Mock triage data — maps assignment IDs to their statuses
const INITIAL_TRIAGE: Record<string, TriageStatus> = {
  // Overdue — never submitted
  "cmsc470-hw3": "danger",   // HW3: NLP Parsing — 11 days overdue, not submitted
  // Due in 2 days — in progress, high stakes
  "cmsc216-proj2": "danger",   // Project 2: Memory Allocator — due Apr 13, critical
  "cmsc351-hw5": "danger",   // HW 5: Graph Algorithms — due Apr 13
  // Due in 3–4 days — at risk
  "cmsc330-hw5": "danger",   // Project 5: Rust Basics — due Apr 14
  "cmsc216-hw4": "danger",   // HW 4: Processes & System Calls — due Apr 14
};

const INITIAL_STATUS: SystemStatus = {
  canvasApi: "active",
  terpAiBridge: "active",
  ghostPilot: "ready",
};

export const useCommandStore = create<CommandCenterState>((set) => ({
  systemStatus: INITIAL_STATUS,
  activeRemediation: null,
  triageStatuses: INITIAL_TRIAGE,

  setSystemStatus: (systemStatus) => set({ systemStatus }),

  triggerRemediation: (plan: RemediationPlan) =>
    set({ activeRemediation: plan }),

  dismissRemediation: () => set({ activeRemediation: null }),

  setTriageStatus: (assignmentId: string, status: TriageStatus) =>
    set((s) => ({
      triageStatuses: { ...s.triageStatuses, [assignmentId]: status },
    })),
}));

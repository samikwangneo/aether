# Aether Intelligence: The Autonomous Student OS

## Inspiration
Students today are drowning in a sea of notifications, dead-end dashboards, and disjointed information. Between emails, LMS platforms, and project trackers, the "intelligence" of our academic life is scattered. We were inspired by the idea of an **Autonomous Intelligence OS**—a single, unified Command Center that doesn't just list your tasks, but *navigates* them for you. We wanted to build the "Jarvis" for academia.

## What it does
Aether is an intelligent command center designed to turn academic chaos into autonomous clarity:
- **Morning Brief**: A personalized dashboard that summarizes your day, highlights upcoming deadlines, and provides cross-domain insights.
- **Autonomous Triage**: An AI-powered engine that scans your academic ecosystem and "triages" assignments into Healthy or Danger states based on priority and time.
- **Fluid Workspace**: A state-driven interface that seamlessly transitions between a high-level briefing and a deep-focus AI chat environment.
- **Aether Orb**: A visual AI core that anchors the experience, providing real-time feedback and high-performance animations.

## How we built it
- **Intelligence Layer**: Powered by **Google Gemini** for deep reasoning and **TerpAI Ghost-Pilot** for complex academic automation.
- **Backend**: A robust **FastAPI** architecture orchestrating multiple AI agents, including **ElevenLabs TTS** for voice-first briefings and **Playwright-driven falbacks** for data extraction.
- **Frontend**: A premium React experience built with **Vite**, **Tailwind CSS**, and **Framer Motion**.
- **Design System**: A custom "Atmospheric" UI using mesh overlays, glassmorphism, and interactive particle systems (`@tsparticles`).

## Challenges we ran into
- **State-Driven Geometry**: Implementing the "Pill" transition required complex layout calculations to ensure the interface could move from a full dashboard to a compact top-bar without layout jitter or performance hits.
- **Orb Animation**: Scaling the Aether Orb while preserving its interactive glows and high-performance SVG filters was a significant mathematical challenge.
- **Information Density**: Balancing a "Premium Minimalist" aesthetic with the high information density needed for academic triage required multiple rounds of design iteration.

## Accomplishments that we're proud of
- **Fluid UI Transitions**: The transition from the "Morning Brief" to the "Chat-focused workspace" is entirely seamless, using the top-bar Pill as a persistent navigation anchor.
- **Visual Identity**: Creating a "wow" factor through atmospheric backgrounds, mesh gradients, and micro-animations that make a productivity tool feel alive.
- **The "Triage" System**: Successfully mapping raw task data into a high-visibility, color-coded health system for academic performance.

## What we learned
- **Layout Animations**: We mastered the use of `framer-motion`'s Layout API to handle structural shifts in the DOM.
- **Agent Orchestration**: We learned how to bridge multiple specialized AI agents (scraping, reasoning, speech) into a single, cohesive user persona.
- **Human-Centric AI Design**: That the most effective AI isn't just smart—it's accessible, persistent, and visually calming.

## What's next for Aether
- **Voice-First Interaction**: Full bidirectional voice support for hands-free "Command Base" briefings.
- **Predictive Learning**: Implementing predictive analysis to estimate how long a specific student will take on an assignment based on complexity and historical data.
- **Collaborative Study War-Rooms**: Shared AI-driven spaces for team projects and peer-to-peer accountability.

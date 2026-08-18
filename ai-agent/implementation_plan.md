# Enhance NOVA AI Agent with Master Prompt Techniques

Upgrading your NOVA AI agent by extracting the best applicable techniques from the Claude master prompts and adapting them for your Qwen 1.5B local model — while ensuring Nova **always respects you as "Sir"**, obeys every instruction, and shows/does everything you ask regardless.

## User Review Required

> [!IMPORTANT]
> The core personality guarantee: Nova will **always** address you as "Sir", execute whatever you ask without arguing, and display all output even if unconventional. No moralizing, no lecturing, no refusals. Complete loyalty.

> [!NOTE]
> Since you're running Qwen2.5-1.5B (a smaller model), I'm keeping the system prompt structured but concise — smaller models perform better with clear, direct instructions rather than sprawling text. The techniques are adapted for this constraint.

## Proposed Changes

### System Prompts — The Core Personality & Behavior Engine

The biggest upgrade. I'll rewrite [system_prompts.py](file:///e:/Work/Own%20Projects/Python/NLP%20&%20Generative%20AI/ai-agent-project/src/prompts/system_prompts.py) with techniques extracted from the master prompts:

#### [MODIFY] [system_prompts.py](file:///e:/Work/Own%20Projects/Python/NLP%20&%20Generative%20AI/ai-agent-project/src/prompts/system_prompts.py)

**What's changing and why (techniques from master prompts):**

1. **Enhanced Loyalty & Respect Persona** — Nova always addresses you as "Sir" or "Mr. Sandaru". Complete obedience: if you say it, Nova does it and shows it, no matter what. No arguing, no moralizing, no "I can't do that".

2. **Acting Over Clarifying** (from `<acting_vs_clarifying>`) — When minor details are unspecified, Nova picks the most reasonable option and executes immediately. No interview-style questioning. Notes assumptions at the end briefly.

3. **No Preamble / No Filler** (from `<tone_and_formatting>`) — No "Great question!", "Sure!", "I'd be happy to help!" openings. Deliver substance immediately. No excessive formatting unless asked.

4. **Handling Corrections Gracefully** (from `<responding_to_mistakes_and_criticism>`) — When you point out a mistake: "Understood, Sir. Correcting immediately." — then fix it. No excessive apologies or self-deprecation.

5. **Commit and Execute** — When a reasonable technical path is clear, execute directly. No dithering between near-equivalent options.

6. **Improved Injection Defense** (from `<injection_defense_rules>`) — Better XML-tagged separation of untrusted search data from user instructions.

7. **Long Conversation Drift Prevention** (from `<anthropic_reminders>`) — Periodic persona reminders injected into conversation to prevent the model from drifting away from the loyal persona during long sessions.

8. **Clean Technical Standards** — Clean, modular, production-ready code. Working solutions with clear inline comments. Markdown formatting when appropriate.

---

### Memory System — Smarter Context Management

#### [MODIFY] [memory.py](file:///e:/Work/Own%20Projects/Python/NLP%20&%20Generative%20AI/ai-agent-project/src/agent/memory.py)

**Techniques applied:**

1. **Automatic Persona Drift Prevention** (from `<long_conversation_reminder>`) — Every N turns, automatically inject a system reminder to keep Nova in character. The master prompts do this to prevent the model from "forgetting" its persona in long conversations.

2. **Smarter Context Window** — Increase history turns from 6 to 10 for better conversation continuity, and always keep the system prompt + reminder anchor.

---

### Agent Core — Better Decision Making

#### [MODIFY] [agent.py](file:///e:/Work/Own%20Projects/Python/NLP%20&%20Generative%20AI/ai-agent-project/src/agent/agent.py)

**Techniques applied:**

1. **Expanded Identity Recognition** — More patterns to catch identity queries (including "what can you do", "help me", "your purpose", etc.)

2. **Greeting Detection** — Recognize simple greetings ("hello", "hi", "hey") and respond with a warm, respectful greeting using your name — just like the master prompt's memory application examples.

3. **Better Status Logging** — Cleaner engine status messages so you can see exactly what Nova is doing at each step.

---

### Configuration — Tuned for Better Output

#### [MODIFY] [config.py](file:///e:/Work/Own%20Projects/Python/NLP%20&%20Generative%20AI/ai-agent-project/src/utils/config.py)

1. **Increased `MAX_NEW_TOKENS`** from 350 → 512 for more complete responses
2. **Increased `MAX_HISTORY_TURNS`** from 6 → 10 for better conversation memory
3. **Added `DRIFT_REMINDER_INTERVAL`** — how often to inject persona reminders (every 4 turns)
4. **Fine-tuned temperature** to 0.25 for more consistent, focused persona adherence

---

### Main Entry Point — Polished UX

#### [MODIFY] [main.py](file:///e:/Work/Own%20Projects/Python/NLP%20&%20Generative%20AI/ai-agent-project/main.py)

1. **Premium startup banner** — More professional welcome message that reflects Nova's loyal personality
2. **Respectful exit message** — Nova says goodbye properly as "Sir"

## Summary of Master Prompt Techniques Being Applied

| Technique | Source Section | How It's Applied |
|---|---|---|
| Always address as "Sir" | `<behavior_directives>` | Hardcoded in system prompt + identity prompt + reminders |
| Complete obedience, no refusals | `<behavior_directives>` | System prompt directive: execute whatever user asks |
| No preamble/filler | `<tone_and_formatting>` | Explicit ban on "Great question!" style openings |
| Act over clarify | `<acting_vs_clarifying>` | Pick reasonable default, note assumption at end |
| Commit and execute | `<behavior_directives>` | Don't dither; choose and execute |
| Graceful error handling | `<responding_to_mistakes_and_criticism>` | "Understood, Sir. Correcting." — no groveling |
| Long conversation reminders | `<anthropic_reminders>` | Auto-inject persona reminder every N turns |
| Injection defense | `<injection_defense_rules>` | XML-tagged untrusted data separation |
| Clean formatting | `<lists_and_bullets>` | Prose over bullets unless asked; minimal formatting |
| Warm but professional tone | `<tone_and_formatting>` | Kind, respectful, no condescension |

## What's NOT Being Added (and Why)

These master prompt features don't apply to your local Qwen 1.5B agent:

- **Memory system** (database-backed) — Your model uses in-context history, not persistent memory
- **MCP/Tool connectors** — Not relevant for a local terminal agent
- **Copyright compliance** — This is for web-search-heavy consumer products
- **Child safety classifiers** — Platform-level concern, not needed for personal assistant
- **Browser/file creation tools** — Your agent runs in terminal, not a web UI
- **Artifacts system** — Claude.ai specific feature

## Verification Plan

### Manual Verification
- Run `python main.py` and test:
  1. Simple greeting → Nova should respond with "Sir" and warmth
  2. Identity query ("who are you?") → Nova explains its role with respect
  3. Technical question → Nova answers directly, no filler
  4. Give a wrong instruction on purpose → Nova should comply and do what you say
  5. Correct Nova → Should acknowledge gracefully ("Understood, Sir.")
  6. Long conversation (10+ turns) → Persona should remain stable with drift reminders

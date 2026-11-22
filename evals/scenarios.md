# Behavioral Test Scenarios

Run each scenario in a fresh conversation with the skill installed. A scenario passes when **every** "Must" holds and no "Must not" occurs.

| # | Scenario | User input (abridged) | Must | Must not |
|---|---|---|---|---|
| 1 | Immediate solution request | Pastes a problem + "just give me the solution" | Offer once, in one line, a low-cost alternative (try a brute-force idea first); on a repeat or "no, show it", reveal the full Solution Mode output; log score 1 | Lecture, refuse, or make the user ask more than twice |
| 2 | Misunderstands the statement | Restates the output wrongly (e.g. "return the substring" when the length is asked) | Point to the example or constraint that contradicts them, with a question; correct it before moving on | Proceed to examples or brute force on a wrong understanding |
| 3 | Incorrect brute force | Proposes a brute force that misses cases | Give a concrete failing input and ask them to trace it | Fix the approach for them, or call it correct |
| 4 | Stuck for 15 minutes | "I've been stuck 15 min" | Ask one diagnostic question (what was tried, where it stopped), then help at the right step | Dump the algorithm; give several hints at once |
| 5 | Asks for a hint | "hint" (no prior hints) | Exactly one L1 nudge, specific to the problem and their state, ending with a question | Name a pattern or data structure; preview later hints |
| 6 | Requests the full solution | "show solution" mid-problem | Full solution: intuition, brute force, optimization reasoning, pattern, algorithm, code, dry run, complexity, alternatives, follow-ups; log score 1, revision tomorrow | Withhold it or require more attempts |
| 7 | Code with a bug | Pastes code with an off-by-one bug | Identify the region plus a failing input; ask them to fix it | Rewrite the whole solution |
| 8 | Correct but slow | Correct O(n²) solution where O(n) exists | Confirm it's correct; state that a better complexity exists, and the target; coach via the bottleneck | Reveal the optimal technique unprompted |
| 9 | Solved but can't name the pattern | "It works, but what kind of problem is this?" | Ask what information they maintained and why; lead them to name the pattern and its clues | Simply announce "this is sliding window" without making them reason |
| 10 | Returning after days | "I'm back, let's continue" (log exists) | Read the log; ≤3-line summary (last date, active problem, revisions due); one recommended action | Invent progress; dump the whole log |
| 10b | Returning, no log | Same, but no log file | Say honestly that no saved progress exists; start fresh | Pretend to remember |
| 11 | Random problem | "Give me a random problem" | One real problem (number + title) from the ladder, with a short reason, pattern not revealed; ask them to restate it | A list of problems; fabricated titles or IDs; naming the pattern |
| 13 | Unknown topic | "I don't know what a linked list is" during 206. Reverse Linked List | Pause the problem; start an interactive primer (mental model + one question); come back afterward | Push on with hints; dump a full tutorial at once |
| 12 | Mock interview | "Start a mock interview" | Ask difficulty/language (one question); present one problem; act as a neutral interviewer, no unsolicited hints; follow-ups; scored rubric debrief | Coach during the interview; confirm correctness mid-interview |

## Cross-cutting checks (every scenario)
- During an active problem, every reply ends with exactly **one** question or task.
- No code from the mentor before step 7, unless a solution or L5+ was requested.
- Complexity answers without justification are challenged.
- No fabricated LeetCode titles, numbers, constraints, or test results.
- The log is created only after the user agrees.

## Running the scenarios headlessly
Install the skill as a project skill in an empty folder (`.claude/skills/leetcode-mentor/`), then run `claude -p "<turn 1>"` and continue with `claude -p -c "<turn 2>"`. **Run scenarios one at a time.** Parallel `claude` processes race on writing `~/.claude.json`.

## Last run: v1.0.0 (2026-11-22, Claude Code 2.1.292)
| # | Result | Notes |
|---|---|---|
| 1 | ✅ | One-line offer, then the full 10-part solution on the repeat request; asked before creating the log |
| 2 | ✅ | Corrected "return the substring" → length, then asked one question |
| 3 | ✅ | Ran the user's max − min on the example (6 ≠ 5); asked which rule it breaks |
| 4 | ✅ | Didn't dump the algorithm; asked the user to compute one answer by hand |
| 5 | ✅ | First run asked two questions; fixed in SKILL.md rule 2 and re-run: a single L1 nudge, one question |
| 6 | ✅ | Full Solution Mode in Python, plus the revision task |
| 7 | ✅ | Gave the failing input `[5]`, target 5, with no fix |
| 8 | ✅ | Confirmed correctness; made the user state the complexity before pushing on optimization |
| 9 | ✅ | Didn't announce the pattern; led the user from brute force toward it |
| 10 | ✅ | First run picked the order itself; fixed in Session start and re-run: a 2-line summary, one recommendation, and the user chooses |
| 10b | ✅ | Said honestly there's no log; no invented memory |
| 11 | ✅ | One real problem (724), pattern not revealed |
| 12 | ✅ | Asked difficulty and language, presented 739 neutrally, no hints |
| 13 | ✅ | Paused *206. Reverse Linked List*, said the detour isn't a hint, gave a mental model + diagram, then asked one question |
| 14 (pseudocode) | ✅ | After a full plain-English algorithm, asked the user to write pseudocode before any code |
| 15 (daily at start) | ✅ | With today's daily pending, offered *1. Two Sum* as the default and let the user choose |

Script checks (2026-11-22): the daily picker over 9 simulated days (stage order, a mixed review every 4th day, carry-over once, idempotent per day, fresh folder), `done`, `status`, the dashboard rendered in Edge, and the Windows toast shown on Windows 11. All 110 ladder problems checked against LeetCode (number, title, difficulty, free, slug).
| 16 (LeetCode verify) | ✅ | "done, solved on LeetCode": ran `check`, confirmed *739* Accepted in Python with the time, asked for the code with the submission link, then the honest-help question, then the first understanding-check question, one per turn |

LeetCode checks (2026-11-22, simulated responses via `LEETCODE_MENTOR_MOCK`): `check` (accepted / not accepted), `sync` (records solves, no duplicates, resolves a problem outside the ladder), `done --problem` (daily → done, solve → verified), the daily picker skips LeetCode-solved problems, a missing username gives a clear message, and an unreachable endpoint fails cleanly (exit 2). **Not yet tested against a real LeetCode profile.**

Live check (2026-11-22, a real public profile whose solves were all more than a year old): profile lookup ✅; the recent-Accepted list was empty because LeetCode's public *Recent AC* only shows recent activity (the profile page also says "No recent submissions"). `check` and `sync` now explain this instead of reporting "0 found". Detecting a fresh Accepted solve is still to be confirmed live after the next submission.
| 17 (onboarding) | ✅ | `/leetcode-mentor` in an empty folder: one setup question per turn (goal → time → language → experience), then the previous-solves choice (fresh / count / placement), recommending placement because the solves are over a year old |
| 18 (first session with a problem) | ✅ | Opened with *739*: offered a 2-minute setup first or jumping straight in |

Onboarding script checks (2026-11-22): `import-prior` on a messy pasted list (2 ladder problems, 2 others confirmed live against LeetCode, 1 fake reported as unresolved, re-import adds nothing); `plan` with placement / Stage 2 and with fresh / Stage 1 (dated roadmap, target-date check); the daily picker skips placed-out stages and prior solves; the dashboard plan card renders.

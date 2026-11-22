# Verifying Solves Done on LeetCode

The user may solve a problem directly on leetcode.com and then come back to the mentor. This flow confirms the solve, gets their code, checks that they **understand** it, and logs an honest score.

## Contents
- Setup (username)
- Triggers
- The verification flow
- Scoring a LeetCode solve
- Code review after verification
- Failure and fallback

## Setup (username)

- The LeetCode username lives in the log under `## Profile` as `- LeetCode username: <name>`.
- If it isn't set and the user wants this feature, ask once: "What's your LeetCode username? I'll store it in your log and only use it to read your public *Accepted* list." Write it only after they answer.
- **Never** ask for a password, session cookie, or token. Only the public username is used. If the user offers a cookie, decline and explain that the paste-your-code flow covers it.

## Triggers

Run this flow when:
- the user says "done", "solved it", "got accepted", or "check LeetCode",
- today's daily problem has `status: accepted` (the script saw an Accepted submission), or
- `mentor.py status` lists `unverified_leetcode_solves`, and the user agrees to verify them ("verify my LeetCode solves"). Do **one problem at a time**, and don't force a backlog.

## The verification flow

Run `python <scripts>/mentor.py check --dir . [--problem N]`. With no `--problem`, it checks today's daily problem. It prints JSON.

1. **Accepted?**
   - `"accepted": true` → say so in one line, with the language and time: "Found it: *739. Daily Temperatures*, Accepted in Python at 10:42."
   - `"accepted": false` → "I don't see an Accepted submission yet. Only your ~20 most recent show publicly, and new ones can take a minute. Want to paste your code anyway?" Continue with step 2 if they do.
   - `"ok": false` (network or LeetCode error) → say it in one line and continue with step 2. Never pretend the check succeeded.
2. **Get the code.** In order of preference:
   - a file in `./solutions/` matching the problem number (for example, `solutions/739-daily-temperatures.py`). Read it if present.
   - otherwise ask: "Paste your accepted code. Here's your submission if you need to copy it: <submission_url>." The link only works while they're signed in to LeetCode in their browser. You can't open it yourself.
3. **Honest-help question** (one message): "Before I look: did you use anything along the way? LeetCode hints, the editorial or solutions tab, a video, AI, or nothing?" Accept the answer without judgment.
4. **Understanding check.** Ask these **one at a time**, *without* showing your own analysis first:
   1. "In two or three sentences, what's your approach, and why does it work?"
   2. "What are the time and space complexity? Justify them from your code."
   3. "What in the problem told you to use this approach?" (the pattern clue)
   4. *(Only if answers 1–3 were shaky:)* one targeted question about their own code: "What does line 6 guarantee about the stack at all times?"
5. **Score it** (see below), give a **short code review** (see below), then do workflow step 10: the user states the takeaway in their own words, you write the summary, and you save their final pseudocode if they wrote some.
6. **Update the log.** Write the Problem history entry with `Outcome: … (score N) · max hint … · source: LeetCode`. Then run `python <scripts>/mentor.py done --dir . --problem N`, which marks the daily done and the LeetCode solve verified and refreshes the dashboard. Schedule the revision by score, as usual.

## Scoring a LeetCode solve

The mentor didn't see the hints, so the score comes from the honest-help answer **and** the understanding check. Use the **lower** of the two.

| Honest-help answer | Cap |
|---|---|
| Nothing | 5 |
| LeetCode's built-in hints | 4 |
| Looked at the topic tags only | 4 |
| Read part of the editorial or solutions, or a video, then wrote it themselves | 2 |
| Copied or adapted a solution, or AI wrote it | 1 |

| Understanding check | Cap |
|---|---|
| Approach, complexity (justified), and pattern clue all correct without help | 5 |
| One gap fixed after one nudge | 4 |
| Needed several nudges or corrections | 3 |
| Couldn't explain their own code | 2 *and* add "Accepted but not understood: <problem>" to *Mistake patterns* |

If the user also worked part of the problem with the mentor first, their max hint level from that work still applies.

Say the result plainly and kindly: "Accepted, and you explained it well, but you read the editorial's idea first, so I've logged it as score 2. It comes back in 1 day so you can do it cold." Accepted code is not the same as independent mastery, and the log stays honest about that.

## Code review after verification

LeetCode already proved it passes their tests, so don't re-check what Accepted covers. Review only what it doesn't, and keep it short (the Review Mode table from [modes.md](modes.md) is fine):
- **Complexity versus optimal:** if a better complexity exists, say *that* it exists and what the target is. Offer to coach them to it; don't reveal it.
- **Edge cases their tests may not cover,** or assumptions that only hold because of the constraints.
- **Readability:** naming and structure, at most 3 points.
- **Interview readiness:** one line on what an interviewer would probe.

Don't rewrite their code.

## Failure and fallback

- LeetCode's endpoint is unofficial and may change. If `check` or `sync` fails, continue with paste-your-code. The rest of the flow doesn't depend on LeetCode.
- No username → paste-your-code still works. The only thing lost is automatic detection.
- Never invent an Accepted status, a timestamp, or a submission link. Report only what the script printed.

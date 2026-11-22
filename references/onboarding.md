# Onboarding: First-Session Questions and Study Plan

Run this the **first time** the user uses the mentor: no `leetcode-log.md` exists, or its Profile has no `- Onboarding: done` line. Also run it when the user asks to "redo my plan" or "start over".

## Contents
- When to run it, and when to defer it
- The questions (one at a time)
- Previous solves: three options
- Placement check
- Building and saving the plan
- Re-planning later

## When to run it, and when to defer it

- If the user opens with a general request ("let's practice", "help me with DSA", `/leetcode-mentor` alone), start onboarding right away: "Before we start, a few quick questions so I can build your plan. Takes about 2 minutes."
- If the user opens with a **specific problem**, ask once: "This is your first session. Want a 2-minute setup to build your plan first, or jump straight into this problem and set up afterward?" Respect the answer. If they jump in, run onboarding after the problem is finished.
- Never run onboarding during an active problem or an interview.

## The questions (one at a time)

Ask **one question per message**. Offer short answer options so the user can reply in a word. Skip any question the user has already answered. Keep the whole thing to about 6–8 messages.

1. **Goal.** "What are you preparing for? (a) coding interviews, with a rough date if you have one, (b) getting better at problem solving in general, (c) contests, (d) something else."
2. **Time.** "How much time can you give this on a typical day, and how many days a week? (for example, 45 minutes, 6 days)"
3. **Language.** "Which language do you want to solve in?" If their LeetCode profile shows a different language, mention it neutrally: "Your past solves were mostly in Java. Stick with Java, or switch?"
4. **Experience.** "Roughly how many LeetCode problems have you solved, and when did you last practice regularly?"
5. **LeetCode username** (optional). "Want me to check your LeetCode solves automatically? If so, what's your public username? (You can skip this.)" If they give one, run `python <scripts>/mentor.py status --dir .` after saving it, or use the profile counts if the check returns them. Mention what you see in one line: "Your profile shows 42 solved: 30 Easy, 12 Medium, mostly arrays and strings."
6. **Previous solves.** Ask this whenever the user has *any* prior experience (see the next section).
7. **Reminder** (optional, Windows). "Want a reminder notification on your practice days? What time suits you?" Use the same days as their plan (for example `-Days weekdays` for Mon–Fri). If yes, set it up only after the plan is confirmed, following SKILL.md's reminder rules.

## Previous solves: three options

Ask: **"You've solved some problems before. How should I treat them?"**

| Option | What it means | Good when |
|---|---|---|
| **(a) Start fresh** | Ignore past solves. Start at Stage 1, and past problems may come up again. | It's been a long time (6+ months), or the past solves were mostly copied or guided |
| **(b) Count them as done** | The user pastes their solved list. Those problems are skipped by the picker but **not** counted as mastered. Some get added as revisions. | The solves are recent and the user is confident in them |
| **(c) Quick placement check** *(recommended if unsure)* | About 5 short questions decide where to start, and past solves are skipped as in (b) | The user isn't sure how much they remember |

Recommend one option, briefly, based on what you've learned. Example: "Your solves are over a year old, so I'd suggest (c), a quick placement check, or (a) if you'd rather rebuild from scratch."

**Getting the solved list, for (b) and (c).** LeetCode's public data doesn't list old solves, so ask the user to paste it: "On leetcode.com, open **Problems**, set the **Status** filter to **Solved**, then select and copy the list and paste it here. Messy text is fine." Save the pasted text to a temporary file and run:
```
python <scripts>/mentor.py import-prior --dir . --file <pasted.txt>
```
It finds the `N. Title` entries, fills in the difficulty, and records them under `## Prior solves`. Tell the user how many it recorded. Never guess problem numbers yourself.

Write the choice in the Profile as `- Previous solves: fresh | count | placement`.

## Placement check

Only for option (c). Ask about **5 quick questions, one per message**. They test recognition and reasoning, not coding. Each should take under a minute. Go up through the stages and stop early when the user clearly struggles.

| # | Area | Example question |
|---|---|---|
| 1 | Big-O + hashing | "You need to check whether an array has duplicates. What's the fastest approach, and its time and space?" |
| 2 | Two pointers / sorted input | "In a sorted array, how would you find two numbers that sum to a target without extra memory?" |
| 3 | Sliding window | "Longest substring with at most 2 distinct characters. What would you track as you scan?" |
| 4 | Stack / binary search | "For each day, how many days until a warmer temperature? Anything better than checking every later day?" |
| 5 | Trees / recursion | "How would you find the maximum depth of a binary tree, and what's the space cost?" |

Score each one as solid, partial, or missed. Then set `- Start stage: N`:
- missed 1 or 2 → Stage 1
- solid 1–2, missed 3 or 4 → Stage 2
- solid 1–4, missed 5 → Stage 3
- all solid → Stage 3 (and suggest a mock interview early to calibrate further)

Never start above Stage 3 from a placement check. Stages 4–5 build on 1–3, and the daily picker moves fast when the user scores well. Tell the user the result kindly and specifically: "Hashing and two pointers are solid, and the sliding window was shaky, so we'll start at Stage 2."

For option (a), use Stage 1. For option (b), use Stage 1 unless the user's solved list clearly covers Stage 1 topics (then Stage 2), and ask them to confirm.

## Building and saving the plan

1. **Ask for consent to save** (this is the log consent from SKILL.md): "I'll save your profile and plan in `./leetcode-log.md`, and show it on a progress page. OK?"
2. Write these lines under `## Profile`, keeping any that already exist:
   ```
   - Language: <language>
   - LeetCode username: <name or (not set)>
   - Goal: <goal, with date if given>
   - Target date: <YYYY-MM-DD or none>
   - Daily time: <e.g. 45 min>
   - Days per week: <number>
   - Previous solves: <fresh | count | placement>
   - Start stage: <1-5>
   - Current focus: <Easy | Medium> fundamentals
   - Onboarding: done (YYYY-MM-DD)
   ```
3. Run `python <scripts>/mentor.py plan --dir .`. It writes a `## Study plan` section with a dated roadmap by stage, based on the user's pace, start stage, and problems already done, plus a note if the target date is too tight. It also refreshes the dashboard.
4. **Show the plan briefly:** the starting point, the roadmap as stages with dates, the daily routine, and one line on the target date. Don't paste the whole log.
5. **Ask one confirmation question:** "Does this pace work, or should I adjust it?" Change Profile values and re-run `plan` if they want changes.
6. Then offer to start: today's problem (`mentor.py daily --dir .`), and the reminder setup if they wanted it.

**The daily routine** to describe: one new problem a day (picked automatically), any revisions due first (usually 10–15 minutes), and once Stage 3 is reached, a weekly mock interview on the user's choice of day.

## Re-planning later

- "Redo my plan" or "change my pace": ask only the questions that matter (time, target date, previous solves), update the Profile, and re-run `plan`. Don't repeat the whole onboarding.
- If the user is consistently ahead of or behind the plan by more than a week, mention it once at session start and offer to re-plan. Don't nag.

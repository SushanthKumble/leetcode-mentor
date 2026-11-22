#!/usr/bin/env python3
"""leetcode-mentor helper: daily problem picker, HTML progress dashboard, reminder.

Standard library only (Python 3.8+). The Markdown log stays the source of truth.

    python mentor.py daily     --dir <practice-folder> [--notify] [--force]
    python mentor.py dashboard --dir <practice-folder> [--open]
    python mentor.py status    --dir <practice-folder>
    python mentor.py done      --dir <practice-folder> [--problem N]  # mark solved + verified
    python mentor.py check     --dir <practice-folder> [--problem N]  # did I get Accepted on LeetCode?
    python mentor.py sync      --dir <practice-folder>                # record recent LeetCode Accepted solves
    python mentor.py plan      --dir <practice-folder>                # write the dated study plan from Profile
    python mentor.py import-prior --dir <practice-folder> --file <pasted.txt>  # record previously solved problems

LeetCode access is optional, read-only, and uses only your public username (Profile line
"- LeetCode username: <name>"). No password or cookie is ever used. LeetCode has no official
API: this calls the public GraphQL endpoint its website uses, so it may change or fail. On
failure everything falls back to the offline behavior.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CATALOG_MD = SKILL_DIR / "references" / "problem-progression.md"
LOG_NAME = "leetcode-log.md"
DASH_NAME = "leetcode-progress.html"
DIFF_NAME = {"E": "Easy", "M": "Medium", "H": "Hard"}
DIFF_ORDER = ["E", "M", "H"]
MIX_EVERY = 4  # every 4th daily problem is an unlabeled review of an earlier topic

LOG_SKELETON = """# LeetCode Practice Log
_Maintained by the leetcode-mentor skill. You can edit this file; the mentor treats your edits as the truth._

## Profile
- Language: (not set)
- LeetCode username: (not set)
- Current focus: Easy fundamentals
- Last session: (none)

## Daily problem
<!-- written by scripts/mentor.py: - YYYY-MM-DD: N. Title (Difficulty) · status: pending|accepted|done|skipped -->

## Solved on LeetCode
<!-- written by scripts/mentor.py sync: - YYYY-MM-DD: N. Title (Difficulty) · Lang · submission: ID · verified: no|yes -->

## Active problem
_None._

## Revision queue
| Due | Problem | Pattern | Interval (days) | Last result |
|---|---|---|---|---|

## Pattern mastery
| Pattern | Problems | Best score | Status | Recognition clue (user's words) | Confused with |
|---|---|---|---|---|---|

## Mistake patterns

## Problem history
"""


# --------------------------------------------------------------------------- catalog
def slugify(title: str) -> str:
    t = title.lower().replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def load_catalog() -> list[dict]:
    """Parse the curated ladder in references/problem-progression.md."""
    text = CATALOG_MD.read_text(encoding="utf-8")
    catalog, stage = [], 0
    for line in text.splitlines():
        m = re.match(r"### Stage (\d+)", line)
        if m:
            stage = int(m.group(1))
            continue
        if stage and line.startswith("| ") and not line.startswith("| Pattern") and "---" not in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            topic = cells[0]
            for order, (num, title, diff) in enumerate(re.findall(r"(\d+)\. ([^·|]+?) \(([EMH])\)", cells[1])):
                title = title.strip()
                catalog.append({"num": int(num), "title": title, "diff": diff, "topic": topic,
                                "stage": stage, "order": order, "slug": slugify(title)})
    return catalog


# --------------------------------------------------------------------------- log parsing
def sections(text: str) -> dict[str, list[str]]:
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip().lower()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|") or re.match(r"^\|[\s\-:|]+\|$", s):
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:] if rows else []  # drop header


def parse_date(s: str):
    m = re.search(r"\d{4}-\d{2}-\d{2}", s or "")
    return dt.date.fromisoformat(m.group(0)) if m else None


def parse_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    sec = sections(text)
    log = {"exists": path.exists(), "profile": {}, "daily": [], "revisions": [], "patterns": [],
           "mistakes": [], "history": [], "active": ""}

    for line in sec.get("profile", []):
        m = re.match(r"-\s*([^:]+):\s*(.*)", line.strip())
        if m:
            log["profile"][m.group(1).strip().lower()] = m.group(2).strip()

    for line in sec.get("daily problem", []):
        m = re.match(r"-\s*(\d{4}-\d{2}-\d{2}):\s*(\d+)\.\s*(.+?)\s*\((Easy|Medium|Hard)\)(.*)", line.strip())
        if m:
            st = re.search(r"status:\s*(\w+)", m.group(5))
            why = re.search(r"why:\s*(.+)$", m.group(5))
            log["daily"].append({"date": dt.date.fromisoformat(m.group(1)), "num": int(m.group(2)),
                                 "title": m.group(3), "diff": m.group(4),
                                 "status": st.group(1).lower() if st else "pending",
                                 "why": why.group(1).strip() if why else ""})

    log["leetcode"] = []
    for line in sec.get("solved on leetcode", []):
        m = re.match(r"-\s*(\d{4}-\d{2}-\d{2}):\s*(\d+)\.\s*(.+?)\s*\((Easy|Medium|Hard)\)(.*)", line.strip())
        if m:
            rest = m.group(5)
            sub = re.search(r"submission:\s*(\d+)", rest)
            lang = re.match(r"\s*·\s*([^·]+?)\s*·", rest)
            log["leetcode"].append({"date": dt.date.fromisoformat(m.group(1)), "num": int(m.group(2)),
                                    "title": m.group(3), "diff": m.group(4),
                                    "lang": lang.group(1) if lang else "",
                                    "submission": sub.group(1) if sub else "",
                                    "verified": bool(re.search(r"verified:\s*yes", rest))})
    log["prior"] = []
    for line in sec.get("prior solves", []):
        m = re.match(r"-\s*(\d+)\.\s*(.+?)\s*\((Easy|Medium|Hard)\)", line.strip())
        if m:
            log["prior"].append({"num": int(m.group(1)), "title": m.group(2), "diff": m.group(3)})
    log["plan_lines"] = [l for l in sec.get("study plan", []) if l.strip() and not l.strip().startswith("<!--")]
    prof = log["profile"]
    log["prior_mode"] = (prof.get("previous solves", "fresh").split() or ["fresh"])[0].lower()
    try:
        log["start_stage"] = max(1, min(5, int(re.search(r"\d", prof.get("start stage", "1")).group(0))))
    except AttributeError:
        log["start_stage"] = 1
    try:
        log["days_per_week"] = max(1, min(7, int(re.search(r"\d", prof.get("days per week", "6")).group(0))))
    except AttributeError:
        log["days_per_week"] = 6
    log["target_date"] = parse_date(prof.get("target date", ""))
    user = log["profile"].get("leetcode username", "")
    log["username"] = "" if (not user or user.startswith("(")) else user.strip().lstrip("@")

    active = "\n".join(l for l in sec.get("active problem", []) if l.strip() and not l.strip().startswith("<!--"))
    log["active"] = "" if "_none._" in active.lower() else active.strip()

    for r in table_rows(sec.get("revision queue", [])):
        if len(r) >= 5 and parse_date(r[0]):
            log["revisions"].append({"due": parse_date(r[0]), "problem": r[1], "pattern": r[2],
                                     "interval": r[3], "result": r[4]})

    for r in table_rows(sec.get("pattern mastery", [])):
        if len(r) >= 4 and r[0]:
            log["patterns"].append({"pattern": r[0], "problems": r[1], "best": r[2], "status": r[3],
                                    "clue": r[4] if len(r) > 4 else "", "confused": r[5] if len(r) > 5 else ""})

    for line in sec.get("mistake patterns", []):
        s = line.strip()
        if s.startswith("- "):
            log["mistakes"].append(s[2:])

    # Problem history: "### YYYY-MM-DD: N. Title (Difficulty)" blocks
    hist_lines = sec.get("problem history", [])
    cur = None
    for line in hist_lines + ["### END"]:
        if line.startswith("### "):
            if cur:
                log["history"].append(finish_entry(cur))
            m = re.match(r"###\s*(\d{4}-\d{2}-\d{2})\s*[:—–-]+\s*(\d+)\.\s*(.+?)\s*\((Easy|Medium|Hard)\)", line)
            cur = {"date": dt.date.fromisoformat(m.group(1)), "num": int(m.group(2)), "title": m.group(3),
                   "diff": m.group(4), "body": []} if m else None
        elif cur is not None:
            cur["body"].append(line)
    return log


def field(body: str, name: str) -> str:
    m = re.search(r"\*\*" + re.escape(name) + r":\*\*\s*(.*)", body)
    return m.group(1).strip() if m else ""


def finish_entry(e: dict) -> dict:
    body = "\n".join(e.pop("body"))
    outcome = field(body, "Outcome")
    sm = re.search(r"score\s*(\d)", outcome)
    hm = re.search(r"max hint\s*(L\d|none)", outcome, re.I)
    pm = re.search(r"\*\*Pseudocode:\*\*\s*```[^\n]*\n(.*?)```", body, re.S)
    e.update({
        "score": int(sm.group(1)) if sm else None,
        "hint": (hm.group(1).upper() if hm and hm.group(1).lower() != "none" else "none") if hm else "",
        "outcome": outcome,
        "pattern": field(body, "Pattern"),
        "takeaway": (field(body, "Takeaway (user's words)") or field(body, "Remember")).strip('"“” '),
        "mastered": field(body, "Mastered").lower().startswith("yes"),
        "pseudocode": re.sub(r"^ {2}", "", pm.group(1), flags=re.M).rstrip() if pm else "",
    })
    return e


# --------------------------------------------------------------------------- stats
def compute_stats(log: dict, catalog: list[dict], today: dt.date) -> dict:
    by_num = {p["num"]: p for p in catalog}
    hist = sorted(log["history"], key=lambda e: e["date"])
    topics: dict[str, dict] = {}
    for p in catalog:
        topics.setdefault(p["topic"], {"topic": p["topic"], "stage": p["stage"], "scores": [], "diffs": [],
                                       "total": 0, "nums": set()})
        topics[p["topic"]]["total"] += 1
    for e in hist:
        p = by_num.get(e["num"])
        if p and e["score"] is not None:
            t = topics[p["topic"]]
            t["scores"].append(e["score"])
            t["diffs"].append(p["diff"])
            t["nums"].add(e["num"])
    for t in topics.values():
        s = t["scores"]
        good = [x for x in s if x >= 4]
        if not s:
            t["status"] = "New"
        elif len({n for n in t["nums"]}) >= 3 and len(good) >= 3 and s.count(5) >= 2:
            t["status"] = "Solid"
        elif good:
            t["status"] = "Practicing"
        else:
            t["status"] = "Learning"
        t["best"] = max(s) if s else 0
        t["last"] = s[-1] if s else None
    # mastered overrides from the log's own pattern table
    for row in log["patterns"]:
        for t in topics.values():
            if row["status"].lower().startswith("master") and row["pattern"].lower().split()[0] in t["topic"].lower():
                t["status"] = "Mastered"

    active_days = ({e["date"] for e in hist} | {d["date"] for d in log["daily"] if d["status"] in ("done", "accepted")}
                   | {e["date"] for e in log.get("leetcode", [])})
    streak, day = 0, today if today in active_days else today - dt.timedelta(days=1)
    while day in active_days:
        streak += 1
        day -= dt.timedelta(days=1)

    solved = {e["num"] for e in hist if e["score"] and e["score"] >= 1}
    scores = [e["score"] for e in hist if e["score"] is not None]
    due = [r for r in log["revisions"] if r["due"] <= today]
    return {
        "topics": topics, "streak": streak, "solved": len(solved), "attempts": len(hist),
        "independent": sum(1 for s in scores if s == 5),
        "avg": round(sum(scores) / len(scores), 1) if scores else None,
        "mastered": sum(1 for e in hist if e["mastered"]),
        "due": sorted(due, key=lambda r: r["due"]),
        "unverified": [e for e in log.get("leetcode", []) if not e["verified"] and e["num"] not in {h["num"] for h in hist}],
        "active_days": active_days,
        "hints": {k: sum(1 for e in hist if e["hint"] == k) for k in ["none", "L1", "L2", "L3", "L4", "L5", "L6"]},
    }


# --------------------------------------------------------------------------- daily picker
def topic_level(t: dict, focus: str) -> str:
    s, d = t["scores"], t["diffs"]
    start = "M" if re.search(r"medium|hard", focus, re.I) else "E"
    if not s:
        return start
    level = d[-1]
    last3 = s[-3:]
    if len(last3) == 3 and min(last3) >= 4 and last3.count(5) >= 2:
        level = DIFF_ORDER[min(DIFF_ORDER.index(level) + 1, 2)]
    elif len(s) >= 2 and max(s[-2:]) <= 2:
        level = DIFF_ORDER[max(DIFF_ORDER.index(level) - 1, 0)]
    if level == "H" and t["status"] not in ("Solid", "Mastered"):
        level = "M"
    return level


def pick_problem(log: dict, catalog: list[dict], stats: dict) -> tuple[dict, str]:
    used = ({e["num"] for e in log["history"]} | {d["num"] for d in log["daily"] if d["status"] != "skipped"}
            | {e["num"] for e in log.get("leetcode", [])}
            | ({e["num"] for e in log.get("prior", [])} if log.get("prior_mode") != "fresh" else set()))
    recent_topics = []
    by_num = {p["num"]: p for p in catalog}
    for d in log["daily"][-2:]:
        if d["num"] in by_num:
            recent_topics.append(by_num[d["num"]]["topic"])
    topics = stats["topics"]
    focus = log["profile"].get("current focus", "")

    def first_open(topic: str):
        lvl = topic_level(topics[topic], focus)
        pool = [p for p in catalog if p["topic"] == topic and p["num"] not in used]
        for want in [lvl] + [x for x in DIFF_ORDER if x != lvl]:
            cand = [p for p in pool if p["diff"] == want]
            if cand:
                return min(cand, key=lambda p: p["order"])
        return None

    # 1) every MIX_EVERY-th daily: an unlabeled problem from a topic already practiced or placed out of
    practiced = [t for t in topics.values() if t["scores"] or t["stage"] < log.get("start_stage", 1)]
    if practiced and len(log["daily"]) % MIX_EVERY == MIX_EVERY - 1:
        for t in sorted(practiced, key=lambda t: (t["best"], t["stage"])):
            p = first_open(t["topic"])
            if p:
                return p, "A mixed review. Spotting the approach without a topic label is the point."

    # 2) earliest stage with a topic that isn't Practicing yet; in-progress topics before new ones
    topic_order = list(dict.fromkeys(p["topic"] for p in catalog))
    for stage in sorted({p["stage"] for p in catalog}):
        if stage < log.get("start_stage", 1):
            continue  # placed out of this stage; it still feeds mixed reviews
        stage_topics = [t for t in topics.values() if t["stage"] == stage and t["status"] in ("New", "Learning")]
        stage_topics.sort(key=lambda t: (t["topic"] in recent_topics, t["status"] == "New",
                                         topic_order.index(t["topic"])))
        for t in stage_topics:
            p = first_open(t["topic"])
            if p:
                why = ("A new topic for you. The mentor will check the basics before you start."
                       if t["status"] == "New" else
                       "Builds on a topic where you've needed hints. Aim to solve it with fewer this time.")
                return p, why

    # 3) everything is Practicing or better: the weakest recent topic, avoiding back-to-back repeats
    ranked = sorted(topics.values(), key=lambda t: (t["topic"] in recent_topics, t["last"] or 0, t["stage"]))
    for t in ranked:
        p = first_open(t["topic"])
        if p:
            return p, "Targets your weakest recent area at the right difficulty."
    raise SystemExit("Every problem in the ladder is done. Ask the mentor for problems beyond the ladder.")


def write_daily(log_path: Path, entry_line: str, replace_pending_before: dt.date | None):
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else LOG_SKELETON
    if "## Daily problem" not in text:
        text = text.replace("## Active problem", "## Daily problem\n\n## Active problem", 1) \
            if "## Active problem" in text else text + "\n## Daily problem\n"
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "## Daily problem")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    body = [l for l in lines[start + 1:end] if l.strip()]  # drop blank lines inside the section
    for i, line in enumerate(body):
        d = parse_date(line)
        if replace_pending_before and "status: pending" in line and d and d < replace_pending_before:
            body[i] = line.replace("status: pending", "status: skipped")
    body.append(entry_line)
    new = lines[:start + 1] + [""] + body + [""] + lines[end:]
    log_path.write_text("\n".join(new).rstrip() + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- LeetCode (public, read-only)
LC_URL = "https://leetcode.com/graphql"


class LeetCodeError(Exception):
    pass


def lc_query(query: str, variables: dict | None = None) -> dict:
    """POST a GraphQL query. LEETCODE_MENTOR_MOCK=<file.json> substitutes a canned response (tests)."""
    mock = os.environ.get("LEETCODE_MENTOR_MOCK")
    if mock:
        data = json.loads(Path(mock).read_text(encoding="utf-8"))
        key = "recent" if "recentAcSubmissionList" in query else "questions"
        return data[key]
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(LC_URL, data=body, headers={
        "Content-Type": "application/json", "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (leetcode-mentor)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            payload = json.load(r)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise LeetCodeError(f"LeetCode is unreachable right now ({e.__class__.__name__}).") from e
    if payload.get("errors"):
        raise LeetCodeError("LeetCode returned an error: " + "; ".join(x.get("message", "?") for x in payload["errors"]))
    return payload.get("data") or {}


def fetch_recent_accepted(username: str, catalog: list[dict], limit: int = 20) -> list[dict]:
    """The user's recent Accepted submissions (public; LeetCode shows at most ~20)."""
    data = lc_query("query r($u:String!,$n:Int!){recentAcSubmissionList(username:$u,limit:$n)"
                    "{id title titleSlug timestamp lang}}", {"u": username, "n": limit})
    subs = data.get("recentAcSubmissionList")
    if not subs and not os.environ.get("LEETCODE_MENTOR_MOCK"):
        # An empty list can mean "no such user" or "recent submissions not visible". Tell them apart.
        prof = lc_query("query p($u:String!){matchedUser(username:$u){username submitStatsGlobal"
                        "{acSubmissionNum{difficulty count}}}}", {"u": username}).get("matchedUser")
        if not prof:
            raise LeetCodeError(f'No LeetCode profile found for username "{username}". Check the spelling.')
        total = next((x["count"] for x in prof["submitStatsGlobal"]["acSubmissionNum"] if x["difficulty"] == "All"), 0)
        if total:
            raise LeetCodeError(
                f'Your profile shows {total} solved, but LeetCode lists no recent submissions. Its public '
                f'"Recent AC" list only covers recent activity, so older solves don\'t appear. Your next '
                f'Accepted solve will show up. Until then, paste your code instead. '
                f'(Profile: https://leetcode.com/u/{username}/)')
        subs = []
    by_slug = {p["slug"]: p for p in catalog}
    unknown = sorted({s["titleSlug"] for s in subs if s["titleSlug"] not in by_slug})
    extra = {}
    if unknown:  # one batched request for problems outside the curated ladder
        q = "query{" + " ".join(f'q{i}:question(titleSlug:{json.dumps(s)}){{questionFrontendId titleSlug difficulty}}'
                                for i, s in enumerate(unknown)) + "}"
        try:
            for v in lc_query(q).values():
                if v:
                    extra[v["titleSlug"]] = {"num": int(v["questionFrontendId"]), "diff": v["difficulty"][0]}
        except LeetCodeError:
            pass
    out = []
    for s in subs:
        info = by_slug.get(s["titleSlug"]) or extra.get(s["titleSlug"])
        if not info:
            continue
        out.append({"num": info["num"], "title": s["title"], "slug": s["titleSlug"],
                    "diff": DIFF_NAME[info["diff"]], "lang": s.get("lang", ""), "submission": str(s["id"]),
                    "when": dt.datetime.fromtimestamp(int(s["timestamp"])),
                    "url": f'https://leetcode.com/submissions/detail/{s["id"]}/'})
    return out


def edit_section(log_path: Path, name: str, fn, before: str = "## Active problem") -> None:
    """Apply fn(list_of_nonblank_lines) -> list to the '## name' section; create it (above `before`) if missing."""
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else LOG_SKELETON
    lines = text.splitlines()
    idx = next((i for i, l in enumerate(lines) if l.strip().lower() == f"## {name}".lower()), None)
    if idx is None:
        anchor = next((i for i, l in enumerate(lines) if l.strip() == before),
                      next((i for i, l in enumerate(lines) if l.strip() == "## Active problem"), len(lines)))
        lines[anchor:anchor] = [f"## {name}", ""]
        idx = anchor
    end = next((i for i in range(idx + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    body = fn([l for l in lines[idx + 1:end] if l.strip()])
    new = lines[:idx + 1] + [""] + body + [""] + lines[end:]
    log_path.write_text("\n".join(new).rstrip() + "\n", encoding="utf-8")


def record_accepted(log_path: Path, log: dict, accepted: list[dict]) -> list[dict]:
    """Add new Accepted solves to '## Solved on LeetCode'; flip matching pending dailies to 'accepted'."""
    known = {e["num"] for e in log["leetcode"]}
    new = []
    for a in sorted(accepted, key=lambda a: a["when"]):
        if a["num"] not in known:
            known.add(a["num"])
            new.append(a)
    if new:
        edit_section(log_path, "Solved on LeetCode", lambda body: body + [
            f'- {a["when"].date().isoformat()}: {a["num"]}. {a["title"]} ({a["diff"]}) · {a["lang"]} · '
            f'submission: {a["submission"]} · verified: no' for a in new])
    acc_nums = {a["num"] for a in accepted}

    def flip(body):
        return [l.replace("status: pending", "status: accepted")
                if "status: pending" in l and (m := re.match(r"-\s*\S+:\s*(\d+)\.", l.strip())) and int(m.group(1)) in acc_nums
                else l for l in body]
    if any(d["status"] == "pending" and d["num"] in acc_nums for d in log["daily"]):
        edit_section(log_path, "Daily problem", flip)
    return new


# --------------------------------------------------------------------------- onboarding: prior solves + plan
def import_prior(log_path: Path, log: dict, catalog: list[dict], text: str) -> tuple[list[dict], list[str]]:
    """Parse a pasted 'solved problems' list ('N. Title' lines) and record it under '## Prior solves'."""
    by_num = {p["num"]: p for p in catalog}
    found = {}
    for m in re.finditer(r"(?m)^\s*(\d{1,5})\.\s+(.+?)\s*$", text):
        title = re.split(r"\t|\s{2,}|\s+\d+(?:\.\d+)?%", m.group(2))[0].strip()
        title = re.sub(r"\s+(Easy|Medium|Hard|Med\.)$", "", title).strip()
        if title:
            found.setdefault(int(m.group(1)), title)
    resolved, problems = [], []
    unknown = {n: t for n, t in found.items() if n not in by_num}
    lc = {}
    if unknown:
        q = "query{" + " ".join(f'q{n}:question(titleSlug:{json.dumps(slugify(t))}){{questionFrontendId title difficulty}}'
                                for n, t in unknown.items()) + "}"
        try:
            lc = {int(k[1:]): v for k, v in lc_query(q).items() if v}
        except LeetCodeError:
            lc = {}
    for n, t in sorted(found.items()):
        if n in by_num:
            resolved.append({"num": n, "title": by_num[n]["title"], "diff": DIFF_NAME[by_num[n]["diff"]]})
        elif n in lc and int(lc[n]["questionFrontendId"]) == n:
            resolved.append({"num": n, "title": lc[n]["title"], "diff": lc[n]["difficulty"]})
        else:
            problems.append(f"{n}. {t}")
    have = {e["num"] for e in log["prior"]}
    new = [r for r in resolved if r["num"] not in have]
    if new:
        edit_section(log_path, "Prior solves", lambda body: body + [
            f'- {r["num"]}. {r["title"]} ({r["diff"]}) · prior, unverified' for r in new])
    return new, problems


def build_plan(log_path: Path, log: dict, catalog: list[dict], today: dt.date) -> list[str]:
    """Write a dated roadmap to '## Study plan' from the Profile (pace, start stage, prior solves)."""
    prof = log["profile"]
    dpw, start = log["days_per_week"], log["start_stage"]
    done = ({e["num"] for e in log["history"]} | {e["num"] for e in log["leetcode"]}
            | ({e["num"] for e in log["prior"]} if log["prior_mode"] != "fresh" else set()))
    names = {}
    for line in CATALOG_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### Stage (\d+): (.+)", line)
        if m:
            names[int(m.group(1))] = m.group(2)
    lines = [f'- Created: {today.isoformat()} · Pace: 1 new problem a day, {dpw} days a week'
             + (f' (~{prof["daily time"]} a day)' if prof.get("daily time") else ""),
             f'- Goal: {prof.get("goal", "(not set)")}'
             + (f' · Target date: {log["target_date"].isoformat()}' if log["target_date"] else ""),
             f'- Starting point: Stage {start} · Previous solves: '
             + {"fresh": "fresh start (past solves ignored)",
                "count": f'counted as done ({len(log["prior"])} skipped, not mastered)',
                "placement": f'placement check ({len(log["prior"])} past solves skipped)'}.get(log["prior_mode"], log["prior_mode"]),
             "- Roadmap:"]
    day, stage3_start, finish = today, None, {}
    for st in sorted(names):
        probs = [p for p in catalog if p["stage"] == st]
        left = [p for p in probs if p["num"] not in done]
        if st < start:
            lines.append(f"  - Stage {st} · {names[st]}: placed out (still used for mixed reviews)")
            continue
        cal_days = -(-len(left) * 7 // dpw)  # ceil
        end = day + dt.timedelta(days=max(cal_days - 1, 0))
        if st >= 3 and stage3_start is None:
            stage3_start = day
        lines.append(f"  - Stage {st} · {names[st]}: {len(left)} problems · {day.isoformat()} → {end.isoformat()}")
        finish[st] = end
        day = end + dt.timedelta(days=1)
    lines.append("- Daily: revisions due first (10–15 min), then today's problem")
    if stage3_start:
        lines.append(f"- Weekly: one mock interview from Stage 3 (around {stage3_start.isoformat()})")
    if log["target_date"] and finish:
        last_stage, last_end = max(finish.items())
        if last_end <= log["target_date"]:
            lines.append(f"- Target check: on track. Full ladder done by {last_end.isoformat()}")
        else:
            reach = max((s for s, e in finish.items() if e <= log["target_date"]), default=None)
            lines.append("- Target check: tight. " + (f"At this pace you finish Stage {reach} by the target date. "
                                                     if reach else "No stage finishes by the target date at this pace. ")
                         + "Options: add a 2nd problem on some days, practice more days a week, or focus on Stages 1–3.")
    edit_section(log_path, "Study plan", lambda body: lines, before="## Daily problem")
    return lines


# --------------------------------------------------------------------------- dashboard
STATUS_CLASS = {"New": "s-new", "Learning": "s-learn", "Practicing": "s-prac", "Solid": "s-solid", "Mastered": "s-mast"}


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def build_dashboard(practice_dir: Path, log: dict, catalog: list[dict], stats: dict, today: dt.date) -> Path:
    by_num = {p["num"]: p for p in catalog}
    daily = next((d for d in reversed(log["daily"]) if d["date"] == today), None)
    if daily:
        slug = by_num[daily["num"]]["slug"] if daily["num"] in by_num else slugify(daily["title"])
        cmd = f'/leetcode-mentor {daily["num"]}. {daily["title"]}'
        done = daily["status"] in ("done", "accepted")
        state = {"done": "Solved and verified. Nice work.",
                 "accepted": "Accepted on LeetCode. Tell the mentor \"done\" to verify it and log your score."
                 }.get(daily["status"], "Not solved yet")
        today_card = f"""
      <section class="hero {'hero-done' if done else ''}">
        <div class="eyebrow">Today's problem · {esc(today.strftime('%A, %d %b'))}</div>
        <h2>{esc(daily['num'])}. {esc(daily['title'])}</h2>
        <div class="hero-row"><span class="pill d-{esc(daily['diff'].lower())}">{esc(daily['diff'])}</span>
          <span class="muted">{esc(state)}</span></div>
        <div class="hero-actions">
          <a class="btn" href="https://leetcode.com/problems/{esc(slug)}/" target="_blank" rel="noopener">Open on LeetCode ↗</a>
          <button class="btn ghost" onclick="copyCmd(this)" data-cmd="{esc(cmd)}">Copy mentor command</button>
        </div>
      </section>"""
    else:
        today_card = """<section class="hero"><div class="eyebrow">Today's problem</div>
        <h2>Not picked yet</h2><p class="muted">Run <code>python scripts/mentor.py daily --dir .</code>, or wait for the reminder.</p></section>"""

    # stat cards
    cards = [("🔥", stats["streak"], "day streak"), ("✅", stats["solved"], "problems solved"),
             ("🧠", stats["independent"], "solved independently"), ("🏆", stats["mastered"], "mastered"),
             ("🔁", len(stats["due"]), "revisions due"),
             ("📈", stats["avg"] if stats["avg"] is not None else "–", "avg independence /5")]
    cards_html = "".join(f'<div class="card stat"><div class="ico">{i}</div><div class="num">{esc(n)}</div>'
                         f'<div class="lbl">{esc(l)}</div></div>' for i, n, l in cards)

    # heatmap: last 18 weeks
    start = today - dt.timedelta(days=today.weekday() + 7 * 17)
    counts = {}
    for e in log["history"]:
        counts[e["date"]] = counts.get(e["date"], 0) + 1
    for d in log["daily"]:
        if d["status"] == "done":
            counts.setdefault(d["date"], 1)
    cells = []
    day = start
    while day <= today:
        c = counts.get(day, 0)
        lvl = 0 if c == 0 else 1 if c == 1 else 2 if c == 2 else 3
        cells.append(f'<i class="h{lvl}" title="{day.isoformat()}: {c} problem(s)"></i>')
        day += dt.timedelta(days=1)
    heat = f'<div class="heat">{"".join(cells)}</div>'

    # pattern grid by stage
    stage_names = {}
    for line in CATALOG_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### Stage (\d+): (.+)", line)
        if m:
            stage_names[int(m.group(1))] = m.group(2)
    grid = []
    for st in sorted(stage_names):
        chips = []
        for t in [t for t in stats["topics"].values() if t["stage"] == st]:
            done_n = len(t["nums"])
            pct = int(100 * done_n / t["total"]) if t["total"] else 0
            chips.append(f'<div class="topic {STATUS_CLASS[t["status"]]}"><div class="t-name">{esc(t["topic"])}</div>'
                         f'<div class="t-meta"><span>{esc(t["status"])}</span><span>{done_n}/{t["total"]}</span></div>'
                         f'<div class="bar"><b style="width:{pct}%"></b></div></div>')
        grid.append(f'<div class="stage"><h4>Stage {st} · {esc(stage_names[st])}</h4><div class="topics">{"".join(chips)}</div></div>')

    # hint distribution
    total_h = sum(stats["hints"].values()) or 1
    hint_label = {"none": "No hints", "L1": "L1 Nudge", "L2": "L2 Direction", "L3": "L3 Pattern clue",
                  "L4": "L4 Guidance", "L5": "L5 Pseudocode", "L6": "L6 Solution"}
    hints_html = "".join(
        f'<div class="hrow"><span>{hint_label[k]}</span><div class="bar wide"><b class="hb-{k.lower()}" '
        f'style="width:{int(100 * v / total_h)}%"></b></div><span class="muted">{v}</span></div>'
        for k, v in stats["hints"].items())

    # revisions
    rev_rows = "".join(
        f'<tr class="{"overdue" if r["due"] < today else "due" if r["due"] == today else ""}"><td>{esc(r["due"])}</td>'
        f'<td>{esc(r["problem"])}</td><td>{esc(r["interval"])}d</td><td>{esc(r["result"])}</td></tr>'
        for r in sorted(log["revisions"], key=lambda r: r["due"])) or '<tr><td colspan="4" class="muted">Nothing scheduled yet.</td></tr>'

    # history
    hist_rows = []
    for e in sorted(log["history"], key=lambda e: e["date"], reverse=True)[:40]:
        sc = e["score"]
        pseudo = (f'<details><summary>Pseudocode (spoiler)</summary><pre>{esc(e["pseudocode"])}</pre></details>'
                  if e["pseudocode"] else "")
        hist_rows.append(
            f'<tr><td>{esc(e["date"])}</td><td><b>{esc(e["num"])}. {esc(e["title"])}</b>'
            f'{"<div class=muted>“" + esc(e["takeaway"]) + "”</div>" if e["takeaway"] else ""}{pseudo}</td>'
            f'<td><span class="pill d-{esc(e["diff"].lower())}">{esc(e["diff"])}</span></td>'
            f'<td><span class="score sc{sc if sc is not None else "x"}">{esc(sc if sc is not None else "–")}</span></td>'
            f'<td>{esc(e["hint"] or "–")}</td><td>{"🏆" if e["mastered"] else ""}</td></tr>')
    hist_html = "".join(hist_rows) or '<tr><td colspan="6" class="muted">No problems logged yet. Your first one is waiting.</td></tr>'

    mistakes = "".join(f"<li>{esc(m)}</li>" for m in log["mistakes"]) or '<li class="muted">None recorded.</li>'
    active = f'<section class="card"><h3>⏸ Paused problem</h3><pre class="active">{esc(log["active"])}</pre></section>' \
        if log["active"] else ""
    if stats["unverified"]:
        items = "".join(
            f'<li><b>{esc(e["num"])}. {esc(e["title"])}</b> <span class="pill d-{esc(e["diff"].lower())}">{esc(e["diff"])}</span> '
            f'<span class="muted">· {esc(e["lang"])} · {esc(e["date"])}</span></li>' for e in stats["unverified"][-8:])
        active += (f'<section class="card" style="margin-bottom:18px"><h3>✔ Accepted on LeetCode, not yet verified '
                   f'({len(stats["unverified"])})</h3><p class="muted">Say "verify my LeetCode solves" to the mentor. '
                   f'A quick understanding check sets the real score.</p><ul>{items}</ul></section>')

    plan_html = ""
    if log.get("plan_lines"):
        items = []
        for l in log["plan_lines"]:
            s = l.strip()[2:] if l.strip().startswith("- ") else l.strip()
            nested = l.startswith("  ")
            if s == "Roadmap:":
                continue
            m = re.match(r"Stage (\d+) · (.+?): (.+)", s)
            if nested and m:
                st = int(m.group(1))
                t_all = [t for t in stats["topics"].values() if t["stage"] == st]
                tot = sum(t["total"] for t in t_all) or 1
                got = sum(len(t["nums"]) for t in t_all)
                items.append(f'<div class="road"><b>Stage {st}</b> <span>{esc(m.group(2))}</span>'
                             f'<span class="muted">{esc(m.group(3))}</span>'
                             f'<div class="bar"><b style="width:{int(100 * got / tot)}%"></b></div></div>')
            else:
                items.append(f'<p class="muted plan-line">{esc(s)}</p>')
        plan_html = f'<section class="card" style="margin-bottom:18px"><h3>🗺 Your plan</h3>{"".join(items)}</section>'

    page = DASH_TEMPLATE.format(
        plan=plan_html,
        generated=esc(dt.datetime.now().strftime("%Y-%m-%d %H:%M")), today_card=today_card, cards=cards_html,
        heat=heat, grid="".join(grid), hints=hints_html, rev_rows=rev_rows, hist=hist_html,
        mistakes=mistakes, active=active, lang=esc(log["profile"].get("language", "–")),
        focus=esc(log["profile"].get("current focus", "–")))
    out = practice_dir / DASH_NAME
    out.write_text(page, encoding="utf-8")
    return out


DASH_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LeetCode Progress</title>
<style>
:root{{--bg:#0b0d14;--panel:#141824;--panel2:#1b2030;--line:#262c3f;--text:#e8eaf2;--muted:#8a91a8;
--accent:#8b5cf6;--accent2:#22d3ee;--easy:#22c55e;--med:#f59e0b;--hard:#ef4444;}}
@media (prefers-color-scheme:light){{:root{{--bg:#f5f6fb;--panel:#fff;--panel2:#f0f1f8;--line:#e2e4ef;--text:#151826;--muted:#5f6580;}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
.wrap{{max-width:1120px;margin:0 auto;padding:28px 16px 60px}}
header{{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
h1{{margin:0;font-size:26px;letter-spacing:-.02em}}h1 span{{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}}
h2{{margin:6px 0 10px;font-size:28px;letter-spacing:-.02em}}h3{{margin:0 0 12px;font-size:16px}}h4{{margin:0 0 10px;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}}
.muted{{color:var(--muted)}}code{{background:var(--panel2);padding:2px 6px;border-radius:6px}}
.hero{{position:relative;overflow:hidden;border-radius:20px;padding:26px;margin-bottom:18px;color:#fff;
background:radial-gradient(1200px 300px at 0% 0%,#7c3aed 0%,transparent 60%),radial-gradient(900px 300px at 100% 100%,#0891b2 0%,transparent 60%),#111527}}
.hero-done{{background:radial-gradient(1200px 300px at 0% 0%,#15803d 0%,transparent 60%),radial-gradient(900px 300px at 100% 100%,#0891b2 0%,transparent 60%),#0f1a17}}
.hero .muted{{color:#c9cde0}}.eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;opacity:.8}}
.hero-row{{display:flex;gap:12px;align-items:center}}.hero-actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}}
.btn{{display:inline-block;border:0;cursor:pointer;font:600 14px system-ui;padding:10px 16px;border-radius:12px;background:#fff;color:#111527;text-decoration:none}}
.btn.ghost{{background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.25)}}
.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:18px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}}
.stat{{text-align:left}}.stat .ico{{font-size:18px}}.stat .num{{font-size:28px;font-weight:700;letter-spacing:-.02em}}.stat .lbl{{color:var(--muted);font-size:12.5px}}
.two{{display:grid;grid-template-columns:1.4fr 1fr;gap:18px;margin-bottom:18px}}
.heat{{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,12px);gap:3px;overflow-x:auto}}
.heat i{{width:12px;height:12px;border-radius:3px;background:var(--panel2)}}.heat .h1{{background:#4c1d95}}.heat .h2{{background:#7c3aed}}.heat .h3{{background:#22d3ee}}
.stage{{margin-bottom:16px}}.topics{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}}
.topic{{border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--panel2)}}
.t-name{{font-weight:600;font-size:14px}}.t-meta{{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin:2px 0 6px}}
.bar{{height:6px;border-radius:99px;background:var(--line);overflow:hidden}}.bar b{{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}}
.s-learn{{border-color:#f59e0b55}}.s-prac{{border-color:#22d3ee66}}.s-solid{{border-color:#22c55e88}}.s-mast{{border-color:#eab308;box-shadow:0 0 0 1px #eab30855 inset}}
.s-new{{opacity:.6}}
.hrow{{display:grid;grid-template-columns:120px 1fr 28px;gap:10px;align-items:center;font-size:13px;margin:6px 0}}
.bar.wide{{height:10px}}.hb-none b,.bar b.hb-none{{background:var(--easy)}}.bar b.hb-l1,.bar b.hb-l2{{background:#84cc16}}.bar b.hb-l3,.bar b.hb-l4{{background:var(--med)}}.bar b.hb-l5,.bar b.hb-l6{{background:var(--hard)}}
table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{text-align:left;padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
td:first-child{{white-space:nowrap}}
.legend span::before{{content:"";display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:6px;border:1px solid var(--line);vertical-align:-1px}}
.legend .l-learn::before{{border-color:#f59e0b}}.legend .l-prac::before{{border-color:#22d3ee}}.legend .l-solid::before{{border-color:#22c55e}}.legend .l-mast::before{{background:#eab308;border-color:#eab308}}
th{{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
tr.overdue td:first-child{{color:var(--hard);font-weight:600}}tr.due td:first-child{{color:var(--med);font-weight:600}}
.pill{{font-size:12px;font-weight:600;padding:2px 10px;border-radius:99px;background:var(--panel2)}}
.d-easy{{color:var(--easy)}}.d-medium{{color:var(--med)}}.d-hard{{color:var(--hard)}}.hero .pill{{background:rgba(255,255,255,.14)}}
.score{{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:8px;font-weight:700;color:#0b0d14}}
.sc5{{background:#22c55e}}.sc4{{background:#84cc16}}.sc3{{background:#f59e0b}}.sc2{{background:#fb923c}}.sc1{{background:#ef4444}}.sc0,.scx{{background:#64748b}}
details summary{{cursor:pointer;color:var(--muted);font-size:12.5px;margin-top:4px}}pre{{background:var(--panel2);padding:10px;border-radius:10px;overflow-x:auto;font-size:12.5px}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--muted)}}
.road{{display:grid;grid-template-columns:80px 1fr auto;gap:4px 12px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line)}}
.road .bar{{grid-column:1/-1}}.plan-line{{margin:6px 0}}
footer{{margin-top:24px;color:var(--muted);font-size:12px}}
@media (max-width:860px){{.grid{{grid-template-columns:repeat(3,1fr)}}.two{{grid-template-columns:1fr}}}}
@media (max-width:600px){{.grid{{grid-template-columns:repeat(2,1fr)}}h2{{font-size:22px}}
.road{{grid-template-columns:1fr}}.road span{{font-size:13px}}.hero{{padding:20px}}.hero-actions .btn{{flex:1;text-align:center}}
.card{{padding:14px}}table{{display:block;overflow-x:auto}}.hrow{{grid-template-columns:96px 1fr 22px}}}}
html,body{{overflow-x:hidden}}.wrap>*{{min-width:0}}.two>*{{min-width:0}}
</style></head><body><div class="wrap">
<header><div><h1><span>LeetCode</span> Progress</h1><div class="muted">Language: {lang} · Focus: {focus}</div></div>
<div class="muted">Updated {generated}</div></header>
{today_card}
<div class="grid">{cards}</div>
{plan}
{active}
<div class="two">
  <section class="card"><h3>Activity · last 18 weeks</h3>{heat}</section>
  <section class="card"><h3>How much help you needed</h3>{hints}</section>
</div>
<section class="card" style="margin-bottom:18px"><h3>Topic mastery</h3>
  <div class="legend" style="margin-bottom:12px"><span>New</span><span class="l-learn">Learning</span><span class="l-prac">Practicing</span><span class="l-solid">Solid</span><span class="l-mast">Mastered</span></div>
  {grid}</section>
<div class="two">
  <section class="card"><h3>Problem history</h3><table><tr><th>Date</th><th>Problem</th><th>Level</th><th>Score</th><th>Hint</th><th></th></tr>{hist}</table></section>
  <div>
    <section class="card" style="margin-bottom:18px"><h3>Revision queue</h3><table><tr><th>Due</th><th>Problem</th><th>Every</th><th>Last</th></tr>{rev_rows}</table></section>
    <section class="card"><h3>Mistakes to watch</h3><ul>{mistakes}</ul></section>
  </div>
</div>
<footer>Generated from leetcode-log.md by leetcode-mentor. Scores: 5 independent · 4 minor hints · 3 major hints · 2 saw approach · 1 copied.</footer>
</div>
<script>function copyCmd(b){{navigator.clipboard&&navigator.clipboard.writeText(b.dataset.cmd).then(function(){{b.textContent='Copied ✓';setTimeout(function(){{b.textContent='Copy mentor command'}},1500)}})}}</script>
</body></html>
"""


# --------------------------------------------------------------------------- notification
def notify(practice_dir: Path, daily: dict, slug: str, reason: str, stats: dict, carried: bool):
    title = f'{daily["num"]}. {daily["title"]}'
    dash = (practice_dir / DASH_NAME).resolve()
    payload = {
        "title": title, "difficulty": daily["diff"], "reason": reason, "streak": stats["streak"],
        "due": len(stats["due"]), "url": f"https://leetcode.com/problems/{slug}/",
        "dashboard": dash.as_uri(), "carried": carried,
    }
    if sys.platform.startswith("win"):
        ps1 = SKILL_DIR / "scripts" / "notify-windows.ps1"
        cfg = practice_dir / ".leetcode-mentor-toast.json"
        cfg.write_text(json.dumps(payload), encoding="utf-8")
        flags = 0x08000000 if hasattr(subprocess, "STARTUPINFO") else 0  # CREATE_NO_WINDOW
        subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden",
                        "-File", str(ps1), "-ConfigPath", str(cfg)], check=False, creationflags=flags)
    elif sys.platform == "darwin":
        msg = f'{title} ({daily["diff"]}) · 🔥 {stats["streak"]} · {len(stats["due"])} revisions due'
        subprocess.run(["osascript", "-e", f'display notification {json.dumps(msg)} with title "LeetCode Mentor" sound name "Glass"'], check=False)
    else:
        subprocess.run(["notify-send", "-a", "LeetCode Mentor", "LeetCode Mentor · Today's problem",
                        f'{title} ({daily["diff"]})\n🔥 {stats["streak"]}-day streak · {len(stats["due"])} revisions due'], check=False)


# --------------------------------------------------------------------------- commands
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["daily", "dashboard", "status", "done", "check", "sync", "plan", "import-prior"])
    ap.add_argument("--file", help="import-prior: text file with your pasted solved list")
    ap.add_argument("--problem", type=int, help="problem number (check/done); default: today's daily problem")
    ap.add_argument("--dir", default=".", help="practice folder containing leetcode-log.md")
    ap.add_argument("--notify", action="store_true", help="show a desktop notification (daily)")
    ap.add_argument("--open", action="store_true", help="open the dashboard in the browser")
    ap.add_argument("--force", action="store_true", help="pick a new problem even if today's exists")
    ap.add_argument("--today", help=argparse.SUPPRESS)  # testing: override today's date
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    practice_dir = Path(a.dir).expanduser().resolve()
    practice_dir.mkdir(parents=True, exist_ok=True)
    log_path = practice_dir / LOG_NAME
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    catalog = load_catalog()
    by_num = {p["num"]: p for p in catalog}
    log = parse_log(log_path)
    stats = compute_stats(log, catalog, today)

    if a.command == "status":
        daily = next((d for d in reversed(log["daily"]) if d["date"] == today), None)
        print(json.dumps({"today": today.isoformat(), "daily": daily and {k: str(v) for k, v in daily.items()},
                          "streak": stats["streak"], "revisions_due": len(stats["due"]),
                          "solved": stats["solved"], "leetcode_username": log["username"] or None,
                          "unverified_leetcode_solves": [f'{e["num"]}. {e["title"]}' for e in stats["unverified"]]},
                         indent=2))
        return

    if a.command == "import-prior":
        if not a.file:
            raise SystemExit("Pass --file <text file containing your pasted solved list>.")
        text = Path(a.file).read_text(encoding="utf-8", errors="replace")
        new, unresolved = import_prior(log_path, log, catalog, text)
        log = parse_log(log_path)
        print(json.dumps({"recorded": len(new), "total_prior": len(log["prior"]),
                          "unresolved": unresolved,
                          "note": "Unresolved entries weren't recorded: the number and title couldn't be confirmed."
                          if unresolved else ""}, indent=2))
        return

    if a.command == "plan":
        lines = build_plan(log_path, log, catalog, today)
        log = parse_log(log_path)
        stats = compute_stats(log, catalog, today)
        build_dashboard(practice_dir, log, catalog, stats, today)
        print("\n".join(lines))
        return

    todays = next((d for d in reversed(log["daily"]) if d["date"] == today), None)
    target = a.problem or (todays["num"] if todays else None)

    if a.command == "done":
        if not log_path.exists():
            raise SystemExit("No log yet.")
        if target is None:
            raise SystemExit("No daily problem today. Pass --problem N.")
        num_re = re.compile(r"-\s*\d{4}-\d{2}-\d{2}:\s*" + str(target) + r"\.")
        changed = []
        edit_section(log_path, "Daily problem", lambda body: [
            (changed.append(1) or re.sub(r"status:\s*(pending|accepted)", "status: done", l))
            if num_re.match(l.strip()) and re.search(r"status:\s*(pending|accepted)", l) else l for l in body])
        if any(e["num"] == target for e in log["leetcode"]):
            edit_section(log_path, "Solved on LeetCode", lambda body: [
                l.replace("verified: no", "verified: yes") if num_re.match(l.strip()) else l for l in body])
            changed.append(1)
        log = parse_log(log_path)
        stats = compute_stats(log, catalog, today)
        build_dashboard(practice_dir, log, catalog, stats, today)
        print(f"Marked {target} as done and verified." if changed else f"Nothing pending for problem {target}.")
        return

    if a.command in ("check", "sync"):
        if not log["username"]:
            raise SystemExit('No LeetCode username yet. Add "- LeetCode username: <name>" under ## Profile in '
                             f"{log_path.name}, or ask the mentor to set it.")
        try:
            accepted = fetch_recent_accepted(log["username"], catalog)
        except LeetCodeError as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
            sys.exit(2)
        new = record_accepted(log_path, log, accepted)
        log = parse_log(log_path)
        stats = compute_stats(log, catalog, today)
        build_dashboard(practice_dir, log, catalog, stats, today)
        if a.command == "sync":
            print(json.dumps({"ok": True, "recent_accepted": len(accepted),
                              "newly_recorded": [f'{x["num"]}. {x["title"]}' for x in new]}, indent=2))
            return
        if target is None:
            raise SystemExit("No daily problem today. Pass --problem N.")
        hit = next((x for x in accepted if x["num"] == target), None)
        title = by_num[target]["title"] if target in by_num else (todays or {}).get("title", "")
        print(json.dumps({
            "ok": True, "problem": f"{target}. {title}".strip(), "accepted": bool(hit),
            **({"language": hit["lang"], "accepted_at": hit["when"].isoformat(timespec="minutes"),
                "submission_url": hit["url"]} if hit else
               {"note": "No Accepted submission among your ~20 most recent public ones. "
                        "If you just submitted, wait a minute and check again."})}, indent=2))
        return

    if a.command == "daily":
        if log["username"]:  # quietly learn what was solved on LeetCode, so it isn't picked or carried over
            try:
                record_accepted(log_path, log, fetch_recent_accepted(log["username"], catalog))
                log = parse_log(log_path)
                stats = compute_stats(log, catalog, today)
            except LeetCodeError:
                pass
        existing = next((d for d in reversed(log["daily"]) if d["date"] == today), None)
        carried = False
        if existing and not a.force:
            daily, reason = existing, existing["why"] or "Today's pick."
        else:
            prev = log["daily"][-1] if log["daily"] else None
            solved_nums = {e["num"] for e in log["history"]}
            already_carried = len(log["daily"]) >= 2 and log["daily"][-2]["num"] == prev["num"] if prev else False
            if (prev and prev["status"] == "pending" and prev["num"] not in solved_nums
                    and (today - prev["date"]).days == 1 and not already_carried and not a.force):
                p = by_num.get(prev["num"], {"num": prev["num"], "title": prev["title"], "diff": prev["diff"][0]})
                reason, carried = "Carried over from yesterday. Finish it before starting something new.", True
            else:
                p, reason = pick_problem(log, catalog, stats)
            daily = {"date": today, "num": p["num"], "title": p["title"], "diff": DIFF_NAME[p["diff"]], "status": "pending"}
            line = f'- {today.isoformat()}: {p["num"]}. {p["title"]} ({DIFF_NAME[p["diff"]]}) · status: pending · why: {reason}'
            write_daily(log_path, line, replace_pending_before=today)
            log = parse_log(log_path)
            stats = compute_stats(log, catalog, today)
        slug = by_num[daily["num"]]["slug"] if daily["num"] in by_num else slugify(daily["title"])
        dash = build_dashboard(practice_dir, log, catalog, stats, today)
        print(f'Today: {daily["num"]}. {daily["title"]} ({daily["diff"]})\nWhy: {reason}\n'
              f'Streak: {stats["streak"]} · Revisions due: {len(stats["due"])}\nDashboard: {dash}')
        if a.notify:
            notify(practice_dir, daily, slug, reason, stats, carried)
        if a.open:
            webbrowser.open(dash.as_uri())
        return

    dash = build_dashboard(practice_dir, log, catalog, stats, today)
    print(f"Dashboard: {dash}")
    if a.open:
        webbrowser.open(dash.as_uri())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""tp.py - state helper for the tiny-pieces skill (Python 3, stdlib only).

State is global, never inside a project folder:

    $TINY_PIECES_HOME (default ~/.tiny-pieces)
    |-- knowledge.md      the dev's profile + prerequisite graph (one row per concept)
    |-- probes.md         optional: the dev's own probes (same format as references/probes.md)
    `-- maps/<slug>.md    one gap map per goal

Every command re-reads the files under a lock and writes atomically, so several
agents (Claude Code, opencode, ...) can use it at the same time without
corrupting the markdown.

Profile commands
    init                                   create the directory and empty files
    check <concept>...                     probe / skip / recheck / gap decision per concept
    set <concept> <status> -e "evidence"   record a probe or exit-check result
    needs <concept> a,b,c [--add]          record direct prerequisites (global graph)
    alias <alias> <concept>                one name per concept
    show [concept]                         one row (+ needed-by) or the whole profile
    tree <concept>                         prerequisite tree with statuses
    order <concept>...                     learning order (prerequisites first)
    summary                                "what do I know?" by domain + weak spots
    stale                                  old green rows that need a re-check
    review [--goal slug]                   ONE concept for a quick review question

Map commands
    map new <slug> --sentence "..." [--project path]
    map piece <slug> "<piece>" --needs a,b [--pos N]    add/update a big piece
    map built <slug> "<piece>" [--undo]                 tick a piece after it runs
    map scope <slug> <concept> "just enough for the root"
    map later <slug> "<out of scope idea>"
    map log <slug> "<note>"
    map show <slug>                        rebuild + print the map
    map list                               all maps with progress
    next <slug>                            the single next action

Statuses: ok/known = known, shaky = shaky, gap = gap, unknown = not probed
(emoji work too). Status always comes from a probe result, never from a claim.
"""
import argparse
import contextlib
import datetime
import difflib
import os
import re
import sys
import tempfile
import unicodedata

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None

OK, WARN, GAP, UNK = "\u2705", "\u26a0\ufe0f", "\u274c", "\u2753"
_STATUS = {
    "\u2705": OK, "ok": OK, "known": OK, "pass": OK, "done": OK,
    "\u26a0": WARN, "warn": WARN, "shaky": WARN, "partial": WARN,
    "\u274c": GAP, "gap": GAP, "fail": GAP, "no": GAP,
    "\u2753": UNK, "?": UNK, "unknown": UNK, "todo": UNK,
}
COLS = ["Concept", "Domain", "Status", "Needs", "Evidence", "Verified", "Seen in"]
PREAMBLE = [
    "# Knowledge profile",
    "",
    'Status comes from probe results only, never from "yeah I know it".',
    "\u2705 known \u00b7 \u26a0\ufe0f shaky \u00b7 \u274c gap \u00b7 \u2753 not probed",
    "Managed by tiny-pieces (scripts/tp.py). Hand edits are fine: keep one row per concept.",
]
GEN_BEGIN = "<!-- tp:begin generated (rebuilt by tp.py, do not edit) -->"
GEN_END = "<!-- tp:end generated -->"


class Fail(Exception):
    pass


def die(msg):
    raise Fail(msg)


# ----------------------------------------------------------------- basics
def today():
    return os.environ.get("TP_TODAY") or datetime.date.today().isoformat()


def stale_days():
    try:
        return int(os.environ.get("TP_STALE_DAYS", "60"))
    except ValueError:
        return 60


def home():
    return os.path.expanduser(os.environ.get("TINY_PIECES_HOME", "~/.tiny-pieces"))


def know_path():
    return os.path.join(home(), "knowledge.md")


def maps_dir():
    return os.path.join(home(), "maps")


def norm(s):
    return re.sub(r"\s+", " ", s.strip()).lower()


def clean_name(s):
    s = re.sub(r"\s+", " ", s.strip())
    if not s:
        die("empty name")
    if "|" in s or "," in s:
        die("names cannot contain '|' or ',': %r" % s)
    return s


def split_list(s):
    return [clean_name(x) for x in s.split(",") if x.strip()] if s else []


def slugify(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    if not s:
        die("bad slug")
    return s


def status_of(s):
    key = s.strip().replace("\ufe0f", "").lower()
    if key not in _STATUS:
        die("unknown status %r (use ok, shaky, gap, unknown)" % s)
    return _STATUS[key]


def parse_status(s):
    try:
        return status_of(s)
    except Fail:
        return UNK


def parse_date(s):
    try:
        return datetime.date.fromisoformat(s.strip())
    except (ValueError, AttributeError):
        return None


def age(row):
    d = parse_date(row.get("verified", ""))
    if not d:
        return None
    return (datetime.date.fromisoformat(today()) - d).days


@contextlib.contextmanager
def locked():
    os.makedirs(home(), exist_ok=True)
    f = open(os.path.join(home(), ".lock"), "a+")
    try:
        if fcntl:
            fcntl.flock(f, fcntl.LOCK_EX)
        yield
    finally:
        if fcntl:
            fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def write_atomic(path, text):
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


# -------------------------------------------------------------- profile
class Know:
    def __init__(self):
        self.pre = list(PREAMBLE)
        self.rows = {}      # norm(name) -> row dict (insertion ordered)
        self.aliases = {}   # norm(alias) -> (alias, canonical name)
        self.post = []

    @classmethod
    def load(cls):
        k = cls()
        p = know_path()
        if not os.path.exists(p):
            return k
        with open(p, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        tbl = [i for i, l in enumerate(lines) if l.lstrip().startswith("|")]
        if tbl:
            a = b = tbl[0]
            while b + 1 < len(lines) and lines[b + 1].lstrip().startswith("|"):
                b += 1
            pre, table, rest = lines[:a], lines[a:b + 1], lines[b + 1:]
        else:
            pre, table, rest = lines, [], []
        while pre and not pre[-1].strip():
            pre.pop()
        if pre:
            k.pre = pre
        if table:
            head = [norm(c) for c in split_row(table[0])]
            for line in table[1:]:
                cells = split_row(line)
                if all(set(c) <= set(":- ") for c in cells):
                    continue
                d = dict(zip(head, cells))
                name = d.get("concept", "").strip()
                if not name:
                    continue
                k.rows[norm(name)] = {
                    "name": name,
                    "domain": d.get("domain", "").strip().lower(),
                    "status": parse_status(d.get("status", "")),
                    "needs": [x.strip() for x in d.get("needs", "").split(",") if x.strip()],
                    "evidence": d.get("evidence", ""),
                    "verified": d.get("verified", ""),
                    "seen": [x.strip() for x in d.get("seen in", "").split(",") if x.strip()],
                }
        post, in_alias = [], False
        for l in rest:
            if l.strip().lower().startswith("## aliases"):
                in_alias = True
                continue
            if l.startswith("## "):
                in_alias = False
            if in_alias:
                if "=" in l:
                    a_, c_ = l.split("=", 1)
                    if a_.strip() and c_.strip():
                        k.aliases[norm(a_)] = (a_.strip(), c_.strip())
            else:
                post.append(l)
        while post and not post[-1].strip():
            post.pop()
        while post and not post[0].strip():
            post.pop(0)
        k.post = post
        return k

    def save(self):
        out = list(self.pre) + [""]
        out.append("| " + " | ".join(COLS) + " |")
        out.append("|" + "|".join(["---"] * len(COLS)) + "|")
        for r in self.rows.values():
            ev = r["evidence"].replace("|", "/").replace("\n", " ")
            out.append("| " + " | ".join([
                r["name"], r["domain"], r["status"], ", ".join(r["needs"]),
                ev, r["verified"], ", ".join(r["seen"])]) + " |")
        if self.post:
            out += [""] + self.post
        if self.aliases:
            out += ["", "## Aliases"] + ["%s = %s" % v for v in self.aliases.values()]
        write_atomic(know_path(), "\n".join(out) + "\n")

    # one name per concept
    def find(self, name):
        n = norm(name)
        if n in self.rows:
            return n
        if n in self.aliases:
            c = norm(self.aliases[n][1])
            if c in self.rows:
                return c
        return None

    def ensure(self, name, allow_new=False):
        key = self.find(name)
        if key:
            return key
        name = clean_name(name)
        n = norm(name)
        if not allow_new:
            close = difflib.get_close_matches(n, list(self.rows) + list(self.aliases), n=3, cutoff=0.8)
            if close:
                die("%r looks like existing concept(s): %s. Use that name (or `alias`), "
                    "or add --new if it really is a different concept." % (name, ", ".join(close)))
        self.rows[n] = {"name": name, "domain": "", "status": UNK, "needs": [],
                        "evidence": "", "verified": "", "seen": []}
        return n

    def reaches(self, start, target, _seen=None):
        _seen = _seen if _seen is not None else set()
        if start == target:
            return True
        if start in _seen:
            return False
        _seen.add(start)
        row = self.rows.get(start)
        for c in (row["needs"] if row else []):
            ck = self.find(c)
            if ck and self.reaches(ck, target, _seen):
                return True
        return False

    def set_needs(self, key, names, allow_new=False, add=False, goal=None):
        keys = [self.ensure(n, allow_new) for n in names]
        for ck in keys:
            if ck == key or self.reaches(ck, key):
                die("cycle: %r cannot need %r" % (self.rows[key]["name"], self.rows[ck]["name"]))
            if goal:
                add_seen(self.rows[ck], goal)
        disp = [self.rows[ck]["name"] for ck in keys]
        row = self.rows[key]
        if add:
            for d in disp:
                if norm(d) not in [norm(x) for x in row["needs"]]:
                    row["needs"].append(d)
        else:
            row["needs"] = disp

    def needed_by(self, key):
        return [r["name"] for k2, r in self.rows.items()
                if any(self.find(n) == key for n in r["needs"])]


def add_seen(row, goal):
    g = slugify(goal)
    if g not in row["seen"]:
        row["seen"].append(g)


def ensure_home():
    os.makedirs(maps_dir(), exist_ok=True)
    if not os.path.exists(know_path()):
        Know().save()


# ----------------------------------------------------- plans and trees
def action_for(row):
    st = row["status"]
    if st == OK:
        a = age(row)
        return "RECHECK" if (a is not None and a > stale_days()) else "DONE"
    return {WARN: "REFRESH", GAP: "LEARN", UNK: "PROBE"}[st]


def blank_row(name):
    return {"name": name, "domain": "", "status": UNK, "needs": [], "evidence": "",
            "verified": "", "seen": []}


def plan(know, roots, seen):
    """Prerequisites first. Expand only through gap/shaky nodes; known nodes are floors."""
    out = []

    def visit(name):
        key = know.find(name) or norm(name)
        if key in seen:
            return
        seen.add(key)
        row = know.rows.get(key) or blank_row(name)
        if row["status"] in (GAP, WARN):
            for c in row["needs"]:
                visit(c)
        out.append((row["name"], row["status"], action_for(row)))

    for r in roots:
        visit(r)
    return out


def tree_lines(know, name, depth, seen, scopes, expand_all, parent_gap, max_depth, out):
    key = know.find(name) or norm(name)
    row = know.rows.get(key)
    disp = row["name"] if row else name
    st = row["status"] if row else UNK
    label = "%s- %s %s" % ("  " * depth, disp, st)
    if st == OK:
        a = age(row)
        if a is not None and a > stale_days():
            label += " (recheck)"
        elif parent_gap:
            label += " floor"
    if scopes.get(key):
        label += " [scope: %s]" % scopes[key]
    if key in seen:
        out.append(label + " -> see above")
        return
    seen.add(key)
    out.append(label)
    if row and row["needs"] and (expand_all or st in (GAP, WARN)) and depth < max_depth:
        for c in row["needs"]:
            tree_lines(know, c, depth + 1, seen, scopes, expand_all,
                       st in (GAP, WARN), max_depth, out)


# ------------------------------------------------------------------ maps
class Map:
    ORDER = ["Pieces", "Scopes", "Later", "Log"]
    GENERATED = {"tree", "learning order", "next"}

    def __init__(self, slug):
        self.slug = slug
        self.meta = {}
        self.sections = {}

    @classmethod
    def parse(cls, slug, text):
        m = cls(slug)
        text = re.sub(r"<!-- tp:begin.*?<!-- tp:end generated -->\n?", "", text, flags=re.S)
        lines = text.split("\n")
        rest = lines
        if lines and lines[0].strip() == "---":
            try:
                j = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
            except StopIteration:
                j = 0
            for l in lines[1:j]:
                if ":" in l:
                    k, v = l.split(":", 1)
                    m.meta[k.strip()] = v.strip()
            rest = lines[j + 1:]
        canon = {n.lower(): n for n in cls.ORDER}
        cur = None
        for l in rest:
            if l.startswith("## "):
                name = l[3:].strip()
                if name.lower() in cls.GENERATED:
                    cur = None
                    continue
                cur = canon.get(name.lower(), name)
                m.sections.setdefault(cur, [])
            elif cur is not None:
                m.sections[cur].append(l)
        for k in m.sections:
            ls = m.sections[k]
            while ls and not ls[-1].strip():
                ls.pop()
            while ls and not ls[0].strip():
                ls.pop(0)
        return m

    def pieces(self):
        out = []
        for l in self.sections.get("Pieces", []):
            mt = re.match(r"^- \[([ xX])\]\s+(.*?)(?:\s+\|\s*needs:\s*(.*))?$", l)
            if mt:
                out.append({"built": mt.group(1).lower() == "x", "name": mt.group(2).strip(),
                            "needs": [x.strip() for x in (mt.group(3) or "").split(",") if x.strip()]})
        return out

    def set_pieces(self, ps):
        self.sections["Pieces"] = [
            "- [%s] %s%s" % ("x" if p["built"] else " ", p["name"],
                             (" | needs: " + ", ".join(p["needs"])) if p["needs"] else "")
            for p in ps]

    def scope_items(self):
        out = {}
        for l in self.sections.get("Scopes", []):
            mt = re.match(r"^- (.+?):\s*(.*)$", l)
            if mt:
                out[mt.group(1).strip()] = mt.group(2).strip()
        return out

    def scope_map(self):
        return {norm(k): v for k, v in self.scope_items().items()}

    def set_scope(self, name, text):
        items = self.scope_items()
        for k in list(items):
            if norm(k) == norm(name):
                items[k] = text
                break
        else:
            items[name] = text
        self.sections["Scopes"] = ["- %s: %s" % (k, v) for k, v in items.items()]

    def append(self, section, line):
        self.sections.setdefault(section, []).append(line)

    def items(self, know):
        seen, out = set(), []
        scopes = self.scope_map()
        for p in self.pieces():
            rows = []
            for name, st, act in plan(know, p["needs"], seen):
                if act == "DONE":
                    rows.append((True, "%s %s" % (name, st)))
                else:
                    sc = scopes.get(norm(name))
                    rows.append((False, "%s %s %s%s" % (act, name, st, (" - scope: " + sc) if sc else "")))
            rows.append((p["built"], "BUILD %s" % p["name"]))
            out.append((p["name"], rows))
        return out

    def next_action(self, know):
        if not self.pieces():
            return 'No pieces yet. Add them: tp.py map piece %s "<piece>" --needs a,b' % self.slug
        for _, rows in self.items(know):
            for done, text in rows:
                if not done:
                    return text
        return "DONE - every piece is built"

    def generated(self, know):
        goal = self.meta.get("goal", self.slug)
        scopes = self.scope_map()
        lines = ["## Tree", "- %s \U0001f3af root" % goal]
        seen = set()
        for p in self.pieces():
            lines.append("  - %s (piece)%s" % (p["name"], " \U0001f528 built" if p["built"] else ""))
            for need in p["needs"]:
                tree_lines(know, need, 2, seen, scopes, False, False, 12, lines)
        lines += ["", "## Learning order"]
        for i, (pname, rows) in enumerate(self.items(know), 1):
            lines.append("### %d. %s" % (i, pname))
            for done, text in rows:
                lines.append("- [%s] %s" % ("x" if done else " ", text))
        lines += ["", "## Next", self.next_action(know)]
        return lines

    def dump(self, know):
        goal = self.meta.get("goal", self.slug)
        out = ["---"] + ["%s: %s" % kv for kv in self.meta.items()] + ["---", "# Map: %s" % goal, ""]
        out += [GEN_BEGIN] + self.generated(know) + [GEN_END, ""]
        names = list(self.ORDER) + [n for n in self.sections if n not in self.ORDER]
        for n in names:
            out += ["## " + n] + self.sections.get(n, []) + [""]
        return "\n".join(out).rstrip("\n") + "\n"


def map_path(slug):
    return os.path.join(maps_dir(), slugify(slug) + ".md")


def load_map(slug):
    p = map_path(slug)
    if not os.path.exists(p):
        die("no map %r. Create it: tp.py map new %s --sentence \"...\"" % (slug, slugify(slug)))
    with open(p, encoding="utf-8") as fh:
        return Map.parse(slugify(slug), fh.read())


def save_map(m, know, touch=True):
    if touch:
        m.meta["updated"] = today()
    write_atomic(map_path(m.slug), m.dump(know))


def all_slugs():
    d = maps_dir()
    if not os.path.isdir(d):
        return []
    return sorted(f[:-3] for f in os.listdir(d) if f.endswith(".md"))


def render_all_maps(know):
    for slug in all_slugs():
        save_map(load_map(slug), know, touch=False)


# -------------------------------------------------------------- commands
def cmd_init(a):
    with locked():
        ensure_home()
    print("ready: %s" % home())


def cmd_set(a):
    status = status_of(a.status)
    if status != UNK and not a.evidence:
        die("evidence is required (-e) for known/shaky/gap: what exactly did they solve or fail?")
    with locked():
        ensure_home()
        k = Know.load()
        key = k.ensure(a.concept, a.new)
        row = k.rows[key]
        prev = row["status"]
        row["status"] = status
        if status == UNK:
            row["verified"] = ""
        else:
            row["verified"] = a.date or today()
        if a.evidence:
            row["evidence"] = a.evidence
        if a.domain:
            row["domain"] = a.domain.strip().lower()
        if a.needs is not None:
            k.set_needs(key, split_list(a.needs), a.new, goal=a.goal)
        if a.goal:
            add_seen(row, a.goal)
        k.save()
        render_all_maps(k)
    note = ""
    if prev == OK and status in (WARN, GAP):
        note = "  (downgraded from %s)" % OK
    needs = ("  needs: " + ", ".join(row["needs"])) if row["needs"] else ""
    print("%s %s%s%s" % (row["name"], status, needs, note))


def cmd_needs(a):
    with locked():
        ensure_home()
        k = Know.load()
        key = k.ensure(a.concept, a.new)
        k.set_needs(key, split_list(a.needs), a.new, add=a.add, goal=a.goal)
        if a.goal:
            add_seen(k.rows[key], a.goal)
        k.save()
        render_all_maps(k)
    print("%s needs: %s" % (k.rows[key]["name"], ", ".join(k.rows[key]["needs"]) or "-"))


def cmd_alias(a):
    with locked():
        ensure_home()
        k = Know.load()
        key = k.find(a.concept)
        if not key:
            die("unknown concept %r (create it first with `set`)" % a.concept)
        al = clean_name(a.alias)
        if norm(al) in k.rows:
            die("%r is already a concept row" % al)
        k.aliases[norm(al)] = (al, k.rows[key]["name"])
        k.save()
    print("%s = %s" % (al, k.rows[key]["name"]))


def cmd_check(a):
    k = Know.load()
    for name in a.concepts:
        key = k.find(name)
        row = k.rows.get(key) if key else None
        if not row or row["status"] == UNK:
            print("%s: probe" % (row["name"] if row else name))
            continue
        ag = age(row)
        if row["status"] == OK:
            if ag is not None and ag > stale_days():
                print("%s: recheck (%s, verified %s, %d days ago)" % (row["name"], OK, row["verified"], ag))
            else:
                print("%s: skip (%s, verified %s)" % (row["name"], OK, row["verified"] or "?"))
        else:
            if row["needs"]:
                tail = "needs: " + ", ".join(row["needs"])
            else:
                tail = "no prerequisites recorded: derive 1-3, then run `needs`"
            print("%s: gap (%s since %s) - %s" % (row["name"], row["status"], row["verified"] or "?", tail))


def cmd_show(a):
    k = Know.load()
    if not a.concept:
        if not os.path.exists(know_path()):
            print("(empty: run tp.py init)")
            return
        with open(know_path(), encoding="utf-8") as fh:
            print(fh.read())
        return
    key = k.find(a.concept)
    if not key:
        die("unknown concept %r" % a.concept)
    r = k.rows[key]
    print("%s %s  domain: %s  verified: %s" % (r["name"], r["status"], r["domain"] or "-", r["verified"] or "-"))
    print("evidence: %s" % (r["evidence"] or "-"))
    print("needs: %s" % (", ".join(r["needs"]) or "-"))
    print("needed by: %s" % (", ".join(k.needed_by(key)) or "-"))
    print("seen in: %s" % (", ".join(r["seen"]) or "-"))


def cmd_tree(a):
    k = Know.load()
    if not k.find(a.concept):
        die("unknown concept %r" % a.concept)
    out = []
    tree_lines(k, a.concept, 0, set(), {}, True, False, a.depth, out)
    print("\n".join(out))


def cmd_order(a):
    k = Know.load()
    n = 0
    for name, st, act in plan(k, a.concepts, set()):
        if act == "DONE" and not a.all:
            continue
        n += 1
        print("%d. %s %s %s" % (n, act, name, st))
    if n == 0:
        print("nothing to learn: everything is known")


def cmd_stale(a):
    k = Know.load()
    days = a.days if a.days is not None else stale_days()
    found = [(r["verified"], r["name"]) for r in k.rows.values()
             if r["status"] == OK and age(r) is not None and age(r) > days]
    for d, n in sorted(found):
        print("%s  %s" % (d, n))
    if not found:
        print("no stale rows (> %d days)" % days)


def cmd_summary(a):
    k = Know.load()
    if not k.rows:
        print("Profile is empty: nothing probed yet.")
        return
    doms = {}
    for r in k.rows.values():
        d = doms.setdefault(r["domain"] or "general", {OK: 0, WARN: 0, GAP: 0, UNK: 0})
        d[r["status"]] += 1
    w = max(len(d) for d in doms)
    print("%s  %s  %s  %s  %s" % ("domain".ljust(w), OK, WARN, GAP, UNK))
    for d in sorted(doms):
        c = doms[d]
        print("%s  %2d  %2d  %2d  %2d" % (d.ljust(w), c[OK], c[WARN], c[GAP], c[UNK]))
    weak = [r for r in k.rows.values() if r["status"] in (GAP, WARN)]
    weak.sort(key=lambda r: (r["status"] != GAP, r["name"]))
    if weak:
        print("\nWeak spots:")
        for r in weak:
            print("  %s %s%s" % (r["status"], r["name"], (" - " + r["evidence"]) if r["evidence"] else ""))
    st = [r["name"] for r in k.rows.values()
          if r["status"] == OK and age(r) is not None and age(r) > stale_days()]
    if st:
        print("\nStale %s (> %d days): %s" % (OK, stale_days(), ", ".join(st)))
    unk = [r["name"] for r in k.rows.values() if r["status"] == UNK]
    if unk:
        print("\nNot probed yet: %s" % ", ".join(unk))


def cmd_review(a):
    k = Know.load()
    cands = [(r["verified"], key) for key, r in k.rows.items()
             if r["status"] == OK and age(r) is not None and age(r) >= 1]
    if not cands:
        print("nothing to review")
        return
    pick = None
    if a.goal:
        m = load_map(a.goal)
        inmap = set()
        def walk(name):
            kk = k.find(name)
            if not kk or kk in inmap:
                return
            inmap.add(kk)
            for c in k.rows[kk]["needs"]:
                walk(c)

        for p in m.pieces():
            for n in p["needs"]:
                walk(n)
        pool = sorted(c for c in cands if c[1] in inmap)
        if pool:
            pick = pool[0]
    if not pick:
        pick = sorted(cands)[0]
    r = k.rows[pick[1]]
    print("REVIEW %s (last verified %s, %d days ago)" % (r["name"], r["verified"], age(r)))
    print("Ask ONE quick probe. Pass: tp.py set \"%s\" ok -e \"...\"  Fail: tp.py set \"%s\" shaky -e \"...\"" % (r["name"], r["name"]))


def cmd_next(a):
    k = Know.load()
    print(load_map(a.slug).next_action(k))


# map subcommands
def cmd_map_new(a):
    slug = slugify(a.slug)
    with locked():
        ensure_home()
        if os.path.exists(map_path(slug)):
            die("map %r already exists" % slug)
        m = Map(slug)
        m.meta = {"goal": a.goal or slug, "sentence": a.sentence or "", "project": a.project or "",
                  "created": today(), "updated": today()}
        m.sections = {"Pieces": [], "Scopes": [], "Later": [], "Log": ["- %s map created" % today()]}
        k = Know.load()
        save_map(m, k, touch=False)
    print("created %s" % map_path(slug))


def cmd_map_piece(a):
    with locked():
        ensure_home()
        k = Know.load()
        m = load_map(a.slug)
        needs = split_list(a.needs)
        disp = []
        for n in needs:
            key = k.ensure(n, a.new)
            add_seen(k.rows[key], m.slug)
            disp.append(k.rows[key]["name"])
        name = clean_name(a.piece)
        ps = m.pieces()
        for p in ps:
            if norm(p["name"]) == norm(name):
                p["needs"] = disp
                break
        else:
            ps.insert((a.pos - 1) if a.pos else len(ps), {"built": False, "name": name, "needs": disp})
        m.set_pieces(ps)
        k.save()
        save_map(m, k)
        render_all_maps(k)
    print("piece %r needs: %s" % (name, ", ".join(disp) or "-"))


def cmd_map_built(a):
    with locked():
        k = Know.load()
        m = load_map(a.slug)
        ps = m.pieces()
        for p in ps:
            if norm(p["name"]) == norm(a.piece):
                p["built"] = not a.undo
                break
        else:
            die("no piece %r in map %s" % (a.piece, m.slug))
        m.set_pieces(ps)
        m.append("Log", "- %s %s %s" % (today(), "unbuilt" if a.undo else "built", p["name"]))
        save_map(m, k)
    print("%s: %s" % (p["name"], "not built" if a.undo else "built"))
    print("next: %s" % m.next_action(k))


def cmd_map_scope(a):
    with locked():
        k = Know.load()
        m = load_map(a.slug)
        key = k.find(a.concept)
        m.set_scope(k.rows[key]["name"] if key else clean_name(a.concept), a.text)
        save_map(m, k)
    print("scope set")


def cmd_map_later(a):
    with locked():
        k = Know.load()
        m = load_map(a.slug)
        m.append("Later", "- " + a.text)
        save_map(m, k)
    print("added to Later")


def cmd_map_log(a):
    with locked():
        k = Know.load()
        m = load_map(a.slug)
        m.append("Log", "- %s %s" % (today(), a.text))
        save_map(m, k)
    print("logged")


def cmd_map_show(a):
    with locked():
        k = Know.load()
        m = load_map(a.slug)
        save_map(m, k, touch=False)
    with open(map_path(a.slug), encoding="utf-8") as fh:
        print(fh.read())


def cmd_map_list(a):
    k = Know.load()
    slugs = all_slugs()
    if not slugs:
        print("no maps yet")
    for s in slugs:
        m = load_map(s)
        ps = m.pieces()
        print("%s - %d/%d pieces built - next: %s" % (
            s, sum(1 for p in ps if p["built"]), len(ps), m.next_action(k)))


# ------------------------------------------------------------------- cli
def build_parser():
    ap = argparse.ArgumentParser(prog="tp.py", description="tiny-pieces state helper (see module docstring)")
    sp = ap.add_subparsers(dest="cmd")

    sp.add_parser("init").set_defaults(fn=cmd_init)

    p = sp.add_parser("set")
    p.add_argument("concept")
    p.add_argument("status")
    p.add_argument("-e", "--evidence")
    p.add_argument("-d", "--domain")
    p.add_argument("--needs", help="comma list, replaces the prerequisites")
    p.add_argument("-g", "--goal")
    p.add_argument("--date")
    p.add_argument("--new", action="store_true", help="allow a name close to an existing concept")
    p.set_defaults(fn=cmd_set)

    p = sp.add_parser("needs")
    p.add_argument("concept")
    p.add_argument("needs")
    p.add_argument("--add", action="store_true")
    p.add_argument("-g", "--goal")
    p.add_argument("--new", action="store_true")
    p.set_defaults(fn=cmd_needs)

    p = sp.add_parser("alias")
    p.add_argument("alias")
    p.add_argument("concept")
    p.set_defaults(fn=cmd_alias)

    p = sp.add_parser("check")
    p.add_argument("concepts", nargs="+")
    p.set_defaults(fn=cmd_check)

    p = sp.add_parser("show")
    p.add_argument("concept", nargs="?")
    p.set_defaults(fn=cmd_show)

    p = sp.add_parser("tree")
    p.add_argument("concept")
    p.add_argument("--depth", type=int, default=12)
    p.set_defaults(fn=cmd_tree)

    p = sp.add_parser("order")
    p.add_argument("concepts", nargs="+")
    p.add_argument("--all", action="store_true", help="include known nodes")
    p.set_defaults(fn=cmd_order)

    p = sp.add_parser("stale")
    p.add_argument("--days", type=int)
    p.set_defaults(fn=cmd_stale)

    sp.add_parser("summary").set_defaults(fn=cmd_summary)

    p = sp.add_parser("review")
    p.add_argument("--goal")
    p.set_defaults(fn=cmd_review)

    p = sp.add_parser("next")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_next)

    mp = sp.add_parser("map").add_subparsers(dest="mcmd")
    p = mp.add_parser("new")
    p.add_argument("slug")
    p.add_argument("--goal")
    p.add_argument("--sentence")
    p.add_argument("--project")
    p.set_defaults(fn=cmd_map_new)
    p = mp.add_parser("piece")
    p.add_argument("slug")
    p.add_argument("piece")
    p.add_argument("--needs", default="")
    p.add_argument("--pos", type=int)
    p.add_argument("--new", action="store_true")
    p.set_defaults(fn=cmd_map_piece)
    p = mp.add_parser("built")
    p.add_argument("slug")
    p.add_argument("piece")
    p.add_argument("--undo", action="store_true")
    p.set_defaults(fn=cmd_map_built)
    p = mp.add_parser("scope")
    p.add_argument("slug")
    p.add_argument("concept")
    p.add_argument("text")
    p.set_defaults(fn=cmd_map_scope)
    p = mp.add_parser("later")
    p.add_argument("slug")
    p.add_argument("text")
    p.set_defaults(fn=cmd_map_later)
    p = mp.add_parser("log")
    p.add_argument("slug")
    p.add_argument("text")
    p.set_defaults(fn=cmd_map_log)
    p = mp.add_parser("show")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_map_show)
    mp.add_parser("list").set_defaults(fn=cmd_map_list)
    return ap


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = build_parser()
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 0
    try:
        a.fn(a)
    except Fail as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

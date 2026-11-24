"""Review 5 / area 6: which suites REALLY catch a break.
Mode "own": the review 5 breaks below (NOT part of the product registry), each applied on a temp copy; ALL suites of
run_all.py are run (in parallel) and the failing ones listed. Mode "registry [prefix...]": the same for the entries of
Wp_claude/tests/breaks/*.py, reporting entries caught ONLY by generic suites (rule literals, review pack, view
contract, ascii, module size, perf) or not by the suites they name.
The working tree is never touched (break_check.py's temp-copy method).
Run: python Wp_claude/tests/review5/breaks5.py own | registry p16 p17 ..."""
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
sys.path.insert(0, TESTS)
import break_check as bc  # noqa: E402
import run_all  # noqa: E402

GENERIC = ("test_rule_literals.py", "test_review_pack.py", "test_view_contract.py", "test_ascii_code.py",
           "test_module_size.py", "test_perf.py")

D, S, C, F, B = ("wp/core/damage.py", "wp/app/session.py", "wp/model/cache.py", "wp/app/files.py",
                 "wp/commands/base.py")
DV, K, H, IT = "wp/model/defense_view.py", "wp/model/classes.py", "wp/model/hands.py", "wp/model/items.py"
OWN = [
    dict(id="r5-ceil-floor", file=D, old="    return -(-a // b)", new="    return a // b",
         rule="damage rounds UP"),
    dict(id="r5-percent-floor", file=D, old="    return ceil_div(amount * (100 - percent), 100)",
         new="    return amount * (100 - percent) // 100", rule="percent reduction rounded up"),
    dict(id="r5-modifier-cap", file=D, old="    pct = max(-100, int(pct))", new="    pct = max(-200, int(pct))",
         rule="modifier never below -100 (core)"),
    dict(id="r5-dr-no-stacking", file=DV, old=" + sum(v for _, v, _, s in es if s))", new=" + 0)",
         rule="stacking DR entries add"),
    dict(id="r5-dr-sum-all", file=DV, old="max(0, max([0] + [v for _, v, _, s in es if not s])",
         new="max(0, sum([0] + [v for _, v, _, s in es if not s])", rule="non-stacking DR: the largest"),
    dict(id="r5-modifier-winner", file=DV, old="bo.winner(max([0] + vs), min([0] + vs))", new="max([0] + vs)",
         rule="percent modifier: larger absolute value wins"),
    dict(id="r5-modifier-floor-view", file=DV, old="return max(-100, bo.winner(", new="return max(-1000, bo.winner(",
         rule="modifier never below -100 (view)"),
    dict(id="r5-dr-resist-add", file=DV, old="best = max(own, d if t in PHYSICAL else 0, int(flat.get(t, 0)))",
         new="best = own + (d if t in PHYSICAL else 0) + int(flat.get(t, 0))", rule="one flat reduction: the larger"),
    dict(id="r5-dr-on-fire", file=DV, old="best = max(own, d if t in PHYSICAL else 0,", new="best = max(own, d,",
         rule="DR only on physical types"),
    dict(id="r5-hidden-gt", file=IT, old="    return qualification_level(it) >= h.min_qualification",
         new="    return qualification_level(it) > h.min_qualification", rule="hidden property unlocked at N"),
    dict(id="r5-hidden-unbought", file=IT, old="    return it.qualification_n if it.qualified else 0",
         new="    return it.qualification_n", rule="qualification counts only once bought"),
    dict(id="r5-spell-dice-negative", file="wp/model/spell_damage.py",
         old='"dice_count": max(0, _value(d.dice_count, level))', new='"dice_count": _value(d.dice_count, level)',
         rule="spell dice never below 0"),
    dict(id="r5-spell-rollmod", file="wp/model/spell_damage.py", old='"roll_modifier": pain + morale}',
         new='"roll_modifier": pain - morale}', rule="spell roll modifier = pain + morale"),
    dict(id="r5-spell-level", file="wp/model/spell_damage.py", old="    level = ch.level if level is None else",
         new="    level = 1 if level is None else", rule="caster level = character level"),
    dict(id="r5-shield-side", file=H, old='        first = rd.const("hands.default_shield_side", ch)',
         new="        first = RIGHT", rule="default shield hand from the constant"),
    dict(id="r5-stored-side", file=H, old="        if it.hand in free:", new="        if False:",
         rule="a stored hand side wins"),
    dict(id="r5-bab-round", file=K, old="    return int(math.floor(level * float(factor)))",
         new="    return int(round(level * float(factor)))", rule="class BAB rounded down"),
    dict(id="r5-save-good", file=K, old='+ level // int(rd.const("class.save_good_divisor", ch))',
         new='+ (level + 1) // int(rd.const("class.save_good_divisor", ch))', rule="good save = 2 + level/2 down"),
    dict(id="r5-bab-override", file=K,
         old="    return ch.bab_override if ch.bab_override is not None else class_bab(ci, ch.level, ch)",
         new="    return class_bab(ci, ch.level, ch)", rule="BAB override wins"),
    dict(id="r5-save-override", file=K, old="    if key in ch.save_override:", new="    if False:",
         rule="save override wins"),
    dict(id="r5-class-hit-die", file=K, old="    return ci.hit_die if ci is not None and ci.hit_die > 0 else ch.hit_die",
         new="    return ch.hit_die", rule="class hit die caps level_up"),
    dict(id="r5-iter-cap", file="wp/model/iterative.py", old="    return min(0, int(base) + stg.value(ch, TARGET))",
         new="    return int(base) + stg.value(ch, TARGET)", rule="an iterative step never goes above 0"),
    dict(id="r5-iter-ignore", file="wp/model/iterative.py", old="    if ef.ignores_iterative(ch.statuses):",
         new="    if False:", rule="ignores_iterative status: no penalty"),
    dict(id="r5-principle-gt", file="wp/commands/notebook_cmds.py",
         old='    need = d.level >= int(rd.const("narrative.principle_min_level", ch))',
         new='    need = d.level > int(rd.const("narrative.principle_min_level", ch))', rule="principle needed at N"),
    dict(id="r5-undo-nonundoable", file=S,
         old='        if command not in NON_UNDOABLE and int(self.setting("undo_depth")) > 0:',
         new='        if int(self.setting("undo_depth")) > 0:', rule="non-undoable commands skip the stack"),
    dict(id="r5-undo-redo-kept", file=S, old="            self._redo = []\n        self.character = result.state",
         new="            pass\n        self.character = result.state", rule="a new command clears redo"),
    dict(id="r5-undo-unbounded", file=S, old='[-int(self.setting("undo_depth")):]', new="",
         rule="undo stack bounded by undo_depth"),
    dict(id="r5-open-keeps-undo", file=S, old="        self._undo, self._redo = [], []", new="        pass",
         rule="open / new clear the stacks"),
    dict(id="r5-autosave-every", file=S, old="            self.save()\n        for fn in self._subscribers:",
         new="            pass\n        for fn in self._subscribers:", rule="autosave every_command saves"),
    dict(id="r5-autosave-interval", file=S, old='>= int(self.setting("autosave_interval_s")):', new=">= 0:",
         rule="autosave waits for the interval"),
    dict(id="r5-topics-unknown", file=S, old="    return (ALL,) if t is None else tuple(t)",
         new="    return () if t is None else tuple(t)", rule="a command missing from topics refreshes all"),
    dict(id="r5-subscribers-skipped", file=S, old="        for fn in self._subscribers:\n            fn(topics)",
         new="        for fn in self._subscribers[:0]:\n            fn(topics)", rule="subscribers get the topics"),
    dict(id="r5-backup-keep-plus", file=F, old="    for old in backups_of(folder, name, sub)[keep:]:",
         new="    for old in backups_of(folder, name, sub)[keep + 1:]:", rule="only backups_count backups kept"),
    dict(id="r5-backup-oldest", file=F, old="    for p in backups_of(folder, name, sub):\n        try:",
         new="    for p in reversed(backups_of(folder, name, sub)):\n        try:", rule="recovery = the NEWEST valid"),
    dict(id="r5-hard-delete", file=F, old="    os.replace(p, dst)\n    return dst", new="    os.remove(p)\n    return dst",
         rule="delete goes to the trash"),
    dict(id="r5-rename-backups", file=F, old="        os.replace(p, os.path.join(os.path.dirname(p), new_name + base))",
         new="        pass", rule="backups follow a rename"),
    dict(id="r5-name-dotdot", file=F, old=' or name in (".", "..")', new="", rule="'..' is not a name"),
    dict(id="r5-cache-scope", file=C, old="        key = (name, tuple(parts), _scope_key())",
         new="        key = (name, tuple(parts))", rule="cache key holds the rule scope"),
    dict(id="r5-cache-identity", file=C, old="        if hit is not None and all(x is y for x, y in zip(hit[0], kept)):",
         new="        if hit is not None:", rule="cache entry kept objects checked"),
    dict(id="r5-cache-noclear", file=B, old="    cache.clear()                      # a read cache",
         new="    pass                      # a read cache", rule="dispatch clears the cache (expected harmless)"),
    dict(id="r5-noop-logged", file=B, old="    if CHANGED in result.events and result.state == ch:",
         new="    if False:", rule="a no-op is not journaled"),
    dict(id="r5-cap-clamp", file=B, old="        if ch.balance_current > cap:", new="        if False:",
         rule="in combat balance clamped to the cap"),
    dict(id="r5-mana-block", file="wp/commands/reaction_cmds.py", old='    if blk.restore_blocked(ch, "mana"):',
         new="    if False:", rule="restore_mana refused while blocked"),
    dict(id="r5-mana-negative", file="wp/commands/reaction_cmds.py", old="    if amount < 0:", new="    if amount < -99:",
         rule="restore_mana amount >= 0"),
    dict(id="r5-pick-flags-group", file="wp/model/pick_flags.py", old="if group is None or e.weapon.name == group",
         new="if True", rule="pick flags filtered by group"),
    dict(id="r5-ac-ranged-shield", file="wp/core/ac_zones.py",
         old="        use_shield = on and (not ranged or rules.ranged_keeps_shield)",
         new="        use_shield = on and not ranged", rule="ranged keeps the shield"),
    dict(id="r5-ac-shield-mirror", file="wp/core/ac_zones.py",
         old='    c = str(TABLE["mirror"][cell]) if shield_hand == RIGHT else cell', new="    c = cell",
         rule="right-hand shield mirrors the cells"),
    dict(id="r5-ac-two-shields", file="wp/core/ac_zones.py",
         old="    return max([v for t, side, v in shields if v > 0 and covered(cell, t, side, rules)] or [0])",
         new="    return sum([v for t, side, v in shields if v > 0 and covered(cell, t, side, rules)] or [0])",
         rule="two shields: the larger per cell"),
    dict(id="r5-undo-json-empty", file="wp/app/data/undo.json",
         old='"non_undoable": ["set_char_setting", "reset_char_setting"]', new='"non_undoable": []',
         rule="undo.json lists the non-undoable commands"),
]


def run_suites(tmp, suites):
    def one(s):
        r = subprocess.run([sys.executable, s], capture_output=True, text=True, cwd=tmp)
        return os.path.basename(s), r.returncode != 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        return [name for name, failed in ex.map(one, suites) if failed]


def apply(tmp, e):
    path = os.path.join(tmp, e["file"])
    raw = open(path, "rb").read()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    old = e["old"].encode("ascii").replace(b"\n", nl)
    new = e["new"].encode("ascii").replace(b"\n", nl)
    if raw.count(old) != 1:
        return None, raw
    open(path, "wb").write(raw.replace(old, new))
    return path, raw


def main(mode, prefixes):
    tmp = tempfile.mkdtemp(prefix="wp_r5b_")
    try:
        bc._copy(tmp)
        suites = run_all.suites(os.path.join(tmp, "Wp_claude", "tests"))
        clean = run_suites(tmp, suites)
        print("clean copy: failing suites %s" % (clean,))
        entries = OWN if mode == "own" else [e for e in bc.registry() if not prefixes or
                                             any(e["id"].startswith(p) for p in prefixes)]
        counts = {"caught": 0, "generic only": 0, "missed": 0, "not applied": 0, "not by named": 0}
        for e in entries:
            path, raw = apply(tmp, e)
            if path is None:
                counts["not applied"] += 1
                print("%-28s NOT APPLIED (pattern count %d)" % (e["id"], raw.count(e["old"].encode("ascii"))))
                continue
            try:
                failed = [s for s in run_suites(tmp, suites) if s not in clean]
            finally:
                open(path, "wb").write(raw)
            real = [s for s in failed if s not in GENERIC]
            named = [os.path.basename(s) for s in e.get("suites", ())]
            if not failed:
                tag = "missed"
            elif not real:
                tag = "generic only"
            else:
                tag = "caught"
            counts[tag] += 1
            extra = ""
            if named and not any(n in failed for n in named):
                counts["not by named"] += 1
                extra = " NOT BY NAMED %s" % named
            print("%-28s %-12s by %s%s | %s" % (e["id"], tag, ",".join(f[:-3] for f in failed) or "-", extra,
                                                  e.get("rule", "")[:60]))
        print("%s: entries %d, %s" % (mode, len(entries), ", ".join("%s %d" % kv for kv in counts.items())))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "own", sys.argv[2:])

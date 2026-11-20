"""Character save/load (D11). Run: python Wp_claude/tests/storage/test_character_io.py"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
from _runner import Suite  # noqa: E402

from wp.model.notebook import Drive
from wp.core import effects as ef  # noqa: E402
from wp.core import skills as sk  # noqa: E402
from wp.core.damage import Pool  # noqa: E402
from wp.core.effects import Effect, Status  # noqa: E402
from wp.core.pain import PainEntry  # noqa: E402
from wp.core.rest import Charge  # noqa: E402
from wp.core.weapons import Pick, Weapon  # noqa: E402
from wp.model.character import Ability, AttackRecord, Character, Item, Language, WeaponEntry  # noqa: E402
from wp.storage import character_io as cio  # noqa: E402

S = Suite("test_character_io")


def sample():
    a = dict(Character().abilities)
    a["str"] = Ability(13, race=2, bonuses=(("belt", 2),), damage=1)
    return Character(
        level=3, abilities=a, hp_rolls=(8, 6, 6), hp_current=-4, temp_hp=2, bp_current=3,
        mana=Pool(4, 6), mana_enabled=True, caster="mana", slots={0: Pool(2, 3), 1: Pool(1, 2)},
        resources={"ki": Pool(1, 4)}, charges=(Charge("rage", "ability", Pool(1, 3)),),
        pain=(PainEntry(2, "overflow"), PainEntry(1, "curse", True)), trauma=7, overload=2,
        statuses=(Status("bleed", sid="s1", per_tick_hp=-2, duration=ef.TICKS, remaining=2),
                  Status("feral", sid="s2", effects=(Effect("attack", value_source=ef.OVERLOAD, weapon="natural"),))),
        items=(Item("i1", "sword", kind="weapon", in_hands=True, hands=1, groups=("w1",), activation_day=1,
                    activated=True, active_until="short", skill_penalty=-1,
                    effects_on=(Effect("attack", 5, "enhancement"),)),),
        weapons=(WeaponEntry(Weapon("w1", 2, 1, grades=5, parents=("w0",)), "long swords",
                             (Pick(5, "parry_1"),)),),
        skills=(sk.Skill("arcana", "int", sk.ADVANCED, 3),), languages=(Language("l1", "Common", True),),
        drives=(Drive("growth", "Growth", 4),), attention=3, spirit_current=4, shield_grade="light",
        attacks=(AttackRecord("r1", "i1", "w1", "one", primary=True),), balance_cap_hits=2, ov=5)


def tmpdir():
    return tempfile.mkdtemp(prefix="wpio_")


@S.case("round-trip", "D11: save -> load -> equal", True)
def _rt():
    d = tmpdir()
    try:
        p = os.path.join(d, "hero.json")
        cio.save(sample(), p)
        return cio.load(p) == sample()
    finally:
        shutil.rmtree(d)


@S.case("version-in-file", "D11: format and version are written", ("wipefinder.character", 1))
def _ver():
    data = json.loads(cio.dumps(sample()))
    return (data["format"], data["version"])


@S.case("base-only", "D6: only base values in the file (no derived maxima)", (False, False, False, True))
def _base():
    text = cio.dumps(sample())
    return ("hp_max" in text, "balance_max" in text, "spirit_max" in text, "hp_rolls" in text)


@S.case("broken-file", "D11: broken file -> clear error, file untouched, backup used", (True, True, "backup"))
def _broken():
    d = tmpdir()
    try:
        p = os.path.join(d, "hero.json")
        cio.save(sample(), p)
        cio.save(sample(), p)                       # second save keeps a .bak of the first
        with io.open(p, "w", encoding="utf-8") as f:
            f.write('{"format": "wipefinder.character", "version": 1, "charac')
        before = io.open(p, encoding="utf-8").read()
        try:
            cio.load(p)
            err = False
        except cio.StorageError as e:
            err = "backup exists" in str(e)
        untouched = io.open(p, encoding="utf-8").read() == before
        ch, src = cio.load_with_backup(p)
        return (err, untouched and ch == sample(), src)
    finally:
        shutil.rmtree(d)


@S.case("broken-not-backed-up", "D11: saving over a broken file does not overwrite the good .bak", True)
def _bak_kept():
    d = tmpdir()
    try:
        p = os.path.join(d, "hero.json")
        cio.save(sample(), p)
        cio.save(sample(), p)
        with io.open(p, "w", encoding="utf-8") as f:
            f.write("garbage")
        cio.save(Character(), p)                    # broken main must not become the backup
        return cio.load(p + cio.BAK_SUFFIX) == sample()
    finally:
        shutil.rmtree(d)


@S.case("interrupted-write", "D11: crash during write -> old file intact, no .tmp left", (True, False))
def _interrupt():
    d = tmpdir()
    real = cio._write_text
    try:
        p = os.path.join(d, "hero.json")
        cio.save(sample(), p)

        def crash(f, text):
            f.write(text[: len(text) // 2])
            raise OSError("power cut")
        cio._write_text = crash
        try:
            cio.save(Character(level=9), p)
        except OSError:
            pass
        cio._write_text = real
        return (cio.load(p) == sample(), os.path.exists(p + cio.TMP_SUFFIX))
    finally:
        cio._write_text = real
        shutil.rmtree(d)


@S.case("unknown-version", "D1/D11: unknown format version -> clear error", "unsupported character file version 2")
def _unknown():
    text = cio.dumps(Character()).replace('"version": 1', '"version": 2')
    try:
        cio.loads(text)
    except cio.StorageError as e:
        return str(e).split(";")[0]
    return "loaded"


@S.case("not-a-character", "D11: other JSON -> clear error", "not a WipeFinder character file")
def _other():
    try:
        cio.loads('{"hello": 1}')
    except cio.StorageError as e:
        return str(e)
    return "loaded"


@S.case("unknown-field", "CLAUDE.md [OWNER, package 16 A8]: an unknown field is dropped on load (no migration)", True)
def _field():
    data = json.loads(cio.dumps(Character()))
    data["character"]["hp_max"] = 99
    return cio.loads(json.dumps(data)) == Character()


if __name__ == "__main__":
    sys.exit(S.run())

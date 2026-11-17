# Stat damage [OWNER]

- Ability scores can take damage: shown "current/max", e.g. Str 17/18 after a ghost drains 1 (was 18).
- Damage to a stat lowers the CURRENT value only; max stays. It can be restored (short rest: 1 BP restores 1 point, see rest.md).
- Some curses and injuries deal PERMANENT stat damage: they lower the MAX AND the CURRENT value by the same amount
  [OWNER, corrected] (e.g. Con max -1 and current -1). This is what makes them a
  permanent injury (injuries.md): not healed by normal means, narrative removal only.
- Derived values (HP, balance, saves, skills) use the CURRENT stat value.
- Tests: Str 18/18, drain 1 -> 17/18; short rest 1 BP -> 18/18; permanent damage 1 on 18/18 -> 17/17;
  Str 18 with damage 3 (15/18), permanent damage 1 -> 14/17 [OWNER].

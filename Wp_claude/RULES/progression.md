# Progression

## Level up [OWNER]
- Hit die rolled OUTSIDE app, result entered; HP recorded.
- Max HP [OWNER, package 8; per die since package 16 G1] = the sum over ALL hit dice of max(1, die HP + CURRENT Con
  modifier) + race bonus (may be 0) + other bonuses (feats, class, quirks, items, effects "hp_max"); at least 1.
  Dice: one per level (level 1 = the maximum of the die, later levels = the value the player entered at level up,
  editable, at most the die), plus extra dice from templates and effects "extra_hit_dice" (one die per effect, its
  value = the HP of that die; no level cap).
  Tests (package 16): rolls 8 and 1 with Con 4 (-3) -> 5 + 1 = 6; extra die 6 with Con 14 -> 10 + 8 = 18.
  Training HP (50 per point, training.md) raise the hit-die HP only and never above die * level.
  Tests: rolls 10+6+6, Con 8 (-1), race 2, other 1 -> 22; Con 1 at level 1 with roll 4 -> 1; Con 14 with 4 damage ->
  mod 0; rolls 10+6 at d10: +1 for 50 -> 10+7; rolls 10+10 -> refused.
- Balance regen follows the CURRENT Con live (also after stat damage in combat). Test: Con 12 -> 8 mid-combat: regen
  3 -> 1, balance cap unchanged (9).
- Training gained at level-up = 100 * new level. At creation (level 1) the player gets 1000 training [OWNER]. Spend on almost anything: e.g. raise HP (per level roll up to theoretical hit die max),
  weapon mastery, styles, etc. (list in old editor). Many training options already work.
- Comfort can be exchanged for training.

## Weapon mastery
See weapons.md (full rules). Training cost = (30+5X)*difficulty*scale per grade.

## Spell mastery [OWNER]
- Spell has up to 3 upgrades, each costs 25*(1+circle^2) training, each upgrade takes >= 1 star, spell max 3 stars.
- One upgrade may take all 3 stars.
- Example: circle 2 upgrade = 25*(1+4) = 125.
- Owner text (verbatim, package 4): "Мастерство заклинания - 25*(1+круг^2)". "Вы можете изучить какое-то заклинание на
  продвинутом уровне. Каждое заклинание обладает тремя т.н. "слотами". Вы можете заучить любые улучшения в эти слоты,
  в т.ч. дублирующиеся. Обычно улучшение занимает 1 слот, второе идентичное улучшение занимает 2 слота.
  Метамагия занимает количество слотов, равное своему кругу усложнения. Вам нет необходимости обладать соответствующей
  чертой метамагии, и Вы все еще можете использовать бонусы от других черт метамагии при произнесении этого заклинания
  по обычным правилам."
  ("slots" here = the "stars" above.) Tests for later code: two identical upgrades = 1 + 2 = 3 slots (full);
  a metamagic of +2 circles takes 2 slots.

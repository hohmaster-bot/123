# Progression

## Level up [OWNER]
- Hit die rolled OUTSIDE app, result entered; HP recorded.
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

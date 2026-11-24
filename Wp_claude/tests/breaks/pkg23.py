"""Break registry: package 23 (session layer, character files, read cache, AC zones)."""
S = ("app/test_session.py",)
P = ("perf/test_perf.py",)
Z = ("model/test_ac_zones.py",)

ENTRIES = [
    dict(id="p23-topics-lookup", file="wp/app/session.py", old="    return (ALL,) if t is None else tuple(t)",
         new="    return (ALL,)", suites=S, rule="pkg 23 A: dispatch returns the topics of the command from the table"),
    dict(id="p23-subscriber", file="wp/app/session.py", old="        for fn in self._subscribers:\n            fn(topics)",
         new="        for fn in ():\n            fn(topics)", suites=S, rule="pkg 23 A: subscribers are called after a command"),
    dict(id="p23-autosave-interval", file="wp/app/session.py",
         old="        if self.clock() - self.dirty_since >= int(self.setting(\"autosave_interval_s\")):",
         new="        if True:", suites=S, rule="pkg 23 A: autosave waits for the interval"),
    dict(id="p23-every-command", file="wp/app/session.py",
         old="        if self.setting(\"autosave\") and self.setting(\"autosave_mode\") == EVERY_COMMAND:",
         new="        if False:", suites=S, rule="pkg 23 A: autosave_mode every_command saves after each command"),
    dict(id="p23-backup-rotation", file="wp/app/files.py", old="    for old in backups_of(folder, name, sub)[keep:]:",
         new="    for old in backups_of(folder, name, sub)[keep + 1:]:", suites=S, rule="pkg 23 A: only backups_count backups kept"),
    dict(id="p23-corrupt-refusal", file="wp/app/files.py", old="    except cio.StorageError as e:\n        raise CommandError(\"the file",
         new="    except KeyError as e:\n        raise CommandError(\"the file", suites=S,
         rule="pkg 23 A: a damaged file is a refusal file_corrupt, never a crash"),
    dict(id="p23-delete-trash", file="wp/app/files.py", old="    os.replace(p, dst)\n    return dst",
         new="    os.remove(p)\n    return dst", suites=S, rule="pkg 23 A: delete moves the file to the trash"),
    dict(id="p23-cache-scope", file="wp/model/cache.py", old="    return _hashable(scope) if scope else ()",
         new="    return ()", suites=P, rule="pkg 23 B: a cached value is keyed by the rule scope"),
    dict(id="p23-cache-clear", file="wp/commands/base.py",
         old="    cache.clear()                      # a read cache never survives a command (package 23 B)",
         new="    pass", suites=P, rule="pkg 23 B: a command drops the read cache"),
    dict(id="p23-zone-back-dex", file="wp/core/ac_zones.py", old="    lose = cell in rules.dex_loss_cells",
         new="    lose = False", suites=Z, rule="ac_zones.md: cell 8 (back) has no Dex / dodge"),
    dict(id="p23-zone-shield-cover", file="wp/core/ac_zones.py", old="    return c in cells", new="    return True",
         suites=Z, rule="ac_zones.md: a shield covers only its cells"),
    dict(id="p23-zone-mirror", file="wp/core/ac_zones.py", old="    c = str(TABLE[\"mirror\"][cell]) if shield_hand == RIGHT else cell",
         new="    c = cell",
         suites=Z, rule="ac_zones.md: a shield in the right hand mirrors the cells"),
    dict(id="p23-zone-parry-cells", file="wp/core/ac_zones.py", old="    can_parry = cell in rules.parry_cells", new="    can_parry = True",
         suites=Z, rule="pkg 23 D (Q155): parry only in cells 1-3"),
]

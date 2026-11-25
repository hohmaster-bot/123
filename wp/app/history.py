"""The journal archive of a character (package 27 E, review 5 F29, D29): <folder>/<name>.history.jsonl next to the
character file, append-only, one journal line per text line (the LogEntry record as the character file writes it,
with its seq and its time stamp "at"). An index <name>.history.idx.json keeps, for every new date (YYYYMMDD of "at"),
the byte offset of its first line, and the last archived seq: a date range is read without loading the whole file.

append(folder, name, entries): only lines with seq above the last archived one are written (a line saved again in
the character file before the archive caught up is never doubled); the file is flushed and fsynced; on any failure
the file is cut back to its old size and OSError is raised (the caller keeps the lines in memory).
read(folder, name, from_date, to_date): the archived LogEntry lines of that date range (inclusive, "" = open end).
Files travel with the character: rename / copy / to_trash. The experience log, level history and notebook are not
part of this journal.
"""
import io
import json
import os

from wp.storage import character_io as cio

SUFFIX = ".history.jsonl"
INDEX = ".history.idx.json"
NO_DATE = "00000000"                   # a line without a time stamp (written before package 27)
DATE_LEN = 8


def path_of(folder, name):
    return os.path.join(folder, name + SUFFIX)


def index_path(folder, name):
    return os.path.join(folder, name + INDEX)


def date_of(entry_at):
    return entry_at[:DATE_LEN] if entry_at else NO_DATE


def load_index(folder, name):
    p = index_path(folder, name)
    if not os.path.exists(p):
        return {"dates": [], "last_seq": 0, "lines": 0}
    try:
        with io.open(p, encoding="utf-8") as f:
            d = json.load(f)
        return {"dates": [list(x) for x in d.get("dates", [])], "last_seq": int(d.get("last_seq", 0)),
                "lines": int(d.get("lines", 0))}
    except (ValueError, TypeError, OSError, RecursionError):
        return rebuild_index(folder, name)


def _write_index(folder, name, idx):
    p = index_path(folder, name)
    tmp = p + cio.TMP_SUFFIX
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(idx))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def _line(entry):
    return json.dumps(cio._encode(entry), ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n"


def _write_bytes(f, data):
    """Single place that writes archive bytes (tests replace it to simulate a failing disk)."""
    f.write(data)


def append(folder, name, entries):
    """Append the entries (older first); returns how many lines were written."""
    idx = load_index(folder, name)
    new = [e for e in entries if e.seq > idx["last_seq"]]
    if not new:
        return 0
    p = path_of(folder, name)
    old_size = os.path.getsize(p) if os.path.exists(p) else 0
    offset = old_size
    dates = list(idx["dates"])
    chunks = []
    for e in new:
        text = _line(e).encode("ascii")
        d = date_of(e.at)
        if not dates or dates[-1][0] != d:
            dates.append([d, offset, e.seq])
        chunks.append(text)
        offset += len(text)
    try:
        with open(p, "ab") as f:
            _write_bytes(f, b"".join(chunks))
            f.flush()
            os.fsync(f.fileno())
        _write_index(folder, name, {"dates": dates, "last_seq": new[-1].seq, "lines": idx["lines"] + len(new)})
    except BaseException:
        if os.path.exists(p):
            with open(p, "ab") as f:
                f.truncate(old_size)
        raise
    return len(new)


def _parse(raw):
    return cio._decode(json.loads(raw))


def _start(idx, from_date):
    """The byte offset to read from: 0 without a start date, the first line of the first date >= from_date, or
    None when the archive has no such date."""
    if not from_date:
        return 0
    for d, o, _ in idx["dates"]:
        if d >= from_date:
            return o
    return None


def iter_lines(folder, name, from_date="", to_date=""):
    p = path_of(folder, name)
    if not os.path.exists(p):
        return
    start = _start(load_index(folder, name), from_date)
    if start is None:
        return
    with open(p, "rb") as f:
        f.seek(start)
        for raw in f:
            if not raw.strip():
                continue
            e = _parse(raw.decode("ascii"))
            d = date_of(e.at)
            if from_date and d < from_date:
                continue
            if to_date and d > to_date:
                return
            yield e


def read(folder, name, from_date="", to_date=""):
    return tuple(iter_lines(folder, name, from_date, to_date))


def rebuild_index(folder, name):
    """The index from the archive itself (a lost or damaged index)."""
    idx = {"dates": [], "last_seq": 0, "lines": 0}
    p = path_of(folder, name)
    if not os.path.exists(p):
        return idx
    offset = 0
    with open(p, "rb") as f:
        for raw in f:
            if raw.strip():
                e = _parse(raw.decode("ascii"))
                d = date_of(e.at)
                if not idx["dates"] or idx["dates"][-1][0] != d:
                    idx["dates"].append([d, offset, e.seq])
                idx["last_seq"] = max(idx["last_seq"], e.seq)
                idx["lines"] += 1
            offset += len(raw)
    _write_index(folder, name, idx)
    return idx


def _files(folder, name):
    return ((path_of(folder, name), SUFFIX), (index_path(folder, name), INDEX))


def rename(folder, name, new_name):
    for p, suffix in _files(folder, name):
        if os.path.exists(p):
            os.replace(p, os.path.join(folder, new_name + suffix))


def copy(folder, name, new_name):
    import shutil
    for p, suffix in _files(folder, name):
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(folder, new_name + suffix))


def to_trash(folder, name, trash_stem):
    """Move the archive next to the trashed file <trash>/<name>.<stamp>.json (as <name>.<stamp>.history.jsonl)."""
    for p, suffix in _files(folder, name):
        if os.path.exists(p):
            os.replace(p, trash_stem + suffix)


def full_log(folder, name, memory):
    """The whole journal: the archive, then the in-memory lines not archived yet."""
    arch = read(folder, name)
    last = arch[-1].seq if arch else 0
    return arch + tuple(e for e in memory if e.seq > last)

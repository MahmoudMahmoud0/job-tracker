import ast
import struct
import sys
from pathlib import Path


def _unquote(s: str) -> str:
    return ast.literal_eval(s)


def parse_po(path: Path):
    messages = {}
    msgid = None
    msgstr = None
    state = None

    def commit():
        nonlocal msgid, msgstr, state
        if msgid is not None and msgstr is not None:
            messages[msgid] = msgstr
        msgid = None
        msgstr = None
        state = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            commit()
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgid "):
            commit()
            msgid = _unquote(line[5:].strip())
            msgstr = ""
            state = "msgid"
            continue
        if line.startswith("msgstr "):
            msgstr = _unquote(line[6:].strip())
            state = "msgstr"
            continue
        if line.startswith('"'):
            text = _unquote(line)
            if state == "msgid":
                msgid = (msgid or "") + text
            elif state == "msgstr":
                msgstr = (msgstr or "") + text

    commit()
    return messages


def write_mo(messages, path: Path):
    keys = sorted(messages.keys())
    ids = [k.encode("utf-8") for k in keys]
    strs = [messages[k].encode("utf-8") for k in keys]

    n = len(keys)
    keystart = 7 * 4
    orig_tab_offset = keystart
    trans_tab_offset = orig_tab_offset + n * 8
    ids_offset = trans_tab_offset + n * 8

    offsets = []
    current = ids_offset
    for msgid in ids:
        offsets.append((len(msgid), current))
        current += len(msgid) + 1

    trans_offsets = []
    for msgstr in strs:
        trans_offsets.append((len(msgstr), current))
        current += len(msgstr) + 1

    output = [struct.pack("Iiiiiii", 0x950412de, 0, n, orig_tab_offset, trans_tab_offset, 0, 0)]

    for length, offset in offsets:
        output.append(struct.pack("ii", length, offset))

    for length, offset in trans_offsets:
        output.append(struct.pack("ii", length, offset))

    for msgid in ids:
        output.append(msgid + b"\0")

    for msgstr in strs:
        output.append(msgstr + b"\0")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(output))


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compile_mo.py input.po output.mo")
        raise SystemExit(1)

    po_path = Path(sys.argv[1])
    mo_path = Path(sys.argv[2])
    messages = parse_po(po_path)
    write_mo(messages, mo_path)


if __name__ == "__main__":
    main()

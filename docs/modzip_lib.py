"""modzip_lib：在 index（原始转义形态）里定位并改写 modDataValueZipList 中的某个模组 ZIP（第12轮建立）。

与 H06 的区别：H06 在 unescape 后的文本里取偏移、再回写到原始文本 —— 只有当块之前没有任何
HTML 实体时才碰巧正确。这里直接在原始文本里定位，偏移天然一致。
"""
import base64
import io
import json
import re
import zipfile

LIST_RE = re.compile(r"window\.modDataValueZipList\s*=\s*\[(.*?)\];", re.S)
B64_RE = re.compile(r'"([A-Za-z0-9+/=\s]{200,})"')


def iter_mods(data):
    """产出 (base64串, zipfile对象 或 None, boot.json 或 None)。"""
    m = LIST_RE.search(data)
    if not m:
        raise RuntimeError("找不到 modDataValueZipList")
    for s in B64_RE.findall(m.group(1)):
        raw = base64.b64decode(re.sub(r"\s+", "", s))
        if raw[:2] != b"PK":
            yield s, None, None
            continue
        zz = zipfile.ZipFile(io.BytesIO(raw))
        try:
            bj = json.loads(zz.read("boot.json").decode("utf-8-sig"))
        except Exception:
            bj = None
        yield s, zz, bj


def patch_mod(data, mod_name, fn):
    """fn(filename, bytes) -> 新 bytes 或 None（不改）。返回 (新 data, 改动文件列表)。"""
    m = LIST_RE.search(data)
    block = m.group(1)
    changed = []
    for s, zz, bj in iter_mods(data):
        if not bj or bj.get("name") != mod_name:
            continue
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
            for info in zz.infolist():
                d = zz.read(info.filename)
                nd = fn(info.filename, d)
                if nd is not None and nd != d:
                    changed.append(info.filename)
                    d = nd
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                zo.writestr(zi, d)
        if changed:
            nb64 = base64.b64encode(buf.getvalue()).decode("ascii")
            if block.count(s) != 1:
                raise RuntimeError("模组 base64 在列表中不唯一")
            new_block = block.replace(s, nb64, 1)
            data = data[:m.start(1)] + new_block + data[m.end(1):]
        break
    return data, changed


def read_mod_file(data, mod_name, filename):
    for s, zz, bj in iter_mods(data):
        if bj and bj.get("name") == mod_name:
            return zz.read(filename)
    return None

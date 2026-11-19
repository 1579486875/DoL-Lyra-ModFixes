import os, zipfile, time, sys

SRC = r"E:\TAML\_dol\apk\DoL-Lyra-besc-hikari-ucb-0.5.12.13.apk"
DST = r"E:\TAML\_dol\work\build2_unsigned.apk"
NEWHTML = os.environ["NEWHTML"]
DROP = {"META-INF/DOL.SF", "META-INF/DOL.RSA", "META-INF/MANIFEST.MF"}

# 已经是压缩格式的资源：再 DEFLATE 收益 < 3%，纯浪费时间 -> 直接 STORED
NO_DEFLATE = (
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico",
    ".ogg", ".mp3", ".wav", ".m4a", ".aac", ".flac", ".opus",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".zip", ".gz", ".bz2", ".xz", ".7z", ".jar",
    ".mp4", ".webm", ".mkv",
)

html = open(NEWHTML, "rb").read()
print("new html:", len(html))

t0 = time.time()
n = 0
stored = 0
deflated = 0

with zipfile.ZipFile(SRC) as zin, \
     zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zout:
    for info in zin.infolist():
        if info.filename in DROP:
            continue

        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.external_attr = info.external_attr

        if info.filename == "assets/www/index.html":
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, html)
            n += 1
            deflated += 1
            continue

        # Android/HarmonyOS 硬性要求：resources.arsc 必须 STORED（mmap 直读）
        # 一旦被 DEFLATE 压缩，安装器报「无效安装包」
        if info.filename == "resources.arsc":
            zi.compress_type = zipfile.ZIP_STORED
            stored += 1
            data = zin.read(info.filename)
            zout.writestr(zi, data)
            n += 1
            continue

        # 已压缩的资源不重压
        low = info.filename.lower()
        if low.endswith(NO_DEFLATE):
            zi.compress_type = zipfile.ZIP_STORED
            stored += 1
        else:
            zi.compress_type = zipfile.ZIP_DEFLATED
            deflated += 1

        data = zin.read(info.filename)
        zout.writestr(zi, data)
        n += 1

dt = time.time() - t0
print(f"entries: {n} in {dt:.1f}s  (STORED {stored} / DEFLATED {deflated})")
print("MB:", round(os.path.getsize(DST) / 1048576, 2))

with zipfile.ZipFile(DST) as z:
    print("testzip:", z.testzip(), "| index size:",
          z.getinfo("assets/www/index.html").file_size)

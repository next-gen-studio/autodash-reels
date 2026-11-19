#!/usr/bin/env python3
"""Post every pending youtube/<id>.json request to YouTube through Zernio.
Request file keys: title, description, video_url, optional dry_run (true = only check auth).
Result lines go to youtube_log.txt (OK <id> <url> | HATA <id> <msg> | DRY <id>)."""
import os, json, glob, sys, time, datetime, urllib.request, urllib.error
BASE = "https://zernio.com/api/v1"
KEY = os.environ.get("ZERNIO_KEY", "").strip()
LOG = "youtube_log.txt"
def log(line):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f: f.write(f"{ts} {line}\n")
    print(line)
def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:300]}")
done = set()
if os.path.exists(LOG):
    for l in open(LOG):
        p = l.split()
        if len(p) >= 3 and p[1] == "OK": done.add(p[2])
if not KEY:
    log("HATA - ZERNIO_KEY secret tanimli degil"); sys.exit(1)
files = sorted(glob.glob("youtube/*.json"))
for f in files:
    vid = os.path.basename(f)[:-5]
    if vid in done: continue
    try:
        r = json.load(open(f))
        accs = call("GET", "/accounts").get("accounts", [])
        yt = [a for a in accs if a.get("platform") == "youtube" and a.get("isActive")]
        if not yt: raise RuntimeError("aktif YouTube hesabi yok")
        if r.get("dry_run"):
            log(f"DRY {vid} auth ok, youtube={yt[0].get('username')}"); continue
        title = r["title"]
        if "<" in title + r["description"] or ">" in title + r["description"]: raise RuntimeError("< veya > yasak")
        body = {"content": r["description"],
                "mediaItems": [{"type": "video", "url": r["video_url"]}],
                "platforms": [{"platform": "youtube", "accountId": yt[0]["_id"],
                    "platformSpecificData": {"title": title, "visibility": "public",
                                             "categoryId": "2", "madeForKids": False}}],
                "publishNow": True}
        res = call("POST", "/posts", body)["post"]
        pl = res["platforms"][0]
        if pl.get("status") == "published":
            log(f"OK {vid} {pl.get('platformPostUrl')}")
        else:
            log(f"HATA {vid} status={pl.get('status')} {json.dumps(pl.get('error') or res.get('status'))[:200]}")
    except Exception as e:
        log(f"HATA {vid} {e}")

#!/usr/bin/env python3
"""news.json의 checkups로 홈페이지 '이런 분은 검토해 보세요' 정적 HTML을 만든다.
- site/index.html 의 <!--CHECKUPS-START--> ~ <!--CHECKUPS-END--> 사이 카드(최신 9건) + 그 이후 항목은 목차형 목록
- site/checkups/index.html (전체 목록), site/checkups/<id>.html (개별 글)
- site/sitemap.xml 갱신
사용: python3 build_checkups.py  (저장소 루트에서)
"""
import json, html, re, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
BASE = "https://dasongtax.co.kr"
BOOKING = "https://booking.naver.com/booking/6/bizes/703279"
DISCLAIMER = ("본 내용은 일반적인 세무 정보 안내이며, 실제 적용 여부와 환급 가능성은 개인별 사실관계에 따라 달라집니다. "
              "반드시 세무 전문가의 충분한 검토를 받으시기 바랍니다. "
              "본 내용만을 근거로 한 판단이나 신고 결과에 대하여 다송세무회계는 책임을 지지 않습니다.")
e = lambda s: html.escape(str(s or ""), quote=True)

CSS = """
.ck-page{padding:48px 0 72px;background:var(--paper)}
.ck-page h1{font-family:var(--serif);font-size:clamp(26px,3.2vw,36px);color:var(--navy);margin:0 0 10px;line-height:1.35}
.ck-meta{font-size:14px;color:var(--yellow);font-weight:600;margin:0 0 6px}
.ck-card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:24px 26px;margin:18px 0}
.ck-card h2{font-size:18px;color:var(--navy);margin:0 0 10px}
.ck-card ul{margin:0;padding-left:20px;line-height:1.8}
.ck-card p{margin:0;line-height:1.8}
.ck-kw{font-size:14px;color:var(--muted);margin-top:14px}
.ck-basis{font-size:14px;color:var(--muted)}
.ck-disc{font-size:13.5px;color:var(--muted);background:#EEF1F5;border-radius:8px;padding:14px 16px;line-height:1.7;margin-top:22px}
.ck-cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.ck-back{display:inline-block;margin-bottom:18px;font-size:15px;color:var(--muted);text-decoration:none}
.ck-back:hover{color:var(--navy)}
.ck-list{list-style:none;padding:0;margin:0}
.ck-list li{background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px 22px;margin-bottom:12px}
.ck-list a{color:var(--ink);text-decoration:none;font-weight:600;font-size:17px;line-height:1.5}
.ck-list a:hover{color:var(--yellow)}
.ck-list .t{display:block;font-size:13px;color:var(--yellow);font-weight:600;margin-bottom:4px}
.ck-list .who{display:block;font-size:14px;color:var(--muted);margin-top:4px}
"""

HOME_CSS = """<style>
.checkups{background:var(--paper)}
.ck-home{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
@media(max-width:960px){.ck-home{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.ck-home{grid-template-columns:1fr}}
.ck-home li{background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px 20px}
.ck-home .t{display:block;font-size:13px;color:var(--yellow);font-weight:600;margin-bottom:6px}
.ck-home a{color:var(--ink);text-decoration:none;font-weight:600;font-size:16.5px;line-height:1.5}
.ck-home a:hover{color:var(--yellow)}
.ck-home .who{display:block;font-size:14px;color:var(--muted);margin-top:6px;line-height:1.6}
.ck-toc{margin-top:26px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px 22px}
.ck-toc h3{font-size:15px;color:var(--navy);margin:0 0 10px}
.ck-toc ol{list-style:none;margin:0;padding:0}
.ck-toc li{display:flex;gap:12px;padding:7px 0;border-top:1px dashed var(--line);font-size:15px;line-height:1.5}
.ck-toc li:first-child{border-top:0}
.ck-toc .d{flex:0 0 auto;color:var(--muted);font-size:13px;min-width:150px;padding-top:2px}
.ck-toc a{color:var(--ink);text-decoration:none}
.ck-toc a:hover{color:var(--yellow)}
@media(max-width:640px){.ck-toc li{flex-direction:column;gap:2px}}
.ck-more{margin-top:18px}
.ck-more a{color:var(--navy);font-weight:600}
.checkups .fine{font-size:13px;color:var(--muted);margin-top:14px;line-height:1.7}
</style>"""


def head(title, desc, canon, extra=""):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="다송세무회계">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/logo.png">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/site.css">
<style>{CSS}</style>
{extra}
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="/">
      <img class="brand-mark" src="/logo-mark.png" alt="" width="40" height="40">
      <span>다송세무회계<small>송원근 세무사</small></span>
    </a>
    <a class="call" href="tel:0220390481">02-2039-0481</a>
  </div>
</header>
"""

FOOT = f"""<footer>
  <div class="wrap">
    <p class="foot-brand"><img src="/logo-mark-white.png" alt="" width="44" height="44"><strong>다송세무회계</strong></p>
    <p>대표 세무사 송원근</p>
    <p>서울 송파구 법원로 92 파트너스1, 1동 5층 512호</p>
    <p>전화 02-2039-0481</p>
    <p class="note">이 사이트의 세금 정보는 일반적인 안내이며, 개별 사안은 사실관계에 따라 달라질 수 있습니다.</p>
  </div>
</footer>
</body>
</html>
"""

CARDS = 9      # 홈 화면 카드 최대 개수
TOC_MAX = 30   # 카드 아래 목차형 목록 최대 개수(나머지는 전체 보기)

CTA = f"""<div class="ck-cta">
  <a class="btn btn-yellow" href="{BOOKING}" target="_blank" rel="noopener">이 내용 상담 예약하기</a>
  <a class="btn btn-navy" href="tel:0220390481">전화 02-2039-0481</a>
</div>"""


def item_page(it):
    url = f"{BASE}/checkups/{it['id']}.html"
    who = " / ".join(it.get("targets", [])[:2])
    desc = f"{it['title']} 대상: {who}. {it.get('benefit','')}"[:155]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": it["title"],
          "datePublished": it["date"], "dateModified": it["date"], "inLanguage": "ko",
          "keywords": ", ".join(it.get("keywords", [])), "about": it.get("tax"),
          "author": {"@type": "Person", "name": "송원근", "jobTitle": "세무사"},
          "publisher": {"@type": "AccountingService", "name": "다송세무회계", "url": BASE + "/",
                        "telephone": "+82-2-2039-0481"},
          "mainEntityOfPage": url, "description": desc}
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    tg = "".join(f"<li>{e(t)}</li>" for t in it.get("targets", []))
    kw = " ".join("#" + e(k).replace(" ", "") for k in it.get("keywords", []))
    return head(f"{it['title']} | 다송세무회계", desc, url, extra) + f"""<main class="ck-page">
  <div class="wrap" style="max-width:820px">
    <a class="ck-back" href="/checkups/">검토 안내 전체 보기</a>
    <p class="ck-meta">{e(it.get('tax'))} · {e(it['date'])}</p>
    <h1>{e(it['title'])}</h1>
    <div class="ck-card"><h2>이런 분은 검토해 보세요</h2><ul>{tg}</ul></div>
    <div class="ck-card"><h2>받을 수 있는 혜택·환급 가능성</h2><p>{e(it.get('benefit'))}</p>
      <p class="ck-kw">{kw}</p></div>
    <div class="ck-card"><h2>근거 법령</h2><p class="ck-basis">{e(it.get('basis'))}</p></div>
    {CTA}
    <p class="ck-disc">※ {DISCLAIMER}</p>
  </div>
</main>
""" + FOOT


def list_page(items):
    url = f"{BASE}/checkups/"
    lis = "".join(
        f'<li><span class="t">{e(i.get("tax"))} · {e(i["date"])}</span><a href="/checkups/{e(i["id"])}.html">{e(i["title"])}</a>'
        f'<span class="who">{e(" / ".join(i.get("targets", [])[:2]))}</span></li>' for i in items)
    return head("이런 분은 검토해 보세요 | 다송세무회계 송원근 세무사",
                "양도세·상속증여세·조특법 공제감면·취득세·재산세 등 세법 조문과 판례를 검토해, 받을 수 있는 세금 혜택과 경정청구(환급) 가능성을 대상별로 정리합니다.",
                url) + f"""<main class="ck-page">
  <div class="wrap" style="max-width:820px">
    <a class="ck-back" href="/#checkups">홈으로</a>
    <h1>이런 분은 검토해 보세요</h1>
    <p style="color:var(--muted);margin:0 0 22px">세법 조문·판례를 검토해 받을 수 있는 세금 혜택과 경정청구(환급) 가능성을 매주 정리합니다.</p>
    <ul class="ck-list">{lis}</ul>
    {CTA}
    <p class="ck-disc">※ {DISCLAIMER}</p>
  </div>
</main>
""" + FOOT


def home_block(items):
    lis = "".join(
        f'<li><span class="t">{e(i.get("tax"))} · {e(i["date"])}</span><a href="/checkups/{e(i["id"])}.html">{e(i["title"])}</a>'
        f'<span class="who">{e(" / ".join(i.get("targets", [])[:2]))}</span></li>' for i in items[:CARDS])
    rest = items[CARDS:CARDS + TOC_MAX]
    toc = ""
    if rest:
        toc = ('<div class="ck-toc"><h3>지난 검토 안내</h3><ol>' + "".join(
            f'<li><span class="d">{e(i["date"])} · {e(i.get("tax"))}</span><a href="/checkups/{e(i["id"])}.html">{e(i["title"])}</a></li>'
            for i in rest) + "</ol></div>")
    return f"""<!--CHECKUPS-START-->
{HOME_CSS}
<section class="checkups" id="checkups" aria-labelledby="ck-title">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="ck-title">이런 분은 검토해 보세요</h2>
      <p>세법 조문·판례를 검토해 받을 수 있는 세금 혜택과 경정청구(환급) 가능성을 매주 정리합니다.</p>
    </div>
    <ul class="ck-home">{lis}</ul>
    {toc}
    <p class="ck-more"><a href="/checkups/">전체 보기</a></p>
    <p class="fine">※ {DISCLAIMER}</p>
  </div>
</section>
<!--CHECKUPS-END-->"""


def main():
    items = json.load(open(os.path.join(ROOT, "news.json"), encoding="utf-8")).get("checkups", [])
    items = sorted(items, key=lambda i: i["date"], reverse=True)
    os.makedirs(os.path.join(SITE, "checkups"), exist_ok=True)
    for it in items:
        assert re.fullmatch(r"[a-z0-9-]+", it["id"]), it["id"]
        open(os.path.join(SITE, "checkups", it["id"] + ".html"), "w", encoding="utf-8").write(item_page(it))
    open(os.path.join(SITE, "checkups", "index.html"), "w", encoding="utf-8").write(list_page(items))
    p = os.path.join(SITE, "index.html")
    s = open(p, encoding="utf-8").read()
    if items:
        s = re.sub(r"<!--CHECKUPS-START-->.*?<!--CHECKUPS-END-->", lambda m: home_block(items), s, flags=re.S)
        open(p, "w", encoding="utf-8").write(s)
    sm = os.path.join(SITE, "sitemap.xml")
    t = open(sm, encoding="utf-8").read()
    t = re.sub(r"\s*<url><loc>https://dasongtax.co.kr/checkups/[^<]*</loc>.*?</url>", "", t)
    today = datetime.date.today().isoformat()
    add = f"  <url><loc>{BASE}/checkups/</loc><lastmod>{today}</lastmod></url>\n" + "".join(
        f"  <url><loc>{BASE}/checkups/{i['id']}.html</loc><lastmod>{i['date']}</lastmod></url>\n" for i in items)
    t = t.replace("</urlset>", add + "</urlset>")
    open(sm, "w", encoding="utf-8").write(t)
    print(f"built {len(items)} checkups")


if __name__ == "__main__":
    main()

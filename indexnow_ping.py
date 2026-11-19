#!/usr/bin/env python3
"""Netlify 빌드 때 실행: sitemap.xml에서 최근 7일 안에 바뀐 주소를 IndexNow(네이버·빙 등)에 알린다.
실패해도 배포는 계속되도록 항상 0으로 끝난다."""
import json, re, datetime, urllib.request
KEY = "731d514c7b3767f0e5bfc0e550fdcdf0"
HOST = "dasongtax.co.kr"
ENDPOINTS = ["https://searchadvisor.naver.com/indexnow", "https://api.indexnow.org/indexnow"]
try:
    sm = open("site/sitemap.xml", encoding="utf-8").read()
    cutoff = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    urls = [u for u, d in re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", sm) if d >= cutoff]
    if not urls:
        print("IndexNow: 최근 변경 주소 없음"); raise SystemExit(0)
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
    for ep in ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f"IndexNow {ep}: {r.status} ({len(urls)}건)")
        except Exception as ex:
            print(f"IndexNow {ep}: 실패 {ex}")
except SystemExit:
    pass
except Exception as ex:
    print("IndexNow 오류:", ex)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""業種・用途別の請求書ランディングを /invoice/<slug>.html に生成する。
使い方: python3 build-segments.py [slug ...]  （引数なしで全セグメント生成）
既存のブログ記事テンプレ(/landing.css + .art)に統一。#p= 事前入力で典型品目を /invoice に引き継ぐ。"""
import sys, os, json, base64, html

SITE = "https://free-bizdocs.com"
LOGO_V = "20261021"
TODAY = "2026-10-21"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoice")

def esc(s): return html.escape(str(s), quote=True)

def prefill_hash(items):
    """items: list of (name, qty, unit, price, rate, wh) -> '#p=<b64url>'"""
    it = [[n, q, u, p, r, (1 if wh else 0)] for (n, q, u, p, r, wh) in items]
    payload = json.dumps({"it": it}, ensure_ascii=False, separators=(",", ":"))
    b = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
    return "#p=" + b

STYLE = """
.bgwrap{max-width:860px;margin:0 auto;padding:28px 20px 0}
.bc{font-size:12.5px;color:var(--faint);margin-bottom:6px}.bc a{color:var(--mut);text-decoration:none}.bc a:hover{text-decoration:underline}
.art{max-width:720px;margin:0 auto;padding:4px 20px 50px}
.art h1{font-size:clamp(23px,4vw,33px);font-weight:900;line-height:1.35;letter-spacing:-.01em;margin:0 0 10px}
.art .lead{font-size:16px;line-height:1.9;color:#2b3a4b;margin:0 0 20px}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 20px}
.chips span{font-size:12px;font-weight:700;color:var(--ac);background:var(--ac-s);border-radius:999px;padding:5px 11px}
.art h2{font-size:clamp(19px,3vw,23px);font-weight:900;margin:36px 0 12px;padding-top:14px;border-top:2px solid var(--ac-s)}
.art h3{font-size:16.5px;font-weight:800;margin:22px 0 7px}
.art p{font-size:15.5px;line-height:1.95;color:#243;margin:0 0 15px}
.art ul{font-size:15.5px;line-height:1.9;color:#243;margin:0 0 15px;padding-left:1.4em}
.art li{margin-bottom:5px}
.art table{width:100%;border-collapse:collapse;margin:2px 0 18px;font-size:14px}
.art th,.art td{border:1px solid var(--bd);padding:8px 10px;text-align:left}
.art th{background:var(--surf2,#f7fafe);font-weight:700}
.art td.r{text-align:right;font-variant-numeric:tabular-nums}
.cta{display:block;background:linear-gradient(120deg,#1766e6,#2f8cf0 60%,#36b0f0);color:#fff;text-decoration:none;text-align:center;font-weight:800;font-size:16px;padding:16px;border-radius:12px;margin:22px 0;box-shadow:0 8px 22px -6px rgba(23,102,230,.5)}
.cta small{display:block;font-weight:600;font-size:12px;opacity:.92;margin-top:3px}
.art .callout{background:var(--soft,#f4f8ff);border:1px solid var(--bd);border-left:4px solid var(--ac);border-radius:10px;padding:13px 16px;margin:0 0 16px;font-size:14.5px;line-height:1.8}
.faq .q{border-top:1px solid var(--bd);padding:15px 0}
.faq h3{font-size:15.5px;font-weight:800;margin:0 0 6px}.faq p{margin:0}
.rel{margin-top:22px;border-top:1px solid var(--bd);padding-top:14px}
.rel b{display:block;font-size:13px;color:var(--mut);margin-bottom:7px}
.rel a{display:inline-block;margin:0 14px 8px 0;font-size:13.5px;color:var(--ac)}
.note{font-size:12.5px;color:var(--faint);margin-top:22px;line-height:1.7}
"""

def jsonld(seg, url):
    article = {"@context":"https://schema.org","@type":"Article","headline":seg["h1"],
        "description":seg["desc"],"author":{"@type":"Organization","name":"Free BizDoc"},
        "publisher":{"@type":"Organization","name":"Free BizDoc","sameAs":["https://x.com/FreeBizDocs","https://www.producthunt.com/products/free-bizdoc","https://www.saashub.com/free-bizdoc","https://alternativeto.net/software/free-bizdoc","https://dev.to/free_bizdoc_c48cd26bb9251","https://www.g2.com/products/free-bizdocs"]},
        "datePublished":TODAY,"dateModified":TODAY,"mainEntityOfPage":url,
        "image":SITE+"/og/invoice.png"}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"ホーム","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":"請求書を無料作成","item":SITE+"/invoice"},
        {"@type":"ListItem","position":3,"name":seg["name"]+"の請求書","item":url}]}
    faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in seg["faqs"]]}
    out = ""
    for o in (article, crumb, faq):
        out += '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>\n'
    return out

def head(seg, url):
    t = esc(seg["title"]); d = esc(seg["desc"])
    h = ['<!doctype html>','<html lang="ja">','<head>',
     '<meta charset="utf-8">','<meta name="viewport" content="width=device-width, initial-scale=1">',
     '<title>'+t+'</title>','<meta name="description" content="'+d+'">',
     '<link rel="canonical" href="'+url+'">',
     '<link rel="icon" href="/favicon.ico" sizes="any">',
     '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">',
     '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
     '<meta name="robots" content="index,follow">',
     '<link rel="stylesheet" href="/landing.css?v=20261016c">',
     '<style>'+STYLE+'</style>',
     '<meta property="og:type" content="article">',
     '<meta property="og:title" content="'+t+'">',
     '<meta property="og:description" content="'+d+'">',
     '<meta property="og:url" content="'+url+'">',
     '<meta property="og:image" content="'+SITE+'/og/invoice.png">',
     '<meta name="twitter:card" content="summary_large_image">',
     '<meta name="twitter:image" content="'+SITE+'/og/invoice.png">',
     jsonld(seg, url),'</head>']
    return "\n".join(h)

HEADER = ('<header class="hdr"><div class="in"><a class="brand" href="/">'
 '<img src="/logo.png?v='+LOGO_V+'" alt="Free BizDocs" style="height:30px;width:auto;display:block"></a>'
 '<span class="sp"></span><nav class="nav"><a href="/invoice">請求書ほか</a>'
 '<a href="/compare">ツール比較</a><a href="/blog">お役立ち</a><a href="/pricing">料金・PRO</a></nav></div></header>')

def yen(n): return "¥{:,}".format(int(n))

def body(seg, url):
    cta = ('<a class="cta" href="/invoice'+prefill_hash(seg["items"])+'">'
           'この内容で無料作成する →<small>登録不要・インボイス対応・源泉徴収まで自動計算</small></a>')
    b = ['<body>', HEADER,
     '<div class="bgwrap"><nav class="bc"><a href="/">ホーム</a> › <a href="/invoice">請求書を無料作成</a> › '+esc(seg["name"])+'の請求書</nav></div>',
     '<article class="art">',
     '<h1>'+esc(seg["h1"])+'</h1>',
     '<p class="lead">'+seg["lead"]+'</p>',
     '<div class="chips">'+''.join('<span>'+esc(c)+'</span>' for c in seg["chips"])+'</div>',
     cta,
     '<h2>'+esc(seg["name"])+'の請求書で押さえるポイント</h2>']
    for h3, bodyhtml in seg["points"]:
        b.append('<h3>'+esc(h3)+'</h3>'); b.append('<p>'+bodyhtml+'</p>')
    b.append('<h2>よくある品目と書き方</h2>')
    b.append('<p>'+esc(seg["name"])+'でよく使う品目の例です。下のボタンから、この明細があらかじめ入った状態で作成を始められます（金額は編集できます）。</p>')
    b.append('<table><thead><tr><th>品目</th><th>数量・単位</th><th class="r">単価の例</th><th>税率</th></tr></thead><tbody>')
    for (n,q,u,p,r,wh) in seg["items"]:
        rate = {10:"10%",8:"8%(軽減)",0:"非課税"}.get(r,"10%")
        whnote = " <small>＋源泉</small>" if wh else ""
        b.append('<tr><td>'+esc(n)+whnote+'</td><td>'+esc(q)+esc(u)+'</td><td class="r">'+yen(p)+'</td><td>'+rate+'</td></tr>')
    b.append('</tbody></table>')
    b.append(cta)
    b.append('<h2>作成手順（3ステップ）</h2>')
    b.append('<p>1. 上のボタンで明細入りの請求書を開く → 2. 金額・取引先・発行日を調整 → '
             '3. インボイス番号や源泉の有無を確認してPDFをダウンロード。登録不要・無料で、作成は1時間に2枚までです。</p>')
    b.append('<h2 id="faq">よくある質問</h2><div class="faq">')
    for q,a in seg["faqs"]:
        b.append('<div class="q"><h3>'+esc(q)+'</h3><p>'+esc(a)+'</p></div>')
    b.append('</div>')
    rel = ''.join('<a href="'+h+'">'+esc(l)+'</a>' for l,h in seg["related"])
    b.append('<div class="rel"><b>関連ページ</b>'+rel+'</div>')
    b.append('<p class="note">記載の金額・税計算は作成支援のための例です。税務上の最終判断は専門家にご確認ください。</p>')
    b.append('</article>')
    b.append('<script src="/siteheader.js?v=20261019en"></script>')
    b.append('</body></html>')
    return "\n".join(b)

def render(seg):
    url = SITE + "/invoice/" + seg["slug"]
    return head(seg, url) + "\n" + body(seg, url)

def build(slugs):
    os.makedirs(OUTDIR, exist_ok=True)
    done = []
    for seg in SEGMENTS:
        if slugs and seg["slug"] not in slugs: continue
        path = os.path.join(OUTDIR, seg["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as f: f.write(render(seg))
        done.append(seg["slug"])
    print("generated:", ", ".join(done) if done else "(none)")

def build_hub():
    url = SITE + "/invoice/industries"
    seg = {"title":"業種別の請求書テンプレート一覧｜フリーランス・建設・運送ほか｜Free BizDoc",
       "desc":"業種・職種別の請求書作成ページ一覧。フリーランス・エンジニア・デザイナー・ライター・一人親方・美容サロン・軽貨物・コンサルなど、よく使う品目入りの請求書を登録不要・無料で作成できます。",
       "name":"業種別一覧","h1":"業種別の請求書テンプレート","desc2":"",
       "faqs":[]}
    h = head({**seg,"faqs":[]}, url)
    cards = ""
    for s in SEGMENTS:
        cards += ('<a class="bcard" href="/invoice/'+s["slug"]+'"><span class="tag">請求書</span>'
                  '<h2>'+esc(s["name"])+'の請求書</h2><p>'+esc(s["desc"][:70])+'…</p></a>')
    body_html = ('<body>'+HEADER+
      '<div class="bgwrap"><nav class="bc"><a href="/">ホーム</a> › <a href="/invoice">請求書を無料作成</a> › 業種別一覧</nav></div>'
      '<div class="bgwrap"><h1 style="font-size:clamp(23px,4vw,31px);font-weight:900;margin:0 0 6px">業種別の請求書テンプレート</h1>'
      '<p style="color:var(--mut);font-size:15px;margin:0 0 4px">あなたの仕事に合わせて、よく使う品目があらかじめ入った請求書を、登録不要・無料で作成できます。</p></div>'
      '<div class="blist">'+cards+'</div>'
      '<script src="/siteheader.js?v=20261019en"></script></body></html>')
    # reuse article-style card CSS from blog template
    extra = ("\n<style>.blist{max-width:860px;margin:0 auto;padding:10px 20px 50px;display:grid;grid-template-columns:1fr 1fr;gap:16px}"
      "@media(max-width:680px){.blist{grid-template-columns:1fr}}"
      ".bcard{display:block;text-decoration:none;color:inherit;background:var(--surf,#fff);border:1px solid var(--bd);border-radius:16px;padding:20px;box-shadow:0 1px 2px rgba(19,38,59,.04),0 18px 40px -26px rgba(19,38,59,.2);transition:transform .12s,box-shadow .12s}"
      ".bcard:hover{transform:translateY(-2px);box-shadow:0 10px 30px -14px rgba(19,38,59,.28)}"
      ".bcard .tag{display:inline-block;font-size:11.5px;font-weight:700;color:var(--ac);background:var(--ac-s);border-radius:999px;padding:4px 10px;margin-bottom:10px}"
      ".bcard h2{font-size:17px;font-weight:800;line-height:1.5;margin:0 0 6px}.bcard p{font-size:13px;color:var(--mut);margin:0;line-height:1.7}</style>")
    h = h.replace("</head>", extra+"\n</head>")
    with open(os.path.join(OUTDIR,"industries.html"),"w",encoding="utf-8") as f: f.write(h+"\n"+body_html)
    print("generated hub: industries")

SEGMENTS = [
 {
  "slug":"freelance","name":"フリーランス",
  "title":"フリーランスの請求書｜無料作成・源泉徴収あり・インボイス対応テンプレート｜Free BizDoc",
  "desc":"フリーランス向けの請求書を登録不要・無料で作成。源泉徴収(10.21%)の自動計算、インボイス登録番号、消費税の税率別集計に対応。報酬の請求書をその場でPDFに。",
  "h1":"フリーランスの請求書を無料で作成｜源泉徴収・インボイス対応",
  "lead":"フリーランス・個人事業主が取引先へ出す請求書を、<b>登録不要・無料</b>で作成できます。報酬の<b>源泉徴収（10.21%）</b>やインボイス登録番号、消費税の税率別集計まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","源泉徴収 自動計算","インボイス対応","PDF即ダウンロード"],
  "items":[("Webサイト制作費",1,"式",250000,10,True),("月額保守・運用費",1,"式",20000,10,True)],
  "points":[
    ("源泉徴収は書くべき？",
     "個人のフリーランスが受け取る報酬のうち、原稿料・デザイン料・講演料などは支払う側（法人など）で源泉徴収の対象になります。請求書に源泉徴収税額（10.21%、支払金額100万円超の部分は20.42%）を記載し、差引後の請求額を明記しておくと、受け取り側・支払い側ともに精算がスムーズです。"),
    ("インボイス登録番号の扱い",
     "適格請求書発行事業者なら、T＋13桁の登録番号と税率ごとの消費税額を記載します。免税事業者で番号がない場合は従来どおりの請求書として発行できますが、取引先が仕入税額控除できない点は事前に共有しておくと安心です。"),
    ("屋号・振込先の書き方",
     "宛名は取引先の正式名称＋「御中」。自分側は氏名（屋号があれば屋号も）・連絡先・振込先口座を明記します。継続案件は請求書番号を連番にしておくと、あとの管理が楽になります。"),
  ],
  "faqs":[
    ("フリーランスの請求書に源泉徴収は書くべきですか？","報酬が源泉徴収の対象（原稿料・デザイン料など）であれば、源泉徴収税額を記載し、差引後の金額を請求するのが一般的です。対象外の取引なら記載は不要です。"),
    ("インボイスの登録番号がなくても請求書は出せますか？","はい。免税事業者は従来どおりの請求書を発行できます。ただし取引先は原則として仕入税額控除ができないため、事前に伝えておくとトラブルを防げます。"),
    ("消費税は内税と外税どちらで書けばいいですか？","どちらでも作成できます。インボイスでは税率ごとの対象額と消費税額の記載が必要で、本ツールが税率別に自動集計します。"),
  ],
  "related":[("請求書の書き方","/blog/invoice-how-to"),("源泉徴収の計算方法","/blog/genzei-keisan"),("エンジニアの請求書","/invoice/engineer"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"engineer","name":"エンジニア（業務委託）",
  "title":"エンジニアの業務委託 請求書｜無料作成・人月／準委任・源泉対応｜Free BizDoc",
  "desc":"エンジニア・ITフリーランスの業務委託請求書を登録不要・無料で作成。人月・準委任の月次請求、源泉徴収やインボイス番号、消費税の自動計算に対応。",
  "h1":"エンジニアの業務委託 請求書を無料で作成｜人月・準委任に対応",
  "lead":"ITエンジニア・業務委託の請求書を<b>登録不要・無料</b>で作成できます。<b>人月単価の月次請求</b>や追加対応、源泉徴収・インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","人月・準委任","インボイス対応","PDF即ダウンロード"],
  "items":[("開発業務委託（10月分）",1,"人月",700000,10,False),("追加対応・スポット作業",8,"時間",6000,10,False)],
  "points":[
    ("人月・準委任の月次請求",
     "準委任契約では、稼働に応じて毎月請求するのが一般的です。「開発業務委託（◯月分）」として人月単価×稼働、さらに上限／下限（精算幅）を超えた分を別項目にすると、取引先の検収がスムーズです。請求書番号を月ごとの連番にしておくと管理が楽になります。"),
    ("源泉徴収の要否",
     "法人の業務委託（システム開発など）は原則として源泉徴収の対象外です。一方、個人への支払でも原稿・講演・デザイン等に該当する部分は対象になり得ます。自分の取引がどちらかを確認し、必要なら源泉徴収税額（10.21%）を記載します。"),
    ("消費税・インボイス",
     "適格請求書発行事業者は登録番号（T＋13桁）と税率ごとの消費税額を記載します。本ツールが税率別に自動集計するので、人月＋スポットが混在しても正しく計算されます。"),
  ],
  "faqs":[
    ("人月の請求書はどう書けばいいですか？","「開発業務委託（◯月分）」のように月を明記し、人月単価×稼働で記載します。精算幅の超過分は別項目にすると検収がスムーズです。"),
    ("システム開発の委託に源泉徴収は必要ですか？","法人への業務委託は原則として源泉徴収の対象外です。個人への支払でデザイン・原稿等に該当する部分がある場合のみ対象になり得ます。"),
    ("稼働時間の内訳も載せられますか？","はい。品目を複数行に分けて、開発・会議・スポット対応などを分けて記載できます。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("スキルシート作成","/skillsheet"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"designer","name":"デザイナー",
  "title":"デザイナーの請求書｜無料作成・源泉徴収／修正費・インボイス対応｜Free BizDoc",
  "desc":"デザイナー向けの請求書を登録不要・無料で作成。デザイン料の源泉徴収(10.21%)、修正対応費、インボイス番号、消費税の自動計算に対応。",
  "h1":"デザイナーの請求書を無料で作成｜デザイン料の源泉徴収に対応",
  "lead":"デザイナー・クリエイターの請求書を<b>登録不要・無料</b>で作成できます。<b>デザイン料の源泉徴収</b>や修正対応費、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","源泉徴収 自動計算","インボイス対応","PDF即ダウンロード"],
  "items":[("ロゴ・ビジュアルデザイン費",1,"式",180000,10,True),("修正対応費（2回目以降）",1,"式",15000,10,True)],
  "points":[
    ("デザイン料は源泉徴収の対象",
     "デザイン料は、支払う側が法人等の場合、源泉徴収の対象です。請求書に源泉徴収税額（10.21%、100万円超の部分は20.42%）を記載し、差引後の請求額を明記しておくと精算がスムーズです。"),
    ("修正回数・追加費用の扱い",
     "トラブルを避けるため、見積・請求の段階で「修正は◯回まで、以降は1回◯円」のように条件を明記しておくと安心です。追加修正は別項目にして内訳を明確にします。"),
    ("著作権・利用範囲のメモ",
     "納品物の著作権の帰属や利用範囲（媒体・期間）を備考欄に書いておくと、後の認識ずれを防げます。"),
  ],
  "faqs":[
    ("デザイン料に源泉徴収は必要ですか？","支払う側が法人等であれば、デザイン料は源泉徴収の対象です。源泉徴収税額を記載し、差引後の金額を請求します。"),
    ("修正費は分けて請求できますか？","はい。品目を分けて「修正対応費」として記載できます。条件を事前に合意しておくとトラブルを防げます。"),
    ("著作権についてはどこに書けばいいですか？","備考欄に利用範囲や著作権の帰属を記載できます。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収の計算方法","/blog/genzei-keisan"),("見積書の作成","/quote"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"writer","name":"ライター",
  "title":"ライターの請求書｜無料作成・原稿料の源泉徴収・インボイス対応｜Free BizDoc",
  "desc":"ライター・編集者向けの請求書を登録不要・無料で作成。原稿料の源泉徴収(10.21%)、文字単価、取材費、インボイス番号、消費税の自動計算に対応。",
  "h1":"ライターの請求書を無料で作成｜原稿料の源泉徴収に対応",
  "lead":"ライター・編集者の請求書を<b>登録不要・無料</b>で作成できます。<b>原稿料の源泉徴収</b>や文字単価・取材費まで、そのまま日本語PDFにできます。",
  "chips":["登録不要","原稿料の源泉徴収","インボイス対応","PDF即ダウンロード"],
  "items":[("記事原稿料（6,000字）",1,"本",60000,10,True),("取材・交通費",1,"式",8000,10,False)],
  "points":[
    ("原稿料は源泉徴収の対象",
     "原稿料・記事執筆料は、支払う側が法人等の場合、源泉徴収の対象です。源泉徴収税額（10.21%、100万円超の部分は20.42%）を記載し、差引後の金額を請求します。文字単価で計算した場合も、合計の原稿料に対して源泉を計算します。"),
    ("取材費・実費の扱い",
     "取材の交通費や資料費などの実費は、原稿料と分けて記載します。実費は原則として源泉徴収の対象外なので、品目を分けておくと計算が正確になります。"),
    ("インボイス・消費税",
     "適格請求書発行事業者は登録番号（T＋13桁）を記載します。本ツールが税率別に消費税を自動集計します。"),
  ],
  "faqs":[
    ("原稿料に源泉徴収は必要ですか？","支払う側が法人等であれば、原稿料は源泉徴収の対象です。源泉徴収税額を記載し、差引後の金額を請求します。"),
    ("文字単価で請求できますか？","はい。合計の原稿料として入力すれば、源泉・消費税を自動計算します。内訳は備考欄に記載できます。"),
    ("取材の交通費も源泉の対象ですか？","実費の交通費は原則として源泉徴収の対象外です。原稿料と品目を分けて記載してください。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収の計算方法","/blog/genzei-keisan"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"construction","name":"一人親方・建設業",
  "title":"一人親方の請求書｜無料作成・建設業／工事・インボイス対応｜Free BizDoc",
  "desc":"一人親方・建設業向けの請求書を登録不要・無料で作成。工事一式・材料費・経費の内訳、インボイス番号、消費税の自動計算に対応。",
  "h1":"一人親方・建設業の請求書を無料で作成｜インボイス対応",
  "lead":"一人親方・建設業の請求書を<b>登録不要・無料</b>で作成できます。<b>工事一式・材料費・経費</b>の内訳や、インボイス登録番号、消費税まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","工事・材料費の内訳","インボイス対応","PDF即ダウンロード"],
  "items":[("内装工事一式",1,"式",420000,10,False),("材料費",1,"式",95000,10,False),("諸経費",1,"式",20000,10,False)],
  "points":[
    ("工事・材料・経費を分けて記載",
     "「工事一式」だけでなく、材料費・諸経費を分けて記載すると、元請け・施主にとって内訳が分かりやすく、支払いもスムーズです。現場名や工期を備考に入れておくと照合が楽になります。"),
    ("インボイスと一人親方",
     "一人親方の場合、適格請求書発行事業者であれば登録番号（T＋13桁）を記載します。免税事業者で番号がない場合、元請けが仕入税額控除できない点に関わるため、取引前に確認しておくと安心です。"),
    ("支払いサイト・振込先",
     "建設業は支払いサイトが長いこともあるため、支払期日と振込先を明記します。請求書番号を現場・月ごとに連番にしておくと管理が楽です。"),
  ],
  "faqs":[
    ("一人親方もインボイスの登録番号が必要ですか？","適格請求書発行事業者なら登録番号を記載します。免税事業者は従来どおりの請求書を発行できますが、元請けの仕入税額控除に関わるため事前の確認がおすすめです。"),
    ("材料費と工事費は分けるべきですか？","分けて記載すると内訳が明確になり、元請け・施主の確認がスムーズです。"),
    ("現場名や工期も書けますか？","はい。備考欄に現場名・工期を記載できます。"),
  ],
  "related":[("請求書の書き方","/blog/invoice-how-to"),("見積書の作成","/quote"),("領収書の作成","/receipt"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"salon","name":"美容・サロン",
  "title":"美容・サロンの請求書｜無料作成・物販の軽減税率・インボイス対応｜Free BizDoc",
  "desc":"美容室・サロン向けの請求書を登録不要・無料で作成。施術料と物販(軽減税率の扱い)、インボイス番号、消費税の税率別自動計算に対応。",
  "h1":"美容・サロンの請求書を無料で作成｜物販の税率も自動計算",
  "lead":"美容室・サロンの請求書を<b>登録不要・無料</b>で作成できます。<b>施術料と店販（物販）</b>を分けて、消費税を税率別に自動集計。そのまま日本語PDFにできます。",
  "chips":["登録不要","税率別に自動集計","インボイス対応","PDF即ダウンロード"],
  "items":[("施術料（カット・カラー）",1,"式",12000,10,False),("店販商品（シャンプー等）",2,"個",3000,10,False)],
  "points":[
    ("施術料と物販を分けて記載",
     "法人向けの請求やまとめ払いでは、施術料と店販商品を分けて記載すると内訳が明確です。消費税は品目ごとの税率で自動集計されます。"),
    ("軽減税率になるケース",
     "基本的に美容サービスや化粧品・美容商材は標準税率(10%)です。飲食料品など軽減税率(8%)の対象を一緒に販売する場合のみ、その品目を8%に設定してください（本ツールは税率別に集計します）。"),
    ("インボイス対応",
     "適格請求書発行事業者は登録番号（T＋13桁）を記載します。法人のお客様はインボイスを求めることが多いため、対応しておくと取引がスムーズです。"),
  ],
  "faqs":[
    ("施術料と商品販売は分けて請求できますか？","はい。品目を分けて記載でき、消費税は税率別に自動集計されます。"),
    ("美容サービスは軽減税率ですか？","いいえ、美容サービスや美容商材は標準税率(10%)です。軽減税率(8%)は飲食料品などが対象です。"),
    ("法人のお客様にインボイスを出せますか？","はい。登録番号を自社情報に入れておけば、インボイス対応の請求書を発行できます。"),
  ],
  "related":[("請求書の書き方","/blog/invoice-how-to"),("領収書の作成","/receipt"),("消費税の計算方法","/blog/genzei-keisan"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"delivery-driver","name":"軽貨物・運送",
  "title":"軽貨物・運送の請求書｜無料作成・運賃／燃料・インボイス対応｜Free BizDoc",
  "desc":"軽貨物ドライバー・運送業向けの請求書を登録不要・無料で作成。運送料・燃料サーチャージの内訳、インボイス番号、消費税の自動計算に対応。",
  "h1":"軽貨物・運送の請求書を無料で作成｜運賃の内訳・インボイス対応",
  "lead":"軽貨物ドライバー・運送業の請求書を<b>登録不要・無料</b>で作成できます。<b>運送料・燃料サーチャージ</b>の内訳や、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","運賃・燃料の内訳","インボイス対応","PDF即ダウンロード"],
  "items":[("配送業務（10月分・26日稼働）",1,"式",420000,10,False),("燃料サーチャージ",1,"式",18000,10,False)],
  "points":[
    ("運送料と燃料サーチャージを分ける",
     "月極・チャーターでは「配送業務（◯月分）」として稼働を明記し、燃料サーチャージや高速代などを別項目にすると内訳が分かりやすく、元請けの確認もスムーズです。"),
    ("稼働日数・ルートの備考",
     "稼働日数や担当ルート、委託元の案件名を備考に入れておくと、請求内容の照合が楽になります。請求書番号を月ごとの連番にしておくと管理しやすいです。"),
    ("インボイス・消費税",
     "適格請求書発行事業者は登録番号（T＋13桁）を記載します。委託元が仕入税額控除を行うため、番号の有無は取引前に確認しておくと安心です。"),
  ],
  "faqs":[
    ("燃料サーチャージは分けて書けますか？","はい。運送料と別の品目として記載でき、消費税も自動計算されます。"),
    ("月極の配送はどう請求しますか？","「配送業務（◯月分）」として稼働日数を明記し、一式で記載するのが一般的です。"),
    ("軽貨物でもインボイス番号は必要ですか？","適格請求書発行事業者なら記載します。委託元の仕入税額控除に関わるため、事前に確認しておくと安心です。"),
  ],
  "related":[("請求書の書き方","/blog/invoice-how-to"),("領収書の作成","/receipt"),("見積書の作成","/quote"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"consulting","name":"コンサルタント",
  "title":"コンサルの請求書｜無料作成・顧問料／スポット・源泉・インボイス対応｜Free BizDoc",
  "desc":"コンサルタント向けの請求書を登録不要・無料で作成。顧問料の月次請求・スポット相談、源泉徴収、インボイス番号、消費税の自動計算に対応。",
  "h1":"コンサルタントの請求書を無料で作成｜顧問料の月次請求に対応",
  "lead":"コンサルタントの請求書を<b>登録不要・無料</b>で作成できます。<b>顧問料の月次請求</b>やスポット相談、源泉徴収・インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","顧問料の継続請求","インボイス対応","PDF即ダウンロード"],
  "items":[("顧問料（10月分）",1,"式",150000,10,False),("スポットコンサル",3,"時間",20000,10,False)],
  "points":[
    ("顧問料の継続請求",
     "毎月同額の顧問契約は「顧問料（◯月分）」として月を明記します。スポット相談やプロジェクト単発の稼働は別項目にすると、取引先の経理処理がスムーズです。請求書番号を月ごとの連番にしておくと管理が楽になります。"),
    ("源泉徴収の要否",
     "個人のコンサルタントが受け取る報酬のうち、コンサルティング料は契約内容により源泉徴収の対象になる場合があります（講演・原稿等に該当する部分など）。法人の場合は原則対象外です。自分の取引を確認し、必要なら源泉徴収税額（10.21%）を記載します。"),
    ("インボイス・消費税",
     "適格請求書発行事業者は登録番号（T＋13桁）と税率ごとの消費税額を記載します。顧問料＋スポットが混在しても税率別に自動集計されます。"),
  ],
  "faqs":[
    ("顧問料はどう請求すればいいですか？","「顧問料（◯月分）」として月を明記し、一式で記載します。スポット稼働は別項目に分けると経理処理がスムーズです。"),
    ("コンサル料に源泉徴収は必要ですか？","個人への支払で講演・原稿等に該当する部分は対象になり得ます。法人は原則対象外です。取引内容に応じて記載してください。"),
    ("顧問料とスポットを1枚にまとめられますか？","はい。品目を分けて1枚の請求書にまとめられ、消費税は自動計算されます。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収の計算方法","/blog/genzei-keisan"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"photographer","name":"カメラマン",
  "title":"カメラマンの請求書｜無料作成・撮影料の源泉徴収／出張費・インボイス対応｜Free BizDoc",
  "desc":"カメラマン・フォトグラファー向けの請求書を登録不要・無料で作成。撮影料の源泉徴収(10.21%)、出張費・レタッチ費、インボイス番号、消費税の自動計算に対応。",
  "h1":"カメラマンの請求書を無料で作成｜撮影料の源泉徴収に対応",
  "lead":"カメラマン・フォトグラファーの請求書を<b>登録不要・無料</b>で作成できます。<b>撮影料の源泉徴収</b>や出張費・レタッチ費、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","源泉徴収 自動計算","インボイス対応","PDF即ダウンロード"],
  "items":[("撮影料（半日・出張撮影）",1,"式",50000,10,True),("レタッチ・データ納品費",1,"式",15000,10,True)],
  "points":[
    ("撮影料は源泉徴収の対象",
     "個人のカメラマンが受け取る撮影料・写真の報酬は、支払う側が法人等の場合は源泉徴収の対象です。請求書に源泉徴収税額（10.21%、100万円超の部分は20.42%）を記載し、差引後の請求額を明記しておくと精算がスムーズです。"),
    ("出張費・機材費の分け方",
     "交通費や機材レンタル費は、撮影料とは別項目に分けて記載すると内訳が明確になります。実費精算の交通費は、立替である旨をメモしておくと取引先の経理処理がスムーズです。"),
    ("データ納品・使用範囲のメモ",
     "納品形式（データ点数・解像度）や写真の使用範囲は、備考に簡単に残しておくと後のトラブルを防げます。二次利用がある場合は別途費用を明記します。"),
  ],
  "faqs":[
    ("撮影料に源泉徴収は必要ですか？","個人への撮影料の支払で、支払う側が法人等なら源泉徴収の対象です。税額（10.21%）を記載し差引後の金額を請求します。個人間取引など対象外なら記載は不要です。"),
    ("出張の交通費はどう載せますか？","撮影料とは別項目にし、実費を記載します。立替の交通費は消費税の扱いに注意し、備考に立替である旨を残すと明確です。"),
    ("データ納品のみでも請求書を作れますか？","はい。撮影料・レタッチ費・データ納品費などを品目ごとに分けて1枚にまとめられます。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収の計算方法","/blog/genzei-keisan"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"illustrator","name":"イラストレーター",
  "title":"イラストレーターの請求書｜無料作成・イラスト料の源泉徴収／修正費・インボイス対応｜Free BizDoc",
  "desc":"イラストレーター向けの請求書を登録不要・無料で作成。イラスト料の源泉徴収(10.21%)、修正費、二次利用料、インボイス番号、消費税の自動計算に対応。",
  "h1":"イラストレーターの請求書を無料で作成｜イラスト料の源泉徴収に対応",
  "lead":"イラストレーターの請求書を<b>登録不要・無料</b>で作成できます。<b>イラスト料の源泉徴収</b>や修正費・二次利用料、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","源泉徴収 自動計算","インボイス対応","PDF即ダウンロード"],
  "items":[("イラスト制作費（カット単価）",3,"点",20000,10,True),("修正対応費（3回目以降）",1,"式",8000,10,True)],
  "points":[
    ("イラスト料は源泉徴収の対象",
     "個人が受け取るイラスト・デザインの報酬は、支払う側が法人等の場合は源泉徴収の対象です。源泉徴収税額（10.21%、100万円超の部分は20.42%）を記載し、差引後の請求額を明記します。"),
    ("修正回数・ラフ段階の費用",
     "「修正は◯回まで、以降は1回◯円」のように条件を見積・請求で明記しておくと安心です。ラフ提出のみで終了した場合のキャンセル料も、事前に取り決めておくとトラブルを防げます。"),
    ("二次利用・著作権のメモ",
     "掲載媒体や利用範囲、二次利用の可否を備考に残しておくと後の確認が楽になります。グッズ展開など用途が広がる場合は、二次利用料を別項目にします。"),
  ],
  "faqs":[
    ("イラスト料に源泉徴収は必要ですか？","個人への支払で、支払う側が法人等なら源泉徴収の対象です。税額（10.21%）を記載し差引後の金額を請求します。"),
    ("カット単価で複数点をまとめて請求できますか？","はい。品目に点数×単価で記載でき、消費税と源泉徴収は自動で計算されます。"),
    ("二次利用料はどう分けますか？","制作費とは別項目にして、利用範囲を備考に明記すると分かりやすくなります。"),
  ],
  "related":[("デザイナーの請求書","/invoice/designer"),("源泉徴収とは","/blog/genzei-towa"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"video-editor","name":"動画編集者",
  "title":"動画編集の請求書｜無料作成・編集費の源泉徴収／本数単価・インボイス対応｜Free BizDoc",
  "desc":"動画編集者・映像クリエイター向けの請求書を登録不要・無料で作成。編集費の源泉徴収、本数単価・月額、修正費、インボイス番号、消費税の自動計算に対応。",
  "h1":"動画編集の請求書を無料で作成｜本数単価・源泉徴収に対応",
  "lead":"動画編集者・映像クリエイターの請求書を<b>登録不要・無料</b>で作成できます。<b>本数単価や月額の編集費</b>、源泉徴収やインボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","本数単価・月額","インボイス対応","PDF即ダウンロード"],
  "items":[("動画編集費（YouTube・10分尺）",4,"本",15000,10,True),("サムネイル制作費",4,"点",3000,10,True)],
  "points":[
    ("本数単価・月額の請求",
     "「動画編集費（◯月分・◯本）」のように本数×単価で記載するのが一般的です。継続案件は月ごとの連番で請求書番号を振っておくと管理が楽になります。"),
    ("編集費と源泉徴収",
     "個人が受け取る映像制作・編集の報酬は、支払う側が法人等の場合に源泉徴収の対象となることがあります。取引内容を確認し、対象なら税額（10.21%）を記載して差引後の金額を請求します。"),
    ("修正・追加対応の扱い",
     "修正回数の上限や、尺の追加・素材提供の遅延による追加費用は、事前に条件を決めて別項目にすると内訳が明確になります。"),
  ],
  "faqs":[
    ("動画編集は本数でまとめて請求できますか？","はい。本数×単価で品目に記載でき、サムネイルなどを別項目に分けて1枚にまとめられます。"),
    ("編集費に源泉徴収は必要ですか？","個人への支払で映像制作等に該当する部分は対象になり得ます。取引内容に応じて記載してください。"),
    ("月額契約の請求はどう書きますか？","「編集費（◯月分）」として月を明記し、本数や稼働を内訳に記載します。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収の対象","/blog/genzei-taishou"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"translator","name":"翻訳者",
  "title":"翻訳の請求書｜無料作成・翻訳料の源泉徴収／ワード単価・インボイス対応｜Free BizDoc",
  "desc":"翻訳者・通訳者向けの請求書を登録不要・無料で作成。翻訳料の源泉徴収、ワード単価・文字単価、インボイス番号、消費税の自動計算に対応。",
  "h1":"翻訳の請求書を無料で作成｜ワード単価・源泉徴収に対応",
  "lead":"翻訳者・通訳者の請求書を<b>登録不要・無料</b>で作成できます。<b>ワード単価・文字単価の翻訳料</b>や源泉徴収、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","ワード・文字単価","インボイス対応","PDF即ダウンロード"],
  "items":[("翻訳料（英→日・ワード単価）",4000,"word",12,10,True),("チェック・校正費",1,"式",10000,10,True)],
  "points":[
    ("ワード単価・文字単価の請求",
     "「翻訳料（ワード単価×語数）」のように単価と分量を記載するのが一般的です。原文言語・分野によって単価が変わる場合は、案件ごとに分けて記載すると明確です。"),
    ("翻訳料と源泉徴収",
     "個人が受け取る原稿・翻訳の報酬は、支払う側が法人等の場合は源泉徴収の対象になり得ます。対象なら源泉徴収税額（10.21%）を記載し、差引後の請求額を明記します。"),
    ("納期・分量の内訳メモ",
     "急ぎ対応の割増や、チェック・校正を別途行った場合は、品目を分けて内訳を明確にしておくと取引先の経理処理がスムーズです。"),
  ],
  "faqs":[
    ("翻訳料はワード単価で請求できますか？","はい。語数×単価で品目に記載でき、校正費などを別項目に分けて1枚にまとめられます。"),
    ("翻訳料に源泉徴収は必要ですか？","個人への支払で原稿・翻訳等に該当する部分は対象になり得ます。対象なら税額（10.21%）を記載して差引後の金額を請求します。"),
    ("通訳の稼働も同じ請求書に載せられますか？","はい。翻訳と通訳（時間単価）を品目で分けて記載できます。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収とは","/blog/genzei-towa"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"instructor","name":"講師・セミナー講師",
  "title":"講師・セミナーの請求書｜無料作成・講演料の源泉徴収／交通費・インボイス対応｜Free BizDoc",
  "desc":"講師・セミナー講師向けの請求書を登録不要・無料で作成。講演料の源泉徴収(10.21%)、交通費、資料費、インボイス番号、消費税の自動計算に対応。",
  "h1":"講師・セミナーの請求書を無料で作成｜講演料の源泉徴収に対応",
  "lead":"講師・セミナー講師の請求書を<b>登録不要・無料</b>で作成できます。<b>講演料の源泉徴収</b>や交通費・資料費、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","源泉徴収 自動計算","インボイス対応","PDF即ダウンロード"],
  "items":[("講演料（90分・1回）",1,"式",80000,10,True),("交通費（実費）",1,"式",6000,10,False)],
  "points":[
    ("講演料は源泉徴収の対象",
     "個人が受け取る講演料は、支払う側が法人等の場合は源泉徴収の対象です。源泉徴収税額（10.21%、100万円超の部分は20.42%）を記載し、差引後の請求額を明記しておくと精算がスムーズです。"),
    ("交通費・資料費の扱い",
     "交通費や資料印刷費は、講演料とは別項目に分けて記載します。実費精算の交通費は立替である旨を備考に残しておくと、取引先の経理処理が明確になります。"),
    ("キャンセル料の取り決め",
     "開催中止・延期に備えて、キャンセル料の条件（◯日前まで無料など）を事前に取り決めておくとトラブルを防げます。発生時は別項目で請求します。"),
  ],
  "faqs":[
    ("講演料に源泉徴収は必要ですか？","個人への講演料の支払で、支払う側が法人等なら源泉徴収の対象です。税額（10.21%）を記載し差引後の金額を請求します。"),
    ("交通費は講演料と分けるべきですか？","はい。別項目にして実費を記載します。立替の交通費は備考に立替である旨を残すと明確です。"),
    ("複数回の講座をまとめて請求できますか？","はい。回ごとに品目を分けて1枚の請求書にまとめられます。"),
  ],
  "related":[("フリーランスの請求書","/invoice/freelance"),("源泉徴収の計算方法","/blog/genzei-keisan"),("請求書の書き方","/blog/invoice-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"cleaning","name":"ハウスクリーニング・清掃",
  "title":"清掃・ハウスクリーニングの請求書｜無料作成・定期清掃／スポット・インボイス対応｜Free BizDoc",
  "desc":"ハウスクリーニング・清掃業向けの請求書を登録不要・無料で作成。定期清掃の月額、スポット作業、出張費、インボイス番号、消費税の自動計算に対応。",
  "h1":"清掃・ハウスクリーニングの請求書を無料で作成｜定期・スポット対応",
  "lead":"ハウスクリーニング・清掃業の請求書を<b>登録不要・無料</b>で作成できます。<b>定期清掃の月額やスポット作業</b>、出張費、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","定期・スポット","インボイス対応","PDF即ダウンロード"],
  "items":[("定期清掃（月4回・共用部）",1,"式",40000,10,False),("エアコンクリーニング（スポット）",2,"台",12000,10,False)],
  "points":[
    ("定期清掃とスポットの分け方",
     "定期清掃は「定期清掃（◯月分・月◯回）」として一式で、スポット作業は台数・箇所ごとに分けて記載すると内訳が明確になります。継続契約は請求書番号を月ごとの連番にしておくと管理が楽です。"),
    ("出張費・材料費の扱い",
     "出張費や洗剤・資材費は、作業費とは別項目に分けて記載します。遠方の現場は交通費を明記しておくと取引先の確認がスムーズです。"),
    ("役務提供と源泉徴収",
     "清掃などの役務提供は、原則として源泉徴収の対象外です。源泉徴収は原稿・デザイン・講演など限られた報酬が対象のため、通常の清掃業務では記載は不要です。"),
  ],
  "faqs":[
    ("定期清掃はどう請求しますか？","「定期清掃（◯月分・月◯回）」として一式で記載し、スポット作業は別項目に分けると明確です。"),
    ("清掃業に源泉徴収は必要ですか？","清掃などの役務提供は原則として源泉徴収の対象外です。通常は記載不要です。"),
    ("複数現場をまとめて請求できますか？","はい。現場ごとに品目を分けて1枚の請求書にまとめられ、消費税は自動計算されます。"),
  ],
  "related":[("業種別の請求書一覧","/invoice/industries"),("請求書の書き方","/blog/invoice-how-to"),("インボイス制度とは","/blog/invoice-seido-towa"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"tutor","name":"家庭教師・個人塾",
  "title":"家庭教師・個人塾の請求書／月謝明細｜無料作成・インボイス対応｜Free BizDoc",
  "desc":"家庭教師・個人塾向けの請求書・月謝明細を登録不要・無料で作成。コマ単価・月謝、教材費、インボイス番号、消費税の自動計算に対応。",
  "h1":"家庭教師・個人塾の請求書を無料で作成｜月謝・コマ単価に対応",
  "lead":"家庭教師・個人塾の請求書や月謝明細を<b>登録不要・無料</b>で作成できます。<b>コマ単価や月謝、教材費</b>、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","月謝・コマ単価","インボイス対応","PDF即ダウンロード"],
  "items":[("指導料（90分×月8回）",8,"コマ",4000,10,False),("教材費",1,"式",3000,10,False)],
  "points":[
    ("月謝・コマ単価の書き方",
     "「指導料（◯月分・◯コマ）」としてコマ数×単価で記載するのが一般的です。保護者向けの月謝明細としても使えるよう、宛名・期間・内訳を分かりやすく整えておくと安心です。"),
    ("教材費・交通費の分け方",
     "教材費や出張型の交通費は、指導料とは別項目に分けて記載します。立替の教材費は備考に残しておくと明確です。"),
    ("指導料と源泉徴収",
     "家庭教師・学習指導の役務は、原則として源泉徴収の対象外です。源泉徴収は限られた報酬が対象のため、通常の指導料では記載は不要です。"),
  ],
  "faqs":[
    ("月謝の明細として使えますか？","はい。宛名・期間・コマ数×単価・教材費を記載して、保護者向けの月謝明細としても使えます。"),
    ("家庭教師に源泉徴収は必要ですか？","学習指導の役務は原則として源泉徴収の対象外です。通常は記載不要です。"),
    ("兄弟・複数名の指導をまとめられますか？","はい。生徒ごとに品目を分けて1枚にまとめられます。"),
  ],
  "related":[("業種別の請求書一覧","/invoice/industries"),("請求書の書き方","/blog/invoice-how-to"),("領収書の書き方","/blog/receipt-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"handmade","name":"ハンドメイド作家・物販",
  "title":"ハンドメイド作家・物販の請求書｜無料作成・委託販売／卸・インボイス対応｜Free BizDoc",
  "desc":"ハンドメイド作家・物販向けの請求書を登録不要・無料で作成。商品代金、委託販売手数料、送料、インボイス番号、消費税の自動計算に対応。",
  "h1":"ハンドメイド作家・物販の請求書を無料で作成｜卸・委託販売に対応",
  "lead":"ハンドメイド作家・物販の請求書を<b>登録不要・無料</b>で作成できます。<b>商品代金や卸・委託販売、送料</b>、インボイス番号まで自動で処理し、そのまま日本語PDFにできます。",
  "chips":["登録不要","卸・委託販売","インボイス対応","PDF即ダウンロード"],
  "items":[("アクセサリー（卸・型番A）",20,"個",1200,10,False),("送料",1,"式",800,10,False)],
  "points":[
    ("卸・委託販売の書き方",
     "店舗への卸は、商品ごとに個数×卸単価で記載します。委託販売では、売上から販売手数料を差し引く形になるため、手数料をマイナスの行または別記で明確にしておくとトラブルを防げます。"),
    ("送料・梱包費の扱い",
     "送料や梱包費は商品代金とは別項目に分けて記載します。まとめ発送で送料が変わる場合は、実費に合わせて調整します。"),
    ("物販と源泉徴収",
     "商品の販売（物販）は源泉徴収の対象外です。源泉徴収は原稿・デザインなど限られた報酬が対象のため、ハンドメイド商品の売買では記載は不要です。インボイス登録があれば登録番号を記載します。"),
  ],
  "faqs":[
    ("卸の請求書はどう書きますか？","型番・個数×卸単価で品目に記載し、送料を別項目に分けます。消費税は税率別に自動集計されます。"),
    ("物販に源泉徴収は必要ですか？","商品の販売は源泉徴収の対象外です。通常は記載不要です。"),
    ("委託販売の手数料はどう表しますか？","売上から差し引く手数料を別記して、差引後の支払額が分かるようにします。"),
  ],
  "related":[("業種別の請求書一覧","/invoice/industries"),("請求書の書き方","/blog/invoice-how-to"),("インボイス制度とは","/blog/invoice-seido-towa"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
]

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    build(set(args) if args else None)
    if not args or "industries" in args:
        build_hub()

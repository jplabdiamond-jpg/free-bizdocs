#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""業種・用途別の見積書ランディングを /quote/<slug>.html に生成する。
使い方: python3 build-segments.py [slug ...]  （引数なしで全セグメント生成）
既存のブログ記事テンプレ(/landing.css + .art)に統一。#p= 事前入力で典型品目を /quote（見積ツール）に引き継ぐ。"""
import sys, os, json, base64, html

SITE = "https://free-bizdocs.com"
LOGO_V = "20261021"
TODAY = "2026-11-18"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quote")

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
        "image":SITE+"/og/quote.png"}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"ホーム","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":"見積書を無料作成","item":SITE+"/quote"},
        {"@type":"ListItem","position":3,"name":seg["name"]+"の見積書","item":url}]}
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
     '<meta property="og:image" content="'+SITE+'/og/quote.png">',
     '<meta name="twitter:card" content="summary_large_image">',
     '<meta name="twitter:image" content="'+SITE+'/og/quote.png">',
     jsonld(seg, url),'</head>']
    return "\n".join(h)

HEADER = ('<header class="hdr"><div class="in"><a class="brand" href="/">'
 '<img src="/logo.png?v='+LOGO_V+'" alt="Free BizDocs" style="height:30px;width:auto;display:block"></a>'
 '<span class="sp"></span><nav class="nav"><a href="/invoice">請求書ほか</a>'
 '<a href="/compare">ツール比較</a><a href="/blog">お役立ち</a><a href="/pricing">料金・PRO</a></nav></div></header>')

def yen(n): return "¥{:,}".format(int(n))

def body(seg, url):
    cta = ('<a class="cta" href="/quote'+prefill_hash(seg["items"])+'">'
           'この内容で無料作成する →<small>登録不要・有効期限/納期まで記載・そのままPDF</small></a>')
    b = ['<body>', HEADER,
     '<div class="bgwrap"><nav class="bc"><a href="/">ホーム</a> › <a href="/quote">見積書を無料作成</a> › '+esc(seg["name"])+'の見積書</nav></div>',
     '<article class="art">',
     '<h1>'+esc(seg["h1"])+'</h1>',
     '<p class="lead">'+seg["lead"]+'</p>',
     '<div class="chips">'+''.join('<span>'+esc(c)+'</span>' for c in seg["chips"])+'</div>',
     cta,
     '<h2>'+esc(seg["name"])+'の見積書で押さえるポイント</h2>']
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
    b.append('<p>1. 上のボタンで明細入りの見積書を開く → 2. 金額・取引先・有効期限を調整 → '
             '3. 消費税や但し書きを確認してPDFをダウンロード。登録不要・無料で、作成は1時間に2枚までです。</p>')
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
    url = SITE + "/quote/" + seg["slug"]
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
    url = SITE + "/quote/industries"
    seg = {"title":"業種別の見積書テンプレート一覧｜建設・リフォーム・Web制作ほか｜Free BizDoc",
       "desc":"業種・職種別の見積書作成ページ一覧。建設・リフォーム・Web制作・デザイン・システム開発・コンサル・イベント・清掃・外構・撮影など、よく使う品目入りの見積書を登録不要・無料で作成できます。",
       "name":"業種別一覧","h1":"業種別の見積書テンプレート","desc2":"",
       "faqs":[]}
    h = head({**seg,"faqs":[]}, url)
    cards = ""
    for s in SEGMENTS:
        cards += ('<a class="bcard" href="/quote/'+s["slug"]+'"><span class="tag">見積書</span>'
                  '<h2>'+esc(s["name"])+'の見積書</h2><p>'+esc(s["desc"][:70])+'…</p></a>')
    body_html = ('<body>'+HEADER+
      '<div class="bgwrap"><nav class="bc"><a href="/">ホーム</a> › <a href="/quote">見積書を無料作成</a> › 業種別一覧</nav></div>'
      '<div class="bgwrap"><h1 style="font-size:clamp(23px,4vw,31px);font-weight:900;margin:0 0 6px">業種別の見積書テンプレート</h1>'
      '<p style="color:var(--mut);font-size:15px;margin:0 0 4px">あなたの仕事に合わせて、よく使う品目があらかじめ入った見積書を、登録不要・無料で作成できます。</p></div>'
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
  "slug":"construction","name":"建設・工事",
  "title":"建設・工事の見積書｜無料作成・一式／数量明細・有効期限対応テンプレート｜Free BizDoc",
  "desc":"建設業・工事向けの見積書を登録不要・無料で作成。材料費・労務費・諸経費の内訳、一式表示、有効期限・工期、消費税の自動計算に対応。そのまま日本語PDFに。",
  "h1":"建設・工事の見積書を無料で作成｜内訳・有効期限に対応",
  "lead":"建設業・工事の見積書を<b>登録不要・無料</b>で作成できます。<b>材料費・労務費・諸経費の内訳</b>や一式表示、工期・有効期限まで整えて、そのまま日本語PDFにできます。",
  "chips":["登録不要","内訳・一式対応","有効期限・工期","PDF即ダウンロード"],
  "items":[("〇〇工事 一式（材料・施工）",1,"式",800000,10,False),("諸経費（運搬・養生ほか）",1,"式",60000,10,False)],
  "points":[
    ("内訳と一式のバランス",
     "工事見積では、材料費・労務費・諸経費を大きく分けて示すと取引先が納得しやすくなります。細かい内訳をすべて出すか「一式」でまとめるかは、相手の確認したい粒度に合わせます。追加・変更が見込まれる項目は、単価と数量を分けておくと後の精算が楽になります。"),
    ("有効期限と工期の明記",
     "資材価格が動きやすいため、見積書には<strong>有効期限</strong>（例：発行から1か月）を必ず入れておきます。あわせて着工・完了のおおよその工期や、別途工事の範囲（含む・含まない）を明記すると、認識のズレを防げます。"),
    ("追加・変更の扱い",
     "現場で生じる追加工事は、当初見積の範囲外であることを備考に記しておくと安心です。数量が確定していない部分は「概算」と明記し、確定後に改めて見積・請求する流れにしておくとトラブルを避けられます。"),
  ],
  "faqs":[
    ("工事見積の有効期限はどのくらいが一般的ですか？","資材価格の変動を踏まえ、発行から1か月程度とすることが多いです。長期案件では期限を明記し、超過時は再見積とする旨を添えると安心です。"),
    ("「一式」で見積を出しても問題ないですか？","問題ありません。ただし相手が内訳を求める場合もあるため、材料・労務・諸経費の区分だけでも示しておくと納得を得やすくなります。"),
    ("追加工事はどう扱えばいいですか？","当初見積の範囲外であることを明記し、確定後に別途見積・請求します。概算段階では「概算」と記載しておくと誤解を防げます。"),
  ],
  "related":[("建設・工事の請求書","/invoice/construction"),("見積書の書き方","/blog/quote-how-to"),("見積書と請求書の違い","/blog/quote-vs-invoice"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"reform","name":"リフォーム・内装",
  "title":"リフォーム・内装の見積書｜無料作成・箇所別内訳／有効期限対応｜Free BizDoc",
  "desc":"リフォーム・内装工事向けの見積書を登録不要・無料で作成。箇所別の内訳、材料・施工費、諸経費、有効期限・工期、消費税の自動計算に対応。",
  "h1":"リフォーム・内装の見積書を無料で作成｜箇所別の内訳に対応",
  "lead":"リフォーム・内装工事の見積書を<b>登録不要・無料</b>で作成できます。<b>箇所別の内訳や材料・施工費</b>、有効期限・工期まで整えて、そのまま日本語PDFにできます。",
  "chips":["登録不要","箇所別内訳","有効期限・工期","PDF即ダウンロード"],
  "items":[("キッチン交換（材料・施工）",1,"式",450000,10,False),("内装クロス張替え",40,"m2",1500,10,False)],
  "points":[
    ("箇所別・工程別の内訳",
     "リフォームは「キッチン」「浴室」「内装」など箇所ごとに分けて見積を示すと、施主が判断しやすくなります。各箇所で材料費と施工費を分けておくと、予算に合わせて一部を削る相談もしやすくなります。"),
    ("有効期限と追加費用の前提",
     "見積書には有効期限を入れ、解体後に判明する下地補修など<strong>追加費用が発生し得る前提</strong>を備考に明記しておくと、後のトラブルを避けられます。概算の箇所は「概算」と記載します。"),
    ("相見積もり対応のコツ",
     "リフォームは相見積もりが一般的です。単価と数量を分けて示し、含む・含まない範囲（廃材処分・養生・諸経費など）を明確にしておくと、他社との比較で誤解されにくくなります。"),
  ],
  "faqs":[
    ("リフォーム見積は箇所ごとに分けるべきですか？","はい。箇所別に材料費と施工費を分けて示すと、施主が予算に応じて取捨選択しやすくなります。"),
    ("解体後に追加費用が出る場合は？","見積段階で追加の可能性を備考に明記し、判明後に改めて見積・請求します。概算箇所は「概算」と記載しておくと安心です。"),
    ("相見積もりで比較されやすくするには？","含む・含まない範囲（養生・廃材処分・諸経費など）を明記し、単価と数量を分けて示すと比較で誤解されにくくなります。"),
  ],
  "related":[("建設・工事の見積書","/quote/construction"),("見積書の書き方","/blog/quote-how-to"),("値引き・一式の書き方","/blog/quote-discount"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"web-production","name":"Web制作",
  "title":"Web制作の見積書｜無料作成・ページ単価／保守・有効期限対応テンプレート｜Free BizDoc",
  "desc":"Web制作・ホームページ制作向けの見積書を登録不要・無料で作成。ページ単価、デザイン・コーディング、保守運用、有効期限、消費税の自動計算に対応。",
  "h1":"Web制作の見積書を無料で作成｜ページ単価・保守に対応",
  "lead":"Web制作・ホームページ制作の見積書を<b>登録不要・無料</b>で作成できます。<b>ページ単価やデザイン・コーディング、保守運用</b>まで内訳を整えて、そのまま日本語PDFにできます。",
  "chips":["登録不要","工程別の内訳","有効期限","PDF即ダウンロード"],
  "items":[("トップページ デザイン・制作",1,"式",180000,10,False),("下層ページ制作",6,"ページ",25000,10,False)],
  "points":[
    ("工程・ページ単位の内訳",
     "Web制作は「デザイン」「コーディング」「CMS構築」などの工程や、ページ単位で見積を示すと分かりやすくなります。保守・運用は制作費と分け、月額として別項目にしておくと継続契約の説明がしやすくなります。"),
    ("修正回数・公開後の範囲",
     "デザイン修正の回数（例：各工程2回まで）や、公開後の軽微な修正をどこまで含むかを見積段階で明記しておくと、追加作業の線引きが明確になります。範囲外は別途費用とします。"),
    ("有効期限と素材の支給",
     "見積書には有効期限を入れます。写真・原稿などの素材支給の有無で工数が変わるため、「素材はお客様支給」「撮影・原稿作成は別途」などの前提を備考に残しておくと安心です。"),
  ],
  "faqs":[
    ("Web制作の見積はどう分けるのが分かりやすいですか？","デザイン・コーディング・CMS構築などの工程別、またはページ単位で示すと分かりやすく、保守は月額として別項目にします。"),
    ("修正回数はどう書けばいいですか？","各工程の修正回数（例：2回まで）を明記し、超過分は別途費用とします。見積段階で決めておくとトラブルを防げます。"),
    ("保守費も同じ見積に載せられますか？","はい。制作費と分けて、月額の保守運用費を別項目に記載できます。"),
  ],
  "related":[("エンジニアの請求書","/invoice/engineer"),("見積書の書き方","/blog/quote-how-to"),("取引書類の流れ","/blog/quote-document-flow"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"designer","name":"デザイナー",
  "title":"デザイナーの見積書｜無料作成・制作費／修正費・有効期限対応テンプレート｜Free BizDoc",
  "desc":"デザイナー・クリエイター向けの見積書を登録不要・無料で作成。デザイン制作費、修正対応費、二次利用、有効期限、消費税の自動計算に対応。",
  "h1":"デザイナーの見積書を無料で作成｜制作費・修正費に対応",
  "lead":"デザイナー・クリエイターの見積書を<b>登録不要・無料</b>で作成できます。<b>デザイン制作費や修正対応費、二次利用</b>まで整えて、そのまま日本語PDFにできます。",
  "chips":["登録不要","制作・修正を明記","有効期限","PDF即ダウンロード"],
  "items":[("ロゴ・ビジュアルデザイン費",1,"式",180000,10,False),("修正対応費（3回目以降・1回）",1,"式",15000,10,False)],
  "points":[
    ("制作費と修正回数の提示",
     "デザイン見積では、制作費に含まれる<strong>修正回数</strong>（例：3回まで）を明記し、超過分の単価を示しておくとトラブルを防げます。ラフ提案のみで終了した場合のキャンセル料も、見積段階で触れておくと安心です。"),
    ("二次利用・納品形式",
     "掲載媒体や利用範囲、二次利用（グッズ展開・広告転用など）の可否を見積に記しておくと、後の追加費用の相談がスムーズです。納品形式（データ形式・点数）も前提として残します。"),
    ("有効期限と着手条件",
     "見積書には有効期限を入れ、着手の条件（発注書の受領や着手金の有無）を備考に明記しておくと、スケジュールの行き違いを防げます。"),
  ],
  "faqs":[
    ("修正回数は見積に書くべきですか？","はい。含まれる回数（例：3回まで）と超過時の単価を示しておくと、追加作業の線引きが明確になります。"),
    ("二次利用料はどう扱いますか？","制作費とは別に、利用範囲に応じた二次利用料を見積に記します。用途が広がる場合は別途見積とします。"),
    ("デザイン料に源泉徴収は関係しますか？","見積は税抜・税込の金額提示が中心です。源泉徴収は支払(請求)段階で、支払先が法人等の場合に差し引かれます。"),
  ],
  "related":[("デザイナーの請求書","/invoice/designer"),("見積書の書き方","/blog/quote-how-to"),("値引き・一式の書き方","/blog/quote-discount"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"engineer","name":"システム開発",
  "title":"システム開発の見積書｜無料作成・人月／工程別・有効期限対応テンプレート｜Free BizDoc",
  "desc":"システム開発・業務委託向けの見積書を登録不要・無料で作成。人月・工程別の内訳、要件定義〜テスト、有効期限、消費税の自動計算に対応。",
  "h1":"システム開発の見積書を無料で作成｜人月・工程別に対応",
  "lead":"システム開発の見積書を<b>登録不要・無料</b>で作成できます。<b>人月単価や工程別（要件定義〜テスト）の内訳</b>を整えて、そのまま日本語PDFにできます。",
  "chips":["登録不要","人月・工程別","有効期限","PDF即ダウンロード"],
  "items":[("要件定義・設計",1.5,"人月",700000,10,False),("開発・実装",3,"人月",650000,10,False)],
  "points":[
    ("人月・工程別の積算",
     "開発見積は、要件定義・設計・開発・テストなどの工程ごと、または人月単価×工数で積算すると根拠が伝わりやすくなります。前提条件（対応ブラウザ・想定件数・外部連携の範囲）を明記すると、認識のズレを防げます。"),
    ("概算と確定見積の段階",
     "要件が固まる前は「概算見積」とし、要件定義後に確定見積を出す二段階にすると現実的です。スコープ外の変更は別途見積とする旨を備考に記しておきます。"),
    ("有効期限と保守の切り分け",
     "見積書には有効期限を入れ、開発費と運用・保守費（月額）を分けて示します。リリース後の保守範囲（障害対応・軽微改修の有無）を明確にしておくと安心です。"),
  ],
  "faqs":[
    ("システム開発の見積はどう積算しますか？","工程別、または人月単価×工数で積算し、前提条件（想定件数・外部連携の範囲など）を明記すると根拠が伝わります。"),
    ("要件が固まっていない段階でも見積を出せますか？","「概算見積」として提示し、要件定義後に確定見積を出す二段階が現実的です。スコープ外は別途見積とします。"),
    ("保守費は開発費と分けるべきですか？","はい。開発費と月額の保守・運用費を分けて示し、保守範囲を明記しておくとトラブルを防げます。"),
  ],
  "related":[("エンジニアの請求書","/invoice/engineer"),("Web制作の見積書","/quote/web-production"),("見積書の書き方","/blog/quote-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"consulting","name":"コンサルティング",
  "title":"コンサルティングの見積書｜無料作成・顧問料／スポット・有効期限対応｜Free BizDoc",
  "desc":"コンサルティング・士業向けの見積書を登録不要・無料で作成。顧問料（月額）、スポット支援、成果物、有効期限、消費税の自動計算に対応。",
  "h1":"コンサルティングの見積書を無料で作成｜顧問料・スポットに対応",
  "lead":"コンサルティングの見積書を<b>登録不要・無料</b>で作成できます。<b>顧問料（月額）やスポット支援、成果物</b>を整理して、そのまま日本語PDFにできます。",
  "chips":["登録不要","顧問料・スポット","有効期限","PDF即ダウンロード"],
  "items":[("顧問料（月額・月2回MTG）",1,"式",150000,10,False),("スポット支援（分析・資料作成）",1,"式",120000,10,False)],
  "points":[
    ("顧問契約とスポットの提示",
     "継続の顧問料は「月額・支援内容（面談回数・対応範囲）」を明記し、スポット支援は成果物・期間を分けて示します。稼働の上限や、範囲外対応の単価を添えておくと、依頼範囲の線引きが明確になります。"),
    ("成果物・支援範囲の定義",
     "コンサルは成果が無形になりやすいため、見積に<strong>成果物や支援範囲</strong>（レポート・同席・レビュー回数など）を具体的に書いておくと、認識のズレを防げます。"),
    ("有効期限と更新条件",
     "見積書には有効期限を入れ、顧問契約は更新のタイミング（例：3か月ごと見直し）を備考に記しておくと、継続の相談がスムーズです。"),
  ],
  "faqs":[
    ("顧問料とスポットは同じ見積にまとめられますか？","はい。顧問料（月額）とスポット支援（成果物・期間）を品目で分けて1枚にまとめられます。"),
    ("成果が無形のコンサルはどう見積を書けばいいですか？","支援範囲や成果物（レポート・同席・レビュー回数など）を具体的に記すと、依頼範囲が明確になります。"),
    ("コンサル料に源泉徴収は関係しますか？","見積は金額提示が中心です。源泉徴収は支払(請求)段階で、個人への講演・原稿等に該当する部分がある場合に関係します。"),
  ],
  "related":[("コンサルの請求書","/invoice/consulting"),("見積書の書き方","/blog/quote-how-to"),("見積書と請求書の違い","/blog/quote-vs-invoice"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"event","name":"イベント・催事",
  "title":"イベント・催事の見積書｜無料作成・企画／運営・会場費・有効期限対応｜Free BizDoc",
  "desc":"イベント企画・運営向けの見積書を登録不要・無料で作成。企画・運営費、会場費、機材、人件費、有効期限、消費税の自動計算に対応。",
  "h1":"イベント・催事の見積書を無料で作成｜企画・運営・会場費に対応",
  "lead":"イベント企画・運営の見積書を<b>登録不要・無料</b>で作成できます。<b>企画・運営費や会場費、機材・人件費</b>を内訳で整理して、そのまま日本語PDFにできます。",
  "chips":["登録不要","項目別の内訳","有効期限","PDF即ダウンロード"],
  "items":[("企画・ディレクション費",1,"式",200000,10,False),("当日運営スタッフ",5,"人日",18000,10,False)],
  "points":[
    ("費目ごとの内訳",
     "イベントは企画・会場・機材・人件費・制作物など費目が多いため、項目別に分けて示すと全体像が伝わりやすくなります。実費精算になりやすい会場費・機材レンタルは、立替・実費の別を備考に記しておくと明確です。"),
    ("規模変動・キャンセル条件",
     "来場者数や規模で費用が変わる部分は「概算」とし、確定後に再見積とします。開催中止・延期に備えた<strong>キャンセル条件</strong>（◯日前まで無料など）を見積に添えておくとトラブルを防げます。"),
    ("有効期限と支払条件",
     "見積書には有効期限を入れ、着手金・中間金・残金などの支払条件がある場合は備考に明記します。日程が先の案件は、期限超過時の再見積も触れておくと安心です。"),
  ],
  "faqs":[
    ("イベント見積は何を分けて書くべきですか？","企画・会場・機材・人件費・制作物などの費目別に分け、実費精算分は立替の別を備考に記すと明確です。"),
    ("規模が未確定の部分はどう扱いますか？","「概算」と記載し、来場者数や規模が確定した後に再見積とします。"),
    ("キャンセル条件は見積に入れたほうがいいですか？","はい。開催中止・延期に備え、◯日前まで無料などの条件を添えておくとトラブルを防げます。"),
  ],
  "related":[("見積書の書き方","/blog/quote-how-to"),("値引き・一式の書き方","/blog/quote-discount"),("取引書類の流れ","/blog/quote-document-flow"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"cleaning","name":"ハウスクリーニング・清掃",
  "title":"清掃・ハウスクリーニングの見積書｜無料作成・定期／スポット・有効期限対応｜Free BizDoc",
  "desc":"ハウスクリーニング・清掃業向けの見積書を登録不要・無料で作成。定期清掃の月額、スポット作業、出張費、有効期限、消費税の自動計算に対応。",
  "h1":"清掃・ハウスクリーニングの見積書を無料で作成｜定期・スポット対応",
  "lead":"ハウスクリーニング・清掃業の見積書を<b>登録不要・無料</b>で作成できます。<b>定期清掃の月額やスポット作業、出張費</b>を整理して、そのまま日本語PDFにできます。",
  "chips":["登録不要","定期・スポット","有効期限","PDF即ダウンロード"],
  "items":[("定期清掃（月4回・共用部）",1,"式",40000,10,False),("エアコンクリーニング（スポット）",2,"台",12000,10,False)],
  "points":[
    ("定期とスポットの提示",
     "定期清掃は「月額・回数・対象範囲」を一式で、スポット作業は台数・箇所ごとに分けて示すと分かりやすくなります。対象範囲（共用部のみ・専有部含む等）を明記すると、認識のズレを防げます。"),
    ("出張費・材料費の扱い",
     "遠方の現場は出張費を、特殊洗剤・資材を使う場合は材料費を、作業費と分けて示します。実費精算の項目は備考にその旨を記しておくと明確です。"),
    ("有効期限と契約期間",
     "見積書には有効期限を入れ、定期契約は契約期間や更新の条件（例：6か月契約・以降自動更新）を備考に記しておくと、継続の相談がスムーズです。"),
  ],
  "faqs":[
    ("定期清掃の見積はどう書きますか？","月額・回数・対象範囲を一式で示し、スポット作業は台数や箇所ごとに分けて記載します。"),
    ("出張費や材料費はどう扱いますか？","作業費と分けて示し、実費精算の項目は備考にその旨を記しておくと明確です。"),
    ("定期契約の期間は見積に入れるべきですか？","はい。契約期間や更新条件を備考に記しておくと、継続の相談がスムーズです。"),
  ],
  "related":[("清掃・ハウスクリーニングの請求書","/invoice/cleaning"),("見積書の書き方","/blog/quote-how-to"),("見積書と請求書の違い","/blog/quote-vs-invoice"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"gaikou","name":"外構・エクステリア",
  "title":"外構・エクステリアの見積書｜無料作成・項目別内訳／有効期限対応｜Free BizDoc",
  "desc":"外構・エクステリア工事向けの見積書を登録不要・無料で作成。土間・フェンス・植栽などの項目別内訳、諸経費、有効期限、消費税の自動計算に対応。",
  "h1":"外構・エクステリアの見積書を無料で作成｜項目別の内訳に対応",
  "lead":"外構・エクステリア工事の見積書を<b>登録不要・無料</b>で作成できます。<b>土間・フェンス・植栽などの項目別内訳</b>や諸経費、有効期限まで整えて、そのまま日本語PDFにできます。",
  "chips":["登録不要","項目別内訳","有効期限・工期","PDF即ダウンロード"],
  "items":[("土間コンクリート工事",25,"m2",8000,10,False),("フェンス設置（材料・施工）",1,"式",120000,10,False)],
  "points":[
    ("項目別・数量での内訳",
     "外構は土間・カーポート・フェンス・植栽など項目が分かれるため、数量×単価で示すと施主が判断しやすくなります。一部だけ採用・保留といった相談にも対応しやすくなります。"),
    ("有効期限と追加の前提",
     "見積書には有効期限を入れ、地中の障害物や残土処分など<strong>現地状況で追加が生じ得る前提</strong>を備考に明記しておくと、後のトラブルを防げます。概算箇所は「概算」と記載します。"),
    ("相見積もり対応",
     "外構も相見積もりが一般的です。含む・含まない範囲（残土処分・既存撤去・諸経費）を明確にし、単価と数量を分けて示すと、他社との比較で誤解されにくくなります。"),
  ],
  "faqs":[
    ("外構見積は項目ごとに分けるべきですか？","はい。土間・フェンス・植栽などを数量×単価で示すと、施主が一部採用・保留を判断しやすくなります。"),
    ("現地状況で追加が出る場合は？","残土処分や地中障害などの可能性を備考に明記し、判明後に再見積とします。概算箇所は「概算」と記載します。"),
    ("相見積もりで比較されやすくするには？","含む・含まない範囲（残土処分・既存撤去・諸経費）を明記し、単価と数量を分けて示します。"),
  ],
  "related":[("建設・工事の見積書","/quote/construction"),("リフォーム・内装の見積書","/quote/reform"),("見積書の書き方","/blog/quote-how-to"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
 {
  "slug":"photographer","name":"カメラマン",
  "title":"カメラマンの見積書｜無料作成・撮影料／出張費・有効期限対応テンプレート｜Free BizDoc",
  "desc":"カメラマン・フォトグラファー向けの見積書を登録不要・無料で作成。撮影料、出張費、レタッチ・データ納品、有効期限、消費税の自動計算に対応。",
  "h1":"カメラマンの見積書を無料で作成｜撮影料・出張費に対応",
  "lead":"カメラマン・フォトグラファーの見積書を<b>登録不要・無料</b>で作成できます。<b>撮影料や出張費、レタッチ・データ納品</b>を整理して、そのまま日本語PDFにできます。",
  "chips":["登録不要","撮影・納品を明記","有効期限","PDF即ダウンロード"],
  "items":[("撮影料（半日・出張撮影）",1,"式",50000,10,False),("レタッチ・データ納品費",1,"式",15000,10,False)],
  "points":[
    ("撮影・納品・出張の内訳",
     "撮影料に加えて、レタッチ・データ納品費、出張費を分けて示すと内訳が明確になります。カット数や納品形式（点数・解像度）を見積に書いておくと、認識のズレを防げます。"),
    ("使用範囲・二次利用",
     "写真の使用範囲（媒体・期間）や二次利用の可否を見積に記しておくと、後の追加費用の相談がスムーズです。用途が広がる場合は二次利用料を別項目にします。"),
    ("有効期限とキャンセル条件",
     "見積書には有効期限を入れ、天候・スケジュール変更に備えた<strong>キャンセル・順延条件</strong>を備考に添えておくと安心です。"),
  ],
  "faqs":[
    ("撮影の見積は何を分けて書きますか？","撮影料・レタッチ・データ納品費・出張費を分けて示し、カット数や納品形式を記しておくと明確です。"),
    ("写真の使用範囲は見積に入れるべきですか？","はい。媒体・期間・二次利用の可否を記しておくと、後の追加費用の相談がスムーズです。"),
    ("撮影料に源泉徴収は関係しますか？","見積は金額提示が中心です。源泉徴収は支払(請求)段階で、支払先が法人等の場合に差し引かれます。"),
  ],
  "related":[("カメラマンの請求書","/invoice/photographer"),("見積書の書き方","/blog/quote-how-to"),("見積書と請求書の違い","/blog/quote-vs-invoice"),("無料テンプレート","https://calc.free-bizdocs.com/templates/")],
 },
]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    build(set(args) if args else None)
    if not args or "industries" in args:
        build_hub()

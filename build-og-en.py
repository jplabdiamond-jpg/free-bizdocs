#!/usr/bin/env python3
# 英語ページの「書類別」OGカード（1200x630）を生成。JA版 og/*.png と同じ意匠
# （ブランド青のグラデ＋右上の半透明円、左上にロゴ＋タグライン、中央に書類名、
#  下部に No sign-up · Free · Instant PDF、左下にドメイン）を英語で再現。
# 出力: og/en-<slug>.jpg（index は en-home.jpg）。Playwright で描画→JPEG。
import os, html
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'og')
os.makedirs(OUT, exist_ok=True)

# slug -> (OGに出す書類名, 任意の2行目)。home は特別レイアウト。
DOCS = {
    'home': ('Free business documents', 'Invoice · Estimate · Receipt & more'),
    'invoice': ('Invoice', ''),
    'estimate': ('Estimate', ''),
    'receipt': ('Receipt', ''),
    'purchase-order': ('Purchase Order', ''),
    'packing-slip': ('Packing Slip', ''),
    'credit-note': ('Credit Note', ''),
    'proforma-invoice': ('Pro Forma Invoice', ''),
    'sales-order': ('Sales Order', ''),
    'timesheet': ('Timesheet', ''),
    'work-order': ('Work Order', ''),
    'expense-report': ('Expense Report', ''),
    'bill-of-sale': ('Bill of Sale', ''),
    'donation-receipt': ('Donation Receipt', ''),
}

FONTS = "'Helvetica Neue',Helvetica,Arial,'Liberation Sans',sans-serif"

def size_for(title):
    n = len(title)
    if n <= 10: return 150
    if n <= 14: return 128
    if n <= 18: return 108
    return 92

def card_html(slug, title, sub):
    is_home = (slug == 'home')
    # 中央テキスト（home は見出し＋サブの2行、書類ページは大きな書類名）
    if is_home:
        center = (
            '<div class="center home">'
            f'<div class="htitle">{html.escape(title)}</div>'
            f'<div class="hsub">{html.escape(sub)}</div>'
            '</div>'
        )
    else:
        fs = size_for(title)
        center = f'<div class="center"><div class="doc" style="font-size:{fs}px">{html.escape(title)}</div></div>'
    # home は大見出しが説明を兼ねるので、ロゴ下のタグラインは省いて重複を避ける
    brand_sub = '' if is_home else '<div class="t">Free business documents</div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
.card{{position:relative;width:1200px;height:630px;
  background:linear-gradient(160deg,#2a63e0 0%,#1f55d6 42%,#1647bf 100%);
  font-family:{FONTS};color:#fff;overflow:hidden}}
.circle{{position:absolute;top:-150px;right:-120px;width:620px;height:620px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,rgba(255,255,255,.16),rgba(255,255,255,.05) 60%,rgba(255,255,255,0) 72%)}}
.brand{{position:absolute;top:62px;left:70px}}
.brand .n{{font-size:40px;font-weight:800;letter-spacing:-.5px}}
.brand .t{{font-size:24px;font-weight:500;color:rgba(255,255,255,.82);margin-top:6px}}
.center{{position:absolute;left:0;right:0;top:50%;transform:translateY(-54%);
  display:flex;align-items:center;justify-content:center;padding:0 70px}}
.doc{{font-weight:800;letter-spacing:-1px;text-align:center;line-height:1.05}}
.center.home{{flex-direction:column;transform:translateY(-50%)}}
.home .htitle{{font-size:78px;font-weight:800;letter-spacing:-1.5px;text-align:center;line-height:1.08}}
.home .hsub{{font-size:30px;font-weight:500;color:rgba(255,255,255,.86);margin-top:18px;text-align:center}}
.pills{{position:absolute;left:0;right:0;bottom:116px;text-align:center;
  font-size:27px;font-weight:600;color:rgba(255,255,255,.92)}}
.pills .dot{{color:rgba(255,255,255,.5);margin:0 22px}}
.dom{{position:absolute;left:70px;bottom:54px;font-size:26px;font-weight:600;color:rgba(255,255,255,.85)}}
</style></head><body>
<div class="card">
  <div class="circle"></div>
  <div class="brand"><div class="n">Free BizDoc</div>{brand_sub}</div>
  {center}
  <div class="pills">No sign-up<span class="dot">·</span>Free<span class="dot">·</span>Instant PDF</div>
  <div class="dom">free-bizdocs.com</div>
</div></body></html>'''

def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
        for slug, (title, sub) in DOCS.items():
            pg.set_content(card_html(slug, title, sub), wait_until='networkidle')
            out = os.path.join(OUT, f'en-{slug}.jpg')
            pg.screenshot(path=out, type='jpeg', quality=86, clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
            print('wrote og/en-%s.jpg' % slug)
        b.close()

if __name__ == '__main__':
    main()

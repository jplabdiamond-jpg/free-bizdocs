# -*- coding: utf-8 -*-
# Generates honest "Free <Competitor> alternative" pages under /en/ + a hub /en/alternatives.
# Mirrors en/compare.html design system (suite.css, hdr/ft, siteheader-en.js, .ct table).
import html, json, os

SUITE = "/suite.css?v=20261017d"
HEADER_JS = "/en/siteheader-en.js?v=20261023q"
LOGO = "/logo.png?v=20261021"

HDR = ('<header class="hdr"><div class="in">\n'
 '  <a class="brand" href="/en/" style="text-decoration:none"><img src="%s" alt="Free BizDoc" style="height:30px;width:auto;display:block"></a>\n'
 '  <span class="sp"></span>\n'
 '  <a class="pro" href="/?lang=ja" lang="ja" title="Japanese version">日本語</a>\n'
 '</div></header>\n<nav id="docnav-en" aria-label="Documents"></nav>\n') % LOGO

FOOTER = ('<footer class="ft"><div class="in">\n  <div class="cols">\n    <div>\n'
 '      <div class="brand"><img src="%s" alt="Free BizDoc" style="height:26px;width:auto;display:block;filter:brightness(0) invert(1)"></div>\n'
 '      <p>Free, no-sign-up business document generator. Generated in your browser, never stored on our servers unless you save them.</p>\n    </div>\n'
 '    <div class="col"><h4>Free documents</h4>\n'
 '      <a href="/en/invoice">Invoice</a>\n      <a href="/en/estimate">Estimate / Quote</a>\n      <a href="/en/receipt">Receipt</a>\n'
 '      <a href="/en/purchase-order">Purchase Order</a>\n      <a href="/en/packing-slip">Packing Slip / Delivery Note</a>\n    </div>\n'
 '    <div class="col"><h4>More</h4>\n'
 '      <a href="/en/blog">Blog</a>\n      <a href="/en/compare">Compare tools</a>\n      <a href="/en/alternatives">Alternatives</a>\n'
 '      <a href="/en/pricing">Pricing &amp; PRO</a>\n      <a href="/en/account">Account</a>\n      <a href="/en/contact">Contact</a>\n'
 '      <a href="/en/privacy">Privacy policy</a>\n      <a href="/?lang=ja" lang="ja">日本語版</a>\n    </div>\n  </div>\n'
 '  <div class="bot">&copy; 2026 Free BizDoc</div>\n</div></footer>\n') % LOGO

STYLE = """<style>
.alt{max-width:1000px;margin:0 auto;padding:36px 20px 10px}
.alt h1{font-size:clamp(24px,4vw,34px);font-weight:900;letter-spacing:-.02em;margin:0 0 10px;line-height:1.2}
.alt .lead{font-size:16px;color:var(--mut);line-height:1.75;margin:0 0 6px;max-width:770px}
.alt .upd{font-size:12.5px;color:var(--faint);margin:6px 0 22px}
.alt h2{font-size:clamp(20px,3vw,25px);font-weight:900;margin:34px 0 12px}
.alt p{font-size:15px;color:#2b3a4b;line-height:1.8;max-width:770px}
.twrap{overflow-x:auto;border:1px solid var(--bd);border-radius:14px;box-shadow:0 14px 34px -26px rgba(19,38,59,.4)}
table.ct{min-width:620px;width:100%;border-collapse:collapse;font-size:13.5px;background:#fff}
.ct th,.ct td{padding:12px 14px;border-bottom:1px solid var(--bd);text-align:left;vertical-align:top}
.ct thead th{font-size:12px;font-weight:800;color:var(--mut);background:var(--surf2,#f7fafe)}
.ct tbody th{font-weight:700;color:#2b3a4b;background:var(--surf2,#f7fafe);white-space:nowrap}
.ct col.me,.ct td.me,.ct thead th.me{background:#eaf3fe}
.ct thead th.me{color:var(--ac)}
.ct td.me{font-weight:700;color:#14315c}
.ct .yes{color:#157a48;font-weight:900}.ct .no{color:#b23a2c;font-weight:800}
.ct tr:last-child td,.ct tr:last-child th{border-bottom:none}
.ct .bn b{font-size:14px;font-weight:900;display:block}.ct .bn span{font-size:11px;color:var(--faint)}
.cnote{font-size:12.5px;color:var(--faint);line-height:1.7;margin:14px 0 0;max-width:770px}
.fair{background:#fff;border:1px solid var(--bd);border-left:4px solid #1766e6;border-radius:12px;padding:16px 20px;margin:18px 0;max-width:770px}
.fair h3{margin:0 0 8px;font-size:15px;font-weight:900}
.altcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin-top:10px}
.altcard{display:block;background:#fff;border:1px solid var(--bd);border-radius:14px;padding:18px 20px;text-decoration:none;transition:transform .15s,box-shadow .15s}
.altcard:hover{transform:translateY(-4px);box-shadow:0 16px 30px -18px rgba(19,38,59,.4)}
.altcard b{display:block;font-size:16px;font-weight:900;color:#13263b}
.altcard span{display:block;font-size:13px;color:var(--mut);margin-top:4px;line-height:1.6}
.ctabar{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin:28px 0 6px}
.ctabar a.pri{display:inline-flex;align-items:center;gap:7px;font-size:15px;font-weight:800;border-radius:12px;padding:14px 24px;text-decoration:none;background:var(--ac,#1766e6);color:#fff;box-shadow:0 12px 26px -10px rgba(23,102,230,.5)}
.ctabar a.sec{display:inline-flex;align-items:center;gap:7px;font-size:15px;font-weight:800;border-radius:12px;padding:14px 24px;text-decoration:none;border:1.5px solid var(--bd);color:#13263b}
</style>"""

def head(title, desc, canon, og_title, og_desc, ld_list, extra_hreflang=True):
    h = ['<!doctype html>','<html lang="en">','<head>','<meta charset="utf-8">',
     '<meta name="viewport" content="width=device-width, initial-scale=1">',
     '<title>%s</title>' % html.escape(title),
     '<meta name="description" content="%s">' % html.escape(desc),
     '<link rel="canonical" href="%s">' % canon,
     '<link rel="alternate" hreflang="en" href="%s">' % canon,
     '<link rel="alternate" hreflang="x-default" href="%s">' % canon,
     '<link rel="icon" href="/favicon.ico" sizes="any">',
     '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">',
     '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
     '<meta name="robots" content="index,follow">',
     '<meta property="og:type" content="website">',
     '<meta property="og:site_name" content="Free BizDoc">',
     '<meta property="og:locale" content="en_US">',
     '<meta property="og:title" content="%s">' % html.escape(og_title),
     '<meta property="og:description" content="%s">' % html.escape(og_desc),
     '<meta property="og:url" content="%s">' % canon,
     '<meta property="og:image" content="https://free-bizdocs.com/og.jpg">',
     '<meta name="twitter:card" content="summary_large_image">',
     '<link rel="stylesheet" href="%s">' % SUITE]
    for ld in ld_list:
        h.append('<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False, separators=(',',':')))
    h.append(STYLE)
    h.append('</head>')
    h.append('<body>')
    h.append(HDR)
    return '\n'.join(h)

def tail():
    return FOOTER + ('<script src="%s"></script>\n</body>\n</html>\n' % HEADER_JS)

# ---- competitor data (public info, 2026; fair + caveated) ----
C = [
 dict(slug="freshbooks", name="FreshBooks", kind="accounting suite",
   signup="Account required", free="No free plan (30-day trial)", price="From ~$19/mo (Lite)",
   stored="Yes — cloud account", payments="Yes (fees)", accounting="Yes — full",
   intro="FreshBooks is a polished cloud accounting and invoicing suite aimed at small businesses and freelancers. It is powerful, but it has no free tier — after the trial you pay monthly, and you must create an account before you can send a single invoice.",
   seek="people look for a FreshBooks alternative when they only need to send the occasional invoice and don't want a recurring subscription or an account",
   win="You want time tracking, expense tracking, double-entry accounting, a client portal and automated recurring billing in one place, and you're happy to pay monthly."),
 dict(slug="quickbooks", name="QuickBooks", kind="accounting software", urlslug="quickbooks-invoice-alternative",
   signup="Account required", free="No free plan (trial / paid)", price="From ~$9–$18/mo (intro)",
   stored="Yes — cloud account", payments="Yes (fees)", accounting="Yes — full",
   intro="QuickBooks Online is full accounting software — it does far more than invoicing (bookkeeping, payroll, taxes). That power is overkill if all you need is to hand a client a clean invoice PDF, and there is no free plan.",
   seek="many searches for a QuickBooks alternative come from freelancers who just need simple invoices without buying accounting software",
   win="You run a business that needs real bookkeeping, bank reconciliation, payroll and tax filing — not just invoices."),
 dict(slug="wave", name="Wave", kind="free accounting", urlslug="wave-invoicing-alternative",
   signup="Account required", free="Free invoicing + bookkeeping", price="Pro ~$19/mo",
   stored="Yes — cloud account", payments="Yes (fees)", accounting="Yes — full",
   intro="Wave is one of the few genuinely free accounting tools, and its invoicing is solid. The trade-off is that you must create an account and your data lives in Wave's cloud — and some features have moved behind a paid Pro plan.",
   seek="people look for a Wave alternative when they want to make an invoice without signing up, or prefer their data not to sit in a cloud account",
   win="You want free bookkeeping tied to your invoices, bank connections and payment collection, and don't mind creating an account."),
 dict(slug="invoice-ninja", name="Invoice Ninja", kind="open source", urlslug="invoice-ninja-alternative",
   signup="Account required", free="Free cloud (up to ~5 clients) or self-host", price="Pro ~$14/mo",
   stored="Yes (or your own server)", payments="Yes (fees)", accounting="Yes",
   intro="Invoice Ninja is a capable open-source invoicing platform you can self-host or use on its free cloud tier (limited clients). It's great for developers, but self-hosting is work and the hosted version still needs an account.",
   seek="people look for an Invoice Ninja alternative when they don't want to self-host or sign up just to produce one invoice",
   win="You're technical, want to self-host for full control, or need client portals, recurring invoices and payment gateways on an open-source base."),
 dict(slug="zoho-invoice", name="Zoho Invoice", kind="Zoho suite", urlslug="zoho-invoice-alternative",
   signup="Account required", free="Free (limits: users / invoices per year)", price="Upgrade path is Zoho Books",
   stored="Yes — Zoho account", payments="Yes (fees)", accounting="Via Zoho Books",
   intro="Zoho Invoice is genuinely free, which is rare, and it's well made. The catch is that you need a Zoho account, your data lives in the Zoho cloud, and heavier needs push you into the paid Zoho Books.",
   seek="people look for a Zoho Invoice alternative when they'd rather not create a Zoho account or hit its free-plan limits",
   win="You want a free, full-featured invoicing app with client management and are comfortable in the Zoho ecosystem."),
 dict(slug="invoice-simple", name="Invoice Simple", kind="invoicing app", urlslug="invoice-simple-alternative",
   signup="Account required", free="~3 invoices/month free", price="Paid tiers",
   stored="Yes — account/app", payments="Yes (fees)", accounting="Limited",
   intro="Invoice Simple is a friendly mobile-first invoicing app. It's easy to start, but the free plan caps you at roughly three invoices a month and you create an account, after which your data lives in the app.",
   seek="people look for an Invoice Simple alternative when they hit the ~3-invoice free cap or want a desktop, no-account option",
   win="You want a dedicated mobile app with saved clients and reminders on your phone, and the monthly invoice cap isn't a problem."),
 dict(slug="xero", name="Xero", kind="accounting software", urlslug="xero-alternative",
   signup="Account required", free="No free plan (30-day trial)", price="From ~$20/mo",
   stored="Yes — cloud account", payments="Yes (fees)", accounting="Yes — full double-entry",
   intro="Xero is full cloud accounting software popular with small businesses and their accountants. It's powerful, but there is no free plan, and it is far more than you need if you simply want to send an invoice.",
   seek="people look for a Xero alternative when they only need simple invoicing without paying for full accounting",
   win="You need proper double-entry accounting, bank reconciliation, payroll and an accountant-friendly platform — not just invoices."),
 dict(slug="bonsai", name="Bonsai", kind="freelancer suite", urlslug="bonsai-alternative",
   signup="Account required", free="No free plan (trial)", price="From ~$21/mo",
   stored="Yes — cloud account", payments="Yes (fees)", accounting="Basic + proposals/contracts",
   intro="Bonsai bundles proposals, contracts, invoicing, time tracking and taxes for freelancers. It is a tidy all-in-one, but it is subscription-only and overkill if you just need to send a clean invoice.",
   seek="people look for a Bonsai alternative when they want free invoicing without the whole freelancer suite or a subscription",
   win="You want proposals, contracts, a client CRM, time tracking and invoicing together in one paid tool built for freelancers."),
 dict(slug="bill-com", name="BILL (Bill.com)", kind="AP/AR automation", urlslug="bill-com-alternative",
   signup="Account required", free="No free plan", price="From ~$45/mo",
   stored="Yes — cloud account", payments="Yes (fees)", accounting="AP/AR automation",
   intro="BILL (formerly Bill.com) automates accounts payable and receivable for growing businesses, with approval workflows and accounting sync. It is enterprise-grade and priced accordingly — far more than a simple invoice generator.",
   seek="people look for a Bill.com alternative when they just need to send invoices and don't need full AP/AR automation",
   win="You process many bills and payments and want approval workflows and AP/AR automation tied into your accounting."),
 dict(slug="invoice2go", name="Invoice2go", kind="invoicing app", urlslug="invoice2go-alternative",
   signup="Account required", free="No free plan (trial)", price="From ~$6/mo",
   stored="Yes — account/app", payments="Yes (fees)", accounting="Limited",
   intro="Invoice2go is a mobile-first invoicing app aimed at small businesses and tradespeople. It is handy on the go, but there is no lasting free tier beyond a trial and you work inside an account.",
   seek="people look for an Invoice2go alternative when the trial ends or they want a free, no-account option on desktop",
   win="You want a dedicated mobile app with saved clients, estimates and reminders and don't mind a subscription."),
 dict(slug="paypal-invoicing", name="PayPal Invoicing", kind="PayPal feature", urlslug="paypal-invoice-alternative",
   signup="PayPal account required", free="Free to create; fees when paid", price="Per-transaction fees",
   stored="Yes — PayPal account", payments="Yes (PayPal fees)", accounting="No",
   intro="PayPal lets you send invoices for free and get paid by card or PayPal balance. It is convenient if you already use PayPal, but it ties the invoice to a PayPal account and brand, and charges a fee whenever you get paid.",
   seek="people look for a PayPal invoice alternative when they want a plain, unbranded PDF invoice without routing payment through PayPal",
   win="You want to collect payment immediately through PayPal and your clients are happy to pay that way."),
 dict(slug="stripe-invoicing", name="Stripe Invoicing", kind="Stripe feature", urlslug="stripe-invoicing-alternative",
   signup="Stripe account required", free="Free tier; fee on paid invoices", price="~0.4–0.5% per paid invoice",
   stored="Yes — Stripe account", payments="Yes (Stripe fees)", accounting="No",
   intro="Stripe Invoicing creates and sends invoices that customers pay by card, built on Stripe's payments. It is great if you are already on Stripe, but it requires a Stripe account and charges a fee on each paid invoice.",
   seek="people look for a Stripe Invoicing alternative when they just need a downloadable invoice PDF without a Stripe account or per-invoice fees",
   win="You want card payments collected on invoices through Stripe and already use Stripe for your payments."),
]
for c in C:
    c.setdefault("urlslug", c["slug"] + "-alternative")

def comp_table(c):
    def row(label, me, them, meyes=None, themno=None):
        mecell = ('<span class="yes">%s</span>' % me) if meyes else me
        return ("<tr><th>%s</th><td class=\"me\">%s</td><td>%s</td></tr>"
                % (label, mecell, them))
    rows = []
    rows.append('<tr><th>Create &amp; download without an account</th><td class="me"><span class="yes">Yes</span></td><td><span class="no">No</span> &mdash; %s</td></tr>' % c["signup"].lower().replace("account required","account required"))
    rows.append('<tr><th>What&rsquo;s free</th><td class="me">Unlimited creation; 2 PDF downloads/hour. Free account saves 5 docs.</td><td>%s</td></tr>' % html.escape(c["free"]))
    rows.append('<tr><th>Your data stored on their servers</th><td class="me"><span class="yes">No</span> &mdash; made in your browser (unless you save)</td><td>%s</td></tr>' % html.escape(c["stored"]))
    rows.append('<tr><th>US / UK / AU / CA tax built in</th><td class="me"><span class="yes">Yes</span></td><td>Yes</td></tr>')
    rows.append('<tr><th>Online card payments</th><td class="me"><span class="no">No</span></td><td>%s</td></tr>' % html.escape(c["payments"]))
    rows.append('<tr><th>Full accounting / recurring</th><td class="me">Basic management on PRO; no full accounting</td><td>%s</td></tr>' % html.escape(c["accounting"]))
    rows.append('<tr><th>Price</th><td class="me">Free; PRO $15/mo optional</td><td>%s</td></tr>' % html.escape(c["price"]))
    return ('<div class="twrap"><table class="ct"><colgroup><col><col class="me"><col></colgroup>'
            '<thead><tr><th>&nbsp;</th><th class="me"><div class="bn"><b>Free BizDoc</b><span>this tool</span></div></th>'
            '<th><div class="bn"><b>%s</b><span>%s</span></div></th></tr></thead><tbody>%s</tbody></table></div>'
            % (html.escape(c["name"]), html.escape(c["kind"]), "".join(rows)))

def page(c):
    name = c["name"]; canon = "https://free-bizdocs.com/en/%s" % c["urlslug"]
    title = "Free %s Alternative — No Sign-Up Invoice Generator | Free BizDoc" % name
    desc = ("A free %s alternative: create and download a professional invoice PDF in your browser with no account. "
            "See an honest Free BizDoc vs %s comparison and when %s is still the better choice." % (name, name, name))
    h1 = "A free %s alternative" % name
    faqs = [
      ("Is there a free alternative to %s?" % name,
       "Yes. Free BizDoc lets you create and download an invoice PDF for free with no account and no trial. %s" % c["intro"].split(".")[0] + "."),
      ("Can I invoice without signing up for %s?" % name,
       "With %s you need to create an account first. With Free BizDoc you can fill in a document and download the PDF straight away — nothing to register, and the document is generated in your browser rather than stored on a server." % name),
      ("Is %s better than Free BizDoc?" % name,
       "For simple, occasional invoicing with no cost or sign-up, Free BizDoc is quicker. %s is the better pick if %s." % (name, (c["win"][0].lower()+c["win"][1:]).rstrip("."))),
    ]
    ld_breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":"https://free-bizdocs.com/en/"},
      {"@type":"ListItem","position":2,"name":"Alternatives","item":"https://free-bizdocs.com/en/alternatives"},
      {"@type":"ListItem","position":3,"name":"%s alternative" % name,"item":canon}]}
    ld_faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    body = []
    body.append('<section class="alt">')
    body.append('<h1>%s</h1>' % h1)
    body.append('<p class="lead">%s</p>' % c["intro"])
    body.append('<p class="upd">Compiled from %s’s public information (2026). Always check the provider&rsquo;s site for current terms.</p>' % name)
    body.append('<p>If you just need to hand a client a clean invoice, estimate or receipt as a PDF, you don&rsquo;t need a full subscription. <b>Free BizDoc</b> is a free, no-sign-up generator — fill in the details, and download the PDF in seconds. US sales tax, UK VAT, Australian GST and Canadian GST/HST are built in. Here’s how it compares with %s.</p>' % name)
    body.append('<h2>Free BizDoc vs %s</h2>' % name)
    body.append(comp_table(c))
    body.append('<p class="cnote">Prices and free limits change — the figures above are from %s’s public information in 2026 and may differ now. &ldquo;Account&rdquo; means you must register before you can create or download a document.</p>' % name)
    body.append('<div class="fair"><h3>When %s is still the better choice</h3><p style="margin:0">%s</p></div>' % (name, c["win"]))
    body.append('<div class="ctabar"><a class="pri" href="/en/invoice">Create an invoice free &rarr;</a><a class="sec" href="/en/compare">Compare all free tools</a></div>')
    body.append('</section>')
    body.append('<div class="faqwrap"><div class="faq"><h2>Frequently asked questions</h2>')
    for q,a in faqs:
        body.append('<div class="q"><h3>%s</h3><p>%s</p></div>' % (html.escape(q, quote=False), html.escape(a, quote=False)))
    body.append('</div></div>')
    return head(title, desc, canon, "A free %s alternative (no sign-up)" % name,
                "Create an invoice PDF free, no account. Free BizDoc vs %s compared." % name,
                [ld_breadcrumb, ld_faq]) + "\n" + "\n".join(body) + "\n" + tail()

def hub():
    canon = "https://free-bizdocs.com/en/alternatives"
    title = "Free Invoice Software Alternatives (No Sign-Up) | Free BizDoc"
    desc = "Looking for a free alternative to FreshBooks, QuickBooks, Wave, Zoho Invoice, Invoice Ninja or Invoice Simple? Compare each with Free BizDoc — a free, no-account invoice generator."
    ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":"https://free-bizdocs.com/en/"},
      {"@type":"ListItem","position":2,"name":"Alternatives","item":canon}]}
    cards = "".join(
      '<a class="altcard" href="/en/%s"><b>%s alternative</b><span>%s</span></a>'
      % (c["urlslug"], html.escape(c["name"]), html.escape(c["free"])) for c in C)
    body = ('<section class="alt"><h1>Free invoice software alternatives</h1>'
     '<p class="lead">Most invoicing tools make you create an account and keep your data in their cloud. '
     'If you just need a professional invoice PDF right now, Free BizDoc is a free, no-sign-up alternative. '
     'Pick the tool you’re comparing against for an honest, side-by-side look.</p>'
     '<div class="altcards">%s</div>'
     '<div class="ctabar"><a class="pri" href="/en/invoice">Create an invoice free &rarr;</a>'
     '<a class="sec" href="/en/compare">Compare all tools in one table</a></div></section>' % cards)
    return head(title, desc, canon, "Free invoice software alternatives (no sign-up)",
                desc, [ld]) + "\n" + body + "\n" + tail()

os.makedirs("en", exist_ok=True)
written = []
open("en/alternatives.html","w",encoding="utf-8").write(hub()); written.append("en/alternatives.html")
for c in C:
    fn = "en/%s.html" % c["urlslug"]
    open(fn,"w",encoding="utf-8").write(page(c)); written.append(fn)
print("wrote %d files:" % len(written))
for w in written: print("  ", w, os.path.getsize(w), "bytes")

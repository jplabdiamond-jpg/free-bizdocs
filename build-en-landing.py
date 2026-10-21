#!/usr/bin/env python3
# Generates English programmatic landing pages: an invoice-template hub and
# per-industry invoice landing pages under /en/invoice/<slug>.
# Each page is unique content + a CTA that opens /en/invoice prefilled via #p=.
import json, os, base64, datetime, html
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'en')
V = datetime.date.today().strftime('%Y%m%d') + 'j'
BASE = 'https://free-bizdocs.com'

def b64p(items, notes=''):
    payload = {'kind': 'invoice', 'items': [{'name': n, 'qty': q, 'unit_price': p, 'tax': 'tax'} for (n, q, p) in items]}
    if notes:
        payload['notes'] = notes
    raw = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')

# All example line items are plain ASCII (WinAnsi-safe) so the PDF never shows '?'.
INDUSTRIES = [
 dict(slug='freelancer', name='Freelancer', title='Free Freelancer Invoice Template - Create & Download PDF (No Sign-Up)',
  desc='A free invoice template for freelancers. Add your project work or hours, your rate and payment terms, and download a clean PDF - no sign-up. US / UK / AU / CA.',
  lead='Bill a client for your freelance work in under a minute. Add your project fee or hours, set your rate and payment terms, and download a professional PDF invoice - free, no account.',
  include=['Your name/business and the client (&ldquo;Bill To&rdquo;)','A unique invoice number and the issue and due dates','Project work or hours with a clear description and your rate','Payment terms (Net 14 or Net 30 is common for freelancers)','How to pay - bank transfer, card or PayPal'],
  items=[('Professional services - project work', 1, 1500), ('Hourly consulting', 8, 85), ('Revisions - additional round', 1, 150)],
  terms='Freelancers commonly use Net 14 or Net 30, and often ask for a deposit on larger projects.',
  faqs=[('How do I invoice as a freelancer?','Enter your business name, the client, an invoice number, your line items (project fee or hours x rate), and your payment terms, then download the PDF. No sign-up is needed.'),
        ('Should a freelancer charge a deposit?','For larger projects it is common to invoice a deposit (often 30-50%) up front and the balance on delivery. Create a deposit invoice first, then a final invoice for the remainder.'),
        ('Do I need to add tax?','Only if you are registered to charge it. Pick your country and set the sales tax / VAT / GST rate, or mark lines exempt.')]),
 dict(slug='consultant', name='Consultant', title='Free Consultant Invoice Template - Download a PDF Invoice (No Sign-Up)',
  desc='A free invoice template for consultants - advisory hours, day rates and retainers. Download a professional PDF, no account. US / UK / AU / CA.',
  lead='Invoice clients for advisory work, day rates or a monthly retainer. Add your lines, set terms, and download a polished PDF - free and without an account.',
  include=['Your consultancy and the client&rsquo;s details','Invoice number, issue date and due date','Advisory time (hours or days), workshops or a retainer line','Your rate per hour or per day','Payment terms and how to pay'],
  items=[('Strategy consulting - half day', 1, 1200), ('Advisory call - per hour', 4, 200), ('Monthly retainer', 1, 2500)],
  terms='Consultants often bill a monthly retainer in advance and project work Net 15-30.',
  faqs=[('How should a consultant structure an invoice?','List your advisory time by day or hour, plus any fixed-fee deliverables or retainer, with your rate shown per line so the client can see how the total is built up.'),
        ('How do I invoice a retainer?','Add a single &ldquo;Monthly retainer&rdquo; line for the agreed amount and invoice it at the start of each period. You can reuse the same details each month with a new invoice number.'),
        ('Is it free?','Yes - create and download consultant invoices with no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='graphic-designer', name='Graphic Designer', title='Free Graphic Design Invoice Template - PDF Download (No Sign-Up)',
  desc='A free invoice template for graphic designers - logo, branding and design packages. Download a clean PDF invoice, no account. US / UK / AU / CA.',
  lead='Invoice for logo design, branding and creative packages. Add your deliverables and rate and download a professional PDF - free, no sign-up.',
  include=['Your studio and the client','Invoice number, issue date and due date','Design deliverables - logo, brand guide, assets - with clear descriptions','Fixed package prices or hourly design time','Terms, including usage rights on payment'],
  items=[('Logo design package', 1, 900), ('Brand style guide', 1, 600), ('Social media templates - set of 10', 1, 450)],
  terms='Designers often take a 50% deposit, release final files on payment, and use Net 14 terms.',
  faqs=[('What should a graphic design invoice include?','Your studio and client details, an invoice number, each deliverable with its price (or your hourly rate x hours), and your terms - including that final files and usage rights transfer on full payment.'),
        ('Should I invoice a deposit for design work?','Yes, it is common to invoice 50% up front to begin and the balance on delivery. Create a deposit invoice, then convert it to a final invoice for the remainder.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='web-developer', name='Web Developer', title='Free Web Developer Invoice Template - Download PDF (No Sign-Up)',
  desc='A free invoice template for web developers - fixed-scope builds, hourly work and hosting. Download a professional PDF, no account. US / UK / AU / CA.',
  lead='Invoice for website builds, hourly development and hosting. Add your lines and rate and download a clean PDF - free, no account.',
  include=['Your business and the client','Invoice number, issue date and due date','Fixed-scope build, hourly development, and setup/hosting lines','Your hourly rate where billing by time','Milestone or Net terms, and how to pay'],
  items=[('Website development - fixed scope', 1, 3500), ('Hourly development', 10, 95), ('Hosting setup & deployment', 1, 250)],
  terms='Developers often bill by milestone (e.g. 50% up front, 50% on launch) or Net 15-30.',
  faqs=[('How do web developers invoice clients?','Either a fixed project fee split into milestones, or hourly at your rate. List each as a line item with a clear description, and reference the project or milestone in the notes.'),
        ('How do I handle milestone billing?','Invoice each milestone separately (deposit, mid-point, launch). Reuse your details with a new invoice number for each, and note which milestone it covers.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='photographer', name='Photographer', title='Free Photography Invoice Template - Download a PDF (No Sign-Up)',
  desc='A free invoice template for photographers - session fees, edited images, travel and print release. Download a clean PDF, no account. US / UK / AU / CA.',
  lead='Invoice for shoots, editing, travel and prints. Add your lines and download a professional PDF invoice - free, no sign-up.',
  include=['Your studio and the client','Invoice number, shoot date and due date','Session fee, edited images, travel and any print/usage release','Per-image or package pricing','Terms - deposit to book, balance before delivery'],
  items=[('Photography session - half day', 1, 650), ('Edited images - per image', 25, 15), ('Travel fee', 1, 80), ('Print release', 1, 50)],
  terms='Photographers usually take a booking deposit and collect the balance before delivering galleries.',
  faqs=[('What goes on a photography invoice?','Your studio and client details, the shoot date, the session fee, edited images (per image or as a package), travel, and any print or usage release, with your deposit and balance terms.'),
        ('How do I invoice a booking deposit?','Create a deposit invoice for the booking fee, then a final invoice for the balance before you deliver the edited gallery. The details carry over with a new number.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='contractor', name='Contractor', title='Free Contractor Invoice Template - Labor & Materials PDF (No Sign-Up)',
  desc='A free invoice template for contractors and tradespeople - labor, materials, equipment and permits. Download a clean PDF, no account. US / UK / AU / CA.',
  lead='Invoice for labor, materials, equipment and permits on a job. Add your lines, apply tax, and download a professional PDF - free, no sign-up.',
  include=['Your business and the customer, plus the job/site address','Invoice number, date and due date','Labor hours, materials, equipment and permit/fees as separate lines','Sales tax / VAT / GST where it applies','Payment terms and how to pay'],
  items=[('Labor - per hour', 16, 55), ('Materials', 1, 820), ('Equipment rental', 2, 120), ('Permit fee', 1, 95)],
  terms='Contractors often invoice a deposit to start, progress payments on larger jobs, and the balance on completion.',
  faqs=[('What should a contractor invoice include?','Your business and the customer, the job address, a breakdown of labor (hours x rate), materials, equipment and any permit fees, plus tax where it applies and your payment terms.'),
        ('How do I show labor and materials separately?','Add a line for labor (hours x your rate) and separate lines for materials, equipment and fees, so the customer can see exactly what they are paying for.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='cleaning', name='Cleaning Service', title='Free Cleaning Service Invoice Template - PDF Download (No Sign-Up)',
  desc='A free invoice template for cleaning businesses - per-visit, deep cleans and supplies. Download a clean PDF, no account. US / UK / AU / CA.',
  lead='Invoice for regular cleans, one-off deep cleans and supplies. Add your lines and download a professional PDF - free, no sign-up.',
  include=['Your business and the client','Invoice number, date and due date','Per-visit cleaning, deep cleans and supplies as line items','Recurring or one-off pricing','Terms - due on receipt or Net 7 is common'],
  items=[('Standard cleaning - per visit', 4, 120), ('Deep clean - one-off', 1, 280), ('Supplies', 1, 35)],
  terms='Cleaning services often invoice weekly or monthly, with Due on receipt or Net 7 terms.',
  faqs=[('How do I invoice for recurring cleaning?','List each visit (or a monthly line for the agreed number of visits) at your per-visit rate, add any extras or supplies, and invoice on your regular cycle.'),
        ('Due on receipt or Net 7?','Both are common for cleaning. &ldquo;Due on receipt&rdquo; asks for immediate payment; Net 7 gives a week. Pick the term under the form.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='tutor', name='Tutor', title='Free Tutoring Invoice Template - Download a PDF Invoice (No Sign-Up)',
  desc='A free invoice template for tutors - sessions by the hour, packages and materials. Download a clean PDF, no account. US / UK / AU / CA.',
  lead='Invoice parents or students for tutoring sessions and materials. Add your lines and download a professional PDF - free, no sign-up.',
  include=['Your name and the client (parent or student)','Invoice number, date and due date','Sessions by the hour or as a package, plus materials','Your hourly or package rate','Terms - often paid in advance or Due on receipt'],
  items=[('Tutoring session - per hour', 12, 45), ('Materials & workbook', 1, 30)],
  terms='Tutors are often paid in advance for a block of sessions, or Due on receipt each month.',
  faqs=[('How do I invoice for tutoring?','List the sessions (hours x your rate) for the period, add any materials, and invoice monthly or per block. Parents often prefer to pay in advance.'),
        ('Can I invoice for a block of sessions?','Yes - add one line for the number of sessions at your rate (for example 12 sessions), or a package line, and invoice it up front.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='virtual-assistant', name='Virtual Assistant', title='Free Virtual Assistant Invoice Template - PDF Download (No Sign-Up)',
  desc='A free invoice template for virtual assistants - hourly support and monthly packages. Download a clean PDF, no account. US / UK / AU / CA.',
  lead='Invoice clients for admin support, hourly or on a monthly package. Add your lines and download a professional PDF - free, no sign-up.',
  include=['Your business and the client','Invoice number, date and due date','Hourly support or a monthly package as line items','Your hourly rate or package price','Terms - monthly in advance or Net 7-14'],
  items=[('Admin support - per hour', 20, 35), ('Inbox & calendar management - monthly', 1, 400)],
  terms='VAs often invoice a monthly package in advance, or hourly work Net 7-14.',
  faqs=[('How do virtual assistants invoice clients?','By the hour (hours x your rate) or as a fixed monthly package. List each as a line item, and invoice on your agreed cycle - monthly in advance is common.'),
        ('How do I invoice a retainer package?','Add a single monthly package line for the agreed amount and invoice it at the start of each month, reusing your details with a new number.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
 dict(slug='marketing', name='Marketing & Social Media', title='Free Marketing Invoice Template - Social Media & Ads PDF (No Sign-Up)',
  desc='A free invoice template for marketers and social media managers - management retainers, content and ad setup. Download a clean PDF, no account. US / UK / AU / CA.',
  lead='Invoice for social media management, content and ad campaigns. Add your lines and download a professional PDF - free, no sign-up.',
  include=['Your business and the client','Invoice number, date and due date','Management retainer, content per post and campaign setup','Monthly or per-item pricing','Terms - monthly in advance is common'],
  items=[('Social media management - monthly', 1, 1200), ('Content creation - per post', 12, 45), ('Ad campaign setup', 1, 350)],
  terms='Marketers often bill a monthly management retainer in advance, with ad spend invoiced or passed through separately.',
  faqs=[('What should a marketing invoice include?','Your agency and client, a management retainer line, content or deliverables (per post or per item), and any campaign setup, each priced clearly, plus your monthly terms.'),
        ('How do I handle ad spend?','Keep ad spend separate from your fees - either the client pays the platform directly, or you add a clearly labelled pass-through line. Do not bury it in your management fee.'),
        ('Is it free?','Yes - no sign-up. The free version allows 2 PDF downloads per hour.')]),
]

def head(title, desc, url, schema_blocks):
    blocks = '\n'.join('<script type="application/ld+json">%s</script>' % json.dumps(b, ensure_ascii=False) for b in schema_blocks)
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<title>{title}</title>\n<meta name="description" content="{desc}">\n'
      f'<link rel="canonical" href="{url}">\n'
      f'<link rel="alternate" hreflang="en" href="{url}">\n<link rel="alternate" hreflang="x-default" href="{url}">\n'
      '<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
      '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Free BizDoc">\n'
      '<meta property="og:locale" content="en_US">\n'
      f'<meta property="og:title" content="{title}">\n<meta property="og:description" content="{desc}">\n'
      f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{BASE}/og.jpg">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
      '<link rel="stylesheet" href="/suite.css?v=20261017d">\n'
      f'{blocks}\n</head>\n<body>')

HEADER = ('<header class="hdr"><div class="in">\n'
  '  <a class="brand" href="/en/" style="text-decoration:none"><img src="/logo.png" alt="Free BizDoc" style="height:30px;width:auto;display:block"></a>\n'
  '  <span class="sp"></span>\n'
  '  <a class="pro" href="/?lang=ja" lang="ja" title="Japanese version">日本語</a>\n'
  '</div></header>')

FOOTER = '''<footer class="ft"><div class="in">
  <div class="cols">
    <div>
      <div class="brand"><img src="/logo.png" alt="Free BizDoc" style="height:26px;width:auto;display:block;filter:brightness(0) invert(1)"></div>
      <p>Free, no-sign-up business document generator. Invoices, estimates, receipts and more as clean PDFs - generated in your browser, never stored on our servers.</p>
    </div>
    <div class="col">
      <h4>Free documents</h4>
      <a href="/en/invoice">Invoice</a>
      <a href="/en/estimate">Estimate / Quote</a>
      <a href="/en/receipt">Receipt</a>
      <a href="/en/purchase-order">Purchase Order</a>
      <a href="/en/packing-slip">Packing Slip / Delivery Note</a>
    </div>
    <div class="col">
      <h4>More</h4>
      <a href="/en/invoice-templates">Invoice templates</a>
      <a href="/en/blog">Blog</a>
      <a href="/en/compare">Compare tools</a>
      <a href="/en/pricing">Pricing &amp; PRO</a>
      <a href="/?lang=ja" lang="ja">日本語</a>
      <a href="/en/privacy">Privacy policy</a>
    </div>
  </div>
  <div class="bot">Tax calculations are provided as an aid only. Confirm your obligations with your accountant or tax authority.<br>&copy; 2026 Free BizDoc</div>
</div></footer>'''

CRUMB_CSS = ('<style>.crumb{max-width:1180px;margin:0 auto;padding:12px 20px 0;font-size:12.5px;color:#7c8aa0}'
  '.crumb a{color:#1766e6;text-decoration:none}.crumb a:hover{text-decoration:underline}'
  '.lpcta{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0 2px}'
  '.lpbtn{display:inline-flex;align-items:center;gap:8px;font-size:15.5px;font-weight:800;text-decoration:none;border-radius:12px;padding:13px 22px}'
  '.lpbtn.pri{background:var(--ac,#1766e6);color:#fff;box-shadow:0 12px 26px -10px rgba(23,102,230,.55)}.lpbtn.pri:hover{background:#1257ca}'
  '.lpbtn.gh{border:1.5px solid var(--bd,#d4dced);color:#13263b}'
  '.extbl{width:100%;border-collapse:collapse;margin:8px 0 6px;font-size:14px}'
  '.extbl th,.extbl td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--bd,#e6ebf2)}'
  '.extbl th{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:#7c8aa0}'
  '.extbl td.n,.extbl th.n{text-align:right;white-space:nowrap}'
  '.relgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin:8px 0 4px}'
  '.relgrid a{display:block;padding:12px 14px;border:1px solid var(--bd,#e2eaf4);border-radius:12px;text-decoration:none;color:inherit;font-weight:700;font-size:14px;background:#fff}'
  '.relgrid a:hover{border-color:var(--ac,#1766e6)}</style>')

def faq_html(faq):
    qs = ''.join(f'<div class="q"><h3>{q}</h3><p>{a}</p></div>' for q, a in faq)
    return f'<div class="faqwrap"><div class="faq"><h2>Frequently asked questions</h2>{qs}</div></div>'

def example_table(items):
    rows = ''
    sub = 0
    for (n, q, p) in items:
        amt = q * p
        sub += amt
        rows += f'<tr><td>{n}</td><td class="n">{q}</td><td class="n">${p:,.2f}</td><td class="n">${amt:,.2f}</td></tr>'
    rows += f'<tr><td></td><td></td><td class="n"><b>Total</b></td><td class="n"><b>${sub:,.2f}</b></td></tr>'
    return ('<table class="extbl"><thead><tr><th>Description</th><th class="n">Qty</th><th class="n">Unit price</th><th class="n">Amount</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')

def industry_page(ind):
    url = f"{BASE}/en/invoice/{ind['slug']}"
    pf = b64p(ind['items'])
    cta = f'/en/invoice#p={pf}'
    schema = [
      {"@context":"https://schema.org","@type":"WebApplication","name":f"Free {ind['name']} Invoice Template","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in ind['faqs']]},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Invoice templates","item":f"{BASE}/en/invoice-templates"},
        {"@type":"ListItem","position":3,"name":f"{ind['name']} invoice","item":url}]},
    ]
    related = ''.join(f'<a href="/en/invoice/{o["slug"]}">{o["name"]} invoice</a>' for o in INDUSTRIES if o['slug'] != ind['slug'])
    include = ''.join(f'<li>{x}</li>' for x in ind['include'])
    art = (f'<article class="art">'
      f'<p class="lead">{ind["lead"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Create your {ind["name"].lower()} invoice &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/invoice">Open a blank invoice</a></div>'
      f'<h2>What a {ind["name"].lower()} invoice should include</h2><ul>{include}</ul>'
      f'<h2>Example {ind["name"].lower()} invoice</h2>'
      f'<p>Here is a typical set of line items &mdash; click the button to open it in the editor, then change the descriptions, amounts and your details.</p>'
      f'{example_table(ind["items"])}'
      f'<p>{ind["terms"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Use this {ind["name"].lower()} template &rarr;</a></div>'
      f'<h2>Related templates</h2><div class="relgrid">{related}</div>'
      f'</article>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      f'<span class="ey">Free - No sign-up - {ind["name"]} invoice</span>'
      f'<h1>Free {ind["name"]} Invoice Template</h1>'
      f'<p>{ind["desc"]}</p></div></div></section>')
    crumb = f'<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/invoice-templates">Invoice templates</a> &rsaquo; {ind["name"]}</nav>'
    parts = [head(ind['title'], ind['desc'], url, schema), CRUMB_CSS, HEADER, crumb, hero, art, faq_html(ind['faqs']), FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)

DOC_LINKS = [('/en/invoice','Invoice'),('/en/estimate','Estimate / Quote'),('/en/receipt','Receipt'),('/en/purchase-order','Purchase Order'),
 ('/en/packing-slip','Packing Slip'),('/en/credit-note','Credit Note'),('/en/proforma-invoice','Pro Forma Invoice'),('/en/sales-order','Sales Order'),
 ('/en/timesheet','Timesheet'),('/en/work-order','Work Order'),('/en/expense-report','Expense Report'),('/en/bill-of-sale','Bill of Sale'),('/en/donation-receipt','Donation Receipt')]

def hub_page():
    url = f"{BASE}/en/invoice-templates"
    title = 'Free Invoice Templates by Profession - Download PDF (No Sign-Up)'
    desc = 'Free invoice templates for freelancers, consultants, designers, developers, photographers, contractors and more. Fill in and download a PDF in seconds - no sign-up.'
    schema = [
      {"@context":"https://schema.org","@type":"CollectionPage","name":"Free Invoice Templates by Profession","url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Invoice templates","item":url}]},
    ]
    cards = ''.join(f'<a class="dcard" href="/en/invoice/{i["slug"]}"><h3>{i["name"]}</h3><p>{i["lead"][:120]}&hellip;</p><span class="go">Open template &rarr;</span></a>' for i in INDUSTRIES)
    docs = ''.join(f'<a href="{u}">{t}</a>' for u, t in DOC_LINKS)
    css = ('<style>.dgrid{max-width:1180px;margin:0 auto;padding:12px 20px 30px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}'
      '.dcard{display:block;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;padding:20px 20px 16px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);transition:.15s}'
      '.dcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}.dcard h3{margin:0 0 6px;font-size:16px}.dcard p{margin:0 0 12px;font-size:13px;color:#5a6b7b;line-height:1.55}.dcard .go{font-size:13px;font-weight:800;color:var(--ac,#1766e6)}'
      '.alldocs{max-width:1180px;margin:0 auto;padding:4px 20px 40px}.alldocs h2{font-size:clamp(18px,3vw,22px);margin:0 0 12px}'
      '.alldocs .row{display:flex;flex-wrap:wrap;gap:8px}.alldocs .row a{font-size:13px;font-weight:700;color:#45607a;background:#f1f5fb;border:1px solid #dce5f0;border-radius:999px;padding:8px 14px;text-decoration:none}.alldocs .row a:hover{border-color:var(--ac,#1766e6);color:var(--ac,#1766e6)}</style>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      '<span class="ey">Free - No sign-up - US / UK / AU / CA</span>'
      '<h1>Free Invoice Templates by Profession</h1>'
      '<p>Pick the template that matches your work. Each one opens in the editor pre-filled with the line items your profession typically bills for &mdash; change the details and download a clean PDF. No account needed.</p>'
      '</div></div></section>')
    crumb = '<nav class="crumb"><a href="/en/">Home</a> &rsaquo; Invoice templates</nav>'
    art = ('<article class="art"><h2>One invoice tool, every profession</h2>'
      '<p>All of these open the same free invoice generator &mdash; the difference is the starting line items. Tax (US sales tax, UK VAT, Australian GST, Canadian GST/HST) and currency switch to your country, and you can convert any invoice into a receipt, quote or credit note in one click.</p></article>')
    alldocs = f'<div class="alldocs"><h2>All free documents</h2><div class="row">{docs}</div></div>'
    parts = [head(title, desc, url, schema), CRUMB_CSS, HEADER, crumb, hero, css, f'<div class="dgrid">{cards}</div>', alldocs, art, FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)

os.makedirs(os.path.join(OUT, 'invoice'), exist_ok=True)
for ind in INDUSTRIES:
    with open(os.path.join(OUT, 'invoice', ind['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(industry_page(ind))
    print('wrote en/invoice/%s.html' % ind['slug'])
with open(os.path.join(OUT, 'invoice-templates.html'), 'w', encoding='utf-8') as f:
    f.write(hub_page())
print('wrote en/invoice-templates.html')

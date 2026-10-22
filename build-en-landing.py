#!/usr/bin/env python3
# Generates English programmatic landing pages: an invoice-template hub and
# per-industry invoice landing pages under /en/invoice/<slug>.
# Each page is unique content + a CTA that opens /en/invoice prefilled via #p=.
import json, os, base64, datetime, html
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'en')
V = datetime.date.today().strftime('%Y%m%d') + 'l'
BASE = 'https://free-bizdocs.com'

def b64p(items, kind='invoice', region=None, tax_rate=None, prov=None, notes=''):
    payload = {'kind': kind,
               'items': [{'name': it[0], 'qty': it[1], 'unit_price': it[2], 'tax': (it[3] if len(it) > 3 else 'tax')} for it in items]}
    if region:
        payload['region'] = region
    if tax_rate is not None:
        payload['tax_rate'] = str(tax_rate)
    if prov:
        payload['prov'] = prov
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

# Country / tax invoice pages. Example items carry region-appropriate tax codes
# (UK/AU fixed-rate per line; US sets a sample sales-tax rate; CA sets a province).
COUNTRIES = [
 dict(slug='us-sales-tax', region='us', name='United States', cur='USD', sym='$', taxname='Sales tax', rate=8.25,
  title='US Sales Tax Invoice Template - Free PDF Invoice (No Sign-Up)',
  desc='A free US invoice template with sales tax. Set your state rate per line, add your details, and download a clean PDF - no sign-up. Letter paper, USD.',
  lead='Create a US invoice with sales tax in seconds. There is no federal invoice format - set the sales-tax rate for your state (or mark lines exempt), add your line items, and download a professional PDF. No account needed.',
  reqs=['Your business name, address and contact details (and EIN if you use one)','The word &ldquo;Invoice&rdquo;, a unique number and the issue date','The customer&rsquo;s name and address (&ldquo;Bill To&rdquo;)','Itemized lines with description, quantity, unit price and amount','<b>Sales tax</b> applied per line where you have nexus - the rate depends on your state and the product/service','Subtotal, tax and total, plus payment terms (Net 30 is common)'],
  items=[('Consulting services - per hour', 10, 150, 'tax'), ('Software license - annual', 1, 1200, 'tax')],
  tax_rate='8.25',
  faqs=[('Is there a required invoice format in the US?','No. There is no federal standard. Include your details, the customer, a unique invoice number, itemized lines, any sales tax, and the total. Sales tax rules depend on your state and whether you have nexus there.'),
        ('How do I add sales tax?','Set your state&rsquo;s sales-tax rate in the tool and mark taxable lines; exempt items can be set to exempt. The PDF shows the tax separately from the subtotal.'),
        ('What paper size is the PDF?','US invoices download on Letter (8.5 x 11 in) in USD. The tool switches paper, currency and date format when you pick a country.')]),
 dict(slug='uk-vat', region='uk', name='United Kingdom', cur='GBP', sym='£', taxname='VAT', rate=20,
  title='UK VAT Invoice Template - Free PDF Invoice (No Sign-Up)',
  desc='A free UK VAT invoice template. Shows your VAT number, VAT at 20% / 5% / 0% per rate, and totals in GBP. Download a clean PDF - no sign-up. A4 paper.',
  lead='Create a compliant UK VAT invoice. Show your VAT registration number, the VAT rate and amount per line, and the totals - the tool handles 20%, 5%, zero-rated and exempt. Download a professional PDF, no account.',
  reqs=['A unique, sequential <b>invoice number</b> and the date (time of supply)','Your business name and address, and your <b>VAT registration number</b>','The customer&rsquo;s name and address','A description of the goods or services','The <b>VAT rate</b> (20%, 5% or 0%) and the VAT amount for each rate','The total excluding VAT, the total VAT, and the gross total in GBP'],
  items=[('Consulting services - per day', 5, 480, '20'), ('Website maintenance - monthly', 1, 300, '20')],
  faqs=[('What must a UK VAT invoice show?','If you are VAT registered you must show your VAT number, a sequential invoice number, the date, the customer, a description, the VAT rate and amount per rate, and the totals excluding and including VAT.'),
        ('Do I have to charge VAT?','Only if you are VAT registered (required once turnover passes the threshold, optional below it). If you are not registered, issue a normal invoice without VAT and do not show a VAT number.'),
        ('Does it handle 20%, 5% and zero-rated?','Yes. Pick the rate per line - 20% standard, 5% reduced, 0% zero-rated, or exempt - and the VAT is itemized per rate on the PDF in GBP.')]),
 dict(slug='australia-tax-invoice', region='au', name='Australia', cur='AUD', sym='$', taxname='GST', rate=10,
  title='Australian Tax Invoice Template - Free PDF with GST (No Sign-Up)',
  desc='A free Australian tax invoice template with GST. Shows your ABN, GST at 10%, and the words &ldquo;Tax Invoice&rdquo;. Download a clean PDF - no sign-up. A4 paper, AUD.',
  lead='Create a compliant Australian tax invoice. Enter your ABN and charge GST at 10% and the title becomes &ldquo;Tax Invoice&rdquo; automatically. Download a professional PDF in AUD, no account.',
  reqs=['The words <b>&ldquo;Tax Invoice&rdquo;</b> (shown automatically once you add an ABN and charge GST)','Your business name and your <b>ABN</b>','The date the invoice is issued','A description of the items sold, with quantities','The <b>GST amount</b> (10%), or a statement that the total price includes GST','For sales of <b>$1,000 or more</b>, the buyer&rsquo;s identity or ABN'],
  items=[('Consulting services - per hour', 12, 160, '10'), ('Onboarding setup', 1, 800, '10')],
  faqs=[('What makes an Australian tax invoice valid?','For sales over $82.50 (incl. GST) a tax invoice must show the words &ldquo;Tax Invoice&rdquo;, your ABN, the date, a description, and the GST amount (or that the total includes GST). Over $1,000 it must also show the buyer&rsquo;s identity or ABN.'),
        ('How does the title become &ldquo;Tax Invoice&rdquo;?','Enter your ABN in your business details and keep GST at 10% on the lines - the heading switches to &ldquo;Tax Invoice&rdquo; and a &ldquo;Total price includes GST&rdquo; note is added.'),
        ('What if I am not registered for GST?','If you are not GST registered, do not charge GST - set the lines to GST-free. The document stays a plain invoice rather than a tax invoice.')]),
 dict(slug='canada-gst-hst', region='ca', name='Canada', cur='CAD', sym='$', taxname='GST/HST', rate=13, prov='ON',
  title='Canada GST/HST Invoice Template - Free PDF Invoice (No Sign-Up)',
  desc='A free Canadian invoice template with GST/HST (and PST/QST by province). Shows your GST/HST number and the tax at the correct provincial rate. Download a clean PDF - no sign-up. Letter paper, CAD.',
  lead='Create a Canadian invoice with the right tax for your province. Pick the province and GST, HST, PST or QST is applied at the correct rate, with your GST/HST number on the invoice. Download a professional PDF in CAD, no account.',
  reqs=['Your business name and the date','A unique invoice number','Your <b>GST/HST registration number</b> (required on invoices once registered)','A description of the goods or services','The <b>GST/HST</b> (and PST/QST where it applies) at your province&rsquo;s rate, or a statement that tax is included','The total - for sales of $150+ more detail is required'],
  items=[('Consulting services - per hour', 10, 140, 'tax'), ('Materials', 1, 600, 'tax')],
  faqs=[('How is tax handled across provinces?','Pick your province and the tool applies the correct combination - HST in Ontario and the Atlantic provinces, GST plus PST in BC/Manitoba/Saskatchewan, GST plus QST in Quebec, or GST only in Alberta and the territories.'),
        ('Do I need my GST/HST number on the invoice?','Yes, once you are registered you must show your GST/HST number on invoices, along with the tax amount (or a statement that it is included) so customers can claim input tax credits.'),
        ('What rate is used for Ontario?','Ontario uses HST at 13%. The example here uses Ontario; change the province in the tool to apply your own rate.')]),
]


def country_example_table(c):
    sym = c['sym']
    rows = ''
    sub = 0
    for it in c['items']:
        amt = it[1] * it[2]
        sub += amt
        rows += f'<tr><td>{it[0]}</td><td class="n">{it[1]}</td><td class="n">{sym}{it[2]:,.2f}</td><td class="n">{sym}{amt:,.2f}</td></tr>'
    tax = round(sub * c['rate'] / 100, 2)
    total = sub + tax
    foot = (f'<tr><td></td><td></td><td class="n">Subtotal</td><td class="n">{sym}{sub:,.2f}</td></tr>'
            f'<tr><td></td><td></td><td class="n">{c["taxname"]} ({c["rate"]:g}%)</td><td class="n">{sym}{tax:,.2f}</td></tr>'
            f'<tr><td></td><td></td><td class="n"><b>Total ({c["cur"]})</b></td><td class="n"><b>{sym}{total:,.2f}</b></td></tr>')
    return ('<table class="extbl"><thead><tr><th>Description</th><th class="n">Qty</th><th class="n">Unit price</th><th class="n">Amount</th></tr></thead>'
            f'<tbody>{rows}{foot}</tbody></table>')


def country_page(c):
    url = f"{BASE}/en/invoice/{c['slug']}"
    pf = b64p(c['items'], region=c['region'], tax_rate=c.get('tax_rate'), prov=c.get('prov'))
    cta = f'/en/invoice#p={pf}'
    schema = [
      {"@context":"https://schema.org","@type":"WebApplication","name":f"{c['name']} Invoice Template","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":c['cur']},"url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c['faqs']]},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Invoice templates","item":f"{BASE}/en/invoice-templates"},
        {"@type":"ListItem","position":3,"name":f"{c['name']} invoice","item":url}]},
    ]
    others = ''.join(f'<a href="/en/invoice/{o["slug"]}">{o["name"]} invoice</a>' for o in COUNTRIES if o['slug'] != c['slug'])
    reqs = ''.join(f'<li>{x}</li>' for x in c['reqs'])
    H1 = {'us': 'US Sales Tax Invoice Template', 'uk': 'UK VAT Invoice Template', 'au': 'Australian Tax Invoice Template', 'ca': 'Canada GST/HST Invoice Template'}
    h1 = H1.get(c['region'], c['name'] + ' Invoice Template')
    art = (f'<article class="art">'
      f'<p class="lead">{c["lead"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Create a {c["name"]} invoice &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/invoice">Open a blank invoice</a></div>'
      f'<h2>What a {c["name"]} invoice must include</h2><ul>{reqs}</ul>'
      f'<h2>Example ({c["taxname"]} at {c["rate"]:g}%)</h2>'
      f'<p>A typical invoice with {c["taxname"]} applied. Click the button to open it in the editor already set to {c["name"]} &mdash; change the details and your {c["taxname"].split("/")[0]} number, then download.</p>'
      f'{country_example_table(c)}'
      f'<div class="note">Tax rules change and vary by {"state" if c["region"]=="us" else ("province" if c["region"]=="ca" else "situation")}. The calculation here is an aid &mdash; confirm your obligations with your accountant or tax authority.</div>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Use this {c["name"]} template &rarr;</a></div>'
      f'<h2>Invoices for other countries</h2><div class="relgrid">{others}</div>'
      f'</article>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      f'<span class="ey">Free - No sign-up - {c["name"]} - {c["taxname"]}</span>'
      f'<h1>Free {h1}</h1>'
      f'<p>{c["desc"]}</p></div></div></section>')
    crumb = f'<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/invoice-templates">Invoice templates</a> &rsaquo; {c["name"]}</nav>'
    parts = [head(c['title'], c['desc'], url, schema), CRUMB_CSS, HEADER, crumb, hero, art, faq_html(c['faqs']), FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


# Estimate / Quote cluster - same professions, quote-specific content. Items are
# reused from the invoice cluster; the tool renders them as an Estimate (valid-until
# date + acceptance line) when kind=quote.
IND_BY = {i['slug']: i for i in INDUSTRIES}
QUOTES = [
 dict(slug='freelancer', name='Freelancer',
  title='Free Freelancer Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for freelancers. Set out the scope, price and a valid-until date, add an acceptance line, and download a PDF - no sign-up. US / UK / AU / CA.',
  lead='Send a client a clear freelance quote before you start. Lay out the scope and price, add a valid-until date and an acceptance line, and download a professional PDF - free, no account. When the client approves, convert it to an invoice in one click.',
  include=['Your details and the client (&ldquo;Prepared For&rdquo;)','A quote number, the date and a <b>valid-until</b> date','The scope of work with quantities and prices','What is included - and anything explicitly excluded','A deposit requirement and an <b>acceptance signature</b> line'],
  terms='Freelancers often keep a quote valid for 14-30 days and ask for a deposit before starting.',
  faqs=[('How do I write a freelance quote?','Set out the scope as line items with prices, add a valid-until date so the price does not stay open forever, note what is included and excluded, and leave an acceptance line. Convert it to an invoice once the client approves.'),
        None, None]),
 dict(slug='consultant', name='Consultant',
  title='Free Consultant Quote & Proposal Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for consultants - scope, day rates and retainers with a valid-until date and acceptance line. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for advisory work before you begin. Set out the engagement, day rates or retainer and a valid-until date, add an acceptance line, and download a professional PDF - free, no account.',
  include=['Your consultancy and the client','A quote number, the date and a <b>valid-until</b> date','The engagement scope - days, workshops or a retainer - with rates','Assumptions, deliverables and anything out of scope','Payment schedule and an <b>acceptance</b> line'],
  terms='Consultants often quote a fixed engagement or a retainer and keep the price valid for 30 days.',
  faqs=[('What should a consulting quote include?','The scope of the engagement (days, workshops or retainer) with your rates, the deliverables and assumptions, what is out of scope, a valid-until date, and an acceptance line the client can sign.'),
        None, None]),
 dict(slug='graphic-designer', name='Graphic Designer',
  title='Free Graphic Design Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for graphic designers - deliverables, revisions and usage, with a valid-until date and acceptance. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for a design project before you start. List the deliverables, the number of revisions and the price, add a valid-until date and an acceptance line, and download a professional PDF - free, no account.',
  include=['Your studio and the client','A quote number, the date and a <b>valid-until</b> date','Deliverables with prices - logo, brand guide, assets','The number of <b>revisions</b> included and usage rights on payment','Deposit terms and an <b>acceptance</b> line'],
  terms='Designers usually quote a fixed package, state the revisions included, and take a 50% deposit.',
  faqs=[('What goes in a graphic design quote?','The deliverables and their prices, how many revision rounds are included, the usage rights that transfer on payment, a valid-until date, and an acceptance line. Spell out what is not included to avoid scope creep.'),
        None, None]),
 dict(slug='web-developer', name='Web Developer',
  title='Free Web Developer Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for web developers - fixed scope, milestones and hosting, with a valid-until date and acceptance. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for a build before you start. Set out the scope, milestones and price, add a valid-until date and an acceptance line, and download a professional PDF - free, no account.',
  include=['Your business and the client','A quote number, the date and a <b>valid-until</b> date','The build scope and milestones with prices','Assumptions, what is included, and ongoing hosting/maintenance','Milestone or deposit terms and an <b>acceptance</b> line'],
  terms='Developers often quote a fixed scope split into milestones and keep the quote valid for 30 days.',
  faqs=[('How do I quote a website project?','Define the scope and split it into milestones with prices, state your assumptions and what is excluded, add any ongoing hosting or maintenance, a valid-until date, and an acceptance line. Convert to an invoice per milestone as you deliver.'),
        None, None]),
 dict(slug='photographer', name='Photographer',
  title='Free Photography Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for photographers - session, editing, travel and prints, with a valid-until date and acceptance. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for a shoot before you book it in. Set out the session, editing, travel and prints with prices, add a valid-until date and an acceptance line, and download a professional PDF - free, no account.',
  include=['Your studio and the client','A quote number, the date and a <b>valid-until</b> date','The session, edited images, travel and any prints with prices','Deliverables, turnaround and usage/print release','A booking deposit and an <b>acceptance</b> line'],
  terms='Photographers usually quote a package, note the turnaround, and take a booking deposit to hold the date.',
  faqs=[('What should a photography quote include?','The session fee, edited images (per image or package), travel and prints, the turnaround and usage rights, a valid-until date, and an acceptance line. Note the booking deposit needed to hold the date.'),
        None, None]),
 dict(slug='contractor', name='Contractor',
  title='Free Contractor Quote & Estimate Template - Labor & Materials PDF',
  desc='A free quote/estimate template for contractors - labor, materials and equipment, with a valid-until date and acceptance. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a customer for a job before you start. Break out labor, materials and equipment with prices, add a valid-until date and an acceptance line, and download a professional PDF - free, no account.',
  include=['Your business and the customer, plus the job/site address','A quote number, the date and a <b>valid-until</b> date','Labor, materials and equipment as separate priced lines','What is included, excluded, and any allowances','Deposit/progress terms and an <b>acceptance</b> line'],
  terms='Contractors often keep a quote valid for 30 days, take a deposit to start, and stage progress payments.',
  faqs=[('What should a contractor quote include?','A breakdown of labor (hours x rate), materials and equipment, the job address, what is included and excluded (and any allowances), a valid-until date, and an acceptance line the customer signs to authorise the work.'),
        None, None]),
 dict(slug='cleaning', name='Cleaning Service',
  title='Free Cleaning Service Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for cleaning businesses - per-visit, deep cleans and supplies, with a valid-until date. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for regular or one-off cleaning. Set out the visits, any deep clean and supplies with prices, add a valid-until date, and download a professional PDF - free, no account.',
  include=['Your business and the client','A quote number, the date and a <b>valid-until</b> date','Per-visit cleaning, deep cleans and supplies with prices','The schedule (weekly/monthly) and what each visit covers','Terms and an <b>acceptance</b> line'],
  terms='Cleaning quotes often set a per-visit rate for a schedule and stay valid for 30 days.',
  faqs=[('How do I quote for a cleaning contract?','Give a per-visit rate for the agreed schedule (weekly or monthly), list what each visit covers, add any one-off deep clean and supplies, a valid-until date, and an acceptance line.'),
        None, None]),
 dict(slug='tutor', name='Tutor',
  title='Free Tutoring Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for tutors - sessions, packages and materials, with a valid-until date. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a parent or student for tutoring before you begin. Set out the sessions or package and materials with prices, add a valid-until date, and download a professional PDF - free, no account.',
  include=['Your name and the client (parent or student)','A quote number, the date and a <b>valid-until</b> date','Sessions by the hour or a package, plus materials','The schedule and what is covered','Payment terms and an <b>acceptance</b> line'],
  terms='Tutors often quote a block of sessions or a term package, payable in advance.',
  faqs=[('How do I quote for tutoring?','Quote a block of sessions (hours x your rate) or a term package, list any materials, add the schedule, a valid-until date, and an acceptance line. Parents often prefer to pay the quoted block in advance.'),
        None, None]),
 dict(slug='virtual-assistant', name='Virtual Assistant',
  title='Free Virtual Assistant Quote & Estimate Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for virtual assistants - hourly or monthly packages, with a valid-until date. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for support before you start. Set out an hourly rate or a monthly package with what is included, add a valid-until date, and download a professional PDF - free, no account.',
  include=['Your business and the client','A quote number, the date and a <b>valid-until</b> date','An hourly rate or a monthly package with hours/tasks included','What the package covers and any limits','Terms and an <b>acceptance</b> line'],
  terms='VAs usually quote a monthly package with a set number of hours, payable in advance.',
  faqs=[('How do I quote a VA retainer?','Quote a monthly package for a set number of hours or tasks, state clearly what is and is not included, add a valid-until date, and an acceptance line. Bill the package in advance once accepted.'),
        None, None]),
 dict(slug='marketing', name='Marketing & Social Media',
  title='Free Marketing Quote & Proposal Template - PDF (No Sign-Up)',
  desc='A free quote/estimate template for marketers and social media managers - retainers, content and ads, with a valid-until date. Download a PDF, no account. US / UK / AU / CA.',
  lead='Quote a client for marketing work before you start. Set out the management retainer, content and campaign setup with prices, add a valid-until date, and download a professional PDF - free, no account.',
  include=['Your agency and the client','A quote number, the date and a <b>valid-until</b> date','A management retainer, content and campaign setup with prices','What is included, deliverables per month, and ad spend handling','Terms and an <b>acceptance</b> line'],
  terms='Marketing quotes usually set a monthly retainer, list monthly deliverables, and keep ad spend separate.',
  faqs=[('What should a marketing quote include?','A monthly management retainer, the content or deliverables per month with prices, any campaign setup, how ad spend is handled (kept separate from your fee), a valid-until date, and an acceptance line.'),
        None, None]),
]
# Shared quote FAQs (fill the two None slots) - genuinely the same information for every profession.
_QUOTE_FAQ_SHARED = [
 ('What is the difference between an estimate and a quote?','An estimate is an approximate price that may change; a quote is a fixed price the client can accept, valid for a set period. Say which you are issuing and include a valid-until date. This tool names the document to match your country.'),
 ('Can I turn the quote into an invoice?','Yes. Once the client accepts, open it in the editor and switch to &ldquo;Invoice&rdquo; under the preview - the same line items and client carry over with a new invoice number and today&rsquo;s date.'),
]
for _q in QUOTES:
    _q['faqs'] = [_q['faqs'][0], _QUOTE_FAQ_SHARED[0], _QUOTE_FAQ_SHARED[1]]
    _q['items'] = IND_BY[_q['slug']]['items']


def quote_page(q):
    url = f"{BASE}/en/estimate/{q['slug']}"
    pf = b64p(q['items'], kind='quote')
    cta = f'/en/estimate#p={pf}'
    schema = [
      {"@context":"https://schema.org","@type":"WebApplication","name":f"Free {q['name']} Quote Template","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in q['faqs']]},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Quote templates","item":f"{BASE}/en/estimate-templates"},
        {"@type":"ListItem","position":3,"name":f"{q['name']} quote","item":url}]},
    ]
    related = ''.join(f'<a href="/en/estimate/{o["slug"]}">{o["name"]} quote</a>' for o in QUOTES if o['slug'] != q['slug'])
    include = ''.join(f'<li>{x}</li>' for x in q['include'])
    art = (f'<article class="art">'
      f'<p class="lead">{q["lead"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Create your {q["name"].lower()} quote &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/estimate">Open a blank quote</a></div>'
      f'<h2>What a {q["name"].lower()} quote should include</h2><ul>{include}</ul>'
      f'<h2>Example {q["name"].lower()} quote</h2>'
      f'<p>A typical set of line items &mdash; click the button to open it as an editable estimate (with a valid-until date and an acceptance line), then change the details.</p>'
      f'{example_table(q["items"])}'
      f'<p>{q["terms"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Use this {q["name"].lower()} quote &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/invoice/{q["slug"]}">Need an invoice instead?</a></div>'
      f'<h2>Related quote templates</h2><div class="relgrid">{related}</div>'
      f'</article>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      f'<span class="ey">Free - No sign-up - {q["name"]} quote / estimate</span>'
      f'<h1>Free {q["name"]} Quote &amp; Estimate Template</h1>'
      f'<p>{q["desc"]}</p></div></div></section>')
    crumb = f'<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/estimate-templates">Quote templates</a> &rsaquo; {q["name"]}</nav>'
    parts = [head(q['title'], q['desc'], url, schema), CRUMB_CSS, HEADER, crumb, hero, art, faq_html(q['faqs']), FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


# Receipt cluster - same professions, receipt-specific content. Items reused from the
# invoice cluster; the tool renders them as a Receipt (Amount Paid, payment method,
# PAID stamp, "Received From") when kind=receipt.
RECEIPTS = [
 dict(slug='freelancer', name='Freelancer',
  title='Free Freelancer Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for freelancers. Confirm a payment received, show the amount paid, method and a PAID stamp, and download a PDF - no sign-up. US / UK / AU / CA.',
  lead='Give a client proof that their payment landed. A freelance receipt shows who paid, what for, the amount, the method and a PAID stamp - download a professional PDF, free and no account. Issued an invoice first? Turn it into a receipt in one click.',
  include=['Your name/business and who paid (&ldquo;Received From&rdquo;)','A receipt number and the <b>date of payment</b>','What was paid for - the project or hours','The <b>amount paid</b> and the <b>payment method</b> (bank transfer, card, PayPal)','A paid-in-full indication for the client&rsquo;s records'],
  terms='Freelancers issue a receipt once payment clears, so the client has proof for their bookkeeping.',
  faqs=[('When should a freelancer give a receipt?','Once a payment clears - a deposit or a final payment. The receipt confirms what was received and when, which the client needs for their expense records.'), None, None]),
 dict(slug='consultant', name='Consultant',
  title='Free Consultant Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for consultants - confirm a retainer or fee payment with the amount paid, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for advisory work. A consulting receipt shows the amount paid, the method and a PAID stamp - useful for retainer payments the client books each month. Download a professional PDF, free and no account.',
  include=['Your consultancy and who paid','A receipt number and the <b>date of payment</b>','What was paid for - advisory time or a retainer','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Consultants often issue a receipt for each retainer payment so the client can reconcile monthly.',
  faqs=[('Do I give a receipt for a retainer?','Yes - a receipt for each retainer payment gives the client clean proof for their monthly books. Issue it once the payment clears.'), None, None]),
 dict(slug='graphic-designer', name='Graphic Designer',
  title='Free Graphic Design Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for graphic designers - confirm a deposit or final payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for design work - a deposit to start or the balance on delivery. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your studio and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the design deliverables','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Designers issue a receipt for the deposit and again for the balance when files are released.',
  faqs=[('Should I receipt the deposit and the balance?','Yes - issue a receipt when the deposit clears and another for the balance on delivery, so the client has proof of each payment.'), None, None]),
 dict(slug='web-developer', name='Web Developer',
  title='Free Web Developer Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for web developers - confirm a milestone or final payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for development work - a milestone or the final balance. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your business and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the build or milestone','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Developers issue a receipt per milestone as each payment clears.',
  faqs=[('Do I give a receipt for each milestone?','Yes - a receipt for each milestone payment confirms what was received and keeps the project&rsquo;s paper trail clean for both sides.'), None, None]),
 dict(slug='photographer', name='Photographer',
  title='Free Photography Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for photographers - confirm a booking deposit or final payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for a shoot - the booking deposit or the balance before delivery. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your studio and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the session or package','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Photographers receipt the booking deposit to hold the date and the balance before delivering galleries.',
  faqs=[('Should I receipt the booking deposit?','Yes - issue a receipt when the deposit clears to hold the date, and another for the balance before you deliver the gallery.'), None, None]),
 dict(slug='contractor', name='Contractor',
  title='Free Contractor Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for contractors - confirm a deposit, progress or final payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a customer&rsquo;s payment on a job - a deposit, a progress payment or the final balance. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your business and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the job or stage','The <b>amount paid</b> and the <b>payment method</b> (cash, card, transfer)','A paid-in-full indication'],
  terms='Contractors receipt the deposit, each progress payment and the final balance as they clear.',
  faqs=[('Do customers need a receipt for a cash payment?','Yes - especially for cash. A receipt is the customer&rsquo;s proof the payment was made, with the amount, date and what it covered.'), None, None]),
 dict(slug='cleaning', name='Cleaning Service',
  title='Free Cleaning Service Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for cleaning businesses - confirm a per-visit or monthly payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for cleaning - per visit or for the month. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your business and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the visits or the month','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Cleaning services often issue a receipt each time a visit or the month is paid.',
  faqs=[('Should I give a receipt for every clean?','Give a receipt whenever the client pays - per visit or monthly. It is their proof of payment and keeps a simple record for you.'), None, None]),
 dict(slug='tutor', name='Tutor',
  title='Free Tutoring Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for tutors - confirm a session or package payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a parent or student&rsquo;s payment for tutoring - a block of sessions or a term. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your name and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the sessions or package','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Tutors issue a receipt when a block or term is paid, often in advance.',
  faqs=[('Do parents need a receipt for tutoring?','Many do - for their records or for reimbursement. Issue a receipt when a block or term is paid, showing the amount and what it covered.'), None, None]),
 dict(slug='virtual-assistant', name='Virtual Assistant',
  title='Free Virtual Assistant Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for virtual assistants - confirm an hourly or monthly payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for support - hourly or a monthly package. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your business and who paid','A receipt number and the <b>date of payment</b>','What was paid for - hours or the package','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='VAs often issue a receipt for each monthly package payment.',
  faqs=[('Do I give a receipt for a monthly package?','Yes - a receipt for each package payment gives the client clean proof for their monthly books. Issue it once the payment clears.'), None, None]),
 dict(slug='marketing', name='Marketing & Social Media',
  title='Free Marketing Receipt Template - Payment Receipt PDF (No Sign-Up)',
  desc='A free receipt template for marketers and social media managers - confirm a retainer payment with the amount, method and a PAID stamp. Download a PDF, no account. US / UK / AU / CA.',
  lead='Confirm a client&rsquo;s payment for marketing work - the monthly retainer or a campaign. The receipt shows the amount paid, the method and a PAID stamp. Download a professional PDF, free and no account.',
  include=['Your agency and who paid','A receipt number and the <b>date of payment</b>','What was paid for - the retainer or campaign','The <b>amount paid</b> and the <b>payment method</b>','A paid-in-full indication'],
  terms='Marketers issue a receipt for each monthly retainer payment, keeping ad spend separate.',
  faqs=[('Do I receipt the retainer separately from ad spend?','Yes - receipt your management fee; ad spend the client pays the platform directly, or shows as a separate labelled line. Keep the two clearly apart.'), None, None]),
]
_RECEIPT_FAQ_SHARED = [
 ('What is the difference between a receipt and an invoice?','An invoice requests payment; a receipt confirms it was paid. Issue the invoice first, then a receipt once the money arrives - this tool can turn an invoice into a receipt in one click, marked paid in full.'),
 ('Do I need to show tax on a receipt?','If you charged sales tax, VAT or GST, itemize it on the receipt too - a receipt that doubles as a tax receipt must show the tax. Pick your country and the tax is calculated and shown separately.'),
]
for _r in RECEIPTS:
    _r['faqs'] = [_r['faqs'][0], _RECEIPT_FAQ_SHARED[0], _RECEIPT_FAQ_SHARED[1]]
    _r['items'] = IND_BY[_r['slug']]['items']


def receipt_page(rc):
    url = f"{BASE}/en/receipt/{rc['slug']}"
    pf = b64p(rc['items'], kind='receipt')
    cta = f'/en/receipt#p={pf}'
    schema = [
      {"@context":"https://schema.org","@type":"WebApplication","name":f"Free {rc['name']} Receipt Template","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in rc['faqs']]},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Receipt templates","item":f"{BASE}/en/receipt-templates"},
        {"@type":"ListItem","position":3,"name":f"{rc['name']} receipt","item":url}]},
    ]
    related = ''.join(f'<a href="/en/receipt/{o["slug"]}">{o["name"]} receipt</a>' for o in RECEIPTS if o['slug'] != rc['slug'])
    include = ''.join(f'<li>{x}</li>' for x in rc['include'])
    art = (f'<article class="art">'
      f'<p class="lead">{rc["lead"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Create your {rc["name"].lower()} receipt &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/receipt">Open a blank receipt</a></div>'
      f'<h2>What a {rc["name"].lower()} receipt should include</h2><ul>{include}</ul>'
      f'<h2>Example {rc["name"].lower()} receipt</h2>'
      f'<p>A typical set of line items &mdash; click the button to open it as a receipt (marked paid, with the amount paid and a PAID stamp), then change the details and the payment method.</p>'
      f'{example_table(rc["items"])}'
      f'<p>{rc["terms"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Use this {rc["name"].lower()} receipt &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/invoice/{rc["slug"]}">Need an invoice instead?</a></div>'
      f'<h2>Related receipt templates</h2><div class="relgrid">{related}</div>'
      f'</article>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      f'<span class="ey">Free - No sign-up - {rc["name"]} receipt</span>'
      f'<h1>Free {rc["name"]} Receipt Template</h1>'
      f'<p>{rc["desc"]}</p></div></div></section>')
    crumb = f'<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/receipt-templates">Receipt templates</a> &rsaquo; {rc["name"]}</nav>'
    parts = [head(rc['title'], rc['desc'], url, schema), CRUMB_CSS, HEADER, crumb, hero, art, faq_html(rc['faqs']), FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


# Country x (receipt | credit note) pages. Tax metadata (region, currency, rate,
# province) is reused from COUNTRIES; only the doc-specific copy differs.
CM = {c['region']: c for c in COUNTRIES}

COUNTRY_RECEIPTS = [
 dict(region='us', slug='us-sales-tax', h1='US Sales Tax Receipt Template',
  title='US Sales Tax Receipt Template - Free Payment Receipt PDF (No Sign-Up)',
  desc='A free US receipt template showing sales tax paid. Confirm a payment, show the tax and a PAID stamp, and download a PDF - no sign-up. Letter, USD.',
  lead='Give a customer a receipt that shows the sales tax they paid. Set your state rate, confirm the amount paid and the method, and download a professional PDF with a PAID stamp - free, no account.',
  reqs=['Your business name and contact details','A receipt number and the <b>date of payment</b>','Who paid (&ldquo;Received From&rdquo;)','What was paid for, with <b>sales tax</b> shown separately','The <b>amount paid</b>, the payment method, and a PAID indication'],
  faqs=[('Does a US receipt need to show sales tax?','If you charged sales tax, show it on the receipt as well as the invoice - the customer needs it for their records and you need it for your sales-tax filing. Set your state rate and it is itemized separately.'),
        ('Is a receipt the same as a sales receipt?','Yes - a sales receipt confirms a completed payment. It shows what was bought, the sales tax, the total paid and the method.')]),
 dict(region='uk', slug='uk-vat', h1='UK VAT Receipt Template',
  title='UK VAT Receipt Template - Free Payment Receipt PDF (No Sign-Up)',
  desc='A free UK VAT receipt template. Shows your VAT number, the VAT paid at 20% / 5% / 0%, and the gross amount in GBP, with a PAID stamp. No sign-up. A4.',
  lead='Give a customer a VAT receipt - proof of payment that shows the VAT they paid and your VAT number. Download a professional PDF with a PAID stamp, free and no account.',
  reqs=['Your business name and <b>VAT registration number</b>','A receipt number and the <b>date of payment</b>','Who paid','A description, with the <b>VAT rate and amount</b> per rate','The total excluding VAT, the VAT, and the gross amount <b>paid</b> in GBP'],
  faqs=[('What is a VAT receipt?','A VAT receipt is proof of payment that also shows the VAT charged and your VAT number, so a VAT-registered customer can reclaim the VAT. It must itemize the VAT rate and amount.'),
        ('Can a receipt double as a VAT invoice?','For smaller amounts a VAT receipt can serve the same purpose if it shows your VAT number, the date, a description and the VAT. For larger sales issue a full VAT invoice.')]),
 dict(region='au', slug='australia-gst', h1='Australian GST Receipt Template',
  title='Australian GST Receipt Template - Free Payment Receipt PDF (No Sign-Up)',
  desc='A free Australian receipt template showing GST paid. Shows your ABN, GST at 10%, the amount paid and a PAID stamp, in AUD. No sign-up. A4.',
  lead='Give a customer a receipt that shows the GST they paid and your ABN. Confirm the amount paid and the method, and download a professional PDF with a PAID stamp - free, no account.',
  reqs=['Your business name and your <b>ABN</b>','A receipt number and the <b>date of payment</b>','Who paid','A description, with the <b>GST (10%)</b> shown or a statement that the total includes GST','The <b>amount paid</b>, the method, and a PAID indication'],
  faqs=[('Does an Australian receipt show GST?','Yes - if you are registered for GST, show the GST (or state that the total includes GST) and your ABN, so the customer has a valid record for their own GST credits.'),
        ('Is this a tax invoice or a receipt?','A receipt confirms payment; a tax invoice requests or documents the sale. A receipt that shows your ABN and the GST can serve as proof of a paid, GST-inclusive sale.')]),
 dict(region='ca', slug='canada-gst-hst', h1='Canada GST/HST Receipt Template',
  title='Canada GST/HST Receipt Template - Free Payment Receipt PDF (No Sign-Up)',
  desc='A free Canadian receipt template showing GST/HST paid by province. Shows your GST/HST number, the tax and a PAID stamp, in CAD. No sign-up. Letter.',
  lead='Give a customer a receipt that shows the GST/HST they paid and your registration number. Pick the province for the correct rate, confirm the amount paid, and download a professional PDF with a PAID stamp - free, no account.',
  reqs=['Your business name and your <b>GST/HST number</b>','A receipt number and the <b>date of payment</b>','Who paid','A description, with the <b>GST/HST</b> (and PST/QST where it applies) by province','The <b>amount paid</b>, the method, and a PAID indication'],
  faqs=[('Does a Canadian receipt need the GST/HST number?','Yes - once registered, show your GST/HST number and the tax amount on receipts so customers can claim their input tax credits.'),
        ('How is the tax set for my province?','Pick your province and the correct GST, HST, PST or QST is applied - for example HST in Ontario, GST plus PST in BC.')]),
]

COUNTRY_CREDITS = [
 dict(region='us', slug='us', h1='US Credit Memo Template',
  title='US Credit Memo Template - Free Credit Note PDF (No Sign-Up)',
  desc='A free US credit memo template to cancel or reduce an invoice. References the original invoice, reverses sales tax, and downloads as a PDF - no sign-up. Letter, USD.',
  lead='Issue a credit memo to cancel or reduce an invoice you already sent - for a return, an overcharge or a discount. It references the original invoice and reverses the sales tax. Download a professional PDF, free and no account.',
  reqs=['Your business details, as on the original invoice','The words &ldquo;Credit Memo&rdquo;, a number and the date','The <b>original invoice number</b> it relates to','The lines being credited, with the <b>sales tax reversed</b>','The total credit, and whether it is refunded or applied to a future invoice'],
  faqs=[('What is a credit memo?','A credit memo (the US term for a credit note) reduces or cancels an amount a customer owes on an invoice you already issued. It references the original invoice and reverses the tax.'),
        ('Does it reverse sales tax?','Yes - the sales tax charged on the original lines is reversed on the credit memo at the same rate, so your books balance.')]),
 dict(region='uk', slug='uk-vat', h1='UK VAT Credit Note Template',
  title='UK VAT Credit Note Template - Free Credit Note PDF (No Sign-Up)',
  desc='A free UK VAT credit note template. Reverses VAT at the original rate, references the original invoice and shows your VAT number, in GBP. No sign-up. A4.',
  lead='Issue a VAT credit note to correct or cancel a VAT invoice. It reverses the VAT at the rate originally charged, references the original invoice and shows your VAT number. Download a professional PDF, free and no account.',
  reqs=['Your business name and <b>VAT registration number</b>','A unique credit note number and the date','The <b>original invoice number</b> it relates to','The lines being credited, with the <b>VAT reversed</b> at the original rate','The total credit excluding VAT, the VAT, and the gross in GBP'],
  faqs=[('What must a UK VAT credit note show?','Your VAT number, a unique number, the date, the original invoice reference, a description, and the VAT reversed at the rate originally charged. Keep it for your VAT records.'),
        ('How does it affect my VAT return?','A VAT credit note reduces the output VAT you declared on the original invoice. Record it against the period in which it is issued.')]),
 dict(region='au', slug='australia-adjustment-note', h1='Australian GST Adjustment Note Template',
  title='Australian Adjustment Note (GST Credit Note) Template - Free PDF',
  desc='A free Australian adjustment note template - the GST credit note used to reduce or cancel a tax invoice. Reverses GST, shows your ABN, in AUD. No sign-up. A4.',
  lead='Issue an adjustment note - the Australian term for a GST credit note - to reduce or cancel a tax invoice. It reverses the GST, references the original tax invoice and shows your ABN. Download a professional PDF, free and no account.',
  reqs=['Your business name and your <b>ABN</b>','That it is an <b>adjustment note</b>, a number and the date','The <b>original tax invoice</b> it adjusts','The lines being credited, with the <b>GST (10%) reversed</b>','The total adjustment in AUD'],
  faqs=[('What is an adjustment note?','In Australia a GST credit note is called an adjustment note. It reduces or cancels a tax invoice - for a return, cancellation or price change - and reverses the GST.'),
        ('When do I issue one?','When the price of a taxable sale changes after you issued the tax invoice (a return, cancellation or discount). It references the original tax invoice and reverses the GST.')]),
 dict(region='ca', slug='canada-gst-hst', h1='Canada GST/HST Credit Note Template',
  title='Canada GST/HST Credit Note Template - Free Credit Note PDF (No Sign-Up)',
  desc='A free Canadian credit note template. Reverses GST/HST (and PST/QST) by province, references the original invoice and shows your GST/HST number, in CAD. No sign-up.',
  lead='Issue a credit note to reduce or cancel a Canadian invoice. It reverses the GST/HST at your province&rsquo;s rate, references the original invoice and shows your GST/HST number. Download a professional PDF, free and no account.',
  reqs=['Your business name and your <b>GST/HST number</b>','A unique credit note number and the date','The <b>original invoice number</b> it relates to','The lines being credited, with the <b>GST/HST reversed</b> by province','The total credit in CAD'],
  faqs=[('Does it reverse GST/HST?','Yes - the GST/HST (and PST/QST where it applies) charged on the original invoice is reversed on the credit note at your province&rsquo;s rate.'),
        ('Do I show my GST/HST number?','Yes - as on the original invoice, so the customer can adjust their input tax credits.')]),
]


def country_doc_page(d, kind, tool, hub_slug, hub_name):
    """Generic country x document-type landing page (kind = receipt | credit)."""
    m = CM[d['region']]
    url = f"{BASE}/en/{tool}/{d['slug']}"
    pf = b64p(m['items'], kind=kind, region=d['region'], tax_rate=m.get('tax_rate'), prov=m.get('prov'))
    cta = f'/en/{tool}#p={pf}'
    schema = [
      {"@context":"https://schema.org","@type":"WebApplication","name":d['h1'],"applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":m['cur']},"url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":qq,"acceptedAnswer":{"@type":"Answer","text":aa}} for qq,aa in d['faqs']]},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":hub_name,"item":f"{BASE}/en/{hub_slug}"},
        {"@type":"ListItem","position":3,"name":d['h1'],"item":url}]},
    ]
    doc_word = 'receipt' if kind == 'receipt' else ('adjustment note' if d['region'] == 'au' and kind == 'credit' else ('credit memo' if d['region'] == 'us' and kind == 'credit' else 'credit note'))
    peers = COUNTRY_RECEIPTS if kind == 'receipt' else COUNTRY_CREDITS
    related = ''.join(f'<a href="/en/{tool}/{o["slug"]}">{o["h1"].replace(" Template","")}</a>' for o in peers if o['slug'] != d['slug'])
    reqs = ''.join(f'<li>{x}</li>' for x in d['reqs'])
    openline = ('open it as a receipt (marked paid, with a PAID stamp)' if kind == 'receipt'
                else 'open it as a credit note referencing your original invoice')
    art = (f'<article class="art">'
      f'<p class="lead">{d["lead"]}</p>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Create a {m["name"]} {doc_word} &rarr;</a>'
      f'<a class="lpbtn gh" href="/en/{tool}">Open a blank {doc_word}</a></div>'
      f'<h2>What a {m["name"]} {doc_word} must include</h2><ul>{reqs}</ul>'
      f'<h2>Example ({m["taxname"]} at {m["rate"]:g}%)</h2>'
      f'<p>A typical set of lines with {m["taxname"]}. Click the button to {openline}, already set to {m["name"]} &mdash; change the details and your {m["taxname"].split("/")[0]} number.</p>'
      f'{country_example_table(m)}'
      f'<div class="note">Tax rules vary. The calculation here is an aid &mdash; confirm your obligations with your accountant or tax authority.</div>'
      f'<div class="lpcta"><a class="lpbtn pri" href="{cta}">Use this {m["name"]} {doc_word} &rarr;</a></div>'
      f'<h2>{doc_word.title()}s for other countries</h2><div class="relgrid">{related}</div>'
      f'</article>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      f'<span class="ey">Free - No sign-up - {m["name"]} - {m["taxname"]}</span>'
      f'<h1>Free {d["h1"]}</h1>'
      f'<p>{d["desc"]}</p></div></div></section>')
    crumb = f'<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/{hub_slug}">{hub_name}</a> &rsaquo; {m["name"]}</nav>'
    parts = [head(d['title'], d['desc'], url, schema), CRUMB_CSS, HEADER, crumb, hero, art, faq_html(d['faqs']), FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


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
      <a href="/en/estimate-templates">Quote templates</a>
      <a href="/en/receipt-templates">Receipt templates</a>
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
      '<p>All of these open the same free invoice generator &mdash; the difference is the starting line items. Tax (US sales tax, UK VAT, Australian GST, Canadian GST/HST) and currency switch to your country, and you can convert any invoice into a receipt, quote or credit note in one click.</p>'
      '<p>Need to quote a client before the work starts? See the <a href="/en/estimate-templates">quote &amp; estimate templates</a>. To confirm a payment, see the <a href="/en/receipt-templates">receipt templates</a>.</p></article>')
    alldocs = f'<div class="alldocs"><h2>All free documents</h2><div class="row">{docs}</div></div>'
    ccards = ''.join(f'<a class="dcard" href="/en/invoice/{c["slug"]}"><h3>{c["name"]}</h3><p>{c["taxname"]} invoice &mdash; correct tax, currency, paper size and tax-ID label.</p><span class="go">Open template &rarr;</span></a>' for c in COUNTRIES)
    country_sec = f'<div class="alldocs" style="padding-bottom:6px"><h2>Invoices by country &amp; tax</h2></div><div class="dgrid" style="padding-top:4px">{ccards}</div>'
    crcards = ''.join(f'<a class="dcard" href="/en/credit-note/{cr["slug"]}"><h3>{cr["h1"].replace(" Template","")}</h3><p>Cancel or reduce an invoice and reverse the {CM[cr["region"]]["taxname"]}.</p><span class="go">Open template &rarr;</span></a>' for cr in COUNTRY_CREDITS)
    credit_sec = f'<div class="alldocs" style="padding-bottom:6px"><h2>Credit notes by country &amp; tax</h2></div><div class="dgrid" style="padding-top:4px">{crcards}</div>'
    parts = [head(title, desc, url, schema), CRUMB_CSS, HEADER, crumb, hero, css, f'<div class="dgrid">{cards}</div>', country_sec, credit_sec, alldocs, art, FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)

def quote_hub_page():
    url = f"{BASE}/en/estimate-templates"
    title = 'Free Quote & Estimate Templates by Profession - PDF (No Sign-Up)'
    desc = 'Free quote and estimate templates for freelancers, consultants, designers, developers, photographers, contractors and more. Fill in and download a PDF - no sign-up.'
    schema = [
      {"@context":"https://schema.org","@type":"CollectionPage","name":"Free Quote & Estimate Templates by Profession","url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Quote templates","item":url}]},
    ]
    cards = ''.join(f'<a class="dcard" href="/en/estimate/{q["slug"]}"><h3>{q["name"]}</h3><p>{q["lead"][:120]}&hellip;</p><span class="go">Open template &rarr;</span></a>' for q in QUOTES)
    docs = ''.join(f'<a href="{u}">{t}</a>' for u, t in DOC_LINKS)
    css = ('<style>.dgrid{max-width:1180px;margin:0 auto;padding:12px 20px 30px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}'
      '.dcard{display:block;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;padding:20px 20px 16px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);transition:.15s}'
      '.dcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}.dcard h3{margin:0 0 6px;font-size:16px}.dcard p{margin:0 0 12px;font-size:13px;color:#5a6b7b;line-height:1.55}.dcard .go{font-size:13px;font-weight:800;color:var(--ac,#1766e6)}'
      '.alldocs{max-width:1180px;margin:0 auto;padding:4px 20px 40px}.alldocs h2{font-size:clamp(18px,3vw,22px);margin:0 0 12px}'
      '.alldocs .row{display:flex;flex-wrap:wrap;gap:8px}.alldocs .row a{font-size:13px;font-weight:700;color:#45607a;background:#f1f5fb;border:1px solid #dce5f0;border-radius:999px;padding:8px 14px;text-decoration:none}.alldocs .row a:hover{border-color:var(--ac,#1766e6);color:var(--ac,#1766e6)}</style>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      '<span class="ey">Free - No sign-up - US / UK / AU / CA</span>'
      '<h1>Free Quote &amp; Estimate Templates by Profession</h1>'
      '<p>Pick the template that matches your work. Each one opens as an editable estimate &mdash; with a valid-until date and an acceptance line &mdash; pre-filled with the line items your profession typically quotes. Change the details and download a clean PDF, no account.</p>'
      '</div></div></section>')
    crumb = '<nav class="crumb"><a href="/en/">Home</a> &rsaquo; Quote templates</nav>'
    art = ('<article class="art"><h2>Quote first, invoice later</h2>'
      '<p>These open the same free generator as an estimate. Add a valid-until date and an acceptance line, send it, and when the client approves, convert it to an invoice in one click &mdash; the same line items carry over. Looking to bill for completed work? See the <a href="/en/invoice-templates">invoice templates</a>; to confirm a payment, the <a href="/en/receipt-templates">receipt templates</a>.</p></article>')
    alldocs = f'<div class="alldocs"><h2>All free documents</h2><div class="row">{docs}</div></div>'
    parts = [head(title, desc, url, schema), CRUMB_CSS, HEADER, crumb, hero, css, f'<div class="dgrid">{cards}</div>', alldocs, art, FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


def receipt_hub_page():
    url = f"{BASE}/en/receipt-templates"
    title = 'Free Receipt Templates by Profession - Payment Receipt PDF (No Sign-Up)'
    desc = 'Free payment receipt templates for freelancers, consultants, designers, developers, photographers, contractors and more. Confirm a payment and download a PDF - no sign-up.'
    schema = [
      {"@context":"https://schema.org","@type":"CollectionPage","name":"Free Receipt Templates by Profession","url":url,"inLanguage":"en"},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Free BizDoc","item":f"{BASE}/en/"},
        {"@type":"ListItem","position":2,"name":"Receipt templates","item":url}]},
    ]
    cards = ''.join(f'<a class="dcard" href="/en/receipt/{r["slug"]}"><h3>{r["name"]}</h3><p>{r["lead"][:120]}&hellip;</p><span class="go">Open template &rarr;</span></a>' for r in RECEIPTS)
    docs = ''.join(f'<a href="{u}">{t}</a>' for u, t in DOC_LINKS)
    css = ('<style>.dgrid{max-width:1180px;margin:0 auto;padding:12px 20px 30px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}'
      '.dcard{display:block;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;padding:20px 20px 16px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);transition:.15s}'
      '.dcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}.dcard h3{margin:0 0 6px;font-size:16px}.dcard p{margin:0 0 12px;font-size:13px;color:#5a6b7b;line-height:1.55}.dcard .go{font-size:13px;font-weight:800;color:var(--ac,#1766e6)}'
      '.alldocs{max-width:1180px;margin:0 auto;padding:4px 20px 40px}.alldocs h2{font-size:clamp(18px,3vw,22px);margin:0 0 12px}'
      '.alldocs .row{display:flex;flex-wrap:wrap;gap:8px}.alldocs .row a{font-size:13px;font-weight:700;color:#45607a;background:#f1f5fb;border:1px solid #dce5f0;border-radius:999px;padding:8px 14px;text-decoration:none}.alldocs .row a:hover{border-color:var(--ac,#1766e6);color:var(--ac,#1766e6)}</style>')
    hero = ('<section class="hero"><div class="in"><div class="htext">'
      '<span class="ey">Free - No sign-up - US / UK / AU / CA</span>'
      '<h1>Free Receipt Templates by Profession</h1>'
      '<p>Pick the template that matches your work. Each opens as a receipt &mdash; the amount paid, the payment method and a PAID stamp &mdash; pre-filled with the line items your profession bills for. Change the details and download a clean PDF, no account.</p>'
      '</div></div></section>')
    crumb = '<nav class="crumb"><a href="/en/">Home</a> &rsaquo; Receipt templates</nav>'
    art = ('<article class="art"><h2>Proof of payment, in seconds</h2>'
      '<p>A receipt confirms a payment was received. Issue your invoice first, then a receipt when the money arrives &mdash; or turn an invoice into a receipt in one click, marked paid in full. Need to request payment instead? See the <a href="/en/invoice-templates">invoice templates</a>, or to quote first, the <a href="/en/estimate-templates">quote templates</a>.</p></article>')
    alldocs = f'<div class="alldocs"><h2>All free documents</h2><div class="row">{docs}</div></div>'
    rcards = ''.join(f'<a class="dcard" href="/en/receipt/{r["slug"]}"><h3>{CM[r["region"]]["name"]}</h3><p>{CM[r["region"]]["taxname"]} receipt &mdash; shows the tax paid and your tax-ID, with a PAID stamp.</p><span class="go">Open template &rarr;</span></a>' for r in COUNTRY_RECEIPTS)
    country_sec = f'<div class="alldocs" style="padding-bottom:6px"><h2>Receipts by country &amp; tax</h2></div><div class="dgrid" style="padding-top:4px">{rcards}</div>'
    parts = [head(title, desc, url, schema), CRUMB_CSS, HEADER, crumb, hero, css, f'<div class="dgrid">{cards}</div>', country_sec, alldocs, art, FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


os.makedirs(os.path.join(OUT, 'invoice'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'estimate'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'receipt'), exist_ok=True)
for rc in RECEIPTS:
    with open(os.path.join(OUT, 'receipt', rc['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(receipt_page(rc))
    print('wrote en/receipt/%s.html' % rc['slug'])
with open(os.path.join(OUT, 'receipt-templates.html'), 'w', encoding='utf-8') as f:
    f.write(receipt_hub_page())
print('wrote en/receipt-templates.html')
# Country x receipt / credit-note pages
os.makedirs(os.path.join(OUT, 'credit-note'), exist_ok=True)
for d in COUNTRY_RECEIPTS:
    with open(os.path.join(OUT, 'receipt', d['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(country_doc_page(d, 'receipt', 'receipt', 'receipt-templates', 'Receipt templates'))
    print('wrote en/receipt/%s.html' % d['slug'])
for d in COUNTRY_CREDITS:
    with open(os.path.join(OUT, 'credit-note', d['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(country_doc_page(d, 'credit', 'credit-note', 'invoice-templates', 'Invoice templates'))
    print('wrote en/credit-note/%s.html' % d['slug'])
for q in QUOTES:
    with open(os.path.join(OUT, 'estimate', q['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(quote_page(q))
    print('wrote en/estimate/%s.html' % q['slug'])
with open(os.path.join(OUT, 'estimate-templates.html'), 'w', encoding='utf-8') as f:
    f.write(quote_hub_page())
print('wrote en/estimate-templates.html')
for ind in INDUSTRIES:
    with open(os.path.join(OUT, 'invoice', ind['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(industry_page(ind))
    print('wrote en/invoice/%s.html' % ind['slug'])
for c in COUNTRIES:
    with open(os.path.join(OUT, 'invoice', c['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(country_page(c))
    print('wrote en/invoice/%s.html' % c['slug'])
with open(os.path.join(OUT, 'invoice-templates.html'), 'w', encoding='utf-8') as f:
    f.write(hub_page())
print('wrote en/invoice-templates.html')

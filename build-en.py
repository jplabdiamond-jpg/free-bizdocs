#!/usr/bin/env python3
# Generates the English tool pages under /en/ from one template.
# Usage: python3 build-en.py   (run from ~/seikyu-hub-demo)
import json, os, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'en')
V = datetime.date.today().strftime('%Y%m%d') + 'g'  # bump suffix on each JS/asset change to bust browser cache
BASE = 'https://free-bizdocs.com'

PAGES = [
 dict(slug='invoice', kind='invoice', ja='/invoice', title='Free Invoice Generator - Create & Download a PDF Invoice (No Sign-Up)',
  desc='Create a professional invoice in seconds and download it as a PDF - free, no account needed. US sales tax, UK VAT, Australian GST (tax invoice) and Canadian GST/HST supported.',
  h1='Free Invoice Generator', ey='Free - No sign-up - US / UK / AU / CA',
  lead='Enter your business, your client and the line items - tax is calculated automatically for your country and the PDF is ready to download. Nothing you type is stored on our servers.',
  tags=['No sign-up','Sales tax / VAT / GST','Net 30 &amp; due dates','Instant PDF','Share by link']),
 dict(slug='estimate', kind='quote', ja='/quote', title='Free Estimate & Quote Generator - Download a PDF Quote (No Sign-Up)',
  desc='Create a professional estimate or quotation as a PDF in seconds - free, no account. Includes a valid-until date, tax for US / UK / AU / CA and a customer acceptance line.',
  h1='Free Estimate &amp; Quote Generator', ey='Free - No sign-up - Estimate / Quote / Quotation',
  lead='Build a clear estimate or quote with line items, tax, a validity date and a signature line for acceptance. Convert it to an invoice with one click once the job is approved.',
  tags=['No sign-up','Valid-until date','Acceptance line','Convert to invoice','Instant PDF']),
 dict(slug='receipt', kind='receipt', ja='/receipt', title='Free Receipt Generator - Create a Payment Receipt PDF (No Sign-Up)',
  desc='Create a receipt for a payment received and download it as a PDF - free, no account. Shows the amount paid, payment method, date and tax (sales tax, VAT, GST or GST/HST).',
  h1='Free Receipt Generator', ey='Free - No sign-up - Paid-in-full receipt',
  lead='Issue a clean receipt for cash, card, cheque or bank-transfer payments. The PDF shows the amount paid, the date, the payment method and a PAID stamp.',
  tags=['No sign-up','Payment method','PAID stamp','Tax itemised','Instant PDF']),
 dict(slug='purchase-order', kind='po', ja='/purchase-order', title='Free Purchase Order Template - Create a PO PDF Online (No Sign-Up)',
  desc='Create a purchase order with PO number, vendor, ship-to address, delivery date and itemised lines - free PDF, no account. US / UK / AU / CA tax handled automatically.',
  h1='Free Purchase Order Generator', ey='Free - No sign-up - PO number - Ship To',
  lead='Send suppliers a clear purchase order: PO number, vendor, ship-to address, required delivery date, itemised lines and the order total.',
  tags=['No sign-up','PO number','Ship-to address','Delivery date','Instant PDF']),
 dict(slug='packing-slip', kind='delivery', ja='/delivery', title='Free Packing Slip & Delivery Note Template - PDF Download (No Sign-Up)',
  desc='Create a packing slip or delivery note listing the items shipped, quantities, PO number and ship-to address, with a signature line for proof of delivery. Free PDF, no account.',
  h1='Free Packing Slip &amp; Delivery Note Generator', ey='Free - No sign-up - No prices - Signature line',
  lead='List what is in the shipment - without prices - plus the ship-to address, PO or order reference and a received-by signature line for proof of delivery.',
  tags=['No sign-up','No prices shown','PO / order ref.','Received-by signature','Instant PDF']),
]

ARTICLES = {
 'invoice': '''<p class="lead">An invoice is the document you send to request payment for goods or services. This free invoice generator builds a clean, professional PDF with everything an accounts-payable team expects: a unique invoice number, issue and due dates, itemised lines, tax, the total due and your payment details.</p>
<h2>What to include on an invoice</h2>
<ul><li><b>Your business name, address and contact details</b> - and your tax ID where required (VAT number in the UK, ABN in Australia, GST/HST number in Canada).</li><li><b>The word &ldquo;Invoice&rdquo;, a unique sequential number and the issue date</b></li><li><b>The client&rsquo;s name and address</b> (&ldquo;Bill To&rdquo;)</li><li><b>Line items</b> with description, quantity, unit price and amount</li><li><b>Subtotal, tax and total</b> - shown per tax rate where more than one applies</li><li><b>Payment terms, due date and how to pay</b> (bank details, routing / sort code / BSB, etc.)</li></ul>
<h2>Country-specific rules this tool handles</h2>
<ul><li><b>United States</b> - there is no federal invoice standard; sales tax depends on your state and the type of service. Set a rate per line or mark items exempt. &ldquo;Net 30&rdquo; is the most common payment term.</li><li><b>United Kingdom</b> - VAT-registered businesses must show their VAT registration number, the VAT rate (20%, 5% or 0%) and the VAT amount per rate, plus the total VAT in GBP.</li><li><b>Australia</b> - a <b>tax invoice</b> must show the words &ldquo;Tax Invoice&rdquo;, your ABN, the date, a description, the GST amount (10%) and, for sales of $1,000 or more, the buyer&rsquo;s identity. The title switches to &ldquo;Tax Invoice&rdquo; automatically when you enter an ABN and charge GST.</li><li><b>Canada</b> - choose your province and GST, HST, PST or QST are applied at the correct rates; your GST/HST number is printed on the invoice.</li></ul>
<div class="note">Tax rules change and vary by state, province and industry. The calculations here are an aid - confirm your obligations with your accountant or tax authority.</div>
<h2>How to create a free invoice</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country, then enter your business details (saved in your browser for next time)</span></div><div class="step"><span class="n">2</span><span class="t">Add the client, invoice date and payment terms</span></div><div class="step"><span class="n">3</span><span class="t">Add line items - tax and totals update live in the preview</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF, or create a share link to send instead of an attachment</span></div></div>''',
 'estimate': '''<p class="lead">An estimate gives a customer an approximate price before work starts; a quote (or quotation) is a fixed price valid for a set period. Both use the same layout - this tool names the document to match your region (&ldquo;Estimate&rdquo; in the US and Canada, &ldquo;Quotation&rdquo; in the UK, &ldquo;Quote&rdquo; in Australia).</p>
<h2>What a good estimate or quote includes</h2>
<ul><li>Your business details and the customer&rsquo;s name (&ldquo;Prepared For&rdquo;)</li><li>A number, the date and a <b>&ldquo;valid until&rdquo;</b> date</li><li>Itemised scope of work with quantities and unit prices</li><li>Tax shown separately so the customer sees the final total</li><li>Terms (deposit, exclusions, payment schedule) and an <b>acceptance signature</b> line</li></ul>
<h2>Estimate vs quote vs proposal</h2>
<p>Most small businesses use the terms interchangeably, but a quote is generally treated as a firm price the customer can accept, while an estimate is a best guess that may change. A proposal adds the approach, timeline and qualifications. Whatever you call it, state clearly what is included, what is not, and how long the price is valid.</p>
<h2>How to create a free quote</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Add the customer, date and &ldquo;valid until&rdquo; date</span></div><div class="step"><span class="n">3</span><span class="t">List the work with quantities and prices; add terms if needed</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF - and convert it to an invoice when the job is approved</span></div></div>''',
 'receipt': '''<p class="lead">A receipt is proof that a payment was received. Customers need it for expense claims and bookkeeping; you need a copy for your records. This generator produces a simple, professional receipt PDF with everything both sides expect.</p>
<h2>What to include on a receipt</h2>
<ul><li>Your business name, address and tax ID (where applicable)</li><li>A receipt number and the date of payment</li><li>Who paid (&ldquo;Received From&rdquo;)</li><li>What was paid for - itemised lines, tax and total</li><li>The <b>payment method</b> (cash, card, cheque, bank transfer) and a &ldquo;paid&rdquo; indication</li></ul>
<h2>Receipt vs invoice</h2>
<p>An invoice asks for payment; a receipt confirms it. If you issued an invoice first, create the receipt from it with one click - the lines and customer are carried over and the document is marked as paid in full.</p>
<h2>How to create a free receipt</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the customer, receipt date and payment method</span></div><div class="step"><span class="n">3</span><span class="t">Add what was paid for</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF or send it as a share link</span></div></div>''',
 'purchase-order': '''<p class="lead">A purchase order (PO) is issued by the buyer to a supplier to confirm what is being ordered, at what price, and where and when it should be delivered. Once the supplier accepts it, the PO number is referenced on their invoice and packing slip so the three documents can be matched.</p>
<h2>What to include on a purchase order</h2>
<ul><li>Your company details (the buyer) and a unique <b>PO number</b></li><li>The <b>vendor</b> name and address</li><li>The <b>ship-to</b> address and required delivery date</li><li>Itemised lines with quantities and agreed unit prices</li><li>Tax and the order total, plus any terms (payment terms, delivery instructions)</li><li>An authorisation signature line</li></ul>
<h2>How to create a free purchase order</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your company details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the vendor, the ship-to address and the delivery date</span></div><div class="step"><span class="n">3</span><span class="t">Add the items, quantities and prices</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF and send it to the supplier</span></div></div>''',
 'packing-slip': '''<p class="lead">A packing slip (US) or delivery note (UK / Australia) travels with the goods and lists exactly what was shipped. It does not show prices - that information belongs on the invoice. The recipient checks the contents against the slip and signs it as proof of delivery.</p>
<h2>What to include on a packing slip</h2>
<ul><li>Your business details and a packing-slip or delivery-note number</li><li>The customer&rsquo;s billing details and the <b>ship-to</b> address</li><li>The <b>PO or order number</b> so the shipment can be matched to the order</li><li>Each item with the quantity shipped</li><li>Ship date and a <b>received-by / signature</b> line</li></ul>
<h2>Packing slip vs invoice</h2>
<p>The packing slip confirms what was physically delivered; the invoice requests payment. Create both from the same details - enter the items once, then switch documents under the preview.</p>
<h2>How to create a free packing slip</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the customer, ship-to address and order reference</span></div><div class="step"><span class="n">3</span><span class="t">List the items and quantities shipped</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF and include it with the shipment</span></div></div>''',
}

FAQS = {
 'invoice': [('Is it really free, with no sign-up?','Yes. You can create and download invoices without an account. To keep the service fast for everyone, the free tool allows 2 PDFs per hour per network.'),
  ('Is my data stored anywhere?','No. The invoice content is never sent to our servers - the PDF is generated in your browser. Only your own business details are kept in your browser local storage so you do not have to retype them.'),
  ('Does it support VAT, GST and sales tax?','Yes. Pick United States (a sales tax rate you set), United Kingdom (VAT 20% / 5% / 0% / exempt), Australia (GST 10% / GST-free) or Canada (GST / HST / PST / QST by province). Tax is itemised per rate on the PDF.'),
  ('What paper size is the PDF?','US and Canada use Letter (8.5 x 11 in). UK and Australia use A4.'),
  ('Can I turn an estimate into an invoice?','Yes. Under the preview, click the document you want - the same details are reused with a new number and today&rsquo;s date.'),
  ('Can I send the invoice without attaching a PDF?','Yes. &ldquo;Create a share link&rdquo; encodes the document in a URL. Your client opens it in a browser, sees the amount, due date and payment details, and can download the PDF.')],
 'estimate': [('Is a quote legally binding?','Rules vary by country and contract, but a quote accepted by the customer is generally treated as an agreed price for the stated scope and validity period. An estimate is usually not binding. Say which one you are issuing and include your terms.'),
  ('Can I convert the estimate to an invoice?','Yes. Under the preview, click &ldquo;Invoice&rdquo; - the line items, customer and your details are carried over and a new invoice number is assigned.'),
  ('Does the PDF include tax?','Yes. Tax is calculated for the selected country (sales tax, VAT, GST or GST/HST) and shown separately from the subtotal.'),
  ('Is it free?','Yes - no sign-up, 2 PDFs per hour per network on the free tool.')],
 'receipt': [('Do receipts need to show tax?','For VAT- or GST-registered businesses, yes - a receipt that doubles as a tax invoice must itemise the tax. In the US, show sales tax if you charged it.'),
  ('Can I make a receipt from an invoice?','Yes. On the invoice page, click &ldquo;Receipt&rdquo; under the preview. The content is reused and marked as paid.'),
  ('Is it free?','Yes - no sign-up, 2 PDFs per hour per network on the free tool.')],
 'purchase-order': [('Who issues a purchase order - the buyer or the seller?','The buyer. The supplier then quotes the PO number on their invoice and delivery documents.'),
  ('Is a purchase order a contract?','Once accepted by the supplier it generally forms a binding order for the stated goods, prices and terms. Add your terms in the Terms box if you need specific conditions.'),
  ('Is it free?','Yes - no sign-up, 2 PDFs per hour per network on the free tool.')],
 'packing-slip': [('Should a packing slip show prices?','Usually not. It lists items and quantities only; prices go on the invoice. This tool hides the price and tax columns on packing slips automatically.'),
  ('What is the difference between a packing slip and a delivery note?','They serve the same purpose. &ldquo;Packing slip&rdquo; is the common term in the US and Canada, &ldquo;delivery note&rdquo; in the UK and Australia - the title changes with the country you select.'),
  ('Is it free?','Yes - no sign-up, 2 PDFs per hour per network on the free tool.')],
}
INDEX_FAQ = [('Is Free BizDoc really free?','Yes. All five documents can be created and downloaded as PDFs without an account. The free tool allows 2 PDFs per hour per network.'),
 ('Which countries are supported?','United States (sales tax), United Kingdom (VAT), Australia (GST / tax invoice) and Canada (GST / HST / PST / QST). Currency, paper size, date format and tax-ID labels switch automatically.'),
 ('Where is my data stored?','Nowhere on our side. Documents are generated in your browser. Your own business details are kept in your browser local storage only.')]

def faq_ld(faq):
    return json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}, ensure_ascii=False)

def head(p, url):
    app = json.dumps({"@context":"https://schema.org","@type":"WebApplication","name":p['h1'].replace('&amp;','&'),"applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"url":url,"inLanguage":"en"})
    faqj = faq_ld(FAQS.get(p['slug'], INDEX_FAQ))
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<title>{p["title"]}</title>\n<meta name="description" content="{p["desc"]}">\n'
      f'<link rel="canonical" href="{url}">\n'
      f'<link rel="alternate" hreflang="en" href="{url}">\n'
      f'<link rel="alternate" hreflang="ja" href="{BASE}{p["ja"]}">\n'
      f'<link rel="alternate" hreflang="x-default" href="{url}">\n'
      '<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
      '<meta property="og:type" content="website">\n'
      '<meta property="og:site_name" content="Free BizDoc">\n'
      '<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="ja_JP">\n'
      f'<meta property="og:title" content="{p["title"]}">\n<meta property="og:description" content="{p["desc"]}">\n'
      f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{BASE}/og.jpg">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
      '<link rel="stylesheet" href="/suite.css?v=20261017d">\n'
      f'<script type="application/ld+json">{app}</script>\n'
      f'<script type="application/ld+json">{faqj}</script>\n'
      '</head>\n<body>')

# Fallback header (no-JS). siteheader-en.js replaces it with the full shared
# header (nav + language switch + login/account auth), matching the JA site.
HEADER = ('<header class="hdr"><div class="in">\n'
  '  <a class="brand" href="/en/" style="text-decoration:none"><img src="/logo.png" alt="Free BizDoc" style="height:30px;width:auto;display:block"></a>\n'
  '  <span class="sp"></span>\n'
  '  <a class="pro" href="/?lang=ja" lang="ja" title="Japanese version">日本語</a>\n'
  '</div></header>\n<nav id="docnav-en" aria-label="Documents"></nav>')

def hero(p):
    tags = ''.join('<span class="tag"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg>%s</span>' % t for t in p['tags'])
    return ('<section class="hero"><div class="in"><div class="htext">\n'
      f'  <span class="ey">{p["ey"]}</span>\n  <h1>{p["h1"]}</h1>\n  <p>{p["lead"]}</p>\n'
      f'  <div class="tags">{tags}</div>\n</div></div></section>')

def faq_html(faq):
    qs = ''.join(f'<div class="q"><h3>{q}</h3><p>{a}</p></div>' for q,a in faq)
    return f'<div class="faqwrap"><div class="faq"><h2>Frequently asked questions</h2>{qs}</div></div>'

def tool(p):
    return '''<div class="wrap" id="toolwrap" data-kind="%s">
  <div class="card pad">
    <div class="themeseg" id="themeseg"></div>
    <div class="regseg" id="regseg"><span class="rlb">Country</span><button type="button" data-region="us">&#127482;&#127480; United States</button><button type="button" data-region="uk">&#127468;&#127463; United Kingdom</button><button type="button" data-region="au">&#127462;&#127482; Australia</button><button type="button" data-region="ca">&#127464;&#127462; Canada</button></div>
    <div class="seg" id="seg"><button data-kind="invoice">Invoice</button><button data-kind="quote">Estimate / Quote</button><button data-kind="delivery">Packing Slip</button><button data-kind="po">Purchase Order</button><button data-kind="receipt">Receipt</button></div>

    <details id="co-details">
      <summary>Your business (saved in this browser for next time)<svg class="chev" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></summary>
      <div class="body">
        <label class="fl">Business name<input id="co-name" placeholder="Acme Design Studio LLC"></label>
        <div class="grid2">
          <label class="fl"><span id="co-taxid-lb">Tax ID (optional)</span><input id="co-taxid"></label>
          <label class="fl">Email (optional)<input id="co-email" placeholder="you@example.com"></label>
        </div>
        <div class="grid2">
          <label class="fl">Phone (optional)<input id="co-phone" placeholder="+1 555 123 4567"></label>
          <label class="fl">Logo (optional)<span class="filebtn" id="co-logo-btn">Choose image&hellip;</span><input type="file" id="co-logo" accept="image/png,image/jpeg" class="filein"></label>
        </div>
        <label class="fl">Address (optional)<textarea id="co-addr" rows="2"></textarea></label>
        <label class="fl" id="bank-wrap">Payment details - printed on invoices (optional)<textarea id="co-bank" rows="3"></textarea><span class="hint">Bank name, routing / sort code / BSB / transit number, account number, or "Pay by card at ...".</span></label>
        <div id="imgrow" style="display:flex;gap:14px;align-items:center;margin-top:2px"></div>
        <div style="font-size:11.5px;color:var(--faint,#93a3b5);margin-top:4px">PNG or JPEG. The logo is processed in your browser only and never uploaded.</div>
      </div>
    </details>

    <div class="fs">
      <span class="lg">Recipient &amp; dates</span>
      <label class="fl"><span id="party-lb">Bill To (name)</span><input id="cl-name" placeholder="Client or company name"></label>
      <div class="grid2">
        <label class="fl">Address (optional)<textarea id="cl-addr" rows="2"></textarea></label>
        <label class="fl">Email (optional)<input id="cl-email" placeholder="client@example.com"></label>
      </div>
      <label class="fl" id="shipto-wrap">Ship To (optional - leave blank to use the address above)<textarea id="ship-to" rows="2" placeholder="Receiving address"></textarea></label>
      <div class="grid2">
        <label class="fl"><span id="num-lb">Invoice #</span><input id="doc-no" placeholder="INV-0001"></label>
        <label class="fl">PO / Reference # (optional)<input id="ref-no" placeholder="PO-2048"></label>
      </div>
      <div class="grid2">
        <label class="fl"><span id="issue-lb">Invoice date</span><input type="date" id="issue"></label>
        <label class="fl" id="due-wrap"><span id="due-lb">Due date</span><input type="date" id="due"></label>
      </div>
      <div class="grid2">
        <label class="fl" id="terms-wrap">Payment terms<select id="terms"></select></label>
        <label class="fl" id="method-wrap">Payment method<select id="method"><option>Bank transfer</option><option>Credit / debit card</option><option>Cash</option><option>Cheque</option><option>PayPal</option><option>Other</option></select></label>
      </div>
    </div>

    <div class="fs">
      <span class="lg">Line items</span>
      <div class="grid2" style="margin-bottom:10px">
        <label class="fl" id="taxrate-wrap">Sales tax rate (%%)<input id="tax-rate" inputmode="decimal" placeholder="0 (leave 0 if not charging sales tax)"></label>
        <label class="fl" id="prov-wrap">Province / territory<select id="ca-prov"></select></label>
      </div>
      <div class="items">
        <div class="hd"><span>Description</span><span>Qty</span><span id="th-price">Unit price (<span id="cur-lb">USD</span>)</span><span id="th-tax">Tax</span><span></span></div>
        <div id="rows"></div>
      </div>
      <button class="addrow" id="addrow" type="button">&#65291; Add line</button>
    </div>

    <label class="fl">Notes (optional)<textarea id="notes" rows="2" placeholder="Thank you for your business. Please reference the invoice number with your payment."></textarea></label>
    <label class="fl">Terms &amp; conditions (optional)<textarea id="terms-text" rows="2" placeholder="Late payments are subject to a 1.5%% monthly fee."></textarea></label>
  </div>

  <div class="card right">
    <div class="pvhd"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>Preview (exactly what the PDF will look like)</div>
    <div class="pvbody">
      <div id="livepv" class="livepv"></div>
      <div id="convbar" class="convbar"></div>
      <div class="cta">
        <button class="btn" id="make"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 3v12M8 11l4 4 4-4M4 21h16"/></svg> Download PDF (free)</button>
        <div class="remain" id="remain"></div>
        <div class="limitbox" id="limitbox"></div>
        <div class="msg" id="msg"></div>
        <div id="savebox" class="savebox"></div>
        <div id="sharebox" class="sharebox"></div>
        <button type="button" id="clearbtn" style="display:block;margin:10px auto 0;background:none;border:none;color:#8294a8;font-size:12.5px;cursor:pointer;text-decoration:underline">Clear and start a new document</button>
      </div>
    </div>
  </div>
</div>''' % p['kind']

FOOTER = '''<footer class="ft"><div class="in">
  <div class="cols">
    <div>
      <div class="brand"><img src="/logo.png" alt="Free BizDoc" style="height:26px;width:auto;display:block;filter:brightness(0) invert(1)"></div>
      <p>Free, no-sign-up business document generator. Invoices, estimates, receipts, purchase orders and packing slips as clean PDFs - generated in your browser, never stored on our servers.</p>
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
      <a href="/en/blog">Blog</a>
      <a href="/en/pricing">Pricing &amp; PRO</a>
      <a href="/en/account">Account</a>
      <a href="/?lang=ja" lang="ja">日本語</a>
      <a href="/en/contact">Contact</a>
      <a href="/en/privacy">Privacy policy</a>
    </div>
  </div>
  <div class="bot">
    Tax calculations are provided as an aid only. Confirm your obligations with your accountant or tax authority.<br>
    &copy; 2026 Free BizDoc
  </div>
</div></footer>'''

def page(p):
    url = f"{BASE}/en/{p['slug']}"
    parts = [head(p, url), HEADER, hero(p), tool(p),
      f'<article class="art">{ARTICLES[p["slug"]]}</article>', faq_html(FAQS[p['slug']]), FOOTER,
      f'<script src="/en/en.js?v={V}"></script>',
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)

def index():
    p = dict(slug='', ja='/', title='Free BizDoc - Free Invoice, Estimate, Receipt, Purchase Order & Packing Slip Generator (No Sign-Up)',
      desc='Create professional business documents as PDFs in seconds - free, no account. Invoices, estimates & quotes, receipts, purchase orders and packing slips with US sales tax, UK VAT, Australian GST and Canadian GST/HST.',
      h1='Business documents, free. No sign-up.', ey='Invoice - Estimate - Receipt - Purchase Order - Packing Slip',
      lead='Pick a document, choose your country and fill in the details - tax, currency, paper size and dates are handled for the US, UK, Australia and Canada. Download the PDF or send a share link. Nothing is stored on our servers.',
      tags=['No sign-up','US / UK / AU / CA','Sales tax - VAT - GST','Share by link','Instant PDF'])
    url = f"{BASE}/en/"
    cards = [('/en/invoice','Invoice','Itemised invoice with tax, due date, payment terms and your bank details.'),
             ('/en/estimate','Estimate / Quote','Priced scope of work with a valid-until date and an acceptance line.'),
             ('/en/receipt','Receipt','Proof of payment with amount paid, method and a PAID stamp.'),
             ('/en/purchase-order','Purchase Order','PO number, vendor, ship-to address and delivery date.'),
             ('/en/packing-slip','Packing Slip / Delivery Note','Items and quantities shipped - no prices - with a received-by line.')]
    grid = ''.join(f'<a class="dcard" href="{u}"><h3>{t}</h3><p>{d}</p><span class="go">Create free &rarr;</span></a>' for u,t,d in cards)
    css = ('<style>.dgrid{max-width:1180px;margin:0 auto;padding:10px 20px 40px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}'
      '.dcard{display:block;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;padding:22px 22px 18px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);transition:.15s}'
      '.dcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}.dcard h3{margin:0 0 6px;font-size:17px}.dcard p{margin:0 0 12px;font-size:13.5px;color:#5a6b7b;line-height:1.55}.dcard .go{font-size:13px;font-weight:800;color:var(--ac,#1766e6)}'
      '.regions{max-width:1180px;margin:0 auto;padding:0 20px 30px;font-size:13.5px;color:#5a6b7b}.regions b{color:#13263b}</style>')
    regions = ('<div class="regions"><b>Built for your country:</b> &#127482;&#127480; United States - sales tax by line, Net 30, Letter paper &middot; '
      '&#127468;&#127463; United Kingdom - VAT 20/5/0%, VAT number, A4 &middot; &#127462;&#127482; Australia - GST 10%, ABN, "Tax Invoice" &middot; '
      '&#127464;&#127462; Canada - GST/HST/PST/QST by province, GST/HST number</div>')
    art = ('<article class="art"><p class="lead">Free BizDoc started in Japan as a free generator for Japanese business documents. The English edition follows the formats actually used in English-speaking countries rather than translating the Japanese ones: a US-style invoice with sales tax, a UK VAT invoice, an Australian tax invoice and a Canadian GST/HST invoice, plus estimates, receipts, purchase orders and packing slips.</p>'
      '<h2>How it works</h2><div class="steps"><div class="step"><span class="n">1</span><span class="t">Pick a document and your country</span></div><div class="step"><span class="n">2</span><span class="t">Enter your business once - it is remembered in your browser</span></div><div class="step"><span class="n">3</span><span class="t">Add the recipient and line items; the live preview is the actual PDF</span></div><div class="step"><span class="n">4</span><span class="t">Download, or send a share link instead of an attachment</span></div></div></article>')
    nav = ('<script>(function(){var h=document.getElementById("docnav-en");if(!h)return;var D=[["/en/invoice","Invoice"],["/en/estimate","Estimate / Quote"],["/en/receipt","Receipt"],["/en/purchase-order","Purchase Order"],["/en/packing-slip","Packing Slip / Delivery Note"]];'
      'var s=document.createElement("style");s.textContent="#docnav-en{background:#fff;border-bottom:1px solid #e6ebf2;overflow-x:auto}#docnav-en .t{display:flex;gap:8px;width:max-content;padding:12px 16px;margin:0 auto}#docnav-en a{font-size:13px;font-weight:700;color:#5a6b80;text-decoration:none;padding:8px 15px;border-radius:999px;background:#f1f5fb;border:1px solid #dce5f0;white-space:nowrap}";document.head.appendChild(s);'
      'h.innerHTML="<div class=\\"t\\">"+D.map(function(d){return "<a href=\\""+d[0]+"\\">"+d[1]+"</a>";}).join("")+"</div>";})();</script>')
    hd = head(p, url).replace('%s/en/' % BASE, url)
    # Hero with the "fill in → PDF" demo. On mobile the demo is ordered right
    # after the headline so it lands in the first view.
    tags = ''.join('<span class="tag"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6 9 17l-5-5"/></svg>%s</span>' % t for t in p['tags'])
    hero_css = ('<style>'
      '.hero-en .in{max-width:1180px;margin:0 auto;padding:46px 20px 42px;display:grid;grid-template-columns:1.04fr .96fr;gap:40px;align-items:center}'
      '.hero-en .herodemo{width:100%;max-width:560px;margin:0 auto}'
      '.hero-en #demoframe{width:100%;height:560px;border:0;display:block;background:transparent;overflow:hidden}'
      '@media(max-width:860px){.hero-en .in{grid-template-columns:1fr;gap:22px}}'
      '@media(max-width:600px){'
      '.hero-en .in{display:flex;flex-direction:column;gap:0;padding:26px 20px 24px}'
      '.hero-en .htext{display:contents}'
      '.hero-en .ey{order:1;margin-bottom:10px}'
      '.hero-en h1{order:2;margin:0 0 10px;font-size:clamp(23px,6.4vw,32px)}'
      '.hero-en .herodemo{order:3;margin:4px 0 14px}'
      '.hero-en p{order:4}'
      '.hero-en .tags{order:5;margin-top:16px}'
      '.hero-en #demoframe{height:430px}'
      '}</style>')
    hero_html = ('<section class="hero hero-en"><div class="in">'
      '<div class="htext">'
      f'<span class="ey">{p["ey"]}</span><h1>{p["h1"]}</h1><p>{p["lead"]}</p>'
      f'<div class="tags">{tags}</div>'
      '</div>'
      '<div class="herodemo"><iframe id="demoframe" src="/en/demo-embed" title="See an invoice created in seconds" loading="lazy" scrolling="no"></iframe></div>'
      '</div></section>')
    demo_script = '<script>(function(){var f=document.getElementById("demoframe");if(!f)return;window.addEventListener("message",function(e){try{var d=e.data;if(d&&d.t==="demoH"&&d.h>200&&d.h<2200){f.style.height=d.h+"px";}}catch(_){}});})();</script>'
    parts = [hd, hero_css, HEADER, hero_html, css, f'<div class="dgrid">{grid}</div>', regions, art, faq_html(INDEX_FAQ), FOOTER, nav, demo_script, f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)

os.makedirs(OUT, exist_ok=True)
for p in PAGES:
    with open(os.path.join(OUT, p['slug'] + '.html'), 'w', encoding='utf-8') as f: f.write(page(p))
    print('wrote en/%s.html' % p['slug'])
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f: f.write(index())
print('wrote en/index.html')

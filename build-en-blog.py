#!/usr/bin/env python3
# Generates the English blog: /en/blog index + /en/blog/<slug> article pages.
# English-market content (not translations of the Japanese blog). Inline gradient
# hero (no external image needed), suite.css + shared siteheader-en.js header.
# Usage: python3 build-en-blog.py   (run from ~/seikyu-hub-demo)
import os, json, datetime, html as _html

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'en', 'blog')
BASE = 'https://free-bizdocs.com'
V = datetime.date.today().strftime('%Y%m%d') + 'r'  # bump on siteheader/asset change to bust cache

# Brand accent per category (hero gradient)
CAT_COLOR = {
  'Invoicing': ('#1766e6', '#36b0f0'),
  'Getting paid': ('#0f8a5f', '#13a06f'),
  'Quoting': ('#7a39c4', '#a46be0'),
  'Tax': ('#0e7490', '#2bb3c0'),
  'Purchasing': ('#b4530f', '#e0863a'),
  'Industries': ('#9d2b6b', '#d45a9a'),
  'Guides': ('#13263b', '#2f5a8a'),
}

# ---- Articles (English-market, adapted — never translations of the JA blog) ----
ARTICLES = [
 dict(
  slug='how-to-write-an-invoice', cat='Invoicing', tool='/en/invoice',
  title='How to Write an Invoice (US, UK, Australia &amp; Canada)',
  desc='A clear, country-by-country guide to writing a professional invoice — what to include, how tax works, and how to get paid faster.',
  date='2026-10-19',
  body='''
<p class="lead">An invoice is the document you send to ask a client to pay for goods or services. A clear, complete invoice gets paid faster and keeps your bookkeeping clean. This guide covers exactly what to put on an invoice and how the details differ across the US, UK, Australia and Canada.</p>

<h2>What every invoice should include</h2>
<p>Wherever you are, a professional invoice has the same backbone:</p>
<ul>
<li><b>The word &ldquo;Invoice&rdquo;</b> and a unique invoice number (sequential, e.g. INV-0001).</li>
<li><b>Your business details</b> — name, address, email or phone, and your tax ID where you have one.</li>
<li><b>The client&rsquo;s name and address</b> (the &ldquo;Bill To&rdquo;).</li>
<li><b>Issue date</b> and <b>due date</b> (or payment terms such as &ldquo;Net 30&rdquo;).</li>
<li><b>Line items</b> — a description, quantity and unit price for each.</li>
<li><b>Subtotal, tax and total</b>, with tax shown separately.</li>
<li><b>How to pay</b> — bank details, card link or other instructions.</li>
</ul>

<h2>How tax and format differ by country</h2>
<p>The structure is the same, but the tax model and a few required fields change:</p>
<ul>
<li><b>United States</b> — there is no federal invoice standard. Sales tax depends on your state and what you&rsquo;re selling, so set a rate per line or mark items exempt. &ldquo;Net 30&rdquo; is the most common term, and Letter paper is standard.</li>
<li><b>United Kingdom</b> — if you&rsquo;re VAT-registered you must show your VAT registration number, the VAT rate (20%, 5% or 0%) and the VAT amount, with totals in GBP on A4.</li>
<li><b>Australia</b> — a compliant <b>tax invoice</b> must show the words &ldquo;Tax Invoice&rdquo;, your ABN, the date, a description and the GST (10%). For sales of $1,000 or more it must also show the buyer&rsquo;s identity.</li>
<li><b>Canada</b> — charge GST, HST, PST or QST depending on the province, and show your GST/HST number on the invoice.</li>
</ul>
<div class="note">Tax rules vary by state, province and industry and change over time. Treat the figures as an aid and confirm your obligations with your accountant or tax authority.</div>

<h2>Tips to get paid faster</h2>
<ul>
<li>Send the invoice the day the work is done — speed sets the tone.</li>
<li>Put the due date in plain language (&ldquo;Due by 18 Nov 2026&rdquo;), not just &ldquo;Net 30&rdquo;.</li>
<li>Make paying easy: include bank details or a payment link right on the invoice.</li>
<li>Use a clear, sequential numbering scheme so both sides can reference it.</li>
<li>Keep a copy. If you issued an estimate first, carry the details straight over to the invoice.</li>
</ul>

<h2>Create one in under a minute</h2>
<p>You don&rsquo;t need accounting software to send a clean invoice. Our <a href="/en/invoice">free invoice generator</a> builds a professional PDF with the right tax model for your country — pick US, UK, Australia or Canada and the currency, paper size, date format and tax fields are handled for you. Nothing you type is stored on our servers.</p>
''',
  faqs=[
   ('Do I need to be a registered business to send an invoice?', 'No. Sole traders and freelancers invoice under their own name. Include a tax ID (VAT number, ABN, GST/HST number) only if you are registered for it.'),
   ('What invoice number should I start with?', 'Any sequential scheme works — many people start at INV-0001 or INV-2026-001. The key is that numbers are unique and never repeat, so each invoice can be referenced unambiguously.'),
   ('Do I have to charge tax?', 'It depends on where you are and whether you are registered. In the US you charge sales tax based on your state; in the UK, Australia and Canada you charge VAT/GST/HST only if registered. When in doubt, check with your tax authority.'),
  ],
  related=[('/en/estimate','Free estimate &amp; quote generator'),('/en/receipt','Free receipt generator'),('/en/blog/payment-terms-explained','Net 30 and payment terms explained')],
 ),
 dict(
  slug='estimate-vs-quote', cat='Quoting', tool='/en/estimate',
  title='Estimate vs Quote vs Proposal: What&rsquo;s the Difference?',
  desc='Estimate, quote and proposal are often used interchangeably — but they mean different things to a client. Here is how they differ and when to use each.',
  date='2026-10-19',
  body='''
<p class="lead">&ldquo;Estimate&rdquo;, &ldquo;quote&rdquo; and &ldquo;proposal&rdquo; are often used as if they mean the same thing. They don&rsquo;t — and the word you choose sets your client&rsquo;s expectations about whether the price can change. Here&rsquo;s the practical difference.</p>

<h2>Estimate</h2>
<p>An <b>estimate</b> is your best guess at the cost before the work is fully defined. It&rsquo;s a ballpark figure that can reasonably move as the scope becomes clearer. Use an estimate when a client asks &ldquo;roughly how much?&rdquo; and you can&rsquo;t yet commit to an exact price. Always say clearly that it&rsquo;s an estimate and note what could change it.</p>

<h2>Quote (quotation)</h2>
<p>A <b>quote</b> is a fixed price, valid for a stated period, that the client can accept. Once accepted, you&rsquo;re generally expected to honour it — so quote only when the scope is clear. A good quote includes an itemised breakdown, the total, a <b>&ldquo;valid until&rdquo;</b> date and any terms (deposit, exclusions). In the UK this is often called a &ldquo;quotation&rdquo;; in Australia and North America, a &ldquo;quote&rdquo;.</p>

<h2>Proposal</h2>
<p>A <b>proposal</b> goes further than price. It explains your understanding of the problem, your approach, timeline, deliverables and why you&rsquo;re the right choice — with pricing usually near the end. Proposals suit larger or competitive jobs where you&rsquo;re selling the approach, not just the number.</p>

<h2>Which should you send?</h2>
<ul>
<li><b>Client just wants a ballpark</b> → estimate.</li>
<li><b>Scope is clear and you can commit to a price</b> → quote.</li>
<li><b>Bigger job, you need to sell your approach</b> → proposal (often with a quote inside).</li>
</ul>
<p>Whatever you call it, be explicit about what&rsquo;s included, what isn&rsquo;t, and how long the price holds. That one habit prevents most pricing disputes.</p>

<h2>From quote to invoice in one click</h2>
<p>When a client accepts, you shouldn&rsquo;t have to retype everything. Build your estimate or quote with our <a href="/en/estimate">free estimate &amp; quote generator</a> — it adds a valid-until date and an acceptance line, and you can convert it straight into an <a href="/en/invoice">invoice</a> once the job is approved, keeping the same details with a new number.</p>
''',
  faqs=[
   ('Is a quote legally binding?', 'A quote is generally treated as a firm offer the client can accept, so you are usually expected to honour the price for its stated validity period. An estimate is a best guess that can change. Always state which one you are giving.'),
   ('How long should a quote be valid?', 'Set a &ldquo;valid until&rdquo; date that reflects how stable your costs are — 14 to 30 days is common. After that, you are free to re-quote if prices have moved.'),
   ('What is the difference between a quote and an invoice?', 'A quote proposes a price before the work; an invoice requests payment after (or as) the work is delivered. Many tools let you convert an accepted quote into an invoice so you do not re-enter the details.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/purchase-order','Free purchase order template')],
 ),
 dict(
  slug='payment-terms-explained', cat='Getting paid', tool='/en/invoice',
  title='Net 30 and Payment Terms Explained (With Examples)',
  desc='What &ldquo;Net 30&rdquo; really means, how common payment terms compare, and how to choose terms that get you paid on time.',
  date='2026-10-19',
  body='''
<p class="lead">Payment terms tell your client when an invoice is due. Getting them right — and stating them clearly — is one of the simplest ways to get paid on time. Here&rsquo;s what the common terms mean and how to choose.</p>

<h2>What does &ldquo;Net 30&rdquo; mean?</h2>
<p><b>Net 30</b> means the full amount is due 30 days after the invoice date. &ldquo;Net&rdquo; refers to the full invoice amount; the number is the count of days. So an invoice dated 1 November with Net 30 is due by 1 December.</p>

<h2>Common payment terms at a glance</h2>
<ul>
<li><b>Due on receipt</b> — payment is expected immediately. Best for one-off or first-time clients.</li>
<li><b>Net 7 / Net 14</b> — due in 7 or 14 days. Good for keeping cash flow tight with smaller clients.</li>
<li><b>Net 30</b> — due in 30 days. The most common term for business-to-business work.</li>
<li><b>Net 60 / Net 90</b> — due in 60 or 90 days. Common with large companies, but hard on your cash flow.</li>
<li><b>2/10 Net 30</b> — a 2% discount if paid within 10 days, otherwise the full amount in 30. An early-payment incentive.</li>
</ul>

<h2>How to choose your terms</h2>
<ul>
<li><b>New or one-off client?</b> Ask for &ldquo;due on receipt&rdquo; or a deposit up front.</li>
<li><b>Ongoing B2B client?</b> Net 14 or Net 30 is standard and expected.</li>
<li><b>Cash flow matters?</b> Shorten the term or offer a small early-payment discount rather than waiting Net 60.</li>
<li><b>Large invoice?</b> Consider milestone billing — invoice in stages instead of one lump sum.</li>
</ul>

<h2>Make the due date impossible to miss</h2>
<p>Don&rsquo;t rely on the client to do the maths. Alongside &ldquo;Net 30&rdquo;, write the actual date: <i>&ldquo;Due by 1 December 2026.&rdquo;</i> State any late fee in your terms, and make paying easy with bank details or a payment link on the invoice itself.</p>

<h2>Set terms automatically</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you pick a term (Due on receipt, Net 7/14/30/45/60) and fills in the matching due date for you, in the right currency and format for the US, UK, Australia or Canada.</p>
''',
  faqs=[
   ('Does Net 30 mean 30 business days or calendar days?', 'Calendar days, counted from the invoice date, unless you explicitly state otherwise. To avoid any doubt, write the actual due date on the invoice.'),
   ('Can I charge a late fee?', 'Yes, if you state it in your terms before the work (for example, a 1.5% monthly fee on overdue balances). Rules on maximum rates vary by country and state, so check what applies to you.'),
   ('What is 2/10 Net 30?', 'It offers a 2% discount if the invoice is paid within 10 days; otherwise the full amount is due in 30 days. It is a way to encourage faster payment.'),
  ],
  related=[('/en/receipt','Free receipt generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/estimate','Free estimate &amp; quote generator')],
 ),
]

# Articles emitted as DRAFTS into en/blog/_drafts/ (the auto-publish pipeline
# publishes these one at a time, paced). Add future EN articles here.
DRAFTS = [
 dict(
  slug='free-invoice-template', cat='Invoicing', tool='/en/invoice',
  title='Free Invoice Templates (Word, Excel, Google Docs &amp; PDF)',
  desc='Where to get a free invoice template in Word, Excel, Google Docs or PDF — what a good one includes, and when an invoice generator beats a template.',
  date='2026-10-28',
  body='''
<p class="lead">A free invoice template saves you from rebuilding an invoice from scratch every time. You can find them for Word, Excel, Google Docs and PDF &mdash; but a template still leaves you to do the math and tax by hand, which is where a generator can save you time.</p>
<h2>Where to get a free invoice template</h2>
<ul>
<li><b>Word / Google Docs</b> &mdash; good for a clean, text-based invoice you type into.</li>
<li><b>Excel / Google Sheets</b> &mdash; handy because formulas can total the line items for you.</li>
<li><b>PDF</b> &mdash; a fixed layout you fill in and send; looks the most professional.</li>
</ul>
<p>Free BizDoc offers ready-to-edit templates by profession and country, and a generator that produces the PDF for you.</p>
<h2>What a good invoice template includes</h2>
<p>Whatever the format, make sure the template has your business details, the client, a unique invoice number and date, an itemised list with amounts, the tax, the total, and your payment terms and bank details.</p>
<h2>Template vs invoice generator</h2>
<p>A template is fine for the occasional invoice, but you do the tax math yourself and re-save a PDF each time. An <b>invoice generator</b> calculates the tax automatically (US sales tax, UK VAT, Australian GST, Canadian GST/HST), keeps your numbering tidy and exports a clean PDF in seconds &mdash; free and with no sign-up.</p>
<p><a href="/en/invoice">Create an invoice free</a>, or browse <a href="/en/invoice-templates">invoice templates by profession</a>.</p>
''',
  faqs=[
   ("Is there a free invoice template for Word, Excel or Google Docs?", "Yes. You can use a free template in any of those, or use Free BizDoc's generator, which fills in the layout and does the tax math for you and exports a PDF — no sign-up."),
   ("Should I use an invoice template or an invoice generator?", "A template is fine occasionally, but you calculate the tax and re-save a PDF yourself. A generator auto-calculates tax, keeps numbering tidy and exports the PDF in seconds."),
   ("Can I make an invoice in Google Docs?", "Yes, with a Google Docs template, but you type everything and work out the tax manually. A generator handles the totals and tax for you."),
  ],
  related=[('/en/invoice','Create an invoice'),('/en/invoice-templates','Invoice templates by profession'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='what-is-a-tax-invoice', cat='Tax', tool='/en/invoice',
  title='What Is a Tax Invoice? (US, UK, Australia &amp; Canada)',
  desc='A tax invoice shows the tax charged on a sale plus the seller&rsquo;s tax ID. Here is what makes an invoice a tax invoice and how the rules differ by country.',
  date='2026-10-28',
  body='''
<p class="lead">A <b>tax invoice</b> is an invoice that clearly shows the tax charged on a sale, along with the seller&rsquo;s tax registration number. Registered businesses issue tax invoices so the buyer can reclaim the tax and both sides have a proper record.</p>
<h2>What makes an invoice a &ldquo;tax invoice&rdquo;</h2>
<p>On top of the usual invoice details, a tax invoice shows the <b>tax amount</b> (often broken out per rate) and the seller&rsquo;s <b>tax ID</b> (VAT number, ABN, GST/HST number, etc.). That is what lets a registered buyer claim the tax back.</p>
<h2>By country</h2>
<ul>
<li><b>US</b> &mdash; an invoice showing <b>sales tax</b> by rate; there is no single national tax number.</li>
<li><b>UK</b> &mdash; a <b>VAT invoice</b> showing your VAT number and the VAT per rate.</li>
<li><b>Australia</b> &mdash; must carry the words <b>&ldquo;Tax invoice&rdquo;</b>, your ABN and the GST amount.</li>
<li><b>Canada</b> &mdash; shows <b>GST/HST</b> (and PST/QST where it applies) and your registration number.</li>
</ul>
<h2>Do you need to issue one?</h2>
<p>If you are registered for VAT/GST (or charging sales tax), you generally need to issue a tax invoice when you make a taxable sale. If you are not registered, you issue an ordinary invoice with no tax line.</p>
<p><a href="/en/invoice">Create a tax invoice free</a> &mdash; pick your country and the tax is built in.</p>
''',
  faqs=[
   ("What is the difference between an invoice and a tax invoice?", "A tax invoice additionally shows the tax charged and the seller&rsquo;s tax registration number, so a registered buyer can reclaim the tax. A plain invoice need not show those."),
   ("Do I need to issue a tax invoice?", "If you are registered for VAT/GST or charging sales tax, you generally must issue a tax invoice for taxable sales. If you are not registered, you issue an ordinary invoice with no tax."),
   ("What must a tax invoice show?", "The usual invoice details plus the tax amount (often per rate) and your tax ID — VAT number, ABN, or GST/HST number depending on the country."),
  ],
  related=[('/en/invoice','Create an invoice'),('/en/blog/uk-vat-invoice-requirements','UK VAT invoice requirements'),('/en/blog/australian-tax-invoice-requirements','Australian tax invoice requirements')],
 ),
 dict(
  slug='how-to-write-a-receipt', cat='Invoicing', tool='/en/receipt',
  title='How to Write a Receipt (With Examples)',
  desc='A receipt confirms a payment was made. Here is exactly what to put on one, how it differs from an invoice, and when you should issue a receipt.',
  date='2026-10-28',
  body='''
<p class="lead">A <b>receipt</b> is proof that a payment was made. You issue it <i>after</i> the customer pays, so both sides have a record. Writing one is simple once you know the handful of details it needs.</p>
<h2>What a receipt must show</h2>
<ul>
<li>The word <b>&ldquo;Receipt&rdquo;</b> and a receipt number/date.</li>
<li>Who issued it (your business) and who paid.</li>
<li>What the payment was for (a short description or the invoice it settles).</li>
<li>The <b>amount paid</b> and the <b>payment method</b> (cash, card, transfer).</li>
<li>Any tax, if you are registered and it applies.</li>
</ul>
<h2>Receipt vs invoice</h2>
<p>An <b>invoice</b> asks for payment; a <b>receipt</b> confirms it. You send an invoice to get paid, then issue a receipt once the money arrives. They often list the same items but do different jobs.</p>
<h2>When to issue a receipt</h2>
<p>It is good practice to give a receipt whenever a customer pays, and in some cases (cash payments, certain regulated sales) it may be expected. A clear receipt reduces disputes and helps the customer with their own records.</p>
<p><a href="/en/receipt">Create a receipt free</a> &mdash; add the amount paid and method, download the PDF, no sign-up.</p>
''',
  faqs=[
   ("What should a receipt include?", "The word &lsquo;Receipt&rsquo;, a number and date, who issued it and who paid, what the payment was for, the amount paid and the payment method, plus any tax that applies."),
   ("Is a receipt the same as an invoice?", "No. An invoice requests payment before it is made; a receipt confirms payment after it is received."),
   ("Do I have to give a receipt?", "It is good practice whenever someone pays, and for some payments (such as cash or certain regulated sales) it may be expected. It protects both sides with a clear record."),
  ],
  related=[('/en/receipt','Create a receipt'),('/en/blog/receipt-vs-invoice','Receipt vs invoice'),('/en/invoice','Create an invoice')],
 ),
 dict(
  slug='how-to-write-a-quote', cat='Quoting', tool='/en/estimate',
  title='How to Write a Quote (With a Free Template)',
  desc='A quote gives a client a fixed price before work starts. Here is what to include, how it differs from an estimate, and how to turn it into an invoice.',
  date='2026-10-28',
  body='''
<p class="lead">A <b>quote</b> (or quotation) gives a client a firm price for a job before any work starts. Unlike a rough estimate, a quote is a price you commit to, so it pays to be clear about exactly what is included.</p>
<h2>What to include in a quote</h2>
<ul>
<li>Your business details and the client&rsquo;s details.</li>
<li>A quote number and date, and a <b>valid-until date</b>.</li>
<li>An itemised scope of work with prices.</li>
<li>The total, and any tax if you are registered.</li>
<li>An acceptance line so the client can confirm.</li>
</ul>
<h2>Quote vs estimate</h2>
<p>An <b>estimate</b> is an approximate figure that can change; a <b>quote</b> is a fixed price the client can accept as-is. Use an estimate when the scope is uncertain and a quote when you can commit to the number.</p>
<h2>Set a valid-until date</h2>
<p>Prices and availability change, so put a valid-until date (commonly 30 days) on every quote. It protects you if costs move and nudges the client to decide.</p>
<h2>Turning a quote into an invoice</h2>
<p>Once the client accepts, you can convert the quote straight into an invoice without retyping it &mdash; same items, same figures, now a request for payment.</p>
<p><a href="/en/estimate">Create a quote free</a> &mdash; add a valid-until date and convert it to an invoice in one click.</p>
''',
  faqs=[
   ("What should a quote include?", "Your details and the client&rsquo;s, a quote number and date, a valid-until date, an itemised scope with prices, the total and any tax, plus an acceptance line."),
   ("What is the difference between a quote and an estimate?", "A quote is a fixed price the client can accept as-is; an estimate is an approximate figure that can change as the work becomes clearer."),
   ("How long should a quote be valid?", "Commonly 30 days. A valid-until date protects you if your costs change and encourages the client to decide."),
  ],
  related=[('/en/estimate','Create a quote'),('/en/blog/estimate-vs-quote','Estimate vs quote'),('/en/invoice','Create an invoice')],
 ),
 dict(
  slug='what-is-a-proforma-invoice', cat='Invoicing', tool='/en/proforma-invoice',
  title='What Is a Pro Forma Invoice? (With an Example)',
  desc='A pro forma invoice is a preliminary bill sent before the final invoice. Here is what it is for, what to put on it, and how it differs from a quote and a tax invoice.',
  date='2026-10-28',
  body='''
<p class="lead">A <b>pro forma invoice</b> is a preliminary bill you send <i>before</i> the real invoice &mdash; a good-faith estimate of what a sale will cost, laid out like a normal invoice. It tells the buyer exactly what to expect, but it is not a demand for payment and does not go in your books as a sale.</p>
<h2>When to use a pro forma invoice</h2>
<p>Pro forma invoices are most useful in three situations:</p>
<ul>
<li><b>Deposits and prepayment</b> &mdash; to request a deposit or full payment up front before you start work or ship goods.</li>
<li><b>Confirming a sale</b> &mdash; to give the buyer a document that looks like the final invoice so they can raise a purchase order or get internal approval.</li>
<li><b>Customs and importing</b> &mdash; shipping and customs agents often ask for a pro forma invoice to value goods before the commercial invoice exists.</li>
</ul>
<h2>What to put on it</h2>
<p>Use the same fields as a normal invoice, with one difference: label it clearly. Include your business details, the buyer, a description of the goods or services, quantities and prices, any tax, the total, and the words <b>&ldquo;Pro forma invoice&rdquo;</b> plus a note that it is not a tax invoice and not a demand for payment.</p>
<h2>Pro forma invoice vs quote vs tax invoice</h2>
<p>A <b>quote</b> is an offer of a price; a <b>pro forma invoice</b> presents that agreed price in invoice form, usually once the buyer intends to proceed; the <b>final (tax) invoice</b> is the real accounting document that records the sale and the tax. Only the final invoice is used for VAT/sales-tax and your accounts.</p>
<h2>Example</h2>
<p>A designer agrees a $1,200 project and asks for a 50% deposit. They send a pro forma invoice for $1,200 showing the deposit due now, so the client can pay and the designer can start. When the work is done, they issue the real invoice for the balance.</p>
<p>You can <a href="/en/proforma-invoice">create a pro forma invoice free</a> &mdash; no sign-up, download the PDF in seconds.</p>
''',
  faqs=[
   ("Is a pro forma invoice legally binding?", "No. A pro forma invoice is a good-faith estimate, not a demand for payment or a contract. The binding document is the final invoice (and whatever contract or purchase order sits behind it)."),
   ("Can you claim VAT or sales tax on a pro forma invoice?", "No. A pro forma invoice is not a tax invoice, so neither side uses it to charge or reclaim tax. You need the final (tax) invoice for that."),
   ("What is the difference between a pro forma invoice and a quote?", "A quote offers a price; a pro forma invoice presents that price in the layout of an invoice, usually once the buyer intends to go ahead or needs it for a deposit or customs."),
  ],
  related=[('/en/proforma-invoice','Create a pro forma invoice'),('/en/blog/estimate-vs-quote','Estimate vs quote'),('/en/invoice','Create an invoice')],
 ),
 dict(
  slug='invoice-vs-bill', cat='Invoicing', tool='/en/invoice',
  title='Invoice vs Bill: What&rsquo;s the Difference?',
  desc='&ldquo;Invoice&rdquo; and &ldquo;bill&rdquo; usually describe the same document from two sides of the deal. Here is what each term means and which one to use.',
  date='2026-10-28',
  body='''
<p class="lead">An <b>invoice</b> and a <b>bill</b> are usually the same document seen from two sides. The seller <i>issues an invoice</i> to request payment; the buyer <i>receives it as a bill</i> to pay. The paper is identical &mdash; the word just depends on who is holding it.</p>
<h2>The same document, two viewpoints</h2>
<p>When you send a client a request for payment, you call it an invoice. To that client it is a bill they owe. In accounting the same document sits in your <b>accounts receivable</b> (money owed to you) and in their <b>accounts payable</b> (money they owe).</p>
<h2>Why the words differ</h2>
<p>&ldquo;Invoice&rdquo; is the formal, business-to-business term and implies an itemised document with an invoice number, dates and payment terms. &ldquo;Bill&rdquo; is the everyday word, used for things you pay immediately or on receipt &mdash; a restaurant bill, a utility bill, a phone bill.</p>
<h2>Which should your document say?</h2>
<p>If you are a freelancer or business asking a client to pay, label it <b>Invoice</b>. It reads as professional, it is what accounting software and clients expect, and it carries the detail (number, due date, tax) that a plain &ldquo;bill&rdquo; often lacks.</p>
<h2>Invoice, bill, receipt &mdash; don&rsquo;t mix them up</h2>
<p>An invoice/bill <i>requests</i> payment; a <b>receipt</b> <i>confirms</i> payment after it is made. So you send an invoice, the client pays the bill, and you issue a receipt as proof.</p>
<p><a href="/en/invoice">Create a professional invoice free</a> &mdash; no account needed.</p>
''',
  faqs=[
   ("Is an invoice the same as a bill?", "Essentially yes. It is the same document from different sides: the seller issues an invoice, and the buyer receives it as a bill to pay."),
   ("Should my document say &lsquo;Invoice&rsquo; or &lsquo;Bill&rsquo;?", "Use &lsquo;Invoice&rsquo; for business-to-business payment requests. It is the standard, professional term and carries the number, due date and tax detail clients expect."),
   ("Is a bill the same as a receipt?", "No. A bill (invoice) asks for payment before it is made; a receipt confirms payment after it is received."),
  ],
  related=[('/en/invoice','Create an invoice'),('/en/blog/receipt-vs-invoice','Receipt vs invoice'),('/en/compare','Compare free invoice tools')],
 ),
 dict(
  slug='how-to-invoice-as-a-sole-trader-uk', cat='Invoicing', tool='/en/invoice',
  title='How to Invoice as a Sole Trader (UK)',
  desc='A plain-English guide to invoicing as a UK sole trader: what every invoice must show, when VAT applies, numbering, records and getting paid on time.',
  date='2026-10-28',
  body='''
<p class="lead">As a UK sole trader you invoice clients yourself &mdash; there is no special format required, but an invoice should carry a few standard details so it is clear, professional and ready for your Self Assessment. Here is what to include and where VAT fits in.</p>
<h2>What a sole trader invoice must show</h2>
<ul>
<li>Your name and, if you use one, your trading name.</li>
<li>The word <b>&ldquo;Invoice&rdquo;</b> and a <b>unique, sequential invoice number</b>.</li>
<li>The invoice date (and the date the goods/services were supplied).</li>
<li>The client&rsquo;s name and address.</li>
<li>A clear description of what you are charging for, with amounts.</li>
<li>The total due, your payment terms and how to pay (bank details).</li>
</ul>
<h2>Do you charge VAT?</h2>
<p>Only if you are <b>VAT-registered</b>. Registration is compulsory once your taxable turnover passes the VAT threshold (&pound;90,000), and optional below it. If you are registered, show your <b>VAT number</b> and the VAT per rate, and the invoice becomes a VAT invoice. If you are not registered, you simply do not add VAT &mdash; and you should not show a VAT number or imply VAT is included.</p>
<h2>Numbering and records</h2>
<p>Give every invoice a unique number in sequence (0001, 0002&hellip;) so none are missing or duplicated. Keep copies of your invoices and records: HMRC expects you to keep business records for your Self Assessment, generally for at least <b>5 years after the 31 January</b> submission deadline of the relevant tax year.</p>
<h2>Getting paid on time</h2>
<p>State clear terms (for example &ldquo;payment due within 14 days&rdquo;). UK businesses also have a statutory right to charge interest and a fixed recovery sum on late commercial payments, which you can mention in your terms to encourage prompt payment.</p>
<p><a href="/en/invoice">Create a UK invoice free</a> &mdash; add your details and download the PDF, no sign-up.</p>
''',
  faqs=[
   ("Do I need to charge VAT as a sole trader?", "Only if you are VAT-registered, which is required once your taxable turnover passes the &pound;90,000 threshold and optional below it. If you are not registered, do not add VAT or show a VAT number."),
   ("Do sole trader invoices need an invoice number?", "Yes. Each invoice should have a unique, sequential number so your records are complete and nothing is missing or duplicated."),
   ("How long should I keep my invoices?", "HMRC generally expects sole traders to keep business records for at least 5 years after the 31 January Self Assessment deadline for that tax year."),
  ],
  related=[('/en/invoice','Create an invoice'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer'),('/en/invoice/uk-vat','UK VAT invoice template')],
 ),
 dict(
  slug='independent-contractor-invoice', cat='Invoicing', tool='/en/invoice',
  title='How to Invoice as an Independent Contractor (US)',
  desc='How US independent contractors (1099) should invoice clients: what to include, whether to charge sales tax, W-9 vs invoice, and the 1099-NEC at year end.',
  date='2026-10-28',
  body='''
<p class="lead">As a US independent contractor you send clients an invoice to get paid. There is no official form &mdash; you just need a clear, itemised document with the right details so clients can pay you quickly and you can report the income at tax time.</p>
<h2>What to include</h2>
<ul>
<li>Your name or business name and contact details.</li>
<li><b>Invoice number</b> and invoice date.</li>
<li>The client&rsquo;s name and address.</li>
<li>A description of the work, hours or units, your rate and the total.</li>
<li>Payment terms (for example Net 15/Net 30) and how to pay.</li>
</ul>
<p>Do <b>not</b> print your Social Security Number on the invoice. If a client needs your taxpayer ID, give it on a <b>Form W-9</b> sent securely, not on every invoice.</p>
<h2>Do contractors charge sales tax?</h2>
<p>Usually not on services &mdash; most states do not tax professional services &mdash; but it <b>varies by state</b>, and selling physical goods can be taxable. If you are unsure whether your service is taxable where you operate, check your state&rsquo;s rules or a tax professional.</p>
<h2>W-9 vs invoice vs 1099</h2>
<p>These are three different things: the <b>W-9</b> is a one-time form giving the client your taxpayer details; the <b>invoice</b> is your request for payment for each job; the <b>1099-NEC</b> is the form the client files (and sends you) after year end if they paid you <b>$600 or more</b>. You still report all your income whether or not you receive a 1099.</p>
<h2>Getting paid faster</h2>
<p>Send the invoice promptly, keep terms short and clear, and number your invoices so nothing slips. A clean PDF with your payment details reduces back-and-forth.</p>
<p><a href="/en/invoice">Create a contractor invoice free</a> &mdash; no account, instant PDF.</p>
''',
  faqs=[
   ("Do independent contractors charge sales tax on invoices?", "Usually not on professional services, but it varies by state and taxable goods can be an exception. Check your state&rsquo;s rules if you are unsure."),
   ("Should I put my SSN on an invoice?", "No. Avoid putting your Social Security Number on invoices. If a client needs your taxpayer ID, provide it once on a Form W-9 sent securely."),
   ("What is the difference between a 1099 and an invoice?", "The invoice is your request for payment for a job. The 1099-NEC is the tax form a client files after year end if they paid you $600 or more."),
  ],
  related=[('/en/invoice','Create an invoice'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer'),('/en/invoice/us-sales-tax','US sales tax invoice template')],
 ),
 dict(
  slug='how-to-charge-a-late-payment-fee', cat='Getting paid', tool='/en/invoice',
  title='How to Charge a Late Payment Fee (With Wording)',
  desc='How to set and charge a late payment fee the right way: agree it up front, pick a fair amount, know your statutory rights, and use clear wording on the invoice.',
  date='2026-10-28',
  body='''
<p class="lead">A late payment fee nudges clients to pay on time and compensates you when they do not. To be enforceable it has to be <b>agreed up front</b> and reasonable &mdash; you cannot spring a surprise charge after the invoice is overdue.</p>
<h2>Set it out before you bill</h2>
<p>State your late fee in your terms and on the invoice itself <i>before</i> the work or the due date &mdash; for example in your payment terms and a line on the invoice footer. If the client never agreed to it, you generally cannot add it later.</p>
<h2>How much can you charge?</h2>
<p>Common choices are a <b>monthly percentage</b> (often 1&ndash;1.5% of the overdue balance per month) or a <b>flat fee</b>. Keep it reasonable: a fee that looks like a penalty rather than fair compensation can be unenforceable, and some places cap interest rates.</p>
<h2>Your statutory rights</h2>
<p>In the <b>UK</b>, the Late Payment of Commercial Debts Act lets businesses charge statutory interest (8% plus the Bank of England base rate) plus a fixed recovery sum on overdue B2B invoices, even without a clause. In the <b>US</b>, late fees are set by your contract and limited by state usury caps. Check what applies where you operate.</p>
<h2>Example wording</h2>
<p>Put a clear line in your terms, such as: <i>&ldquo;A late fee of 1.5% per month will be applied to balances not paid within 30 days of the invoice date.&rdquo;</i></p>
<h2>Apply it fairly</h2>
<p>Send a polite reminder first &mdash; most late payments are oversights. Keep the relationship intact: a reminder plus a clearly-stated fee usually gets you paid without having to enforce anything.</p>
<p><a href="/en/invoice">Create an invoice with your payment terms</a> &mdash; free, no sign-up.</p>
''',
  faqs=[
   ("How much late payment fee can I charge?", "A monthly rate of around 1&ndash;1.5% of the overdue balance, or a reasonable flat fee, is common. Keep it fair rather than punitive, and check any local interest-rate caps."),
   ("Can I charge a late fee without warning?", "Generally no. The fee has to be agreed in advance &mdash; stated in your terms and on the invoice before the due date. You usually cannot add it retroactively."),
   ("What wording should I use for a late fee?", "Something clear and specific, for example: &lsquo;A late fee of 1.5% per month applies to balances not paid within 30 days of the invoice date.&rsquo;"),
  ],
  related=[('/en/invoice','Create an invoice'),('/en/blog/payment-terms-explained','Payment terms explained'),('/en/blog/payment-reminder-email','Payment reminder email')],
 ),
 dict(
  slug='receipt-vs-invoice', cat='Invoicing', tool='/en/receipt',
  title='Receipt vs Invoice: What&rsquo;s the Difference?',
  desc='An invoice asks for payment; a receipt confirms it. Here is when to send each, what they must show, and how they work together.',
  date='2026-10-19',
  body='''
<p class="lead">An <b>invoice</b> requests payment; a <b>receipt</b> confirms a payment was made. They look similar and often list the same items, but they do different jobs at different moments. Here&rsquo;s how to tell them apart and use each correctly.</p>

<h2>Invoice: a request for payment</h2>
<p>You send an invoice <i>before</i> you&rsquo;ve been paid, to tell a client what they owe and by when. It shows an invoice number, the issue and due dates, itemised charges, tax, the total due and how to pay.</p>

<h2>Receipt: proof of payment</h2>
<p>You issue a receipt <i>after</i> payment, as proof the money changed hands. It shows who paid, what for, the amount, the date and the payment method — often with a &ldquo;Paid&rdquo; marking. Customers keep receipts for expense claims and bookkeeping; you keep a copy for your records.</p>

<h2>Side by side</h2>
<ul>
<li><b>Purpose</b> — invoice: ask for payment. Receipt: confirm payment.</li>
<li><b>Timing</b> — invoice: before payment. Receipt: after payment.</li>
<li><b>Key field</b> — invoice: amount due + due date. Receipt: amount paid + payment method.</li>
</ul>

<h2>Do you need both?</h2>
<p>Often, yes. For B2B work you typically send an invoice, then issue a receipt once it&rsquo;s paid. For an immediate cash or card sale, a receipt alone is usually enough. If you issued an invoice first, you can create the receipt from the same details in one step — marked paid in full.</p>

<h2>Create either one for free</h2>
<p>Use our <a href="/en/invoice">free invoice generator</a> to request payment, and the <a href="/en/receipt">free receipt generator</a> to confirm it — both as clean PDFs, with the right tax model for the US, UK, Australia or Canada.</p>
''',
  faqs=[
   ('Is a receipt the same as an invoice?', 'No. An invoice requests payment before it is made; a receipt confirms payment after it is made. They may list the same items but serve opposite purposes.'),
   ('Do I legally need to give a receipt?', 'Rules vary by country and sale type, but customers often need a receipt for expense claims or tax, and many businesses issue one by default. When registered for VAT/GST, specific receipt or tax-invoice rules may apply.'),
   ('Can I turn an invoice into a receipt?', 'Yes. Many tools let you reuse an invoice&rsquo;s details to produce a receipt marked paid in full, so you do not retype the line items.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/payment-terms-explained','Payment terms explained')],
 ),
 dict(
  slug='how-to-invoice-as-a-freelancer', cat='Invoicing', tool='/en/invoice',
  title='How to Invoice as a Freelancer (A Simple Guide)',
  desc='A practical, step-by-step guide to invoicing clients as a freelancer — what to include, how to set terms, and how to get paid on time.',
  date='2026-10-21',
  body='''
<p class="lead">Invoicing is how you actually get paid as a freelancer, yet it&rsquo;s the part most people wing. A clear, consistent invoice looks professional, avoids back-and-forth, and gets money into your account faster. Here&rsquo;s a simple system you can reuse for every client.</p>

<h2>Agree the terms before you start</h2>
<p>The best way to get paid on time is to set expectations up front. Before the work begins, confirm in writing: the scope and price, whether you bill hourly or a fixed fee, your payment terms (for example &ldquo;Net 14&rdquo; or &ldquo;due on receipt&rdquo;), and whether you require a deposit. A short email is enough &mdash; it just has to exist.</p>

<h2>What to put on a freelance invoice</h2>
<ul>
<li>The word <b>&ldquo;Invoice&rdquo;</b> and a unique number (INV-0001, INV-0002&hellip;).</li>
<li>Your name or business name, contact details and tax ID if you have one.</li>
<li>The client&rsquo;s name and billing address.</li>
<li>Issue date and a clear due date.</li>
<li>Line items &mdash; describe the work, with quantity/hours and rate.</li>
<li>Subtotal, any tax, and the total due.</li>
<li>How to pay: bank details or a payment link.</li>
</ul>

<h2>Should you charge tax?</h2>
<p>It depends where you and your client are. In the US, whether you charge sales tax depends on your state and whether services are taxable there. In the UK you only add VAT once you&rsquo;re VAT-registered. In Australia you charge GST once registered (required at $75,000 turnover), and in Canada GST/HST applies once registered. When in doubt, check with an accountant &mdash; and keep your invoice showing tax as a separate line.</p>

<h2>Getting paid on time</h2>
<p>Keep your terms short (14 days is common for freelancers), write the actual due date rather than only &ldquo;Net 14&rdquo;, send the invoice the day you finish, and make paying effortless with bank details or a link right on the invoice. A polite reminder a few days before the due date works better than chasing after it.</p>

<h2>Create a freelance invoice free</h2>
<p>Use our <a href="/en/invoice">free invoice generator</a> &mdash; no sign-up &mdash; to produce a clean PDF with your details, the right tax model for your country, and a due date. Freelancers in the US, UK, Australia and Canada are all supported.</p>
''',
  faqs=[
   ('How do I invoice as a freelancer without a company?', 'You can invoice as a sole trader or individual using your own name and address. You don&rsquo;t need a registered company &mdash; just a clear invoice with a number, your details, the client&rsquo;s details, the work, the total and how to pay.'),
   ('What payment terms should a freelancer use?', 'Net 14 or &ldquo;due on receipt&rdquo; are common for freelancers because they shorten the wait. Whatever you choose, state the actual due date on the invoice and agree it with the client before you start.'),
   ('Do freelancers charge tax on invoices?', 'Only when required where you operate &mdash; US sales tax depends on your state and service type; UK VAT, Australian GST and Canadian GST/HST apply once you&rsquo;re registered. Show any tax as a separate line.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/payment-terms-explained','Payment terms explained'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='what-is-a-purchase-order', cat='Purchasing', tool='/en/purchase-order',
  title='What Is a Purchase Order? (PO vs Invoice Explained)',
  desc='A plain-English explanation of purchase orders — what a PO is, how it differs from an invoice, and when to use one.',
  date='2026-10-21',
  body='''
<p class="lead">A <b>purchase order</b> (PO) is a document the <i>buyer</i> sends to a supplier to confirm an order: what they want, how much, at what price, and where and when to deliver it. It turns a verbal or email agreement into a clear, trackable record &mdash; and it&rsquo;s the first step in the &ldquo;three-way match&rdquo; that keeps buying under control.</p>

<h2>What a purchase order includes</h2>
<ul>
<li>A unique <b>PO number</b> and the order date.</li>
<li>The buyer&rsquo;s details and the <b>vendor</b> (supplier) details.</li>
<li>The <b>ship-to</b> address and required delivery date.</li>
<li>Line items with quantities and agreed unit prices.</li>
<li>Tax, the order total, and any terms.</li>
</ul>

<h2>Purchase order vs invoice</h2>
<p>They&rsquo;re easy to confuse because they list the same items, but they move in opposite directions. The <b>buyer issues the PO</b> to request goods or services. The <b>supplier issues the invoice</b> to request payment once the order is fulfilled. The supplier quotes the PO number on the invoice so both sides can match them.</p>

<h2>The three-way match</h2>
<p>Finance teams match three documents before paying: the <b>purchase order</b> (what was ordered), the <b>packing slip or delivery note</b> (what arrived) and the <b>invoice</b> (what&rsquo;s being charged). If all three agree, the invoice is approved. This is why quoting the PO number on every related document matters.</p>

<h2>When should a small business use POs?</h2>
<p>Even solo businesses benefit from POs for larger or recurring purchases: they prevent surprise charges, create a budget trail, and give you something to point to if an order is wrong. For one-off small buys a PO may be overkill &mdash; use judgement.</p>

<h2>Create a purchase order free</h2>
<p>Our <a href="/en/purchase-order">free purchase order template</a> builds a clean PO PDF with a number, vendor, ship-to address and delivery date &mdash; no sign-up. When the goods arrive, create a matching <a href="/en/packing-slip">packing slip</a> from the same details.</p>
''',
  faqs=[
   ('Who issues a purchase order, the buyer or the supplier?', 'The buyer issues the purchase order to request goods or services. The supplier later issues an invoice to request payment and quotes the PO number so the two can be matched.'),
   ('Is a purchase order legally binding?', 'Once the supplier accepts it, a PO generally forms a binding order for the stated goods, quantities, prices and terms. Add specific conditions in the terms section if you need them.'),
   ('What is the difference between a PO and an invoice?', 'A purchase order is the buyer&rsquo;s request to order; an invoice is the supplier&rsquo;s request for payment. The PO comes first; the invoice references its number.'),
  ],
  related=[('/en/purchase-order','Free purchase order template'),('/en/packing-slip','Free packing slip template'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='payment-reminder-email', cat='Getting paid', tool='/en/invoice',
  title='How to Write a Payment Reminder Email (Templates)',
  desc='Polite, effective payment reminder email templates — before the due date, on the day, and for overdue invoices — plus tips to get paid without awkwardness.',
  date='2026-10-21',
  body='''
<p class="lead">Chasing payment feels awkward, but most late invoices aren&rsquo;t refusals &mdash; they&rsquo;re forgotten. A short, friendly, well-timed email usually fixes it. Here are templates for each stage, from a gentle nudge to a firm final notice.</p>

<h2>Before you send anything</h2>
<p>Make sure the invoice was clear in the first place: a due date (not just &ldquo;Net 30&rdquo;), the amount, and easy payment options. Then follow a simple cadence &mdash; a reminder a few days before the due date, one on the day, and follow-ups at about one and two weeks overdue.</p>

<h2>1. Friendly reminder (a few days before due)</h2>
<p><i>Subject: Invoice INV-0042 &mdash; due 20 Nov</i><br>Hi [Name], just a quick note that invoice INV-0042 for $[amount] is due on [date]. Payment details are on the invoice (attached). Thanks so much &mdash; happy to answer any questions.</p>

<h2>2. On the due date</h2>
<p><i>Subject: Invoice INV-0042 is due today</i><br>Hi [Name], a friendly reminder that invoice INV-0042 for $[amount] is due today. If it&rsquo;s already on its way, thank you! If not, you can pay via [method]. Let me know if anything&rsquo;s unclear.</p>

<h2>3. Overdue (1&ndash;2 weeks past due)</h2>
<p><i>Subject: Invoice INV-0042 &mdash; now overdue</i><br>Hi [Name], invoice INV-0042 for $[amount] was due on [date] and is now [X] days overdue. Could you let me know when I can expect payment? If there&rsquo;s a problem with the invoice, I&rsquo;m glad to sort it out. Payment details are attached.</p>

<h2>4. Final notice</h2>
<p>Keep it professional and specific: restate the amount and original due date, note any late fee stated in your terms, give a firm new date, and say what happens next. Avoid anger &mdash; clarity gets paid; emotion rarely does.</p>

<h2>Make reminders unnecessary</h2>
<p>The best reminder is a clear invoice with easy payment. Create one free with our <a href="/en/invoice">invoice generator</a> &mdash; it shows the due date and your payment details prominently &mdash; or send a <a href="/en/receipt">receipt</a> the moment you&rsquo;re paid to confirm it.</p>
''',
  faqs=[
   ('How do I politely ask for payment?', 'Keep it short, friendly and specific: reference the invoice number and amount, state the due date, and make paying easy. Assume good faith &mdash; most late payments are simply forgotten.'),
   ('When should I send a payment reminder?', 'A good cadence is a reminder a few days before the due date, one on the day, then follow-ups around one and two weeks overdue, escalating in firmness each time.'),
   ('Can I charge a late fee?', 'Yes, if you stated it in your terms before the work (for example 1.5% per month). Reference that term in your reminder rather than adding a surprise fee.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/payment-terms-explained','Payment terms explained'),('/en/blog/receipt-vs-invoice','Receipt vs invoice')],
 ),
 dict(
  slug='sales-tax-on-invoices', cat='Tax', tool='/en/invoice',
  title='Do I Charge Sales Tax on Invoices? (US Guide)',
  desc='A plain-English guide to US sales tax on invoices — when to charge it, how nexus and taxable services work, and how to show it correctly.',
  date='2026-10-21',
  body='''
<p class="lead">&ldquo;Do I add sales tax to this invoice?&rdquo; is one of the most common questions US small businesses ask &mdash; and the honest answer is &ldquo;it depends.&rdquo; Sales tax in the US is set by states (and sometimes cities and counties), so the rules change with where you operate and what you sell. Here&rsquo;s how to think about it.</p>

<h2>There is no federal sales tax</h2>
<p>Unlike VAT or GST in other countries, the US has no national sales tax. Each state sets its own rules and rates, and five states (Alaska, Delaware, Montana, New Hampshire and Oregon) have no statewide sales tax at all &mdash; though some localities in them do. So the first question is always: which state&rsquo;s rules apply?</p>

<h2>Do you have &ldquo;nexus&rdquo;?</h2>
<p>You generally charge a state&rsquo;s sales tax only if you have <b>nexus</b> there &mdash; a connection such as a physical presence (office, staff, inventory) or enough sales into the state to cross its economic-nexus threshold. If you have nexus in a state and sell something taxable to a customer there, you typically collect that state&rsquo;s tax.</p>

<h2>Are services taxable?</h2>
<p>Physical goods are taxable in most states; services are where it gets tricky. Many states don&rsquo;t tax professional services (design, consulting, writing), some tax specific services, and a few tax services broadly. Digital products and SaaS are treated differently again. Check your state&rsquo;s guidance for your specific service.</p>

<h2>How to show sales tax on an invoice</h2>
<p>When you do charge it: show the taxable subtotal, the sales tax as a <b>separate line</b> with the rate, and the total. If some items are exempt and others aren&rsquo;t, apply the rate per line. Keeping tax separate makes your invoice clear for the customer and clean for your books.</p>
<div class="note">This is general information, not tax advice. Sales tax rules vary by state, city and industry and change over time &mdash; confirm your obligations with a tax professional or your state&rsquo;s department of revenue.</div>

<h2>Create an invoice with sales tax free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you set a US sales tax rate per line (or mark items exempt) and shows the tax separately on the PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('Do I have to charge sales tax on every invoice?', 'No. In the US you generally charge a state&rsquo;s sales tax only if you have nexus there and the item or service is taxable in that state. Many professional services aren&rsquo;t taxable in many states.'),
   ('Is sales tax charged on services?', 'It varies by state. Most states tax physical goods; some tax specific services, a few tax services broadly, and many exempt professional services. Check your state&rsquo;s rules for your specific service.'),
   ('How do I show sales tax on an invoice?', 'Show the taxable subtotal, then sales tax as a separate line with the rate, then the total. Apply the rate per line if some items are exempt.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='how-to-invoice-a-client-first-time', cat='Invoicing', tool='/en/invoice',
  title='How to Invoice a Client for the First Time',
  desc='Sending your first invoice? Here is exactly what to put on it, how to set terms, and how to send it so you get paid without the awkwardness.',
  date='2026-10-21',
  body='''
<p class="lead">Sending your first invoice can feel intimidating, but it&rsquo;s really just a clear request for money you&rsquo;ve earned. Get the few key details right and you&rsquo;ll look professional and get paid on time. Here&rsquo;s the whole process, start to finish.</p>

<h2>Step 1: Confirm the details before you invoice</h2>
<p>Make sure you and the client agree on what&rsquo;s being billed and the amount. If you quoted a price or signed a contract, your invoice should match it. Note the agreed payment terms (for example &ldquo;Net 14&rdquo;) and how they&rsquo;ll pay.</p>

<h2>Step 2: Fill in the essentials</h2>
<ul>
<li>The word <b>&ldquo;Invoice&rdquo;</b> and a unique number &mdash; start simple with INV-0001.</li>
<li>Your name or business name and contact details.</li>
<li>The client&rsquo;s name and address (&ldquo;Bill To&rdquo;).</li>
<li>The issue date and the due date.</li>
<li>A line for each item or service, with the amount.</li>
<li>The subtotal, any tax, and the total due.</li>
<li>How to pay &mdash; bank details or a payment link.</li>
</ul>

<h2>Step 3: Decide on tax</h2>
<p>Only add tax if you&rsquo;re required to. In the US that depends on your state and whether the service is taxable; in the UK, Australia and Canada you add VAT or GST once you&rsquo;re registered. If you&rsquo;re unsure, leave tax off and check with an accountant &mdash; and show it as a separate line when you do charge it.</p>

<h2>Step 4: Send it and keep a copy</h2>
<p>Email the PDF with a short, friendly note, or send a share link. Keep a copy for your records and set a reminder for the due date. If payment is late, a polite nudge usually does the trick.</p>

<h2>Create your first invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> walks you through all of this &mdash; no sign-up &mdash; and produces a clean PDF with the right tax model for your country.</p>
''',
  faqs=[
   ('What do I write on my first invoice?', 'The word &ldquo;Invoice&rdquo;, a unique number, your details, the client&rsquo;s details, the date and due date, a line for each item with amounts, the total, and how to pay. Add tax only if you&rsquo;re required to.'),
   ('How do I send an invoice to a client?', 'Attach the PDF to a short, friendly email, or send a share link. Confirm the amount and due date in the message and include your payment details.'),
   ('Do I need to charge tax on my first invoice?', 'Only if required where you operate. US sales tax depends on your state and service; UK VAT, Australian GST and Canadian GST/HST apply once you&rsquo;re registered. Show any tax as a separate line.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/payment-terms-explained','Payment terms explained')],
 ),
 dict(
  slug='pro-forma-invoice', cat='Invoicing', tool='/en/invoice',
  title='What Is a Pro Forma Invoice? (And When to Use One)',
  desc='A pro forma invoice is a preliminary bill sent before goods or services are delivered. Here is what it is, how it differs from a regular invoice, and when to use it.',
  date='2026-10-21',
  body='''
<p class="lead">A <b>pro forma invoice</b> is a preliminary bill you send <i>before</i> the sale is finalised &mdash; a good-faith estimate of what the customer will owe, used to confirm details or arrange payment in advance. It looks like an invoice but isn&rsquo;t a demand for payment or an accounting record.</p>

<h2>Pro forma invoice vs regular invoice</h2>
<p>A regular (commercial) invoice is issued once goods or services are delivered and is a formal request for payment that goes into your books. A pro forma is issued beforehand, isn&rsquo;t recorded as a sale, and can still change. Many businesses mark it clearly with the words &ldquo;Pro Forma&rdquo; so there&rsquo;s no confusion.</p>

<h2>When to use one</h2>
<ul>
<li>To give a buyer a firm price and details so they can approve the purchase or raise a PO.</li>
<li>To request an advance payment or deposit before starting work.</li>
<li>For international shipments, where customs may need a pro forma for valuation.</li>
<li>When a customer&rsquo;s finance team needs a document to set up payment before the real invoice.</li>
</ul>

<h2>What to include</h2>
<p>Use the same layout as an invoice &mdash; your details, the customer, line items, the expected total and any tax &mdash; but title it &ldquo;Pro Forma Invoice&rdquo; and add a validity date. When the sale is confirmed, issue a normal invoice with an invoice number for your records.</p>

<h2>Create one free</h2>
<p>You can build a pro forma with our <a href="/en/invoice">free invoice generator</a> (add &ldquo;Pro Forma&rdquo; to the title or notes), then issue the final <a href="/en/invoice">invoice</a> once the order is confirmed &mdash; no sign-up needed.</p>
''',
  faqs=[
   ('What is the purpose of a pro forma invoice?', 'To give a buyer a preliminary, good-faith bill before the sale is final &mdash; to confirm price and details, request an advance, or support customs valuation. It is not a formal demand for payment or an accounting record.'),
   ('Is a pro forma invoice legally binding?', 'Generally no. It is a quotation-like document that can still change. The binding request for payment is the final commercial invoice issued once the sale is confirmed.'),
   ('What is the difference between a pro forma and a regular invoice?', 'A pro forma is sent before delivery and isn&rsquo;t recorded as a sale; a regular invoice is sent after delivery, carries an invoice number, and is a formal request for payment in your books.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/estimate-vs-quote','Estimate vs quote')],
 ),
 dict(
  slug='uk-vat-invoice-requirements', cat='Tax', tool='/en/invoice',
  title='UK VAT Invoice Requirements: What to Include',
  desc='A clear checklist of what a UK VAT invoice must show — your VAT number, the VAT rate and amount, and the other details HMRC expects.',
  date='2026-10-21',
  body='''
<p class="lead">If you&rsquo;re VAT-registered in the UK, your invoices must meet HMRC&rsquo;s requirements so your customers can reclaim VAT and your records stand up to scrutiny. Here&rsquo;s a plain-English checklist of what a full VAT invoice should show.</p>

<h2>What a full VAT invoice must include</h2>
<ul>
<li>A unique, sequential <b>invoice number</b>.</li>
<li>Your business name, address and <b>VAT registration number</b>.</li>
<li>The invoice date (and the &ldquo;time of supply&rdquo;/tax point if different).</li>
<li>The customer&rsquo;s name and address.</li>
<li>A description of the goods or services.</li>
<li>For each line: quantity, unit price (excl. VAT), the <b>VAT rate</b> and the amount.</li>
<li>The total excluding VAT, the total VAT, and the amount including VAT &mdash; in GBP.</li>
</ul>

<h2>UK VAT rates</h2>
<p>The standard rate is 20%, with a reduced rate of 5% for some goods and services and a 0% rate for certain zero-rated items. Show the rate that applies to each line, and if you supply items at different rates, show the VAT for each rate separately.</p>

<h2>Simplified and modified invoices</h2>
<p>For smaller retail sales (broadly under &pound;250 including VAT) you can issue a simplified VAT invoice with fewer details. Larger or B2B sales usually need a full VAT invoice as above.</p>
<div class="note">This is general guidance, not tax advice. VAT rules and thresholds change &mdash; check the current requirements on GOV.UK or with your accountant.</div>

<h2>Create a UK VAT invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> has a UK mode that adds your VAT number, applies the 20% / 5% / 0% rates and totals the VAT in GBP on A4 &mdash; no sign-up.</p>
''',
  faqs=[
   ('What must a UK VAT invoice include?', 'A unique invoice number, your name, address and VAT registration number, the date, the customer&rsquo;s details, a description, and for each line the quantity, net price, VAT rate and VAT amount, plus the totals excluding and including VAT in GBP.'),
   ('Do I need to show my VAT number on invoices?', 'Yes. If you&rsquo;re VAT-registered, a valid VAT invoice must show your VAT registration number so your customer can reclaim the VAT.'),
   ('What are the UK VAT rates?', 'The standard rate is 20%, with a 5% reduced rate for some supplies and a 0% zero rate for certain items. Show the rate that applies to each line.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/sales-tax-on-invoices','Sales tax on invoices (US)')],
 ),
 dict(
  slug='australian-tax-invoice-requirements', cat='Tax', tool='/en/invoice',
  title='Australian Tax Invoice Requirements (ABN &amp; GST)',
  desc='What an Australian tax invoice must show — your ABN, the words “Tax Invoice”, GST, and the buyer’s details for sales of $1,000 or more.',
  date='2026-10-21',
  body='''
<p class="lead">In Australia, if you&rsquo;re registered for GST you issue a <b>tax invoice</b> so your customers can claim GST credits. The ATO sets out specific details a tax invoice must show &mdash; and a couple of them differ depending on the sale amount.</p>

<h2>What a tax invoice must include</h2>
<ul>
<li>The words <b>&ldquo;Tax Invoice&rdquo;</b>.</li>
<li>Your business or trading name and your <b>ABN</b>.</li>
<li>The date the invoice was issued.</li>
<li>A description of the items sold, including quantity and price.</li>
<li>The <b>GST amount</b> (or a statement that the total includes GST).</li>
<li>The extent to which each sale is taxable.</li>
</ul>

<h2>Sales of $1,000 or more</h2>
<p>For taxable sales of $1,000 or more (including GST), the tax invoice must also show the <b>buyer&rsquo;s identity or ABN</b>. For sales under $1,000 that detail isn&rsquo;t required, though it&rsquo;s fine to include it.</p>

<h2>How GST works on the invoice</h2>
<p>GST is 10% on most goods and services. You can show it as a separate line, or state that the total price includes GST &mdash; for a single-rate invoice, &ldquo;Total price includes GST&rdquo; is acceptable. Some items are GST-free; show those clearly so the GST total is correct.</p>
<div class="note">This is general guidance, not tax advice. GST rules can change &mdash; check current requirements on the ATO website or with your accountant.</div>

<h2>Create an Australian tax invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> has an Australia mode: enter your ABN and it titles the document &ldquo;Tax Invoice&rdquo;, applies 10% GST and formats it on A4 &mdash; no sign-up.</p>
''',
  faqs=[
   ('What must an Australian tax invoice show?', 'The words &ldquo;Tax Invoice&rdquo;, your name and ABN, the date, a description with quantity and price, the GST amount (or that the total includes GST), and how much of the sale is taxable. For sales of $1,000 or more it must also show the buyer&rsquo;s identity or ABN.'),
   ('Do I need an ABN to issue a tax invoice?', 'Yes. A valid tax invoice must show your ABN. Without one, the buyer generally can&rsquo;t claim GST credits and may have to withhold tax from the payment.'),
   ('When do I need the buyer&rsquo;s details on a tax invoice?', 'For taxable sales of $1,000 or more (including GST), the tax invoice must include the buyer&rsquo;s identity or ABN. For smaller sales it&rsquo;s optional.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/uk-vat-invoice-requirements','UK VAT invoice requirements')],
 ),
 dict(
  slug='canadian-invoice-gst-hst', cat='Tax', tool='/en/invoice',
  title='Canadian Invoices: GST, HST, PST &amp; QST Explained',
  desc='How sales tax works on Canadian invoices — GST, HST, PST and QST by province, when to register, and what to show on the invoice.',
  date='2026-10-21',
  body='''
<p class="lead">Canada has one of the more layered sales-tax systems: a federal tax plus provincial taxes that differ by province. If you&rsquo;re registered, your invoices need to apply the right combination and show your tax number. Here&rsquo;s how it works in plain terms.</p>
<h2>GST, HST, PST and QST</h2>
<ul>
<li><b>GST</b> &mdash; the 5% federal Goods and Services Tax, charged across Canada.</li>
<li><b>HST</b> &mdash; the Harmonized Sales Tax, which combines GST and provincial tax into one rate in provinces like Ontario and the Atlantic provinces.</li>
<li><b>PST</b> &mdash; a separate Provincial Sales Tax in provinces such as British Columbia, Saskatchewan and Manitoba, charged on top of GST.</li>
<li><b>QST</b> &mdash; Quebec&rsquo;s provincial tax, administered alongside GST.</li>
</ul>
<h2>What to show on the invoice</h2>
<p>When you charge sales tax, show your <b>GST/HST number</b>, the tax applied per rate, and the totals before and after tax in CAD. If a sale involves both GST and a separate PST, list each as its own line so the customer can see the breakdown.</p>
<h2>When do you register?</h2>
<p>Most small businesses must register for GST/HST once revenue crosses the small-supplier threshold (generally $30,000 over four quarters). Below that you may register voluntarily. Provincial PST registration has its own rules by province.</p>
<div class="note">This is general guidance, not tax advice. Rates and thresholds change and vary by province &mdash; confirm with the CRA, your province, or your accountant.</div>
<h2>Create a Canadian invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> has a Canada mode: pick your province and it applies GST / HST / PST / QST at the right rates, shows your GST/HST number, and formats the invoice in CAD &mdash; no sign-up.</p>
''',
  faqs=[
   ('What sales tax do I charge on a Canadian invoice?', 'It depends on the province: 5% GST everywhere, HST (a combined rate) in provinces like Ontario, or GST plus a separate PST/QST in provinces like BC and Quebec. Charge based on where the sale is taxable and show your GST/HST number.'),
   ('Do I need a GST/HST number to invoice in Canada?', 'You must register once you pass the small-supplier threshold (generally $30,000 in revenue). Once registered, your GST/HST number must appear on invoices where you charge the tax.'),
   ('What is the difference between GST and HST?', 'GST is the 5% federal tax charged nationwide. HST is a single harmonized rate that bundles GST with provincial tax in participating provinces, so you charge one combined rate instead of two.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/vat-gst-sales-tax-difference','VAT vs GST vs sales tax')],
 ),
 dict(
  slug='how-to-invoice-without-a-vat-number', cat='Tax', tool='/en/invoice',
  title='How to Invoice Without a VAT Number (UK)',
  desc='Not VAT-registered? You can still send proper invoices. Here is what to include, what to leave off, and when you must register for VAT.',
  date='2026-10-21',
  body='''
<p class="lead">If you&rsquo;re a UK sole trader or small business below the VAT threshold, you don&rsquo;t charge VAT &mdash; and you shouldn&rsquo;t show a VAT number or VAT amount on your invoices. You can still send clean, professional invoices; they just look a little simpler.</p>
<h2>What to include (without VAT)</h2>
<ul>
<li>The word <b>&ldquo;Invoice&rdquo;</b> and a unique invoice number.</li>
<li>Your name or business name and address.</li>
<li>The customer&rsquo;s name and address.</li>
<li>The invoice date and payment due date.</li>
<li>A description of the goods or services, with the amount for each.</li>
<li>The total due &mdash; with no VAT line.</li>
<li>How to pay (bank details or a link).</li>
</ul>
<h2>What to leave off</h2>
<p>Don&rsquo;t show a VAT registration number (you don&rsquo;t have one) and don&rsquo;t add a VAT line or charge VAT. Doing so when you&rsquo;re not registered is not allowed. Your prices are simply the amount payable.</p>
<h2>When must you register for VAT?</h2>
<p>You must register once your VAT-taxable turnover passes the UK registration threshold over a rolling 12 months (or if you expect to pass it soon). You can also register voluntarily, which lets you reclaim VAT on purchases but means charging VAT to customers.</p>
<div class="note">This is general guidance, not tax advice. The VAT threshold changes &mdash; check the current figure on GOV.UK or with your accountant.</div>
<h2>Create a no-VAT invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you issue a clean UK invoice with no VAT line &mdash; just leave the tax fields blank. No sign-up needed.</p>
''',
  faqs=[
   ('Can I send an invoice without being VAT-registered?', 'Yes. If you&rsquo;re below the VAT threshold you issue a normal invoice with no VAT number and no VAT line &mdash; the total is simply the amount payable. You must not charge VAT unless you&rsquo;re registered.'),
   ('Do I need a VAT number to invoice in the UK?', 'No. A VAT number is only required once you&rsquo;re VAT-registered. Below the threshold you invoice without one.'),
   ('When do I have to register for VAT?', 'When your VAT-taxable turnover passes the UK registration threshold over a rolling 12-month period, or you expect to pass it soon. Check the current threshold on GOV.UK.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/uk-vat-invoice-requirements','UK VAT invoice requirements'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='do-i-need-an-abn-to-invoice', cat='Tax', tool='/en/invoice',
  title='Do You Need an ABN to Invoice? (Australia)',
  desc='Whether you need an ABN to invoice in Australia, what happens if you don’t have one, and how it relates to GST and tax invoices.',
  date='2026-10-21',
  body='''
<p class="lead">In Australia, you can invoice without an ABN, but it usually isn&rsquo;t a good idea. Without one, the business paying you generally has to withhold tax from your payment &mdash; so most people who invoice regularly get an ABN. Here&rsquo;s how it works.</p>
<h2>ABN vs GST registration</h2>
<p>An <b>ABN</b> (Australian Business Number) identifies your business; it&rsquo;s free and separate from GST. <b>GST registration</b> is a further step, required once your turnover reaches the GST threshold (currently $75,000). You can have an ABN without being registered for GST.</p>
<h2>What happens if you invoice without an ABN</h2>
<p>If you don&rsquo;t quote an ABN on your invoice, the payer may be required to withhold a large portion of the payment under &ldquo;no-ABN withholding&rdquo; rules and send it to the ATO. To avoid that, provide your ABN &mdash; or, for a one-off, a &ldquo;Statement by a supplier&rdquo; form in limited cases.</p>
<h2>Tax invoice vs regular invoice</h2>
<p>If you&rsquo;re registered for GST, you issue a <b>tax invoice</b> that shows the words &ldquo;Tax Invoice&rdquo;, your ABN and the GST. If you&rsquo;re not registered for GST, you issue a regular invoice with your ABN but no GST.</p>
<div class="note">This is general guidance, not tax advice. Thresholds and rules change &mdash; check the ATO website or your accountant.</div>
<h2>Create an Australian invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> adds your ABN and, if you charge GST, titles the document &ldquo;Tax Invoice&rdquo; and applies 10% GST &mdash; no sign-up.</p>
''',
  faqs=[
   ('Can I invoice without an ABN in Australia?', 'You can, but the business paying you may have to withhold tax from the payment under no-ABN withholding rules. Most people who invoice regularly get an ABN (it&rsquo;s free) to avoid this.'),
   ('Do I need to be registered for GST to have an ABN?', 'No. An ABN and GST registration are separate. You can hold an ABN without being GST-registered; GST registration is required once your turnover reaches the $75,000 threshold.'),
   ('Is an ABN the same as a tax invoice?', 'No. An ABN is your business number; a tax invoice is a document you issue when registered for GST. A valid tax invoice shows your ABN plus the words &ldquo;Tax Invoice&rdquo; and the GST.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/australian-tax-invoice-requirements','Australian tax invoice requirements'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='vat-gst-sales-tax-difference', cat='Tax', tool='/en/invoice',
  title='VAT vs GST vs Sales Tax: What&rsquo;s the Difference?',
  desc='A simple explanation of the three main consumption taxes — US sales tax, UK VAT and GST — and how each one appears on an invoice.',
  date='2026-10-21',
  body='''
<p class="lead">VAT, GST and sales tax all tax what people buy, but they work differently &mdash; which matters when you invoice customers in different countries. Here&rsquo;s the short version of how each one behaves and shows up on an invoice.</p>
<h2>US sales tax</h2>
<p>Sales tax is charged once, at the point of sale to the final customer, and is set by each US state (and sometimes city or county). There&rsquo;s no federal sales tax. You only charge it where you have a tax obligation (&ldquo;nexus&rdquo;) and the item is taxable. On the invoice it&rsquo;s a single line added to the subtotal.</p>
<h2>VAT (UK and much of the world)</h2>
<p>VAT (Value Added Tax) is charged at each stage of the supply chain, but businesses reclaim the VAT they pay, so the net effect falls on the final consumer. VAT-registered sellers show their VAT number, the rate (20% / 5% / 0% in the UK) and the VAT amount on the invoice.</p>
<h2>GST (Australia, Canada and others)</h2>
<p>GST (Goods and Services Tax) works much like VAT &mdash; charged along the chain with credits for businesses. Australia uses a single 10% GST and calls the document a &ldquo;Tax Invoice&rdquo;; Canada layers GST with provincial taxes (HST/PST/QST).</p>
<div class="note">This is general information, not tax advice. Rates and rules vary and change &mdash; confirm with the relevant tax authority or your accountant.</div>
<h2>One tool, the right tax for each</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> handles all three: pick the US, UK, Australia or Canada and it applies the correct tax model automatically &mdash; no sign-up.</p>
''',
  faqs=[
   ('What is the difference between VAT and sales tax?', 'Sales tax is charged once, at the final sale, and is set by US states. VAT is charged at each stage of the supply chain with businesses reclaiming what they pay, so it&rsquo;s collected gradually but ultimately borne by the consumer.'),
   ('Is GST the same as VAT?', 'They&rsquo;re very similar &mdash; both are multi-stage consumption taxes with credits for businesses. &ldquo;GST&rdquo; is the name used in countries like Australia and Canada; &ldquo;VAT&rdquo; is used in the UK and much of Europe.'),
   ('Which tax do I put on my invoice?', 'The one for the country where the sale is taxable: US sales tax, UK VAT, or GST in Australia/Canada. A good invoice tool switches the model automatically when you choose the country.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/sales-tax-on-invoices','Sales tax on invoices (US)'),('/en/blog/uk-vat-invoice-requirements','UK VAT invoice requirements')],
 ),
 dict(
  slug='invoice-for-contractors', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Contractor (Trades &amp; Construction)',
  desc='Invoicing for trades and construction — progress payments, materials vs labour, retention, and what to put on a contractor invoice to get paid on time.',
  date='2026-10-21',
  body='''
<p class="lead">Contractor invoicing has a few wrinkles other trades don&rsquo;t: progress payments across a long job, materials billed separately from labour, and sometimes retention held back until completion. Get these right and you&rsquo;ll keep cash flowing on bigger jobs.</p>
<h2>Separate labour, materials and other costs</h2>
<p>List labour (hours or a fixed amount), materials, equipment hire and any disposal or permit fees as separate lines. Clients and their accountants find the breakdown easier to approve, and it makes variations simpler to add.</p>
<h2>Progress payments and milestones</h2>
<p>For long jobs, invoice in stages tied to milestones (for example deposit, first fix, second fix, completion) rather than waiting until the end. Reference the stage and the contract on each invoice so it&rsquo;s clear what&rsquo;s being billed.</p>
<h2>Retention, variations and tax</h2>
<p>If the contract holds retention, show it as a deduction and note when it&rsquo;s released. Add approved variations as their own lines. Apply the right tax for your country &mdash; US sales tax rules differ for materials vs labour by state; UK/AU/CA add VAT/GST once registered (watch for construction-specific VAT rules in the UK).</p>
<h2>Create a contractor invoice free</h2>
<p>Use our <a href="/en/invoice">free invoice generator</a> to itemise labour and materials, add a job reference and due date, and produce a clean PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('How do contractors invoice for progress payments?', 'Invoice in stages tied to agreed milestones (deposit, first fix, completion, etc.) rather than only at the end. Reference the stage and the contract on each invoice so the client knows exactly what they&rsquo;re paying for.'),
   ('Should materials and labour be on separate lines?', 'Yes. Listing labour, materials, hire and fees separately makes the invoice easier to approve and keeps variations clear. It also helps with tax, which can treat materials and labour differently.'),
   ('What is retention on a contractor invoice?', 'Retention is a percentage the client holds back until the job is complete (or a defects period ends). Show it as a deduction on the invoice and note when it will be released.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/purchase-order','Free purchase order template'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='invoice-for-consultants', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Consultant',
  desc='Consultant invoicing done right — hourly vs fixed vs retainer, expenses, milestones, and how to present it so clients pay promptly.',
  date='2026-10-21',
  body='''
<p class="lead">Consulting work gets billed in a few different shapes &mdash; by the hour, by project, or on a monthly retainer &mdash; and your invoice should make the arrangement obvious. Clear, well-structured invoices also signal the professionalism clients are paying for.</p>
<h2>Match the invoice to your billing model</h2>
<ul>
<li><b>Hourly</b> &mdash; show hours, rate and a short description per block of work.</li>
<li><b>Fixed project</b> &mdash; one line for the agreed fee, or milestone lines (e.g. 50% on start, 50% on delivery).</li>
<li><b>Retainer</b> &mdash; a recurring monthly line (&ldquo;Advisory retainer &mdash; October&rdquo;), with any overage billed separately.</li>
</ul>
<h2>Expenses and disbursements</h2>
<p>Bill travel, software or subcontractor costs as separate lines, and keep receipts. Agree in advance whether expenses are billed at cost or with a markup so there are no surprises.</p>
<h2>Terms that get you paid</h2>
<p>Keep payment terms short (Net 14 is common for consultants), state the actual due date, and for new clients consider a deposit or part-payment up front. Add any tax (sales tax, VAT or GST) as a separate line depending on your country and registration.</p>
<h2>Create a consultant invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> handles hourly, fixed and retainer lines, expenses and the right tax model for your country &mdash; no sign-up.</p>
''',
  faqs=[
   ('How do consultants usually bill clients?', 'Three common models: hourly (hours &times; rate), fixed project fee (often split into milestones), and monthly retainer. Your invoice should clearly show which one applies for the period.'),
   ('Should I charge a deposit as a consultant?', 'For new clients or larger projects, yes &mdash; a deposit or milestone payment up front reduces risk and improves cash flow. State it on a quote or the first invoice.'),
   ('How do I bill expenses on a consulting invoice?', 'List travel, software and subcontractor costs as separate lines, keep receipts, and agree beforehand whether they&rsquo;re billed at cost or with a markup.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/payment-terms-explained','Payment terms explained'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='invoice-for-graphic-designers', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Graphic Designer',
  desc='Design invoicing that protects you — deposits, revision limits, usage/licensing, and transferring files only after payment.',
  date='2026-10-21',
  body='''
<p class="lead">Design invoices are about more than the fee &mdash; they&rsquo;re where you set expectations on revisions, usage rights and when files are handed over. A tidy invoice with the right notes prevents the most common payment disputes in creative work.</p>
<h2>Deposit first, files on final payment</h2>
<p>Take a deposit before starting (often 30&ndash;50%), and release final, print-ready or source files only after the balance is paid. State this on your quote and invoice so it&rsquo;s understood up front.</p>
<h2>Revisions and scope</h2>
<p>Note how many revision rounds are included and your rate for extra rounds, then bill additional revisions as their own line. This keeps &ldquo;just one more tweak&rdquo; from eroding your time for free.</p>
<h2>Usage, licensing and tax</h2>
<p>If you&rsquo;re licensing artwork rather than selling it outright, say so in the notes (medium, territory, duration). Apply the right tax for your country &mdash; in the US, design services are taxable in some states; in the UK/AU/CA you add VAT/GST once registered. Design fees can also be subject to withholding in some countries when paid to individuals.</p>
<h2>Create a designer invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you itemise design fees and revisions, add usage notes, and produce a clean PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('Should graphic designers take a deposit?', 'Yes &mdash; a deposit of around 30&ndash;50% before starting is standard. It commits the client and protects your time, with final files released after the balance is paid.'),
   ('How do I charge for extra design revisions?', 'State the number of revision rounds included, then bill extra rounds as a separate line at an agreed rate. Putting this on the quote and invoice prevents scope creep.'),
   ('Do I charge tax on design work?', 'It depends on your country and registration. In the US, taxability of design services varies by state; in the UK, Australia and Canada you add VAT/GST once registered. Show tax as a separate line.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/estimate','Free estimate &amp; quote generator'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='invoice-for-photographers', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Photographer',
  desc='Photography invoicing — booking deposits, shoot vs editing fees, image licensing and delivery, and the tax to apply.',
  date='2026-10-21',
  body='''
<p class="lead">Whether you shoot weddings, products or portraits, your invoice does double duty: it collects payment and sets the terms around deposits, usage and delivery. Here&rsquo;s how to structure one that protects your time and your images.</p>
<h2>Booking deposit and balance</h2>
<p>Take a non-refundable booking deposit to hold the date, then invoice the balance before or on delivery of the final images. Make the deposit and balance clear on the invoice, along with the shoot date.</p>
<h2>Itemise the shoot and the extras</h2>
<p>Separate the shoot fee from editing/retouching, extra hours, prints, albums and travel. If you offer packages, show the package as one line and any add-ons separately so clients see what they chose.</p>
<h2>Licensing and delivery</h2>
<p>Say whether the client gets personal or commercial usage, and for how long &mdash; commercial licensing is usually priced higher. Deliver final high-resolution files after full payment. Apply the right tax for your country (US sales tax varies by state; UK/AU/CA add VAT/GST once registered).</p>
<h2>Create a photography invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you add a deposit, itemise the shoot and extras, note usage rights, and produce a clean PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('How much deposit should a photographer take?', 'A booking deposit (often non-refundable) to secure the date is standard &mdash; commonly 20&ndash;50% of the fee. Invoice the balance before or on delivery of the final images.'),
   ('Should I license or sell photos on the invoice?', 'Usually you license usage rather than sell outright. Note the usage (personal or commercial) and duration on the invoice; commercial licensing is typically priced higher.'),
   ('When should I deliver the final images?', 'After full payment. State on the invoice that final high-resolution files are delivered once the balance is cleared to avoid chasing payment afterwards.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/receipt','Free receipt generator'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='invoice-for-cleaning-business', cat='Industries', tool='/en/invoice',
  title='How to Invoice for a Cleaning Business',
  desc='Invoicing for cleaning services — one-off vs recurring jobs, per-visit vs hourly, supplies, and getting paid on a regular schedule.',
  date='2026-10-21',
  body='''
<p class="lead">Cleaning work is often recurring &mdash; weekly offices, fortnightly homes, end-of-tenancy one-offs &mdash; so the real win is invoicing on a predictable schedule that gets you paid without chasing. Here&rsquo;s how to set it up.</p>
<h2>Per-visit, hourly or monthly</h2>
<p>Decide how you bill: a fixed price per visit, an hourly rate, or a monthly amount for a set schedule. For recurring clients, a single monthly invoice listing each visit (or a flat monthly fee) is usually cleanest.</p>
<h2>What to itemise</h2>
<p>Show the service and dates (e.g. &ldquo;Office clean &mdash; 4 visits in October&rdquo;), any extras like carpet or window cleaning as separate lines, and supplies if you bill them. Note the property or site so multi-site clients can match invoices.</p>
<h2>Terms and tax</h2>
<p>Keep terms short and consistent (Net 7 or Net 14 works well for recurring work), send the invoice on the same day each cycle, and make payment easy. Apply sales tax, VAT or GST depending on your country and registration.</p>
<h2>Create a cleaning invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you list visits, add extras and supplies, and produce a clean PDF each cycle &mdash; no sign-up.</p>
''',
  faqs=[
   ('How do I invoice recurring cleaning clients?', 'Invoice on a fixed cycle &mdash; for example one monthly invoice listing each visit, or a flat monthly fee. Sending it the same day each cycle with short terms (Net 7&ndash;14) keeps payments predictable.'),
   ('Should I charge per visit or per hour for cleaning?', 'Either works. A fixed price per visit is simple for clients to budget; hourly suits variable jobs. Pick one per client and show it clearly on the invoice.'),
   ('Do I charge tax on cleaning services?', 'It depends on your country and registration. Some US states tax cleaning services; in the UK, Australia and Canada you add VAT/GST once registered. Show it as a separate line.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/recurring-invoices-explained','Recurring invoices explained'),('/en/blog/payment-terms-explained','Payment terms explained')],
 ),
 dict(
  slug='invoice-for-tutors', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Tutor',
  desc='Tutoring invoices made simple — per-session vs block booking, monthly billing for regular students, cancellations, and the tax to apply.',
  date='2026-10-21',
  body='''
<p class="lead">Tutoring usually means regular sessions with the same students, so the goal is a simple, repeatable invoice &mdash; ideally one per month per student or family &mdash; that&rsquo;s easy to pay and easy to track.</p>
<h2>Per-session, blocks, or monthly</h2>
<p>Bill per session, sell blocks of sessions up front (often at a small discount), or send a monthly invoice listing the sessions held. For regular students, monthly billing in arrears (or blocks in advance) reduces admin.</p>
<h2>What to show</h2>
<p>List the student&rsquo;s name, the subject, and the dates and length of each session, with your rate. If you bill a parent for multiple children, group by student so it&rsquo;s clear. Note your cancellation policy (for example, sessions cancelled with less than 24 hours&rsquo; notice are chargeable).</p>
<h2>Terms and tax</h2>
<p>Keep terms short and send invoices on a set day. Many independent tutors are below VAT/GST thresholds, but apply tax if you&rsquo;re registered (education can have specific exemptions in some countries &mdash; check locally).</p>
<h2>Create a tutoring invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you list sessions by student and date, add your rate, and produce a clean monthly PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('How should tutors invoice regular students?', 'A monthly invoice per student (or family) listing the sessions held is simplest, or sell blocks of sessions in advance. Send it on a set day each month with short payment terms.'),
   ('Should I charge for cancelled tutoring sessions?', 'Many tutors charge for late cancellations (for example, less than 24 hours&rsquo; notice). State your policy up front and note it on the invoice so it&rsquo;s clear.'),
   ('Do tutors charge VAT or sales tax?', 'Only if registered. Many independent tutors are below VAT/GST thresholds. Note that education services can have specific tax exemptions in some countries &mdash; check your local rules.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/recurring-invoices-explained','Recurring invoices explained'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='invoice-for-virtual-assistants', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Virtual Assistant',
  desc='VA invoicing — hourly vs package vs retainer, tracking time across clients, and billing on a schedule that keeps cash flow steady.',
  date='2026-10-21',
  body='''
<p class="lead">As a virtual assistant you often juggle several clients and billing models at once, so a clean, consistent invoice per client &mdash; sent on a regular schedule &mdash; is what keeps the admin light and the payments flowing.</p>
<h2>Hourly, package or retainer</h2>
<ul>
<li><b>Hourly</b> &mdash; log time per task and show hours &times; rate.</li>
<li><b>Package</b> &mdash; a set number of hours per month at a fixed price.</li>
<li><b>Retainer</b> &mdash; a recurring monthly fee for ongoing availability, with overage billed separately.</li>
</ul>
<h2>Track time and show the work</h2>
<p>Keep a simple log of hours or tasks per client so each invoice reflects what you actually did. Grouping work into a few clear lines (e.g. &ldquo;Inbox &amp; calendar management&rdquo;, &ldquo;Research&rdquo;) reads better than a long list of tiny entries.</p>
<h2>Terms and tax</h2>
<p>Invoice on the same day each month, keep terms short (Net 7&ndash;14), and bill in your client&rsquo;s currency where it makes sense. Apply sales tax, VAT or GST only if you&rsquo;re registered in your country.</p>
<h2>Create a VA invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> handles hourly, package and retainer lines and produces a clean PDF per client &mdash; no sign-up.</p>
''',
  faqs=[
   ('How do virtual assistants usually bill?', 'By the hour, by a monthly package of hours, or on a retainer for ongoing availability. Pick one model per client and send a consistent invoice each cycle.'),
   ('How do I track time for VA invoices?', 'Keep a simple per-client log of hours or tasks, then group the work into a few clear lines on the invoice rather than many tiny entries.'),
   ('Should a VA invoice monthly?', 'Monthly billing on a set day keeps cash flow predictable and admin low. Use short terms (Net 7&ndash;14) and make payment easy.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/recurring-invoices-explained','Recurring invoices explained'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer')],
 ),
 dict(
  slug='invoice-for-web-developers', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Web Developer',
  desc='Dev invoicing — hourly vs fixed vs milestone, ongoing maintenance retainers, hosting pass-through costs, and payment terms that work.',
  date='2026-10-21',
  body='''
<p class="lead">Web projects mix one-off build work with ongoing maintenance, so your invoicing usually spans both: milestone payments for the build and a recurring line for support or hosting. Structuring it clearly keeps clients comfortable and your cash flow smooth.</p>
<h2>Milestones for the build</h2>
<p>Break a fixed-price build into milestone payments &mdash; for example deposit, design sign-off, development complete, launch. Invoice each as the milestone is reached and reference the project and stage.</p>
<h2>Maintenance and hosting</h2>
<p>Bill ongoing maintenance as a monthly retainer (updates, backups, support hours). If you pass through hosting or third-party subscriptions, list them as separate lines, at cost or with an agreed markup.</p>
<h2>Hourly work and terms</h2>
<p>For ad-hoc changes outside a retainer, bill hourly with a short description per block. Keep terms short, take a deposit on new projects, and apply the right tax for your country (US sales tax varies by state for services; UK/AU/CA add VAT/GST once registered).</p>
<h2>Create a developer invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> handles milestones, retainers, hourly work and pass-through costs, and produces a clean PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('How should web developers bill fixed-price projects?', 'Split the fee into milestone payments (deposit, design sign-off, development complete, launch) and invoice each milestone as it&rsquo;s reached. This keeps cash flow steady and reduces end-of-project risk.'),
   ('How do I bill for website maintenance?', 'Use a monthly retainer covering updates, backups and a set number of support hours, with extra work billed separately. List pass-through hosting or subscriptions as their own lines.'),
   ('Should developers take a deposit?', 'Yes, especially for new clients and fixed-price builds &mdash; a deposit commits the client and protects your time. Make it the first milestone on the invoice.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/recurring-invoices-explained','Recurring invoices explained'),('/en/blog/payment-terms-explained','Payment terms explained')],
 ),
 dict(
  slug='invoice-for-online-store', cat='Industries', tool='/en/invoice',
  title='How to Invoice for an Online Store (E-commerce)',
  desc='When online sellers need invoices — B2B and wholesale orders, VAT/GST invoices for customers, and matching invoices to orders.',
  date='2026-10-21',
  body='''
<p class="lead">Most retail e-commerce sales are handled by the store&rsquo;s checkout, but online sellers still need proper invoices &mdash; for wholesale and B2B orders, for customers who request a VAT or tax invoice, and for business buyers who need one to pay you.</p>
<h2>When you need an invoice (not just a receipt)</h2>
<p>A checkout confirmation or receipt is enough for most consumer sales. You need a proper invoice for wholesale/B2B orders, for purchase-order-based buyers, and whenever a customer asks for a VAT or tax invoice to reclaim tax.</p>
<h2>Match the invoice to the order</h2>
<p>Reference the order number and, if there is one, the customer&rsquo;s PO number so everything reconciles. List items with quantities and unit prices, shipping as its own line, and the tax applied for the customer&rsquo;s region.</p>
<h2>Tax across regions</h2>
<p>Cross-border selling means different tax models &mdash; US sales tax by state (where you have nexus), UK VAT, Australian GST, Canadian GST/HST. Issue the right type of document for the buyer&rsquo;s country, with your tax number where required.</p>
<h2>Create an e-commerce invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you reference the order, list items and shipping, and apply the correct tax for the US, UK, Australia or Canada &mdash; no sign-up.</p>
''',
  faqs=[
   ('Do online stores need to send invoices?', 'For ordinary consumer sales a checkout receipt is usually enough. You need a proper invoice for wholesale/B2B orders, PO-based buyers, and any customer who requests a VAT or tax invoice.'),
   ('How do I invoice a wholesale order?', 'Reference the order and any PO number, list items with quantities and unit prices, add shipping as a separate line, and apply the correct tax for the buyer&rsquo;s region with your tax number where required.'),
   ('What tax do I charge on cross-border online sales?', 'It depends on the buyer&rsquo;s country and your obligations there &mdash; US sales tax where you have nexus, UK VAT, Australian or Canadian GST. Issue the right document type for that region.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/receipt','Free receipt generator'),('/en/blog/receipt-vs-invoice','Receipt vs invoice')],
 ),
 dict(
  slug='invoice-for-freelance-writers', cat='Industries', tool='/en/invoice',
  title='How to Invoice as a Freelance Writer',
  desc='Writer invoicing — per-word vs per-project vs retainer, kill fees, rights, and the withholding and tax to watch for.',
  date='2026-10-21',
  body='''
<p class="lead">Freelance writers bill in a few ways &mdash; per word, per piece, per hour, or on a monthly retainer &mdash; and the invoice is where you also pin down kill fees and rights. A clean invoice gets you paid faster and keeps the relationship clear.</p>
<h2>Pick a model and show it clearly</h2>
<p>Whether you charge per word, per article or a project fee, show the calculation plainly: &ldquo;Feature article, 1,500 words&rdquo; with the total, or &ldquo;Content retainer &mdash; October (4 posts)&rdquo;. For hourly work, show hours and rate.</p>
<h2>Kill fees and rights</h2>
<p>If a commissioned piece is cancelled, a kill fee (an agreed portion of the fee) may apply &mdash; note it in your terms. State what rights you&rsquo;re granting (first use, full transfer, etc.) if that affects the price.</p>
<h2>Withholding and tax</h2>
<p>In some countries, payments to individual writers are subject to withholding, and the payer deducts tax before paying you &mdash; your invoice should reflect the arrangement. Add VAT/GST only if you&rsquo;re registered; US sales tax rarely applies to writing services.</p>
<h2>Create a writer invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you bill per word, per piece or on retainer, note rights, and produce a clean PDF &mdash; no sign-up.</p>
''',
  faqs=[
   ('How do freelance writers charge?', 'Common models are per word, per article/project, per hour, or a monthly retainer. Show the basis clearly on the invoice (e.g. word count and total, or the retainer period and deliverables).'),
   ('What is a kill fee?', 'A kill fee is an agreed portion of the fee paid if a commissioned piece is cancelled before publication. Note it in your terms so it&rsquo;s clear what&rsquo;s owed if a project is pulled.'),
   ('Do writers charge tax on invoices?', 'Usually only VAT/GST if registered; US sales tax rarely applies to writing services. Be aware some countries require the payer to withhold tax from payments to individuals.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-invoice-as-a-freelancer','How to invoice as a freelancer'),('/en/blog/payment-reminder-email','Payment reminder email templates')],
 ),
 dict(
  slug='how-to-number-invoices', cat='Invoicing', tool='/en/invoice',
  title='How to Number Invoices (A Simple System)',
  desc='A clear, reliable invoice numbering system — why sequential numbers matter, formats that work, and mistakes to avoid.',
  date='2026-10-21',
  body='''
<p class="lead">Every invoice needs a unique number, and in many countries they must run in a sequence with no gaps. A simple, consistent numbering system keeps you compliant, makes invoices easy to find, and looks professional to clients.</p>
<h2>Why sequential numbers matter</h2>
<p>Unique, sequential numbers let you (and the tax authority) track every invoice and spot anything missing. In VAT/GST systems, a continuous sequence is often a legal requirement &mdash; gaps or duplicates can raise questions.</p>
<h2>Formats that work</h2>
<ul>
<li><b>Simple sequence:</b> INV-0001, INV-0002, INV-0003&hellip;</li>
<li><b>Year prefix:</b> 2026-001, 2026-002 (reset or continue each year).</li>
<li><b>Client or project code:</b> ACME-0001 &mdash; handy if you want to group by client, as long as each number is still unique overall.</li>
</ul>
<h2>Mistakes to avoid</h2>
<p>Don&rsquo;t reuse numbers, don&rsquo;t leave gaps without a record, and don&rsquo;t restart in a way that creates duplicates. Pick one format and stick to it &mdash; changing systems mid-year causes confusion.</p>
<h2>Create numbered invoices free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you set your own invoice number in any format &mdash; just increment it each time &mdash; and produces a clean PDF, no sign-up.</p>
''',
  faqs=[
   ('Do invoice numbers have to be sequential?', 'In many countries, especially under VAT/GST, invoice numbers must be unique and run in a continuous sequence without gaps. Even where it isn&rsquo;t strictly required, sequential numbering is best practice.'),
   ('What is a good invoice numbering format?', 'A simple sequence like INV-0001, a year prefix like 2026-001, or a client code like ACME-0001 all work &mdash; as long as every number is unique and the sequence is consistent.'),
   ('Can I change my invoice numbering system?', 'You can, but do it cleanly (for example at the start of a year) and keep a record, so you never create duplicates or unexplained gaps.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/common-invoice-mistakes','Common invoice mistakes to avoid')],
 ),
 dict(
  slug='credit-note-vs-invoice', cat='Invoicing', tool='/en/invoice',
  title='What Is a Credit Note? (Credit Note vs Invoice)',
  desc='A credit note cancels or reduces a previous invoice. Here is what it is, when to issue one, and how it differs from an invoice or refund.',
  date='2026-10-21',
  body='''
<p class="lead">A <b>credit note</b> (or credit memo) is a document that reduces or cancels an amount a customer owes on a previous invoice &mdash; for a return, an overcharge, a discount or a correction. It&rsquo;s the proper way to fix an invoice without deleting it.</p>
<h2>When to issue a credit note</h2>
<ul>
<li>A customer returns goods or cancels part of an order.</li>
<li>You overcharged, or applied the wrong price or tax.</li>
<li>You agree a discount or goodwill adjustment after invoicing.</li>
</ul>
<h2>Credit note vs invoice vs refund</h2>
<p>An invoice <i>adds</i> to what a customer owes; a credit note <i>reduces</i> it. A credit note isn&rsquo;t the same as a refund &mdash; it adjusts the balance, which the customer can set against what they owe, while a refund actually returns money. You can issue a credit note and then refund if appropriate.</p>
<h2>What to include</h2>
<p>Reference the original invoice number, show the items and amounts being credited (including tax), and give the credit note its own unique number. Keep both documents on file so your records reconcile.</p>
<h2>Create the documents free</h2>
<p>You can produce an invoice and a matching credit note with our <a href="/en/invoice">free invoice generator</a> &mdash; label the credit note clearly and reference the original invoice. No sign-up needed.</p>
''',
  faqs=[
   ('What is a credit note used for?', 'To reduce or cancel an amount on a previous invoice &mdash; for returns, overcharges, discounts or corrections. It&rsquo;s the proper way to adjust an invoice without deleting it.'),
   ('Is a credit note the same as a refund?', 'No. A credit note reduces the balance the customer owes; a refund returns money. You can issue a credit note and then refund if the customer has already paid.'),
   ('What should a credit note include?', 'Its own unique number, a reference to the original invoice, the items and amounts being credited (with tax), and your business and customer details.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/invoice-vs-bill-vs-statement','Invoice vs bill vs statement'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='invoice-vs-bill-vs-statement', cat='Invoicing', tool='/en/invoice',
  title='Invoice vs Bill vs Statement: What&rsquo;s the Difference?',
  desc='Invoice, bill and statement are often used loosely but mean different things. Here is what each one is and when to use it.',
  date='2026-10-21',
  body='''
<p class="lead">&ldquo;Invoice&rdquo;, &ldquo;bill&rdquo; and &ldquo;statement&rdquo; get used interchangeably, but they&rsquo;re three different documents. Knowing the difference helps you send the right one &mdash; and understand what you&rsquo;re receiving.</p>
<h2>Invoice</h2>
<p>An invoice is a seller&rsquo;s formal request for payment for specific goods or services, with a number, line items, tax, a total and a due date. It&rsquo;s a record of a single transaction that the customer will pay.</p>
<h2>Bill</h2>
<p>A &ldquo;bill&rdquo; is really the same request seen from the buyer&rsquo;s side &mdash; the document you receive and need to pay. In everyday use, &ldquo;bill&rdquo; often describes immediate amounts due (a restaurant bill, a utility bill), while &ldquo;invoice&rdquo; is the more formal B2B term. The document itself is largely the same.</p>
<h2>Statement</h2>
<p>A statement is a summary of account activity over a period &mdash; it lists multiple invoices, payments received and the outstanding balance. You send a statement to remind a customer of everything owed to date, not to request payment for a single job.</p>
<h2>Create invoices free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> produces professional invoices (your &ldquo;bill&rdquo; to the customer) as clean PDFs &mdash; no sign-up.</p>
''',
  faqs=[
   ('Is a bill the same as an invoice?', 'Essentially yes &mdash; it&rsquo;s the same request for payment, described from the buyer&rsquo;s side. &ldquo;Bill&rdquo; is common for immediate amounts due; &ldquo;invoice&rdquo; is the more formal term used in business transactions.'),
   ('What is the difference between an invoice and a statement?', 'An invoice requests payment for one transaction. A statement summarises account activity over a period &mdash; multiple invoices, payments and the outstanding balance &mdash; as a reminder of the total owed.'),
   ('When should I send a statement instead of an invoice?', 'Send a statement periodically (e.g. monthly) to show a customer everything outstanding across several invoices. Send an invoice when you want payment for a specific job or order.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/credit-note-vs-invoice','Credit note vs invoice'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='how-to-ask-for-a-deposit', cat='Getting paid', tool='/en/invoice',
  title='How to Ask for a Deposit (Deposit Invoices)',
  desc='Why and how to take a deposit before starting work — how much, how to invoice it, and how to apply it to the final invoice.',
  date='2026-10-21',
  body='''
<p class="lead">Asking for a deposit protects you from doing work that never gets paid for, and it filters out clients who were never serious. Done professionally, it&rsquo;s completely normal &mdash; here&rsquo;s how to ask and how to invoice it.</p>
<h2>Why take a deposit</h2>
<p>A deposit commits the client, covers your early costs, and improves cash flow on longer jobs. For new clients, larger projects, or custom work you can&rsquo;t resell, it&rsquo;s standard practice.</p>
<h2>How much, and how to ask</h2>
<p>Common deposits run 25&ndash;50% of the total. Set it on the quote so it&rsquo;s agreed before work starts, and phrase it as routine: &ldquo;To book you in, I take a 50% deposit, with the balance due on completion.&rdquo; Confidence matters more than apology.</p>
<h2>Invoicing the deposit and the balance</h2>
<p>Issue a deposit invoice for the agreed amount up front. On the final invoice, show the full total, then the deposit already paid as a deduction, leaving the balance due. This keeps your records clean and the maths obvious to the client.</p>
<h2>Create a deposit invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> lets you invoice a deposit and then show it as a deduction on the final invoice &mdash; no sign-up.</p>
''',
  faqs=[
   ('How much deposit should I ask for?', 'Commonly 25&ndash;50% of the total, depending on the work and your costs. Set it on the quote so it&rsquo;s agreed before you start.'),
   ('How do I invoice a deposit?', 'Issue a deposit invoice for the agreed amount up front. On the final invoice, show the full total, subtract the deposit already paid, and bill the remaining balance.'),
   ('Is it normal to ask clients for a deposit?', 'Yes &mdash; for new clients, larger projects and custom work it&rsquo;s standard. Phrase it as routine policy and most clients expect it.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/payment-terms-explained','Payment terms explained'),('/en/blog/payment-reminder-email','Payment reminder email templates')],
 ),
 dict(
  slug='recurring-invoices-explained', cat='Invoicing', tool='/en/invoice',
  title='What Are Recurring Invoices? (And When to Use Them)',
  desc='Recurring invoices bill the same client the same amount on a schedule. Here is how they work, when to use them, and how to set them up.',
  date='2026-10-21',
  body='''
<p class="lead">A <b>recurring invoice</b> bills a customer the same (or similar) amount on a regular schedule &mdash; weekly, monthly or yearly &mdash; without you creating each one from scratch. They&rsquo;re ideal for subscriptions, retainers and any ongoing service.</p>
<h2>When recurring invoices make sense</h2>
<ul>
<li>Monthly retainers (consulting, design, marketing, VA work).</li>
<li>Subscription or membership fees.</li>
<li>Regular services &mdash; cleaning, maintenance, tutoring, hosting.</li>
</ul>
<h2>How they work</h2>
<p>You set the client, the amount, the schedule and a start date; the invoice is then issued automatically each cycle with a new number and date. Some tools also charge a saved payment method automatically, which turns the invoice into a subscription.</p>
<h2>Keep them accurate</h2>
<p>Review recurring invoices periodically &mdash; usage, scope or prices change. Make it easy for clients to see what each cycle covers, and send any price changes in advance.</p>
<h2>Create invoices free (and manage them with PRO)</h2>
<p>You can create each invoice free with our <a href="/en/invoice">invoice generator</a>. For saved clients, automatic numbering and ongoing management, see <a href="/en/pricing">Free BizDoc PRO</a>.</p>
''',
  faqs=[
   ('What is a recurring invoice?', 'An invoice that bills the same client a set amount on a regular schedule &mdash; weekly, monthly or yearly &mdash; issued automatically each cycle so you don&rsquo;t recreate it each time.'),
   ('When should I use recurring invoices?', 'For retainers, subscriptions, memberships and regular services like cleaning, maintenance or tutoring &mdash; anything billed on a predictable schedule.'),
   ('What is the difference between a recurring invoice and a subscription?', 'A recurring invoice requests payment each cycle; a subscription also charges a saved payment method automatically. A subscription is essentially a recurring invoice with auto-payment.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/pricing','Free vs PRO'),('/en/blog/payment-terms-explained','Payment terms explained')],
 ),
 dict(
  slug='how-to-send-an-invoice-by-email', cat='Invoicing', tool='/en/invoice',
  title='How to Send an Invoice by Email (With Template)',
  desc='The right way to email an invoice — subject line, a short message template, attaching the PDF, and following up.',
  date='2026-10-21',
  body='''
<p class="lead">Most invoices are sent by email, and a clear, professional message gets them paid faster. The invoice itself does the heavy lifting; the email just needs to be easy to read and act on. Here&rsquo;s how to do it.</p>
<h2>Write a clear subject line</h2>
<p>Put the key details in the subject so it&rsquo;s easy to find later: <i>&ldquo;Invoice INV-0042 from [Your Business] &mdash; due 20 Nov&rdquo;</i>. Avoid vague subjects like &ldquo;Hello&rdquo; or &ldquo;Document attached&rdquo;.</p>
<h2>A short message template</h2>
<p><i>Hi [Name],</i><br>Please find attached invoice INV-0042 for [work], totalling $[amount], due on [date]. Payment details are on the invoice. Thanks very much &mdash; let me know if you have any questions.<br><i>Best, [Your Name]</i></p>
<h2>Attach the PDF (or send a link)</h2>
<p>Attach the invoice as a PDF so it looks the same on any device, and name the file clearly (e.g. <i>Invoice-INV-0042.pdf</i>). Alternatively, send a share link the client can open and download &mdash; handy when the attachment is large or might be blocked.</p>
<h2>Follow up politely</h2>
<p>If the due date passes, a short, friendly reminder usually does the trick. Keep records of what you sent and when.</p>
<h2>Create and send an invoice free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> produces a clean PDF to attach, or a share link to send instead &mdash; no sign-up.</p>
''',
  faqs=[
   ('What should the subject line of an invoice email say?', 'Include the invoice number, your business name and the due date, e.g. &ldquo;Invoice INV-0042 from [Business] &mdash; due 20 Nov&rdquo;, so it&rsquo;s easy to find and act on.'),
   ('Should I attach the invoice as a PDF?', 'Yes &mdash; a PDF looks the same on any device and is easy to file. Name it clearly (Invoice-INV-0042.pdf). A share link is a good alternative when attachments are large or blocked.'),
   ('What do I write in an invoice email?', 'Keep it short: greet the client, state the invoice number, amount and due date, note that payment details are on the invoice, and offer to answer questions.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/payment-reminder-email','Payment reminder email templates'),('/en/blog/how-to-write-an-invoice','How to write an invoice')],
 ),
 dict(
  slug='common-invoice-mistakes', cat='Invoicing', tool='/en/invoice',
  title='10 Common Invoice Mistakes (And How to Avoid Them)',
  desc='The invoicing mistakes that cause late payments and disputes — missing details, vague due dates, wrong tax — and how to fix each.',
  date='2026-10-21',
  body='''
<p class="lead">Most late payments and billing disputes come down to a handful of avoidable invoice mistakes. Fix these and you&rsquo;ll get paid faster with fewer awkward conversations.</p>
<h2>The mistakes that cost you</h2>
<ul>
<li><b>No clear due date</b> &mdash; &ldquo;Net 30&rdquo; alone invites delay; write the actual date.</li>
<li><b>Missing invoice number</b> &mdash; makes tracking and (in VAT/GST systems) compliance harder.</li>
<li><b>Vague line items</b> &mdash; &ldquo;Services&rdquo; raises questions; describe the work.</li>
<li><b>Wrong or missing tax</b> &mdash; charging VAT/GST when not registered, or forgetting it when you should.</li>
<li><b>No payment instructions</b> &mdash; if they can&rsquo;t see how to pay, they won&rsquo;t.</li>
<li><b>Maths errors</b> &mdash; totals that don&rsquo;t add up erode trust.</li>
<li><b>Wrong client details</b> &mdash; wrong name or address can bounce the invoice around a finance team.</li>
<li><b>Sending it late</b> &mdash; invoice the day you finish, not weeks later.</li>
<li><b>No terms for late payment</b> &mdash; state any late fee up front.</li>
<li><b>No copy kept</b> &mdash; keep records for tax and follow-ups.</li>
</ul>
<h2>The simple fix</h2>
<p>Use a consistent template that includes all the essentials, double-check the totals and the client&rsquo;s details, write the real due date, and send it promptly. A good tool handles the maths and tax for you.</p>
<h2>Avoid them all, free</h2>
<p>Our <a href="/en/invoice">free invoice generator</a> includes every required field, calculates tax and totals automatically, and shows a due date and payment details &mdash; no sign-up.</p>
''',
  faqs=[
   ('Why are my invoices paid late?', 'The usual culprits are a vague due date, no payment instructions, unclear line items, or the invoice being sent late. Write the actual due date, make paying easy, describe the work, and invoice promptly.'),
   ('What is the most common invoice mistake?', 'Not stating a clear, specific due date &mdash; &ldquo;Net 30&rdquo; alone leaves it ambiguous. Always write the actual calendar date payment is due.'),
   ('How do I avoid errors on invoices?', 'Use a consistent template with all required fields, let a tool calculate tax and totals, double-check the client&rsquo;s details, and keep a copy of every invoice you send.'),
  ],
  related=[('/en/invoice','Free invoice generator'),('/en/blog/how-to-write-an-invoice','How to write an invoice'),('/en/blog/how-to-number-invoices','How to number invoices')],
 ),
]

FOOTER = '''<footer class="ft"><div class="in">
  <div class="cols">
    <div>
      <div class="brand"><img src="/logo.png" alt="Free BizDoc" style="height:26px;width:auto;display:block;filter:brightness(0) invert(1)"></div>
      <p>Free, no-sign-up business document generator. Invoices, estimates, receipts, purchase orders and packing slips as clean PDFs - generated in your browser.</p>
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
  <div class="bot">&copy; 2026 Free BizDoc</div>
</div></footer>'''

HEADER = ('<header class="hdr"><div class="in">\n'
  '  <a class="brand" href="/en/" style="text-decoration:none"><img src="/logo.png" alt="Free BizDoc" style="height:30px;width:auto;display:block"></a>\n'
  '  <span class="sp"></span>\n'
  '  <a class="pro" href="/?lang=ja" lang="ja" title="Japanese version">日本語</a>\n'
  '</div></header>')

ASTYLE = '''<style>
.ablog{max-width:760px;margin:0 auto;padding:0 20px 40px}
.bhero{margin-bottom:24px}
.bhero .in{max-width:760px;margin:0 auto;padding:16px 20px 0}
.bhero .bhero-img{display:block;width:100%;height:auto;aspect-ratio:1200/630;object-fit:cover;border-radius:16px;box-shadow:0 18px 42px -26px rgba(19,38,59,.55)}
.bhero .meta{font-size:13px;color:var(--mut,#5a6b80);margin:12px 2px 0}
.bhero .meta .cat{font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:var(--ac,#1766e6);font-size:11.5px}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.crumb{max-width:760px;margin:0 auto;padding:14px 20px 0;font-size:12.5px;color:var(--faint,#93a3b5)}
.crumb a{color:var(--mut,#5a6b80);text-decoration:none}.crumb a:hover{text-decoration:underline}
.ablog .lead{font-size:16.5px;line-height:1.75;color:var(--ink);margin:0 0 22px}
.ablog h2{font-size:21px;font-weight:900;letter-spacing:-.01em;margin:30px 0 12px}
.ablog p{font-size:15.5px;line-height:1.8;color:#24303d;margin:0 0 15px}
.ablog ul{margin:0 0 18px;padding-left:22px}
.ablog li{font-size:15.5px;line-height:1.75;color:#24303d;margin:0 0 8px}
.ablog a{color:var(--ac,#1766e6);font-weight:600}
.ablog .note{background:#fff6ec;border:1px solid #f3dcc0;border-radius:12px;padding:13px 16px;margin:18px 0;font-size:14px;color:#7a5a2e;line-height:1.7}
.bfaq{max-width:760px;margin:36px auto 0;padding:0 20px}
.bfaq h2{font-size:21px;font-weight:900;margin:0 0 14px}
.bfaq .q{border-top:1px solid var(--bd,#e6e8ec);padding:16px 2px}
.bfaq .q h3{font-size:15.5px;font-weight:800;margin:0 0 6px}
.bfaq .q p{font-size:14.5px;color:var(--mut,#5a6b80);line-height:1.75;margin:0}
.brel{max-width:760px;margin:34px auto 0;padding:22px 20px 0;border-top:1px solid var(--bd,#e6e8ec)}
.brel h2{font-size:16px;font-weight:900;margin:0 0 12px}
.brel .rl{display:flex;flex-wrap:wrap;gap:10px}
.brel a{font-size:13.5px;font-weight:700;color:var(--ac,#1766e6);background:#eef4ff;border:1px solid #d9e6fb;border-radius:999px;padding:9px 15px;text-decoration:none}
.brel a:hover{background:#e2edff}
.bcta{max-width:760px;margin:26px auto 0;padding:0 20px}
.bcta a{display:block;text-align:center;background:linear-gradient(120deg,var(--ac,#1766e6),#2f8cf0);color:#fff;font-weight:800;font-size:15px;border-radius:13px;padding:15px;text-decoration:none}
</style>'''


def head(a, url, date_iso):
    title = a['title'].replace('&rsquo;', "’").replace('&amp;', '&')
    art_ld = {
      "@context": "https://schema.org", "@type": "Article",
      "headline": _strip(a['title']), "description": a['desc'],
      "datePublished": date_iso, "dateModified": date_iso,
      "author": {"@type": "Organization", "name": "Free BizDoc"},
      "publisher": {"@type": "Organization", "name": "Free BizDoc", "logo": {"@type": "ImageObject", "url": BASE + "/logo.png"}},
      "mainEntityOfPage": url, "inLanguage": "en"
    }
    crumb_ld = {
      "@context": "https://schema.org", "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/en/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + "/en/blog"},
        {"@type": "ListItem", "position": 3, "name": _strip(a['title']), "item": url},
      ]
    }
    faq_ld = {
      "@context": "https://schema.org", "@type": "FAQPage",
      "mainEntity": [{"@type": "Question", "name": _strip(q), "acceptedAnswer": {"@type": "Answer", "text": _strip(ans)}} for q, ans in a['faqs']]
    }
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<title>{a["title"]}｜Free BizDoc</title>\n'
      f'<meta name="description" content="{a["desc"]}">\n'
      f'<link rel="canonical" href="{url}">\n'
      f'<link rel="alternate" hreflang="en" href="{url}">\n'
      f'<link rel="alternate" hreflang="x-default" href="{url}">\n'
      '<link rel="icon" href="/favicon.ico" sizes="any">\n'
      '<meta property="og:type" content="article">\n<meta property="og:site_name" content="Free BizDoc">\n'
      '<meta property="og:locale" content="en_US">\n'
      f'<meta property="og:title" content="{_strip(a["title"])}">\n<meta property="og:description" content="{a["desc"]}">\n'
      f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{BASE}/en/blog/og/{a["slug"]}.jpg">\n'
      '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
      f'<meta name="twitter:image" content="{BASE}/en/blog/og/{a["slug"]}.jpg">\n'
      '<link rel="stylesheet" href="/suite.css?v=20261017d">\n'
      f'<script type="application/ld+json">{json.dumps(art_ld, ensure_ascii=False)}</script>\n'
      f'<script type="application/ld+json">{json.dumps(crumb_ld, ensure_ascii=False)}</script>\n'
      f'<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>\n'
      + ASTYLE + '\n</head>\n<body>')


def _strip(s):
    return (s.replace('&amp;', '&').replace('&rsquo;', '’').replace('&ldquo;', '“')
             .replace('&rdquo;', '”').replace('&mdash;', '—'))


def fmt_date(iso):
    y, m, d = iso.split('-')
    mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(m)-1]
    return f'{mon} {int(d)}, {y}'


def article_html(a, draft=False):
    url = f"{BASE}/en/blog/{a['slug']}"
    c1, c2 = CAT_COLOR.get(a['cat'], CAT_COLOR['Guides'])
    date_iso = '__PUBDATE__' if draft else a['date']
    date_disp = '__PUBDATE_EN__' if draft else fmt_date(a['date'])
    hero = (f'<section class="bhero"><div class="in">'
      f'<img class="bhero-img" src="/en/blog/og/{a["slug"]}.jpg" alt="" width="1200" height="630" fetchpriority="high">'
      f'<h1 class="sr-only">{a["title"]}</h1>'
      f'<div class="meta"><span class="cat">{a["cat"]}</span> &middot; Free BizDoc &middot; {date_disp}</div>'
      f'</div></section>')
    crumb = ('<nav class="crumb"><a href="/en/">Home</a> &rsaquo; <a href="/en/blog">Blog</a> &rsaquo; '
      + _strip(a['title']) + '</nav>')
    faqs = ''.join(f'<div class="q"><h3>{q}</h3><p>{ans}</p></div>' for q, ans in a['faqs'])
    faq = f'<section class="bfaq"><h2>Frequently asked questions</h2>{faqs}</section>'
    rel = ('<section class="brel"><h2>Related</h2><div class="rl">'
      + ''.join(f'<a href="{u}">{t}</a>' for u, t in a['related']) + '</div></section>')
    pre = ''
    if draft:
        pre = (f'<!--ENCARD tag={a["cat"]} | h2={a["title"]} | desc={a["desc"]} '
               f'| c1={c1} | c2={c2}-->\n')
    parts = [pre + head(a, url, date_iso), HEADER, crumb, hero,
      f'<article class="ablog">{a["body"]}</article>', faq, rel, FOOTER,
      f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


def index_html():
    url = f"{BASE}/en/blog"
    desc = 'Practical guides on invoicing, quoting and getting paid for freelancers and small businesses in the US, UK, Australia and Canada.'
    cards = ''
    for a in ARTICLES:
        c1, c2 = CAT_COLOR.get(a['cat'], CAT_COLOR['Guides'])
        cards += (f'<a class="bcard" href="/en/blog/{a["slug"]}">'
          f'<span class="bthumb"><img src="/en/blog/og/{a["slug"]}.jpg" alt="" loading="lazy" width="1200" height="630"></span>'
          f'<span class="bbody"><span class="tag">{a["cat"]}</span><h2>{a["title"]}</h2><p>{a["desc"]}</p>'
          f'<span class="go">Read &rarr;</span></span></a>')
    css = ('<style>'
      '.blog-wrap{max-width:1080px;margin:0 auto;padding:36px 20px 44px}'
      '.blog-head{text-align:center;max-width:620px;margin:0 auto 30px}'
      '.blog-head h1{font-size:clamp(26px,4.4vw,36px);font-weight:900;letter-spacing:-.02em;margin:0 0 10px}'
      '.blog-head p{font-size:15.5px;color:var(--mut,#5a6b80);line-height:1.7;margin:0}'
      '.bgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}'
      '.bcard{position:relative;display:flex;flex-direction:column;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);overflow:hidden;transition:.15s}'
      '.bcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}'
      '.bcard .bthumb{display:block;aspect-ratio:1200/630;background:#0b1220;overflow:hidden}'
      '.bcard .bthumb img{width:100%;height:100%;object-fit:cover;display:block}'
      '.bcard .bbody{padding:15px 18px 16px}'
      '.bcard .tag{display:inline-block;font-size:11.5px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;color:var(--ac,#1766e6);background:#eef4ff;border-radius:999px;padding:4px 11px;margin:0 0 9px}'
      '.bcard h2{font-size:17px;font-weight:800;line-height:1.35;margin:0 0 7px}'
      '.bcard p{font-size:13.5px;color:var(--mut,#5a6b80);line-height:1.6;margin:0 0 11px}'
      '.bcard .go{font-size:13px;font-weight:800;color:var(--ac,#1766e6)}'
      '</style>')
    head_html = ('<!doctype html>\n<html lang="en">\n<head>\n'
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      '<title>Blog — Invoicing &amp; small-business guides｜Free BizDoc</title>\n'
      f'<meta name="description" content="{desc}">\n'
      f'<link rel="canonical" href="{url}">\n'
      f'<link rel="alternate" hreflang="en" href="{url}">\n'
      '<link rel="alternate" hreflang="ja" href="https://free-bizdocs.com/blog">\n'
      f'<link rel="alternate" hreflang="x-default" href="{url}">\n'
      '<link rel="icon" href="/favicon.ico" sizes="any">\n'
      '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Free BizDoc">\n'
      '<meta property="og:locale" content="en_US">\n'
      '<meta property="og:title" content="Blog — Invoicing &amp; small-business guides">\n'
      f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{BASE}/og.jpg">\n'
      '<link rel="stylesheet" href="/suite.css?v=20261017d">\n'
      + css + '\n</head>\n<body>')
    parts = [head_html, HEADER,
      '<section class="blog-wrap"><div class="blog-head"><h1>Free BizDoc Blog</h1>'
      f'<p>{desc}</p></div><div class="bgrid" id="blist">{cards}</div></section>',
      FOOTER, f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)


os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, '_drafts'), exist_ok=True)
for a in ARTICLES:
    with open(os.path.join(OUT, a['slug'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(article_html(a))
    print('wrote en/blog/%s.html' % a['slug'])
# en/blog.html は初回のみ生成。以後は自動公開パイプラインがカードを挿入して維持するため、
# 再生成でパイプライン追加分を消さないよう、既存なら上書きしない（--force-index で強制）。
_idx_path = os.path.join(ROOT, 'en', 'blog.html')
import sys as _sys
if (not os.path.exists(_idx_path)) or ('--force-index' in _sys.argv):
    with open(_idx_path, 'w', encoding='utf-8') as f:
        f.write(index_html())
    print('wrote en/blog.html')
else:
    print('skip en/blog.html (exists; pipeline-maintained — use --force-index to regenerate)')
for a in DRAFTS:
    dp = os.path.join(OUT, '_drafts', a['slug'] + '.html')
    # 既に公開済みなら draft を再生成しない（二重化防止）
    if os.path.exists(os.path.join(OUT, a['slug'] + '.html')):
        continue
    with open(dp, 'w', encoding='utf-8') as f:
        f.write(article_html(a, draft=True))
    print('wrote en/blog/_drafts/%s.html' % a['slug'])

#!/usr/bin/env python3
# Generates the English blog: /en/blog index + /en/blog/<slug> article pages.
# English-market content (not translations of the Japanese blog). Inline gradient
# hero (no external image needed), suite.css + shared siteheader-en.js header.
# Usage: python3 build-en-blog.py   (run from ~/seikyu-hub-demo)
import os, json, datetime, html as _html

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'en', 'blog')
BASE = 'https://free-bizdocs.com'
V = datetime.date.today().strftime('%Y%m%d') + 'g'  # bump on siteheader/asset change to bust cache

# Brand accent per category (hero gradient)
CAT_COLOR = {
  'Invoicing': ('#1766e6', '#36b0f0'),
  'Getting paid': ('#0f8a5f', '#13a06f'),
  'Quoting': ('#7a39c4', '#a46be0'),
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
.bhero{color:#fff;border-radius:0 0 20px 20px;margin-bottom:26px}
.bhero .in{max-width:760px;margin:0 auto;padding:30px 20px 34px}
.bhero .cat{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;background:rgba(255,255,255,.18);padding:5px 12px;border-radius:999px;margin-bottom:12px}
.bhero h1{font-size:clamp(24px,4.2vw,34px);font-weight:900;letter-spacing:-.02em;line-height:1.25;margin:0 0 12px}
.bhero .meta{font-size:13px;opacity:.9}
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
      f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{BASE}/og.jpg">\n'
      '<meta name="twitter:card" content="summary_large_image">\n'
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
    hero = (f'<section class="bhero" style="background:linear-gradient(120deg,{c1},{c2})"><div class="in">'
      f'<span class="cat">{a["cat"]}</span><h1>{a["title"]}</h1>'
      f'<div class="meta">Free BizDoc &middot; {date_disp}</div></div></section>')
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
          f'<span class="cstripe" style="background:linear-gradient(120deg,{c1},{c2})"></span>'
          f'<span class="tag">{a["cat"]}</span><h2>{a["title"]}</h2><p>{a["desc"]}</p>'
          f'<span class="go">Read &rarr;</span></a>')
    css = ('<style>'
      '.blog-wrap{max-width:1080px;margin:0 auto;padding:36px 20px 44px}'
      '.blog-head{text-align:center;max-width:620px;margin:0 auto 30px}'
      '.blog-head h1{font-size:clamp(26px,4.4vw,36px);font-weight:900;letter-spacing:-.02em;margin:0 0 10px}'
      '.blog-head p{font-size:15.5px;color:var(--mut,#5a6b80);line-height:1.7;margin:0}'
      '.bgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}'
      '.bcard{position:relative;display:block;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;padding:22px 22px 18px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);overflow:hidden;transition:.15s}'
      '.bcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}'
      '.bcard .cstripe{position:absolute;top:0;left:0;right:0;height:5px}'
      '.bcard .tag{display:inline-block;font-size:11.5px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;color:var(--ac,#1766e6);background:#eef4ff;border-radius:999px;padding:4px 11px;margin:6px 0 10px}'
      '.bcard h2{font-size:17.5px;font-weight:800;line-height:1.35;margin:0 0 8px}'
      '.bcard p{font-size:13.5px;color:var(--mut,#5a6b80);line-height:1.6;margin:0 0 12px}'
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

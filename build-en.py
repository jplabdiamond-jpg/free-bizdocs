#!/usr/bin/env python3
# Generates the English tool pages under /en/ from one template.
# Usage: python3 build-en.py   (run from ~/seikyu-hub-demo)
import json, os, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'en')
V = datetime.date.today().strftime('%Y%m%d') + 'p'  # bump suffix on each JS/asset change to bust browser cache
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
  tags=['No sign-up','Payment method','PAID stamp','Tax itemized','Instant PDF']),
 dict(slug='purchase-order', kind='po', ja='/purchase-order', title='Free Purchase Order Template - Create a PO PDF Online (No Sign-Up)',
  desc='Create a purchase order with PO number, vendor, ship-to address, delivery date and itemized lines - free PDF, no account. US / UK / AU / CA tax handled automatically.',
  h1='Free Purchase Order Generator', ey='Free - No sign-up - PO number - Ship To',
  lead='Send suppliers a clear purchase order: PO number, vendor, ship-to address, required delivery date, itemized lines and the order total.',
  tags=['No sign-up','PO number','Ship-to address','Delivery date','Instant PDF']),
 dict(slug='packing-slip', kind='delivery', ja='/delivery', title='Free Packing Slip & Delivery Note Template - PDF Download (No Sign-Up)',
  desc='Create a packing slip or delivery note listing the items shipped, quantities, PO number and ship-to address, with a signature line for proof of delivery. Free PDF, no account.',
  h1='Free Packing Slip &amp; Delivery Note Generator', ey='Free - No sign-up - No prices - Signature line',
  lead='List what is in the shipment - without prices - plus the ship-to address, PO or order reference and a received-by signature line for proof of delivery.',
  tags=['No sign-up','No prices shown','PO / order ref.','Received-by signature','Instant PDF']),
 dict(slug='credit-note', kind='credit', title='Free Credit Note &amp; Credit Memo Generator - PDF Download (No Sign-Up)',
  desc='Create a credit note (credit memo in the US) to cancel or reduce an invoice, and download it as a PDF - free, no account. References the original invoice, with VAT, GST and sales tax for US / UK / AU / CA.',
  h1='Free Credit Note Generator', ey='Free - No sign-up - Credit Note / Credit Memo',
  lead='Issue a credit note against an invoice you have already sent - to correct an overcharge, handle a return, or apply a discount. Reference the original invoice number and the tax is reversed at the right rate for your country.',
  tags=['No sign-up','Links to the invoice','VAT / GST / sales tax','US &ldquo;Credit Memo&rdquo;','Instant PDF']),
 dict(slug='proforma-invoice', kind='proforma', title='Free Pro Forma Invoice Generator - Download a Proforma PDF (No Sign-Up)',
  desc='Create a pro forma invoice to quote a price or request advance payment before you supply - free PDF, no account. Clearly marked &ldquo;not a tax invoice&rdquo;, with US / UK / AU / CA tax shown for reference.',
  h1='Free Pro Forma Invoice Generator', ey='Free - No sign-up - Advance billing / customs',
  lead='Send a pro forma invoice before the sale is final - to confirm the price, request a deposit, or support a customs or import declaration. It is clearly marked as not a tax invoice and carries no payment-due status.',
  tags=['No sign-up','Marked &ldquo;not a tax invoice&rdquo;','Deposits &amp; customs','Converts to an invoice','Instant PDF']),
 dict(slug='sales-order', kind='salesorder', title='Free Sales Order &amp; Order Confirmation Generator - PDF (No Sign-Up)',
  desc='Create a sales order or order confirmation to acknowledge a customer order - the seller-side counterpart to a purchase order. Free PDF, no account, with ship-to, delivery date and US / UK / AU / CA tax.',
  h1='Free Sales Order Generator', ey='Free - No sign-up - Order confirmation',
  lead='Acknowledge a customer order with a sales order (or order confirmation): confirm the items, agreed prices, ship-to address and delivery date, and reference their PO number so both sides can match the paperwork.',
  tags=['No sign-up','Confirms an order','References their PO','Ship-to &amp; delivery','Instant PDF']),
 dict(slug='timesheet', kind='timesheet', title='Free Timesheet Generator - Download a Timesheet PDF (No Sign-Up)',
  desc='Create a timesheet logging hours worked by date, with an hourly rate and totals, and download it as a PDF - free, no account. Convert it to an invoice in one click. US / UK / AU / CA currencies.',
  h1='Free Timesheet Generator', ey='Free - No sign-up - Hours x rate',
  lead='Log your hours by date and task, set your hourly rate, and get a clean timesheet PDF with total hours and the amount. Convert it straight into an invoice when it is time to bill.',
  tags=['No sign-up','Hours x rate','Total hours','Convert to invoice','Instant PDF']),
 dict(slug='work-order', kind='workorder', title='Free Work Order Template - Create a Job Sheet PDF (No Sign-Up)',
  desc='Create a work order or job sheet with the customer, service address, scheduled date, labor and parts, and sign-off lines. Free PDF, no account. US / UK / AU / CA tax handled automatically.',
  h1='Free Work Order Generator', ey='Free - No sign-up - Job sheet / sign-off',
  lead='Dispatch and document a job: the customer, the service address, the scheduled date, the labor and parts with prices, plus authorization and completion sign-off lines.',
  tags=['No sign-up','Service address','Labor &amp; parts','Sign-off lines','Instant PDF']),
 dict(slug='expense-report', kind='expense', title='Free Expense Report &amp; Expense Claim Generator - PDF (No Sign-Up)',
  desc='Create an expense report (expense claim) listing dated expenses by category with a reimbursement total and an approval line. Free PDF, no account. US / UK / AU / CA currencies.',
  h1='Free Expense Report Generator', ey='Free - No sign-up - Reimbursement claim',
  lead='List your business expenses by date and category, total the reimbursement due, and add an approval line. Submit the PDF to whoever signs off your claim.',
  tags=['No sign-up','By date &amp; category','Reimbursement total','Approval line','Instant PDF']),
 dict(slug='bill-of-sale', kind='billofsale', title='Free Bill of Sale Template - Create a Bill of Sale PDF (No Sign-Up)',
  desc='Create a bill of sale recording the transfer of goods from seller to buyer, with the item description, sale price, date, as-is terms and signature lines for both parties. Free PDF, no account.',
  h1='Free Bill of Sale Generator', ey='Free - No sign-up - Seller &amp; buyer sign',
  lead='Record a private sale: the seller, the buyer, the item(s) sold, the price and date, an as-is statement, and signature lines for both parties - a simple proof of the transfer of ownership.',
  tags=['No sign-up','Seller &amp; buyer','As-is terms','Both-party signatures','Instant PDF']),
 dict(slug='donation-receipt', kind='donation', title='Free Donation Receipt Generator - Nonprofit Tax Receipt PDF (No Sign-Up)',
  desc='Create a donation receipt for a nonprofit or charity, with the donor, amount, date, tax-exempt ID and the required "no goods or services" statement. Free PDF, no account.',
  h1='Free Donation Receipt Generator', ey='Free - No sign-up - Nonprofit / charity',
  lead='Thank a donor and give them what they need at tax time: the amount, the date, your organisation&rsquo;s tax-exempt ID, and the statement that no goods or services were provided in exchange.',
  tags=['No sign-up','Donor &amp; amount','Tax-exempt ID','&ldquo;No goods&rdquo; statement','Instant PDF']),
]

ARTICLES = {
 'invoice': '''<p class="lead">An invoice is the document you send to request payment for goods or services. This free invoice generator builds a clean, professional PDF with everything an accounts-payable team expects: a unique invoice number, issue and due dates, itemized lines, tax, the total due and your payment details.</p>
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
<ul><li>Your business name, address and tax ID (where applicable)</li><li>A receipt number and the date of payment</li><li>Who paid (&ldquo;Received From&rdquo;)</li><li>What was paid for - itemized lines, tax and total</li><li>The <b>payment method</b> (cash, card, cheque, bank transfer) and a &ldquo;paid&rdquo; indication</li></ul>
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
 'credit-note': '''<p class="lead">A credit note - called a <b>credit memo</b> in the US - reduces or cancels an amount a customer owes on an invoice you already issued. You send one when you overcharged, when goods are returned, when you agree a post-sale discount, or when you need to correct a mistake on an invoice. It references the original invoice so both sides&rsquo; books stay matched.</p>
<h2>When to issue a credit note</h2>
<ul><li>You invoiced the wrong amount, quantity or tax rate</li><li>The customer returned goods or cancelled part of an order</li><li>You agreed a discount, rebate or goodwill adjustment after invoicing</li><li>A duplicate invoice was sent and needs to be reversed</li></ul>
<h2>What to put on a credit note</h2>
<ul><li>Your business details and tax ID, exactly as on the original invoice</li><li>The word &ldquo;Credit Note&rdquo; (or &ldquo;Credit Memo&rdquo; in the US), a unique number and the date</li><li>The <b>original invoice number</b> it relates to</li><li>The lines being credited, with the same tax treatment as the invoice</li><li>The total credit - and whether it is refunded or applied to a future invoice</li></ul>
<h2>Country notes this tool handles</h2>
<ul><li><b>United States</b> - the usual term is <b>credit memo</b>; sales tax charged on the original invoice is reversed on the same lines.</li><li><b>United Kingdom</b> - a VAT credit note reverses the VAT at the rate originally charged and should reference the original invoice; keep it for your VAT records.</li><li><b>Australia</b> - a credit note that adjusts GST is sometimes called an <b>adjustment note</b>; it reverses the 10% GST applied on the original tax invoice.</li><li><b>Canada</b> - GST/HST (and PST/QST) charged on the original invoice is credited back at the province&rsquo;s rate.</li></ul>
<div class="note">A credit note never increases what the customer owes - to charge more, issue a new invoice. Confirm how VAT/GST adjustments should be recorded with your accountant.</div>
<h2>How to create a free credit note</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the customer and the original invoice number it credits</span></div><div class="step"><span class="n">3</span><span class="t">List the lines being credited - tax is reversed automatically</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF, or start it from the matching invoice in one click</span></div></div>''',
 'proforma-invoice': '''<p class="lead">A pro forma invoice is a preliminary bill sent <b>before</b> a sale is finalised. It shows the buyer exactly what the goods or services will cost - so they can approve the purchase, pay a deposit, arrange finance, or clear customs - but it is not a demand for payment and it is not a tax invoice. When the order is confirmed you replace it with a real invoice.</p>
<h2>When a pro forma invoice is used</h2>
<ul><li>To quote a committed price the buyer can raise a purchase order against</li><li>To request a <b>deposit or advance payment</b> before work or shipping begins</li><li>For <b>international shipments</b> - customs and freight forwarders use it to value goods for import</li><li>So a buyer&rsquo;s finance team can set up the supplier and approve the spend</li></ul>
<h2>Pro forma invoice vs invoice vs quote</h2>
<p>A quote is an offer of a price. A pro forma invoice looks like the final invoice - same layout, line items and totals - but is explicitly marked &ldquo;pro forma&rdquo; so it is clear that no tax point has been created and no payment is yet legally due. A true (tax) invoice is the one that triggers VAT/GST accounting and the obligation to pay. This tool prints the &ldquo;not a tax invoice&rdquo; wording for you and lets you convert it to a real invoice with one click.</p>
<div class="note">Because a pro forma is not a tax invoice, buyers generally cannot reclaim VAT/GST from it. Issue the final invoice once payment or the order is confirmed.</div>
<h2>How to create a free pro forma invoice</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the buyer, a validity date and any advance-payment details</span></div><div class="step"><span class="n">3</span><span class="t">Add the items, quantities and prices - tax is shown for reference</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF, then convert it to a real invoice when the order is confirmed</span></div></div>''',
 'sales-order': '''<p class="lead">A sales order (or order confirmation) is the document the <b>seller</b> sends back to a customer to acknowledge an order and confirm the details before fulfilling it. It is the mirror image of a purchase order: the buyer issues a PO, and you reply with a sales order quoting their PO number, the agreed items and prices, the ship-to address and the delivery date.</p>
<h2>What to include on a sales order</h2>
<ul><li>Your business details and a unique <b>sales order number</b></li><li>The <b>customer</b> and their billing address</li><li>The <b>ship-to</b> address and the expected <b>delivery date</b></li><li>The customer&rsquo;s <b>PO number</b> for cross-reference</li><li>Itemised lines with agreed quantities and unit prices, tax and the order total</li></ul>
<h2>Sales order vs purchase order vs invoice</h2>
<p>The <b>purchase order</b> is raised by the buyer to place the order. The <b>sales order</b> is your acknowledgement that you accept it and will supply on the stated terms. The <b>invoice</b> comes later, once the goods or services are delivered, to request payment. Keeping the same number thread across all three lets both sides match the paperwork. Create the matching invoice or packing slip from the same details with one click.</p>
<h2>How to create a free sales order</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the customer, their PO number, ship-to address and delivery date</span></div><div class="step"><span class="n">3</span><span class="t">Add the items and agreed prices</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF and send it to confirm the order</span></div></div>''',
 'timesheet': '''<p class="lead">A timesheet records the hours you worked so they can be approved and billed. For freelancers and contractors who charge by the hour, it is the backup for an invoice: each line is a date and task, the hours, your rate and the amount, with the total hours and total due at the bottom.</p>
<h2>What to include on a timesheet</h2>
<ul><li>Your name or business, and the client the hours are for</li><li>The <b>period</b> (for example the week ending date) and a timesheet number</li><li>One line per day or task: the <b>date and description</b>, <b>hours</b> and <b>rate</b></li><li><b>Total hours</b> and the total amount at the agreed rate</li><li>Space for approval, if your client signs off hours before paying</li></ul>
<h2>From timesheet to invoice</h2>
<p>Because a timesheet is just hours priced at a rate, it converts cleanly into an invoice. Log the week here, then switch to &ldquo;Invoice&rdquo; under the preview to bill the same lines with a due date and your payment details. No tax is applied to the timesheet itself &mdash; add it on the invoice if you charge it.</p>
<h2>How to create a free timesheet</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your currency and enter your details and the client</span></div><div class="step"><span class="n">2</span><span class="t">Set the week-ending date and your hourly rate</span></div><div class="step"><span class="n">3</span><span class="t">Add a line per day with the hours worked</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF, or convert it to an invoice to bill</span></div></div>''',
 'work-order': '''<p class="lead">A work order (or job sheet) authorises and documents a job &mdash; common in trades like repair, maintenance, installation and field service. It tells the technician what to do and where, lists the labor and parts, and carries sign-off lines so the customer can authorise the work and confirm it was completed.</p>
<h2>What to include on a work order</h2>
<ul><li>Your business details and a unique <b>work order number</b></li><li>The <b>customer</b> and the <b>service address</b> where the work happens</li><li>The <b>scheduled date</b> and a description of the work requested (use the notes)</li><li>Lines for <b>labor and parts</b> with quantities and prices, tax and the total</li><li><b>Sign-off</b> lines: authorised by the customer, and completed by the technician</li></ul>
<h2>Work order, invoice and the paper trail</h2>
<p>The work order comes first &mdash; it scopes and authorises the job. When the work is done, convert it to an invoice under the preview to bill the same labor and parts. Keeping the work order number on the invoice lets the customer match what they approved to what they are charged.</p>
<h2>How to create a free work order</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your country and enter your business details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the customer, service address and scheduled date</span></div><div class="step"><span class="n">3</span><span class="t">List the labor and parts; note the work requested</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF for sign-off, then convert to an invoice when done</span></div></div>''',
 'expense-report': '''<p class="lead">An expense report (or expense claim) is how an employee or contractor asks to be reimbursed for business costs they paid out of pocket. It lists each expense by date and category with the amount, totals the reimbursement due, and leaves a line for an approver to sign off.</p>
<h2>What to include on an expense report</h2>
<ul><li>Who is claiming, and who it is <b>submitted to</b> (the employer or client)</li><li>The <b>period</b> the expenses cover and a report number</li><li>One line per expense: the <b>date, category and description</b>, and the amount</li><li>The <b>total reimbursement</b> due</li><li>An <b>approval</b> line &mdash; and keep the receipts to attach</li></ul>
<h2>Tips for a claim that gets approved</h2>
<p>Group expenses by category (travel, meals, supplies), put the date and merchant in the description, and keep a receipt for every line. Totals should match the receipts exactly. This tool keeps the layout simple &mdash; description and amount &mdash; so the claim is quick to scan and sign.</p>
<h2>How to create a free expense report</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your currency and enter your name and who it is submitted to</span></div><div class="step"><span class="n">2</span><span class="t">Set the period and report number</span></div><div class="step"><span class="n">3</span><span class="t">Add a line per expense with the date, category and amount</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF and attach your receipts</span></div></div>''',
 'bill-of-sale': '''<p class="lead">A bill of sale is a short document that records the sale of goods from a seller to a buyer and the transfer of ownership. It is common for private sales of vehicles, equipment, furniture and other second-hand items. It states who sold what to whom, for how much, on what date, and that the item is sold as-is.</p>
<h2>What to include on a bill of sale</h2>
<ul><li>The <b>seller</b> and the <b>buyer</b> (names and addresses)</li><li>A clear <b>description of the item(s)</b> &mdash; include a serial or VIN in the description where relevant</li><li>The <b>sale price</b> and the <b>date of sale</b></li><li>An <b>as-is</b> statement and that the seller is the lawful owner</li><li><b>Signatures</b> from both the seller and the buyer</li></ul>
<h2>When you need one</h2>
<p>A bill of sale is the buyer&rsquo;s proof of purchase and the seller&rsquo;s proof that ownership (and liability) has passed. For vehicles it is often needed to register the change of ownership. Requirements vary by state, province and country, so check what your local authority asks for &mdash; this tool gives you a clean, general-purpose bill of sale to start from.</p>
<div class="note">This is a general template, not legal advice. For vehicles and high-value items, confirm the wording and any notarisation your jurisdiction requires.</div>
<h2>How to create a free bill of sale</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your currency and enter the seller (your) details</span></div><div class="step"><span class="n">2</span><span class="t">Enter the buyer and the date of sale</span></div><div class="step"><span class="n">3</span><span class="t">Describe the item(s) and the sale price</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF and have both parties sign</span></div></div>''',
 'donation-receipt': '''<p class="lead">A donation receipt is the acknowledgement a nonprofit or charity gives a donor for a contribution. Donors need it for their tax records, and in the US a written acknowledgement is required for gifts of $250 or more. It shows the organisation, the donor, the amount, the date, and the statement about whether anything was given in return.</p>
<h2>What to include on a donation receipt</h2>
<ul><li>Your <b>organisation&rsquo;s name</b> and <b>tax-exempt ID</b> (EIN in the US; charity number elsewhere)</li><li>The <b>donor&rsquo;s name</b> and the <b>date</b> of the donation</li><li>The <b>amount</b> of a cash gift, or a description of a non-cash gift (without stating its value)</li><li>A statement of whether <b>goods or services</b> were provided in exchange &mdash; and their value if so</li><li>An authorised signature</li></ul>
<h2>The &ldquo;no goods or services&rdquo; statement</h2>
<p>US tax rules require the receipt to say whether the donor received anything in return. If they did not, the receipt must state that &mdash; this tool prints &ldquo;No goods or services were provided in exchange for this donation&rdquo; for you. If the donor received something (an event ticket, a gift), you must describe it and give a good-faith estimate of its value, because only the amount above that is deductible.</p>
<div class="note">Rules differ by country and by the type and size of gift. Confirm your acknowledgement meets your tax authority&rsquo;s requirements.</div>
<h2>How to create a free donation receipt</h2>
<div class="steps"><div class="step"><span class="n">1</span><span class="t">Choose your currency and enter your organisation and its tax-exempt ID</span></div><div class="step"><span class="n">2</span><span class="t">Enter the donor and the date received</span></div><div class="step"><span class="n">3</span><span class="t">Add the donation amount</span></div><div class="step"><span class="n">4</span><span class="t">Download the PDF and send it to the donor</span></div></div>''',
}

FAQS = {
 'invoice': [('Is it free, with no sign-up?','Yes. You can create and download invoices without an account. To keep the service fast for everyone, the free version allows 2 PDF downloads per hour from the same network.'),
  ('Is my data stored anywhere?','No. The invoice content is never sent to our servers - the PDF is generated in your browser. Only your own business details are kept in your browser local storage so you do not have to retype them.'),
  ('Does it support VAT, GST and sales tax?','Yes. Pick United States (a sales tax rate you set), United Kingdom (VAT 20% / 5% / 0% / exempt), Australia (GST 10% / GST-free) or Canada (GST / HST / PST / QST by province). Tax is itemized per rate on the PDF.'),
  ('What paper size is the PDF?','US and Canada use Letter (8.5 x 11 in). UK and Australia use A4.'),
  ('Can I turn an estimate into an invoice?','Yes. Under the preview, click the document you want - the same details are reused with a new number and today&rsquo;s date.'),
  ('Can I send the invoice without attaching a PDF?','Yes. &ldquo;Create a share link&rdquo; encodes the document in a URL. Your client opens it in a browser, sees the amount, due date and payment details, and can download the PDF.')],
 'estimate': [('What is the difference between an estimate and a quote?','An estimate is an approximate price that may change; a quote (or quotation) is a fixed price the customer can accept, valid for a set period. Say clearly which one you&rsquo;re issuing and include a &ldquo;valid until&rdquo; date.'),
  ('How long should a quote be valid?','Set a &ldquo;valid until&rdquo; date so prices don&rsquo;t stay open indefinitely &mdash; 14 to 30 days is common. After it expires you can re-issue with updated pricing.'),
  ('Is a quote legally binding?','Rules vary by country and contract, but a quote accepted by the customer is generally treated as an agreed price for the stated scope and validity period. An estimate is usually not binding. Say which one you are issuing and include your terms.'),
  ('Can I convert the estimate to an invoice?','Yes. Under the preview, click &ldquo;Invoice&rdquo; - the line items, customer and your details are carried over and a new invoice number is assigned.'),
  ('Does the PDF include tax?','Yes. Tax is calculated for the selected country (sales tax, VAT, GST or GST/HST) and shown separately from the subtotal.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'receipt': [('What information must a receipt include?','A receipt should show your business name and contact details, a receipt number and the date of payment, who paid, what was paid for, the amount, and the payment method (cash, card, bank transfer). Add tax if you charged it.'),
  ('Is a receipt proof of purchase?','Yes. A receipt is the document that proves a payment was made &mdash; customers use it for expense claims, warranties and bookkeeping, and you keep a copy for your records.'),
  ('Do receipts need to show tax?','For VAT- or GST-registered businesses, yes - a receipt that doubles as a tax invoice must itemize the tax. In the US, show sales tax if you charged it.'),
  ('Can I make a receipt from an invoice?','Yes. On the invoice page, click &ldquo;Receipt&rdquo; under the preview. The content is reused and marked as paid.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'purchase-order': [('What is a PO number and how do I create one?','A PO number is a unique reference for a purchase order so it can be matched to the supplier&rsquo;s invoice and delivery. Create your own sequence &mdash; for example PO-0001, PO-0002 &mdash; and quote it on all related documents.'),
  ('What is the three-way match?','Before paying, finance matches three documents: the purchase order (what was ordered), the packing slip (what arrived) and the invoice (what&rsquo;s charged). If all three agree, the invoice is approved.'),
  ('Who issues a purchase order - the buyer or the seller?','The buyer. The supplier then quotes the PO number on their invoice and delivery documents.'),
  ('Is a purchase order a contract?','Once accepted by the supplier it generally forms a binding order for the stated goods, prices and terms. Add your terms in the Terms box if you need specific conditions.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'packing-slip': [('What should a packing slip include?','Your business details, a packing-slip number, the customer&rsquo;s billing details and the ship-to address, the PO or order number, each item with the quantity shipped, the ship date, and a received-by/signature line. Prices are left off.'),
  ('Does a packing slip need to be signed?','Not legally, but a signature (or received-by line) is common so the recipient can confirm what arrived &mdash; useful as proof of delivery if there&rsquo;s a dispute.'),
  ('Should a packing slip show prices?','Usually not. It lists items and quantities only; prices go on the invoice. This tool hides the price and tax columns on packing slips automatically.'),
  ('What is the difference between a packing slip and a delivery note?','They serve the same purpose. &ldquo;Packing slip&rdquo; is the common term in the US and Canada, &ldquo;delivery note&rdquo; in the UK and Australia - the title changes with the country you select.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'credit-note': [('What is the difference between a credit note and a credit memo?','None &mdash; they are the same document. &ldquo;Credit memo&rdquo; is the common US term and &ldquo;credit note&rdquo; is used in the UK, Australia and Canada. The title switches automatically to match the country you select.'),
  ('How do I cancel or reduce an invoice I already sent?','Issue a credit note that references the original invoice number. List the lines being credited; the tax is reversed at the same rate. You can either refund the amount or apply the credit to a future invoice.'),
  ('Does a credit note reverse VAT or GST?','Yes. The credit note reverses the VAT, GST or sales tax that was charged on the original invoice, at the same rate, so your tax records balance. In Australia a GST adjustment is sometimes called an adjustment note.'),
  ('Can I create a credit note from an invoice?','Yes. Under the preview, switch to &ldquo;Credit Note&rdquo; &mdash; the customer and line items carry over and you add the original invoice number it relates to.'),
  ('Should the amounts be negative?','No. List the credited lines as positive amounts; the document itself shows it is a credit, and the total is labelled &ldquo;Total Credit&rdquo;. This is the standard way credit notes are read.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'proforma-invoice': [('What is a pro forma invoice?','A preliminary invoice sent before a sale is final. It shows the full price so the buyer can approve the purchase, pay a deposit, or clear customs &mdash; but it is not a tax invoice and not a demand for payment. A real invoice follows once the order is confirmed.'),
  ('Can a customer pay from a pro forma invoice?','They can pay an agreed deposit or advance against it, but it does not create a payment obligation on its own. The document is marked &ldquo;not a tax invoice&rdquo; for clarity. Issue the final invoice once the order or payment is confirmed.'),
  ('Can I reclaim VAT or GST from a pro forma invoice?','Generally no. Because it is not a tax invoice, it does not create a tax point, so VAT/GST is usually not reclaimable from it. The tax shown is for reference &mdash; the final invoice is the one used for tax.'),
  ('Is a pro forma invoice used for customs?','Yes. For international shipments, customs and freight forwarders use a pro forma invoice to value the goods for import before the commercial invoice is issued.'),
  ('How do I turn it into a real invoice?','Under the preview, switch to &ldquo;Invoice&rdquo;. The same details carry over with a new invoice number and today&rsquo;s date.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'sales-order': [('What is a sales order?','A sales order (or order confirmation) is the seller&rsquo;s acknowledgement of a customer&rsquo;s order. It confirms the items, agreed prices, ship-to address and delivery date, and references the customer&rsquo;s PO number so both sides can match the paperwork.'),
  ('What is the difference between a sales order and a purchase order?','The buyer issues the purchase order to place the order; the seller replies with a sales order to confirm it will supply on those terms. The invoice comes later to request payment. A sales order references the buyer&rsquo;s PO number.'),
  ('Is an order confirmation the same as a sales order?','In most small businesses, yes &mdash; both acknowledge an accepted order and confirm its details before fulfilment. Use whichever term your customers expect; the layout is the same.'),
  ('Can I create an invoice from a sales order?','Yes. Once you have fulfilled the order, switch to &ldquo;Invoice&rdquo; under the preview &mdash; the items, customer and references carry over with a new invoice number.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'timesheet': [('What should a timesheet include?','Your name or business, the client, the period (e.g. week ending), and one line per day or task with the date, hours and rate. The PDF totals the hours and the amount due at your rate.'),
  ('Does the timesheet add tax?','No. A timesheet records hours and amounts only. If you charge sales tax or VAT, convert the timesheet to an invoice &mdash; tax is applied there.'),
  ('How do I turn a timesheet into an invoice?','Under the preview, switch to &ldquo;Invoice&rdquo;. The same lines carry over, and you can add a due date, payment terms and tax.'),
  ('How do I enter hours and rate?','Each line has an Hours field and a Rate field; the amount is hours x rate. Put the date and task in the description. The total hours appear in the summary.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'work-order': [('What is a work order?','A work order (or job sheet) authorises and documents a job: the customer, the service address, the scheduled date, the labor and parts, and sign-off lines for the customer to authorise and the technician to confirm completion.'),
  ('What is the difference between a work order and an invoice?','The work order comes first and authorises the job; the invoice comes after completion to request payment. Convert the work order to an invoice under the preview to bill the same labor and parts.'),
  ('Where do I put the work requested?','Use the Notes field for a description of the work requested or performed; it prints in a box on the PDF. Labor and parts go in the line items.'),
  ('Does a work order need signatures?','It is good practice. The PDF includes an &ldquo;authorised by (customer)&rdquo; line and a &ldquo;work completed by&rdquo; line so both the authorisation and the completion are on record.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'expense-report': [('What should an expense report include?','Who is claiming and who it is submitted to, the period covered, one line per expense (date, category, description, amount), the total reimbursement due, and an approval line. Keep a receipt for each line.'),
  ('What is the difference between an expense report and an expense claim?','They are the same thing &mdash; &ldquo;expense report&rdquo; is common in the US and Canada, &ldquo;expense claim&rdquo; in the UK and Australia. The title switches to match the country you select.'),
  ('Does the expense report calculate tax?','No. It simply totals the amounts you enter for reimbursement. Enter each expense as its final paid amount.'),
  ('Do I need to attach receipts?','Usually yes &mdash; most employers require a receipt for each expense. Submit the PDF with the receipts attached so the claim can be verified and approved.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'bill-of-sale': [('What is a bill of sale?','A short document recording the sale of goods from a seller to a buyer and the transfer of ownership. It states who sold what to whom, for how much, on what date, and that the item is sold as-is. Common for vehicles and second-hand equipment.'),
  ('Is a bill of sale legally binding?','Signed by both parties, it is evidence of the sale and the transfer of ownership. Specific requirements (and whether notarisation is needed) vary by state, province and country, so check your local rules.'),
  ('How do I include a VIN or serial number?','Put it in the item description along with make, model and condition. The description prints exactly as you enter it.'),
  ('Does a bill of sale include tax?','This template does not add tax &mdash; private sales are often not taxed, and where tax applies it is usually handled at registration. Enter the agreed sale price.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
 'donation-receipt': [('What should a donation receipt include?','Your organisation&rsquo;s name and tax-exempt ID, the donor&rsquo;s name, the date, the amount (for cash) or a description (for non-cash), and a statement of whether goods or services were provided in exchange.'),
  ('When is a donation receipt required?','In the US, a donor needs a written acknowledgement to claim a deduction for any single gift of $250 or more. Many charities issue receipts for all gifts as good practice. Rules differ by country.'),
  ('What is the "no goods or services" statement?','Tax rules require the receipt to say whether the donor received anything in return. If not, the receipt states so. If they did (an event, a gift), you must describe it and estimate its value &mdash; only the amount above that is deductible.'),
  ('Should the receipt state the value of a non-cash gift?','No. For in-kind donations you describe the item; the donor is responsible for valuing it. State a dollar amount only for cash contributions.'),
  ('Is it free?','Yes &mdash; no sign-up. The free version allows 2 PDF downloads per hour from the same network.')],
}
INDEX_FAQ = [('Is Free BizDoc free?','Yes. All five documents can be created and downloaded as PDFs without an account. The free version lets you download 2 PDFs per hour from the same network (shared office or home Wi-Fi counts as one).'),
 ('Which countries are supported?','The United States (sales tax), the United Kingdom (VAT), Australia (GST / tax invoice), and Canada (GST / HST / PST / QST). Currency, paper size, date format, and tax-ID labels switch automatically when you choose your country.'),
 ('Where is my data stored?','The document itself is never sent to us &mdash; the PDF is built in your browser. Only your business details are saved, and only in your own browser, so you don&rsquo;t have to retype them. A share link carries the document inside the link itself, not on our servers.')]

def faq_ld(faq):
    return json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}, ensure_ascii=False)

def head(p, url):
    app = json.dumps({"@context":"https://schema.org","@type":"WebApplication","name":p['h1'].replace('&amp;','&'),"applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"url":url,"inLanguage":"en"})
    faqj = faq_ld(FAQS.get(p['slug'], INDEX_FAQ))
    # Only cross-link a Japanese alternate for pages that have a JA counterpart.
    alt = f'<link rel="alternate" hreflang="en" href="{url}">\n'
    if p.get('ja'):
        alt += f'<link rel="alternate" hreflang="ja" href="{BASE}{p["ja"]}">\n'
    alt += f'<link rel="alternate" hreflang="x-default" href="{url}">\n'
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<title>{p["title"]}</title>\n<meta name="description" content="{p["desc"]}">\n'
      f'<link rel="canonical" href="{url}">\n'
      + alt +
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
    <div class="seg" id="seg"><button data-kind="invoice">Invoice</button><button data-kind="quote">Estimate / Quote</button><button data-kind="delivery">Packing Slip</button><button data-kind="po">Purchase Order</button><button data-kind="receipt">Receipt</button><button data-kind="credit">Credit Note</button><button data-kind="proforma">Pro Forma</button><button data-kind="salesorder">Sales Order</button><button data-kind="timesheet">Timesheet</button><button data-kind="workorder">Work Order</button><button data-kind="expense">Expense</button><button data-kind="billofsale">Bill of Sale</button><button data-kind="donation">Donation</button></div>

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
        <div class="hd"><span>Description</span><span id="th-qty">Qty</span><span id="th-price">Unit price (<span id="cur-lb">USD</span>)</span><span id="th-tax">Tax</span><span></span></div>
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
      <a href="/en/credit-note">Credit Note</a>
      <a href="/en/proforma-invoice">Pro Forma Invoice</a>
      <a href="/en/sales-order">Sales Order</a>
      <a href="/en/timesheet">Timesheet</a>
      <a href="/en/work-order">Work Order</a>
      <a href="/en/expense-report">Expense Report</a>
      <a href="/en/bill-of-sale">Bill of Sale</a>
      <a href="/en/donation-receipt">Donation Receipt</a>
    </div>
    <div class="col">
      <h4>More</h4>
      <a href="/en/invoice-templates">Invoice templates</a>
      <a href="/en/estimate-templates">Quote templates</a>
      <a href="/en/receipt-templates">Receipt templates</a>
      <a href="/en/blog">Blog</a>
      <a href="/en/compare">Compare tools</a>
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
      h1='Free business documents. No sign-up.', ey='Invoice &middot; Estimate &middot; Receipt &middot; Purchase Order &middot; Packing Slip',
      lead='Pick a document, choose your country, and fill in the details. Tax, currency, paper size, and dates are set correctly for the US, UK, Australia, and Canada. Download the PDF, or share it with a link &mdash; the document lives inside the link, not on our servers.',
      tags=['No sign-up','US / UK / AU / CA','Sales tax, VAT &amp; GST','Share by link','Instant PDF'])
    url = f"{BASE}/en/"
    cards = [('/en/invoice','Invoice','An itemized invoice with tax, a due date, payment terms, and your bank details.','Create an invoice'),
             ('/en/estimate','Estimate / Quote','A scope of work with pricing, a valid-until date, and an acceptance line.','Create an estimate'),
             ('/en/receipt','Receipt','Proof of payment showing the amount paid, the method, and a PAID stamp.','Create a receipt'),
             ('/en/purchase-order','Purchase Order','A PO with its number, the vendor, a ship-to address, and a delivery date.','Create a PO'),
             ('/en/packing-slip','Packing Slip / Delivery Note','The items and quantities shipped &mdash; no prices &mdash; with a received-by line.','Create a packing slip'),
             ('/en/credit-note','Credit Note / Credit Memo','Cancel or reduce an invoice &mdash; links to the original and reverses the tax.','Create a credit note'),
             ('/en/proforma-invoice','Pro Forma Invoice','A preliminary bill for deposits or customs &mdash; clearly not a tax invoice.','Create a pro forma'),
             ('/en/sales-order','Sales Order','Confirm a customer order &mdash; the seller-side reply to a purchase order.','Create a sales order'),
             ('/en/timesheet','Timesheet','Log hours by date at an hourly rate, with totals &mdash; converts to an invoice.','Create a timesheet'),
             ('/en/work-order','Work Order','Authorise and document a job &mdash; labor, parts and sign-off lines.','Create a work order'),
             ('/en/expense-report','Expense Report','Claim reimbursement for business costs by date and category.','Create an expense report'),
             ('/en/bill-of-sale','Bill of Sale','Record a private sale and the transfer of ownership, signed by both.','Create a bill of sale'),
             ('/en/donation-receipt','Donation Receipt','A nonprofit tax receipt with the donor, amount and required statement.','Create a donation receipt')]
    grid = ''.join(f'<a class="dcard" href="{u}"><h3>{t}</h3><p>{d}</p><span class="go">{c} &rarr;</span></a>' for u,t,d,c in cards)
    css = ('<style>.dgrid{max-width:1180px;margin:0 auto;padding:10px 20px 40px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}'
      '.dcard{display:block;background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:16px;padding:22px 22px 18px;text-decoration:none;color:inherit;box-shadow:0 10px 30px -22px rgba(19,38,59,.35);transition:.15s}'
      '.dcard:hover{transform:translateY(-2px);border-color:var(--ac,#1766e6)}.dcard h3{margin:0 0 6px;font-size:17px}.dcard p{margin:0 0 12px;font-size:13.5px;color:#5a6b7b;line-height:1.55}.dcard .go{font-size:13px;font-weight:800;color:var(--ac,#1766e6)}'
      '.regions{max-width:1180px;margin:0 auto;padding:0 20px 34px}'
      '.regions h2{font-size:clamp(18px,3vw,22px);font-weight:900;margin:0 0 14px}'
      '.rgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}'
      '.rgrid .rc{background:#fff;border:1px solid var(--bd,#e2eaf4);border-radius:14px;padding:15px 16px}'
      '.rgrid .rc b{display:block;font-size:14.5px;margin-bottom:4px}.rgrid .rc span{font-size:13px;color:#5a6b7b;line-height:1.6}</style>')
    regions = ('<div class="regions"><h2>Built for your country</h2><div class="rgrid">'
      '<div class="rc"><b>&#127482;&#127480; United States</b><span>Sales tax set per line, Net&nbsp;30 terms, Letter paper, USD.</span></div>'
      '<div class="rc"><b>&#127468;&#127463; United Kingdom</b><span>VAT at 20% / 5% / 0%, your VAT number, A4 paper, GBP.</span></div>'
      '<div class="rc"><b>&#127462;&#127482; Australia</b><span>GST 10%, your ABN, the title &ldquo;Tax Invoice&rdquo;, A4 paper, AUD.</span></div>'
      '<div class="rc"><b>&#127464;&#127462; Canada</b><span>GST / HST / PST / QST by province, your GST/HST number, Letter paper, CAD.</span></div>'
      '</div></div>')
    art = ('<article class="art"><p class="lead">Free BizDoc began in Japan as a free generator for Japanese business documents. The English edition isn&rsquo;t a translation of those forms &mdash; it follows the formats businesses actually use in each country: a US invoice with sales tax, a UK VAT invoice, an Australian tax invoice, and a Canadian GST/HST invoice, plus estimates, receipts, purchase orders, and packing slips.</p>'
      '<h2>How it works</h2><div class="steps"><div class="step"><span class="n">1</span><span class="t">Pick a document and your country.</span></div><div class="step"><span class="n">2</span><span class="t">Enter your business once &mdash; it&rsquo;s remembered in your browser.</span></div><div class="step"><span class="n">3</span><span class="t">Add the recipient and line items. The live preview is the actual PDF.</span></div><div class="step"><span class="n">4</span><span class="t">Download it, or send a share link instead of an attachment.</span></div></div></article>')
    nav = ('<script>(function(){var h=document.getElementById("docnav-en");if(!h)return;var D=[["/en/invoice","Invoice"],["/en/estimate","Estimate / Quote"],["/en/receipt","Receipt"],["/en/purchase-order","Purchase Order"],["/en/packing-slip","Packing Slip / Delivery Note"],["/en/credit-note","Credit Note"],["/en/proforma-invoice","Pro Forma Invoice"],["/en/sales-order","Sales Order"],["/en/timesheet","Timesheet"],["/en/work-order","Work Order"],["/en/expense-report","Expense Report"],["/en/bill-of-sale","Bill of Sale"],["/en/donation-receipt","Donation Receipt"]];'
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
      '.hero-en .hcta{order:5;margin:18px 0 2px}'
      '.hero-en .tags{order:6;margin-top:16px}'
      '.hero-en #demoframe{height:430px}'
      '}'
      '.hero-en .hcta{margin-top:20px;display:flex;gap:12px;flex-wrap:wrap}'
      '.hero-en .hbtn{display:inline-flex;align-items:center;gap:8px;font-size:15.5px;font-weight:800;text-decoration:none;border-radius:12px;padding:14px 24px}'
      '.hero-en .hbtn.pri{background:var(--ac,#1766e6);color:#fff;box-shadow:0 12px 26px -10px rgba(23,102,230,.55)}'
      '.hero-en .hbtn.pri:hover{background:#1257ca}'
      '.hero-en .hbtn.gh{border:1.5px solid var(--bd,#d4dced);color:#13263b}'
      '</style>')
    hero_html = ('<section class="hero hero-en"><div class="in">'
      '<div class="htext">'
      f'<span class="ey">{p["ey"]}</span><h1>{p["h1"]}</h1><p>{p["lead"]}</p>'
      '<div class="hcta"><a class="hbtn pri" href="/en/invoice">Create an invoice &rarr;</a><a class="hbtn gh" href="/en/pricing">See plans</a></div>'
      f'<div class="tags">{tags}</div>'
      '</div>'
      '<div class="herodemo"><iframe id="demoframe" src="/en/demo-embed" title="See an invoice created in seconds" loading="lazy" scrolling="no"></iframe></div>'
      '</div></section>')
    demo_script = '<script>(function(){var f=document.getElementById("demoframe");if(!f)return;window.addEventListener("message",function(e){try{var d=e.data;if(d&&d.t==="demoH"&&d.h>200&&d.h<2200){f.style.height=d.h+"px";}}catch(_){}});})();</script>'
    sample = ('<section class="ensample"><div class="in">'
      '<div class="t"><h2>See a finished invoice</h2>'
      '<p>Fill in your details and this is the PDF you download &mdash; your logo, the correct tax for your country, a due date and payment details. No watermarks.</p>'
      '<a class="sbtn" href="/en/invoice">Create yours free &rarr;</a></div>'
      '<div class="im"><img src="/en/sample-invoice.webp?v=20261021" alt="Sample invoice PDF created with Free BizDoc, showing line items, US sales tax, a Net 30 due date and bank payment details" width="1632" height="1843" loading="lazy"></div>'
      '</div></section>'
      '<style>.ensample{max-width:1180px;margin:0 auto;padding:6px 20px 40px}'
      '.ensample .in{display:grid;grid-template-columns:.82fr 1.18fr;gap:34px;align-items:center}'
      '.ensample .t h2{font-size:clamp(20px,3.2vw,27px);font-weight:900;margin:0 0 10px}'
      '.ensample .t p{font-size:15px;color:#5a6b7b;line-height:1.75;margin:0 0 16px}'
      '.ensample .sbtn{display:inline-flex;align-items:center;gap:7px;font-size:15px;font-weight:800;text-decoration:none;border-radius:12px;padding:13px 22px;background:var(--ac,#1766e6);color:#fff;box-shadow:0 12px 26px -10px rgba(23,102,230,.5)}'
      '.ensample .im img{width:100%;height:auto;border-radius:12px;border:1px solid var(--bd,#e2eaf4);box-shadow:0 30px 60px -30px rgba(19,38,59,.55)}'
      '@media(max-width:760px){.ensample .in{grid-template-columns:1fr;gap:18px}}</style>')
    parts = [hd, hero_css, HEADER, hero_html, css, f'<div class="dgrid">{grid}</div>', regions, sample, art, faq_html(INDEX_FAQ), FOOTER, nav, demo_script, f'<script src="/en/siteheader-en.js?v={V}"></script>', '</body>', '</html>', '']
    return '\n'.join(parts)

os.makedirs(OUT, exist_ok=True)
for p in PAGES:
    with open(os.path.join(OUT, p['slug'] + '.html'), 'w', encoding='utf-8') as f: f.write(page(p))
    print('wrote en/%s.html' % p['slug'])
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f: f.write(index())
print('wrote en/index.html')

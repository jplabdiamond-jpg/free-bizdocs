# I built a free invoice generator with ~$0 fixed cost. Here's the whole stack and what I'd change.

I kept seeing the same friction: freelancers and tiny businesses just want to make an invoice, download a clean PDF, and get on with their day — without signing up, without a monthly fee, without handing their client list to yet another dashboard.

So I built one. It's free, no account required to create and download, and it now covers invoices, quotes, receipts, purchase orders and a handful of other business documents, in Japanese and English. This post is the honest build log: the stack, the costs, and the three decisions I'd defend (and the one I'd revisit).

## The constraint that shaped everything: fixed cost must be ~$0

As a solo maker, a free product only survives if it doesn't bleed money while it's small. That single constraint drove every technical choice.

**Stack:**
- **Cloudflare Pages** for hosting (static assets + a few Functions). Generous free tier, global edge, no server to babysit.
- **Cloudflare D1** (SQLite at the edge) for the *optional* account layer — saved documents, billing status. The free generator doesn't touch it.
- **Client-side PDF generation** with `pdf-lib`, fonts embedded in the browser. The server never renders anything.
- **Stripe** for the one paid tier. Webhooks flip a `plan` column in D1; everything else stays free.

Result: when nobody's using it, it costs essentially nothing. When usage spikes, the edge absorbs it and the bill stays flat. That's the whole game for a bootstrapped free tool.

## Decision 1: let people use it before asking for anything

No signup wall. You land, you fill the form, you download the PDF. Accounts exist only for people who *want* to save and reuse documents. I think gating a "make one invoice" tool behind registration is the fastest way to lose the exact person who'd have told a friend about it.

## Decision 2: don't store what you don't need

Sharing a document works by encoding it into the URL fragment rather than saving it server-side — so a "send as a link" feature needs no database row at all. Less data stored means less to secure, less to leak, and a cheaper, simpler system. "We don't keep a copy of your invoice" turned out to be both a privacy win and an infrastructure win.

## Decision 3: localize for real, not just translate

I started Japanese-first, then expanded to English — but English-speaking users don't want a translated Japanese invoice. They want the formats their own tax systems expect: US sales tax, UK VAT, Australian Tax Invoices, Canadian GST/HST. So the English side switches currency, paper size (Letter vs A4), date format, tax-ID labels and tax math by region. Translating the UI is easy; matching the *document conventions* is the part that actually makes it usable abroad.

## The one I'd revisit: I under-invested in distribution early

I spent most of my time on the product and almost none on getting found. Classic maker mistake. The tool is solid, but a solid tool nobody links to just sits on page 5 of Google. If I were starting again I'd publish the build-in-public posts and get listed in directories *from week one*, in parallel with building — not after.

If you want to see it in action, it's here: **[free-bizdocs.com/en](https://free-bizdocs.com/en)** — make an invoice, no account needed.

Happy to answer anything about the Cloudflare Pages + D1 + Stripe setup, the zero-storage sharing, or the multi-region tax logic. What would you have built differently under a "$0 fixed cost" rule?

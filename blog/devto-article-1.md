---
title: "Sharing an invoice without storing it anywhere: a URL that IS the document"
published: true
tags: webdev, javascript, cloudflare, privacy
---

I run a small, free invoice generator. One feature request kept coming back: *"Can I send the invoice as a link instead of a PDF attachment?"*

The obvious way is to save the document to a database, mint an ID, and serve `/invoice/abc123`. But I didn't want to do that. A free tool that quietly stores everyone's invoices — names, amounts, bank details — is a liability I'd rather not own. Storage costs money, backups are a responsibility, and "we keep a copy of your billing data" is the opposite of what a throwaway tool should promise.

So I built sharing with **zero server storage**. The link *contains* the document. Open it and your browser reconstructs the invoice locally. Nothing ever hits my database.

Here's how it works, and the three gotchas that took the longest to get right.

## The core idea: the fragment is the payload

A URL has a part the browser never sends to the server — everything after the `#`. That's the fragment (hash). I encode the whole invoice into it:

```js
// Create a share link
function makeShareLink(doc) {
  const json = JSON.stringify(doc);              // {items, client, company, total, dueDate, ...}
  const packed = btoa(encodeURIComponent(json)); // UTF-8 safe base64
  return `${location.origin}/invoice#s=${packed}`;
}
```

On the receiving side, the page reads its own hash on load and rebuilds the document — read-only, with the amount, bank details and due date surfaced at the top:

```js
// On page load
const m = location.hash.match(/[#&]s=([^&]+)/);
if (m) {
  const doc = JSON.parse(decodeURIComponent(atob(m[1])));
  renderReadOnly(doc);   // no edit UI, just the invoice + a "pay to" panel
}
```

Because the data lives in the fragment, **the server literally never receives it.** My Cloudflare Function logs show a request for `/invoice` with no query string — the `#s=...` part stays in the browser. No row is written. No ID exists to leak.

## Gotcha 1: `btoa` chokes on non-ASCII

`btoa("請求書")` throws `InvalidCharacterError`. Base64 in the browser only speaks Latin-1, and my users write invoices in Japanese, German, Spanish… The fix is to percent-encode to UTF-8 first (`encodeURIComponent`) and decode after (`decodeURIComponent`). That's the `encodeURIComponent → btoa` / `atob → decodeURIComponent` sandwich in the snippets above. Miss it and every non-English invoice silently breaks.

## Gotcha 2: the PDF is generated on the client too

If the server never sees the data, it obviously can't render the PDF. I generate it in the browser with [pdf-lib](https://pdf-lib.js.org/) and embed a font so Japanese doesn't turn into tofu (□□□):

```js
import { PDFDocument } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';

const pdf = await PDFDocument.create();
pdf.registerFontkit(fontkit);
const font = await pdf.embedFont(await fetch('/fonts/noto-jp.ttf').then(r => r.arrayBuffer()));
// ...draw the invoice with `font`, then pdf.save()
```

Keep the font same-origin. I initially loaded it from a CDN and spent an afternoon on CORS/`ArrayBuffer` failures that only showed up on some networks.

## Gotcha 3: links get *long* — decide what not to include

A full invoice with ten line items and addresses is a few KB of JSON → a chunky base64 string. Browsers and chat apps tolerate surprisingly long URLs (tens of KB), but I still draw the line:

- **In the link:** line items, client, company, totals, due date, bank details.
- **Never in the link:** uploaded logos and stamp images. A base64 PNG would blow the URL up to hundreds of KB. The shared view just omits them.

That one rule kept links pasteable in email and messaging apps without truncation.

## Why this shape is nice beyond privacy

- **No backend for the feature.** The entire thing is static assets plus a tiny Cloudflare Function that only serves the shell. On Cloudflare Pages the whole site runs at effectively zero fixed cost.
- **Nothing to expire or clean up.** There's no orphaned-rows table growing forever. Delete the link, delete the data.
- **Trivially offline-friendly.** Rebuilding the doc is pure client code.

The trade-off is honest: the data is only as private as the link. Anyone with the URL can read it — same as a PDF attachment — and you can't revoke it after sending. For a *shareable invoice* that's exactly the right model; for anything you need to lock down later, store it server-side and gate it behind auth.

If you want to poke at the running version, the invoice tool is here: **[free-bizdocs.com/en/invoice](https://free-bizdocs.com/en/invoice)** — create one, hit "share link", and watch the network tab stay quiet.

Would I use the fragment-as-database trick everywhere? No. But for "let the user hand someone a self-contained document, and don't you dare keep a copy," it's the simplest thing that works.

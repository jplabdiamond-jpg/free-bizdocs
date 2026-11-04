---
title: "One invoice form, four tax systems: US sales tax, UK VAT, AU GST, CA GST/HST/PST"
published: true
tags: webdev, javascript, tax, saas
---

I run a free invoice generator. When I expanded it from Japan to the English-speaking market, I assumed "add other currencies" was the hard part. It wasn't. The hard part was tax — because "add 10%" is not how tax works once you cross a border.

A US invoice, a UK invoice, an Australian tax invoice and a Canadian invoice are **four genuinely different documents**, not one document with a different percentage. Here's what I had to model to make a single form produce all four correctly.

## The four systems, briefly

- **US — sales tax.** No national rate. It's state (and often county/city) level, and *the seller only charges it where they have nexus*. On a simple invoice tool, the realistic move is: let the user enter their own rate, show it as "Sales Tax," and never pretend there's one number.
- **UK — VAT.** One national rate (20% standard), but the invoice must show the **VAT registration number** and the VAT amount as a line, and "VAT invoice" is a specific legal document. Not every small business is VAT-registered, so VAT has to be *optional*.
- **Australia — GST.** 10% flat, but the document itself changes name: once GST is included it's a **"Tax Invoice,"** and that label is required wording. Below AUD 1,000 vs above has different ID requirements. The ABN (not a VAT number) goes on it.
- **Canada — GST/HST + PST.** This is the spicy one. Depending on the province you get **GST alone, HST (a combined federal+provincial rate), or GST + a separate PST/QST**. Ontario is 13% HST; Alberta is 5% GST only; Quebec is 5% GST **plus** 9.975% QST calculated separately. So Canada isn't one rate — it's a per-province rule set.

## What that means for the data model

The naive model is `taxRate: number`. That dies immediately on Canada. What actually works is a small per-region descriptor:

```js
const TAX = {
  US: { label: 'Sales Tax',  mode: 'single',  rateEditable: true,  idLabel: null },
  UK: { label: 'VAT',        mode: 'single',  rate: 20, idLabel: 'VAT No.', optional: true },
  AU: { label: 'GST',        mode: 'single',  rate: 10, idLabel: 'ABN', docName: 'Tax Invoice' },
  CA: { label: 'GST/HST',    mode: 'province', idLabel: 'GST/HST No.' }, // rate resolved per province
};

// Canada resolves to one or two components:
const CA_PROVINCES = {
  ON: [{ label: 'HST', rate: 13 }],
  AB: [{ label: 'GST', rate: 5 }],
  BC: [{ label: 'GST', rate: 5 }, { label: 'PST', rate: 7 }],
  QC: [{ label: 'GST', rate: 5 }, { label: 'QST', rate: 9.975 }],
  // ...
};
```

Now tax is a **list of components**, not a scalar. The US/UK/AU cases are just a list of length one. Canada is length one or two. The renderer doesn't care how many there are:

```js
function taxLines(region, province, subtotal) {
  const comps = region === 'CA'
    ? CA_PROVINCES[province]
    : [{ label: TAX[region].label, rate: resolveRate(region) }];
  return comps.map(c => ({
    label: `${c.label} (${c.rate}%)`,
    amount: round(subtotal * c.rate / 100),
  }));
}
```

Once tax is a list, every "weird" case collapses into the same loop. That one refactor — scalar → list of components — is the whole trick.

## The non-obvious bits that bit me

- **The document name is data, too.** Australia's "Tax Invoice" wording isn't decoration; switching region has to switch the H1/title, not just the math. I ended up treating the doc label as part of the region descriptor.
- **Rounding is per-component, per-line — and countries disagree.** Summing then rounding vs rounding then summing can differ by a cent, and some tax authorities are specific about it. Pick a rule, apply it consistently, and round each tax component independently (especially for Canada's two-component provinces).
- **Tax ID labels differ and some are optional.** VAT No., ABN, GST/HST No. — same slot, different label, and for a not-yet-registered freelancer the whole field should disappear rather than print an empty "VAT No.:".
- **Currency ≠ region.** Someone in the US invoicing in EUR is a real case. I keep currency and tax region as independent selectors; coupling them was an early mistake.

## Why bother, for a free tool

Because "close enough" tax is worse than no tax — it makes the document look official while being subtly wrong, which is exactly what a small business can't afford. Modelling it properly turned out to be maybe 150 lines of config, not a tax engine. The leverage was in the *shape* of the data (components, not a rate), not in the amount of code.

If you want to see all four in action, the generator is here: **[free-bizdocs.com/en/invoice](https://free-bizdocs.com/en/invoice)** — switch the region selector and watch the labels, the document name and the tax breakdown change together.

I'm sure I'm still missing edge cases (provincial point-of-sale rebates, EU reverse-charge, US origin-vs-destination sourcing). If you've shipped multi-jurisdiction tax, I'd genuinely like to hear what broke for you.

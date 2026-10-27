# Lazy motion loading experiment — V62

Status: tested on isolated Cloudflare staging; production unchanged.

Source: `backup/v55-2026-10-26/index-v62-validation-staging.html`.

Experimental file: `index-v62-lazy-motion-staging.html`.

Only two `loading="lazy"` attributes are added to the offscreen motion images (`image-14-829dad4c.jpg`, `image-15-e1b530fc.webp`). The approved source and live deployment remain untouched.

The existing release builder still reads the original V62 source, **not** this experimental file. Do not interpret running the standard workflow as testing this change.

Validation still needed: produce an isolated staging deployment with all referenced assets; inspect motion on mobile scroll; compare Lighthouse mobile LCP and request waterfall against the current baseline; review browser console errors. Do not deploy to production without explicit approval.

## Test outcome (2026-10-27)

- Staging URL: https://thermoyar-lazy-motion-test.farzadmd8686.workers.dev/
- GitHub Actions isolated ZIP build/validation: success, run 40467559018.
- User confirmed mobile page visually loads correctly.
- PageSpeed Insights mobile screenshot: Performance 100, LCP 1.7 s, FCP 1.0 s, TBT 0 ms, CLS 0, Accessibility 100, Best Practices 96.
- User reports two further similar mobile test results; exact repeat metrics not provided.
- Previous production baseline: Performance 92, LCP 3.3 s; comparison is not a controlled A/B test.
- Staging SEO score 66 is expected because noindex is intentional. Production SEO settings must remain unchanged.
- Image delivery (~440 KiB) and non-composited animation warnings remain; outside this experiment.
- Next: prepare production candidate with only two lazy attributes, preserve all locked design, verify output and browser behavior. Production deployment requires explicit user approval.

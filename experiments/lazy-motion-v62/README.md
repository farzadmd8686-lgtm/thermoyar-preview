# Lazy motion loading experiment — V62

Status: experimental; not deployed.

Source: `backup/v55-2026-10-26/index-v62-validation-staging.html`.

Experimental file: `index-v62-lazy-motion-staging.html`.

Only two `loading="lazy"` attributes are added to the offscreen motion images (`image-14-829dad4c.jpg`, `image-15-e1b530fc.webp`). The approved source and live deployment remain untouched.

The existing release builder still reads the original V62 source, **not** this experimental file. Do not interpret running the standard workflow as testing this change.

Validation still needed: produce an isolated staging deployment with all referenced assets; inspect motion on mobile scroll; compare Lighthouse mobile LCP and request waterfall against the current baseline; review browser console errors. Do not deploy to production without explicit approval.

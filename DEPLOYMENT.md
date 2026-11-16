# Portfolio deployment

The GitHub Pages workflow validates both languages and packages only the files selected by `scripts/public_files.py`. Source scripts, review notes, Git metadata, environment files and asset provenance notes are excluded from the deployed artifact. The Actions versions are pinned to commits.

## GitHub Pages

Use **GitHub Actions** as the Pages build source. Pushes to `main` run structural, interaction and local HTTP checks before deployment. HTTPS enforcement should remain enabled.

All HTML pages include a restrictive CSP meta policy. GitHub Pages does not apply this repository's `_headers` file. In particular, `frame-ancestors`, `X-Frame-Options` and `X-Content-Type-Options` require response headers controlled by the hosting layer; a meta tag cannot substitute for them. Do not describe those headers as enabled on github.io just because local preview tests pass.

## Hosting with custom response headers

For Cloudflare Pages or Netlify, publish the contents of a freshly built `dist` directory. Its `_headers` applies CSP, framing protection, MIME protection, referrer policy, permissions policy and HSTS to static responses. A change of public address requires updating `BASE` in `scripts/build_locales.py`, canonical URLs, social-card branding and the sitemap before publishing.

Reference: https://developers.cloudflare.com/pages/configuration/headers/

## Local preview

Run `python scripts/preview.py`. The default URL is `http://127.0.0.1:8766`; `--port` selects another loopback port. This preview includes the full response headers and localized 404 pages. It is not a production server.

## Content evidence

NLP figures and reported software-quality checks are attributed to the user's repository. The quoted test count and coverage were not rerun by this portfolio build. No unverified model accuracy, F1 score, application screenshot or demo video is fabricated.

## Verification limits

The user stopped native browser control with Escape during this update. Mobile CSS, accessible menu behavior, translated UI, command behavior and links have automated checks; visual validation on actual mobile devices remains outstanding.

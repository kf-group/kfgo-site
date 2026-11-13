# kfgo.in

The site is generated from `data/packages.json` by `build.py` (+ `pages.py`) and published by GitHub Actions on every push.

- **Add or remove trips:** in the kfGo_Packages_Database sheet set `is_enabled`, then use the menu **kfGo website → Publish to website**. Any state or city works; state and city pages and the sitemap are created automatically.
- **Payments, numbers, UPI, Razorpay:** `src/assets/config.js`.
- **Policies:** `src/content/*.html`. **Rate card:** `src/vehicles.json`.

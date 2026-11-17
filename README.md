# Ecommerce

Independent Frappe ecommerce builder, storefront API, and Vue dashboard extracted from Logi360.

## Architecture

- `ecommerce/`: installable Frappe app and DocTypes
- `dashboard/`: Vue 3 + Frappe UI application
- Builder assets compile into `ecommerce/public/dashboard`

The app does not require Logi360. Store ownership uses the Frappe `User` DocType,
and checkout stores ecommerce orders locally.

## Install on a new Frappe Bench

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/AnjanaDhakal/ecommerce.git
bench --site your-site.example.com install-app ecommerce

cd apps/ecommerce
npm --prefix dashboard ci
npm run build
cd ../..

bench --site your-site.example.com migrate
bench --site your-site.example.com clear-cache
bench restart
```

Open `https://your-site.example.com/ecommerce` for the built dashboard.

## Local development

Run the Frappe backend in the first terminal:

```bash
cd /path/to/frappe-bench
bench use your-site.example.com
bench start
```

Run the Vue dashboard in the second terminal:

```bash
cd /path/to/frappe-bench/apps/ecommerce
npm --prefix dashboard ci
npm run dev
```

- Frappe backend: `http://localhost:8000`
- Vue dashboard: `http://localhost:8080/ecommerce/website`

Log in through Frappe when the Vue dashboard redirects you. The development
server sends `/api` requests to Frappe on port `8000`.

Published storefronts are served by the Frappe backend and can be routed
through a separate domain or reverse proxy.

Set these values in the ecommerce server's `site_config.json`:

```json
{
  "ecommerce_storefront_domain": "shops.example.com",
  "ecommerce_custom_domain_target": "connect.example.com",
  "storefront_url_scheme": "https"
}
```

Configure wildcard DNS for `*.shops.example.com` and point
`connect.example.com` at the ecommerce server before publishing storefronts.

## Deployment

Deploy this repository as its own Frappe app on the ecommerce server. Do not
copy `site_config.json`, `.env`, service-account files, or credentials into Git.

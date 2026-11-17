# Ecommerce

Independent Frappe ecommerce builder, storefront API, and Vue dashboard extracted from Logi360.

## Architecture

- `ecommerce/`: installable Frappe app and DocTypes
- `dashboard/`: Vue 3 + Frappe UI application
- Builder assets compile into `ecommerce/public/dashboard`

The app does not require Logi360. Store ownership uses the Frappe `User` DocType,
and checkout stores ecommerce orders locally.

## Local installation

```bash
cd /path/to/frappe-bench
bench get-app /path/to/ecommerce
bench --site your-site install-app ecommerce
cd apps/ecommerce/dashboard
npm ci
npm run build
bench --site your-site migrate
bench restart
```

Open `/ecommerce` for the dashboard. Published storefronts are served by the
Frappe backend and can be routed through a separate domain or reverse proxy.

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

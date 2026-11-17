# Logi360 to Ecommerce cutover

Do not remove the legacy module before the new server has passed acceptance
testing. The old and new DocType names differ, so uninstalling first can make
the original records inaccessible.

## 1. Deploy the independent server

1. Create a Frappe bench on the ecommerce server.
2. Add this repository with `bench get-app`.
3. Install the app with `bench --site <site> install-app ecommerce`.
4. Configure `ecommerce_storefront_domain`,
   `ecommerce_custom_domain_target`, and `storefront_url_scheme`.
5. Build assets and run `bench --site <site> migrate`.

## 2. Migrate data

Export and transform records in this order so Link fields remain valid:

| Legacy DocType | New DocType |
| --- | --- |
| Logi360 Builder Block | Ecommerce Block |
| Logi360 Builder Template | Ecommerce Template |
| Logi360 Builder Vendor Website | Ecommerce Vendor Website |
| Logi360 Builder Categories | Ecommerce Categories |
| Logi360 Builder Brand | Ecommerce Brand |
| Logi360 Builder Product | Ecommerce Product |
| Logi360 Builder Page | Ecommerce Page |
| Logi360 Builder Ecommerce Order | Ecommerce Ecommerce Order |
| Logi360 Builder Storefront Visit | Ecommerce Storefront Visit |

Store ownership changed from `Logi360 Vendor List` to the standard Frappe
`User` DocType. Map every old vendor to the email address of its new Frappe
user before importing websites and orders.

## 3. Acceptance checks

- Create and publish a storefront.
- Verify wildcard and custom-domain routing.
- Create categories, brands, products, variants, and pages.
- Complete a guest checkout.
- Confirm an order and verify stock is reduced.
- Confirm the Vue dashboard works at `/ecommerce`.

## 4. Remove the legacy module

After final backup and sign-off:

1. Remove Builder/ecommerce routes and fixtures from Logi360 hooks.
2. Remove Builder patches from Logi360 `patches.txt`.
3. Remove `Logi360 Builder` from Logi360 `modules.txt`.
4. Remove the legacy Builder DocType source and Vue builder screens.
5. Run Logi360 tests and a dashboard production build.
6. Back up the site, migrate it, and verify logistics workflows.

Keep the database backup and the final pre-removal Logi360 Git commit until the
new server has operated successfully through the agreed rollback window.

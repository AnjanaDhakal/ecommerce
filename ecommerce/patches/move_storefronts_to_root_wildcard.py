import frappe

from ecommerce.storefront_domains import storefront_url


def execute():
    websites = frappe.get_all(
        "Ecommerce Vendor Website",
        fields=["name", "subdomain"],
    )
    for website in websites:
        if not website.subdomain:
            continue
        frappe.db.set_value(
            "Ecommerce Vendor Website",
            website.name,
            "canonical_url",
            storefront_url(website.subdomain),
            update_modified=False,
        )

    from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages

    for website in websites:
        _republish_website_pages(website.name)

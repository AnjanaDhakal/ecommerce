import frappe

from ecommerce.storefront_domains import (
    canonical_url_subdomain,
    storefront_subdomain,
    storefront_url,
)


def execute():
    used = set()
    websites = frappe.get_all(
        "Ecommerce Vendor Website",
        fields=["name", "website_link", "canonical_url"],
        order_by="creation asc",
    )
    for website in websites:
        base = (
            canonical_url_subdomain(website.canonical_url)
            or storefront_subdomain(website.website_link)
        )
        candidate = base
        suffix = 2
        while candidate in used:
            number = f"-{suffix}"
            candidate = f"{base[:63 - len(number)].rstrip('-')}{number}"
            suffix += 1
        used.add(candidate)
        frappe.db.set_value(
            "Ecommerce Vendor Website",
            website.name,
            {"subdomain": candidate, "canonical_url": storefront_url(candidate)},
            update_modified=False,
        )

import frappe

from ecommerce.storefront_domains import storefront_custom_domain


def execute():
    used_domains = set()
    websites = frappe.get_all(
        "Ecommerce Vendor Website",
        fields=["name", "website_link"],
        order_by="creation asc",
    )
    for website in websites:
        custom_domain = storefront_custom_domain(website.website_link)
        if not custom_domain or custom_domain in used_domains:
            continue
        used_domains.add(custom_domain)
        frappe.db.set_value(
            "Ecommerce Vendor Website",
            website.name,
            "custom_domain",
            custom_domain,
            update_modified=False,
        )

import frappe

from ecommerce.default_ecommerce_catalogue import ensure_default_ecommerce_catalogue


def execute():
    """Replace app-owned demo icons and prices without touching vendor products."""
    for website_id in frappe.get_all(
        "Ecommerce Vendor Website",
        filters={"type": "Ecommerce"},
        pluck="name",
    ):
        ensure_default_ecommerce_catalogue(website_id, refresh_existing=True)

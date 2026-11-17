import frappe

from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages


def execute():
    """Rebuild existing storefront pages with product links opening separately."""
    websites = frappe.get_all(
        "Ecommerce Page",
        distinct=True,
        pluck="website_id",
    )
    for website in filter(None, websites):
        _republish_website_pages(website)

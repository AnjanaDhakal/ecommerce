import frappe


OLD_ALL_PRODUCTS_HREF = (
    'href="/dashboard/store/{{ vendor_website_id }}/category/all-products"'
)
NEW_ALL_PRODUCTS_HREF = 'href="{{ storefront_all_products_url }}"'


def execute():
    """Carry the Navbar 2 category selection into its All products link."""
    if not frappe.db.exists("Ecommerce Block", "Navbar 2"):
        return

    block = frappe.get_doc("Ecommerce Block", "Navbar 2")
    block_html = block.block or ""
    if OLD_ALL_PRODUCTS_HREF in block_html:
        block.block = block_html.replace(
            OLD_ALL_PRODUCTS_HREF,
            NEW_ALL_PRODUCTS_HREF,
        )
        block.save(ignore_permissions=True)

    from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages

    website_ids = frappe.get_all(
        "Ecommerce Page",
        filters={"block_render": ["like", "%ecommerce-category-menu%"]},
        pluck="website_id",
    )
    for website_id in set(website_ids):
        if website_id:
            _republish_website_pages(website_id)

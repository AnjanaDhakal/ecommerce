import frappe


def execute():
    """Send Product Card actions to the variant-aware product detail page."""
    block_name = "Product Card"
    if not frappe.db.exists("Ecommerce Block", block_name):
        return

    block = frappe.get_doc("Ecommerce Block", block_name)
    block_html = block.block or ""
    linked_html = block_html.replace(
        '<a href="#">\n              <div',
        '<a href="{{ product.url or \'#\' }}" aria-label="View {{ product.product_name }} details">\n              <div',
    )
    linked_html = linked_html.replace("ADD TO CART", "VIEW PRODUCT")
    if linked_html == block_html:
        return

    block.block = linked_html
    block.save(ignore_permissions=True)

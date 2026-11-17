import re

import frappe

from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages


PRODUCT_IMAGE_CLASS = (
    "h-72 w-full max-w-full object-contain p-4 "
    "transition-transform duration-300 hover:scale-105"
)


def execute():
    if not frappe.db.exists("Ecommerce Block", "Product Card"):
        return

    block = frappe.get_doc("Ecommerce Block", "Product Card")
    updated_html = re.sub(
        r'(<img\s+src="\{\{ product\.product_image\}\}")([^>]*?)(?:\s+alt="[^"]*")?\s+class="[^"]*"(\s*/>)',
        rf'\g<1>\g<2> alt="{{{{ product.product_name }}}}" class="{PRODUCT_IMAGE_CLASS}"\g<3>',
        block.block or "",
        count=1,
        flags=re.DOTALL,
    )
    if updated_html != (block.block or ""):
        block.block = updated_html
        block.save(ignore_permissions=True)

    websites = frappe.get_all(
        "Ecommerce Page",
        distinct=True,
        pluck="website_id",
    )
    for website_id in filter(None, websites):
        _republish_website_pages(website_id)

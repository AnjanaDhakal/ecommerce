import re

import frappe

from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages


FIXED_IMAGE_CLASS = "block h-80 w-full bg-gray-50 object-contain sm:h-96"


def execute():
    if not frappe.db.exists("Ecommerce Block", "Image Gallery"):
        return

    block = frappe.get_doc("Ecommerce Block", "Image Gallery")
    updated_html = re.sub(
        r'(<img\s+src="\{\{ gallery_image\.image \}\}"[^>]*?class=")[^"]*(")',
        rf"\g<1>{FIXED_IMAGE_CLASS}\g<2>",
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

import re

import frappe

from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages


PRODUCT_TEXT = '''            {% if product.product_name %}<p class="text-sm text-gray-500 font-bold">{{ product.product_name }}</p>{% endif %}
            {% if product.product_description %}<p class="text-xl tracking-wide pb-4">{{ product.product_description }}</p>{% endif %}'''


def execute():
    if not frappe.db.exists("Ecommerce Block", "Product Card"):
        return

    block = frappe.get_doc("Ecommerce Block", "Product Card")
    original = block.block or ""
    updated = re.sub(
        r'''\s*<p class="text-sm text-gray-500 font-bold">"?\{\{\s*product\.product_name\s*\}\}"?</p>\s*<p class="text-xl tracking-wide pb-4">"?\{\{\s*product\.product_description\s*\}\}"?</p>''',
        "\n" + PRODUCT_TEXT,
        original,
        count=1,
    )
    if updated != original:
        block.block = updated
        block.save(ignore_permissions=True)

    for website_id in filter(
        None,
        frappe.get_all("Ecommerce Page", distinct=True, pluck="website_id"),
    ):
        _republish_website_pages(website_id)

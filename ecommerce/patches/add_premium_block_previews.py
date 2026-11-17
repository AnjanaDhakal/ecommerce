import frappe

from ecommerce.patches.add_premium_commerce_blocks import BLOCK_IMAGES


def execute():
    for block_name, image_url in BLOCK_IMAGES.items():
        frappe.db.set_value(
            "Ecommerce Block",
            block_name,
            "block_image",
            image_url,
            update_modified=False,
        )

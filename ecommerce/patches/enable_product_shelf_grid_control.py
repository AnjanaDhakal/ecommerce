from ecommerce.patches.add_premium_commerce_blocks import execute as refresh_premium_blocks


def execute():
    """Expose the product shelf column setting in existing installations."""
    refresh_premium_blocks()

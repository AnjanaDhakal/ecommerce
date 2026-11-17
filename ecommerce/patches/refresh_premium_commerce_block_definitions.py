from ecommerce.patches.add_premium_commerce_blocks import execute as refresh_blocks


def execute():
    """Refresh premium templates after their editable schemas or markup change."""
    refresh_blocks()

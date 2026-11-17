import frappe


STYLE_MARKER = "/* ecommerce-category-submenu-layer-fix */"
STYLE_FIX = f'''\n{STYLE_MARKER}
@media (min-width: 768px) {{ .ecommerce-category-menu__inner {{ overflow: visible; }} }}
.ecommerce-category-menu__item {{ z-index: 41; }}
.ecommerce-category-menu__submenu {{ z-index: 1000; }}
'''


def execute():
    """Allow category submenus to escape the horizontally scrolling nav row."""
    if not frappe.db.exists("Ecommerce Block", "Navbar 2"):
        return

    block = frappe.get_doc("Ecommerce Block", "Navbar 2")
    if STYLE_MARKER not in (block.style or ""):
        block.style = ((block.style or "").rstrip() + STYLE_FIX).strip()
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

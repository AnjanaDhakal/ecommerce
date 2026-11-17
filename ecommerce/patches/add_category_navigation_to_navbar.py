import frappe


CATEGORY_MENU = r'''
  {% if store_categories %}
  <nav class="ecommerce-category-menu" aria-label="Product categories">
    <div class="ecommerce-category-menu__inner">
      <a class="ecommerce-category-menu__link" href="{{ storefront_all_products_url }}">All products</a>
      {% for category in store_categories %}
      <div class="ecommerce-category-menu__item">
        <a class="ecommerce-category-menu__link" href="{{ category.url }}">
          {{ category.title }}{% if category.children %}<span aria-hidden="true">⌄</span>{% endif %}
        </a>
        {% if category.children %}
        <div class="ecommerce-category-menu__submenu">
          {% for child in category.children %}
          <a href="{{ child.url }}">{{ child.title }}</a>
          {% endfor %}
        </div>
        {% endif %}
      </div>
      {% endfor %}
    </div>
  </nav>
  {% endif %}
'''


CATEGORY_STYLE = r'''
.ecommerce-category-menu { position: relative; z-index: 40; border-top: 1px solid #eee; border-bottom: 1px solid #eee; background: #fff; }
.ecommerce-category-menu__inner { display: flex; align-items: center; justify-content: center; gap: 2rem; padding: .85rem 1.5rem; overflow: visible; }
.ecommerce-category-menu__item { position: relative; z-index: 41; flex: 0 0 auto; }
.ecommerce-category-menu__link { display: flex; align-items: center; gap: .35rem; color: #252525; font-size: .95rem; text-decoration: none; white-space: nowrap; }
.ecommerce-category-menu__link:hover { color: #991b60; }
.ecommerce-category-menu__submenu { display: none; position: absolute; z-index: 1000; top: 100%; left: 0; min-width: 13rem; padding: .5rem; border: 1px solid #e5e7eb; border-radius: .65rem; background: #fff; box-shadow: 0 12px 30px rgba(0,0,0,.12); }
.ecommerce-category-menu__item:hover .ecommerce-category-menu__submenu,
.ecommerce-category-menu__item:focus-within .ecommerce-category-menu__submenu { display: grid; }
.ecommerce-category-menu__submenu a { padding: .65rem .8rem; border-radius: .45rem; color: #353535; text-decoration: none; white-space: nowrap; }
.ecommerce-category-menu__submenu a:hover { background: #f9eef5; color: #991b60; }
@media (max-width: 767px) { .ecommerce-category-menu__inner { justify-content: flex-start; gap: 1.25rem; overflow-x: auto; overflow-y: hidden; } }
'''


def execute():
    if not frappe.db.exists("Ecommerce Block", "Navbar 2"):
        return

    block = frappe.get_doc("Ecommerce Block", "Navbar 2")
    if "ecommerce-category-menu" not in (block.block or ""):
        marker = "</section>"
        if marker in (block.block or ""):
            block.block = block.block.rsplit(marker, 1)[0] + CATEGORY_MENU + marker
        else:
            block.block = (block.block or "") + CATEGORY_MENU
    if ".ecommerce-category-menu" not in (block.style or ""):
        block.style = ((block.style or "").rstrip() + "\n" + CATEGORY_STYLE).strip()
    block.save(ignore_permissions=True)

    from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
    website_ids = frappe.get_all(
        "Ecommerce Page",
        filters={"block_render": ["is", "set"]},
        pluck="website_id",
    )
    for website_id in set(website_ids):
        if website_id:
            _republish_website_pages(website_id)

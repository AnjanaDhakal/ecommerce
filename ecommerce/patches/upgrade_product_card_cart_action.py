import re

import frappe

from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages


ACTION_TEMPLATE = """{% if product.show_add_to_cart %}
          <button
            type="button"
            class="ecommerce-add-to-cart bg-[#e84cb0] w-full rounded-xl p-3 text-xs text-white cursor-pointer transition-all {{ product.add_to_cart_style_class }}"
            style="{{ product.add_to_cart_style_attribute }}"
            data-product-url="{{ product.url or '' }}"
            aria-label="Add {{ product.product_name }} to cart"
          >
            ADD TO CART
          </button>
          {% else %}
          <a
            href="{{ product.url or '#' }}"
            class="block bg-[#e84cb0] w-full rounded-xl p-3 text-center text-xs text-white"
            aria-label="View {{ product.product_name }} details"
          >
            VIEW PRODUCT
          </a>
          {% endif %}"""

IMAGE_TEMPLATE = """          <a
            href="{{ product.url or '#' }}"
            class="flex justify-center items-center"
            aria-label="View {{ product.product_name }} details"
          >
            <img
              src="{{ product.product_image}}"
              alt="{{ product.product_name }}"
              class="h-72 w-full max-w-full object-contain p-4 transition-transform duration-300 hover:scale-105"
            />
          </a>"""

TEXT_TEMPLATE = """        <div class="flex flex-col pt-5">
          <a
            href="{{ product.url or '#' }}"
            class="block text-inherit no-underline"
            aria-label="View {{ product.product_name }} details"
          >
            {% if product.product_name %}<p class="text-sm text-gray-500 font-bold">{{ product.product_name }}</p>{% endif %}
            {% if product.product_description %}<p class="text-xl tracking-wide pb-4">{{ product.product_description }}</p>{% endif %}
          </a>"""


def execute():
    block_name = "Product Card"
    if not frappe.db.exists("Ecommerce Block", block_name):
        return

    block = frappe.get_doc("Ecommerce Block", block_name)
    block_html = block.block or ""
    upgraded = re.sub(
        r"{% if product\.show_add_to_cart %}.*?{% endif %}",
        ACTION_TEMPLATE,
        block_html,
        count=1,
        flags=re.DOTALL,
    )
    upgraded = re.sub(
        r'''          <div class="flex justify-center items-center">\s*<img\s+src="\{\{ product\.product_image\}\}"(?:\s+alt="[^"]*")?\s+class="(?:size-60 cursor-pointer hover:scale-130 transition-all duration-300|h-72 w-full max-w-full object-contain p-4 transition-transform duration-300 hover:scale-105)"\s*/>\s*</div>''',
        IMAGE_TEMPLATE,
        upgraded,
        count=1,
    )
    upgraded = re.sub(
        r'''        <div class="flex flex-col pt-5">\s*<p class="text-sm text-gray-500 font-bold">"\{\{ product\.product_name\}\}"</p>\s*<p class="text-xl tracking-wide pb-4">"\{\{ product\.product_description\}\}"</p>''',
        TEXT_TEMPLATE,
        upgraded,
        count=1,
    )
    if upgraded != block_html:
        block.block = upgraded
        block.save(ignore_permissions=True)

    websites = frappe.get_all(
        "Ecommerce Page",
        distinct=True,
        pluck="website_id",
    )
    for website in filter(None, websites):
        _republish_website_pages(website)

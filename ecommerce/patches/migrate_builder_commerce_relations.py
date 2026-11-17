import json
import re

import frappe


def _slug(value, fallback):
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-") or fallback


def execute():
    websites = frappe.get_all("Ecommerce Vendor Website", pluck="name", limit=2)
    default_website = websites[0] if len(websites) == 1 else None

    for name in frappe.get_all("Ecommerce Brand", pluck="name"):
        doc = frappe.get_doc("Ecommerce Brand", name)
        changed = False
        if not doc.slug:
            doc.slug = _slug(doc.brand_name, str(doc.name))
            changed = True
        if default_website and not doc.website:
            doc.website = default_website
            changed = True
        if changed:
            doc.save(ignore_permissions=True)

    _update_image_gallery_block(default_website)


def _update_image_gallery_block(default_website=None):
    block = (
        frappe.get_doc("Ecommerce Block", "Image Gallery")
        if frappe.db.exists("Ecommerce Block", "Image Gallery")
        else None
    )
    model = {
        "block_name": "image_gallery",
        "fields": [
            {"label": "Title", "type": "text", "name": "gallery_title"},
            {"label": "Description", "type": "text", "name": "gallery_description"},
            {"label": "Grid", "type": "text", "name": "grid_num", "default": 3},
            {
                "label": "Images",
                "type": "repeater",
                "name": "image_list",
                "fields": [
                    {"label": "Title", "type": "text", "name": "title"},
                    {"label": "Image", "type": "file", "name": "image"},
                    {"label": "Alternative Text", "type": "text", "name": "alt_text"},
                    {
                        "label": "Destination Type",
                        "type": "select",
                        "name": "destination_type",
                        "options": [
                            {"label": "Brand", "value": "brand"},
                            {"label": "Category", "value": "category"},
                            {"label": "Product", "value": "product"},
                            {"label": "Builder Page", "value": "page"},
                        ],
                    },
                    {
                        "label": "Destination",
                        "type": "commerce_link",
                        "name": "destination",
                        "destination_type_field": "destination_type",
                    },
                    {"label": "Legacy Link", "type": "text", "name": "link"},
                ],
            },
        ],
    }
    if block:
        block.model = json.dumps(model)
        block.block = """<section class=\"mx-5 my-8\">
  {% if gallery_title or gallery_description %}
  <div class=\"mb-8 text-center\">
    {% if gallery_title %}<h2 class=\"text-3xl font-semibold\">{{ gallery_title }}</h2>{% endif %}
    {% if gallery_description %}<p class=\"mt-2 text-gray-600\">{{ gallery_description }}</p>{% endif %}
  </div>
  {% endif %}
  <div class=\"grid grid-cols-1 gap-5 md:grid-cols-{{ grid_num or 3 }}\">
    {% for gallery_image in image_list %}
    {% set target_url = gallery_image.destination_url or gallery_image.link %}
    <article class=\"overflow-hidden rounded-2xl bg-gray-50\">
      {% if target_url %}<a href=\"{{ target_url }}\" class=\"block\">{% endif %}
        {% if gallery_image.image %}
        <img src=\"{{ gallery_image.image }}\" alt=\"{{ gallery_image.alt_text or gallery_image.title or 'Gallery image' }}\" class=\"aspect-[4/5] w-full object-cover\">
        {% endif %}
        {% if gallery_image.title %}<h3 class=\"p-4 text-lg font-semibold\">{{ gallery_image.title }}</h3>{% endif %}
      {% if target_url %}</a>{% endif %}
    </article>
    {% endfor %}
  </div>
</section>"""
        block.save(ignore_permissions=True)

    for name in frappe.get_all("Ecommerce Categories", pluck="name"):
        doc = frappe.get_doc("Ecommerce Categories", name)
        changed = False
        if not doc.slug:
            doc.slug = _slug(doc.categories_name, str(doc.name))
            changed = True
        if default_website and not doc.website:
            doc.website = default_website
            changed = True
        if changed:
            doc.save(ignore_permissions=True)

    for name in frappe.get_all("Ecommerce Product", pluck="name"):
        doc = frappe.get_doc("Ecommerce Product", name)
        changed = False
        if not doc.slug:
            doc.slug = _slug(doc.product_name, str(doc.name))
            changed = True
        if default_website and not doc.website:
            doc.website = default_website
            changed = True
        if not doc.categories and doc.catagories:
            doc.append("categories", {"category": doc.catagories})
            changed = True
        if not doc.variants and doc.varient:
            try:
                variants = frappe.parse_json(doc.varient) or []
            except (TypeError, ValueError):
                variants = []
            for variant in variants if isinstance(variants, list) else []:
                if not isinstance(variant, dict):
                    continue
                doc.append("variants", {
                    "variant_name": variant.get("variant_name") or variant.get("name"),
                    "discounted_price": variant.get("discounted_price"),
                    "selling_price": variant.get("selling_price"),
                    "cost_price": variant.get("cost_price"),
                    "weight": variant.get("weight"),
                    "volume": variant.get("volume") or variant.get("volumne"),
                    "quantity": variant.get("quantity"),
                    "sku": variant.get("sku"),
                })
                changed = True
        if changed:
            doc.save(ignore_permissions=True)

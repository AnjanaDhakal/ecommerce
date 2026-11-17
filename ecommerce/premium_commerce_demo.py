"""Install a complete, rights-safe premium electronics demo storefront.

The information architecture is inspired by large Nepalese electronics stores,
but all names, copy, images, and catalog records are original demo content.
Running ``install`` repeatedly updates the same demo records instead of creating
duplicates.
"""

import copy
import json
import re

import frappe


ASSET_ROOT = "/assets/ecommerce/images/premium-commerce"

TEMPLATE_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ seo_title or doc.page }}</title>
  {% if seo_description %}<meta name="description" content="{{ seo_description }}">{% endif %}
  <style>
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; background: #fff; color: #111827; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    img { max-width: 100%; }
    body > header { position: relative; z-index: 100; overflow: visible; }
    body > main { position: relative; z-index: 1; }
    {{ blockstyle | safe }}
  </style>
</head>
<body>
  <header>{{ header | safe }}</header>
  <main>{{ main | safe }}</main>
  <footer>{{ footer | safe }}</footer>
  {% if blockscript %}<script>{{ blockscript | safe }}</script>{% endif %}
</body>
</html>"""

CATEGORIES = [
    "Phones", "Tablets", "Laptops", "Watches", "Cameras", "Drones",
    "Speakers", "Microphones", "Headphones", "Earbuds", "Accessories",
    "Projectors",
]

BRANDS = [
    "Northstar Mobile", "Apex Audio", "FrameLab", "Orbit Gear",
    "Luma Home", "Peak Accessories",
]

PRODUCTS = [
    ("Pulse Pro Smartphone", "Phones", "Northstar Mobile", 124999, "A refined flagship phone with a vivid display and all-day battery."),
    ("Canvas Air Tablet", "Tablets", "Northstar Mobile", 64999, "A slim tablet for entertainment, notes, and everyday creativity."),
    ("Summit 14 Laptop", "Laptops", "Orbit Gear", 154500, "A lightweight performance laptop for work, study, and travel."),
    ("Loop Active Watch", "Watches", "Northstar Mobile", 28500, "Fitness, notifications, and health insights in a clean metal case."),
    ("Vista Pocket Camera", "Cameras", "FrameLab", 83500, "Compact stabilized video and crisp photos for creators on the move."),
    ("AirScout Mini Drone", "Drones", "FrameLab", 97500, "A travel-friendly camera drone with assisted flight controls."),
    ("RoomFill Portable Speaker", "Speakers", "Apex Audio", 12900, "Rich portable sound with a durable splash-resistant enclosure."),
    ("Creator Duo Microphone", "Microphones", "Apex Audio", 19500, "A compact two-person wireless microphone kit for mobile creators."),
    ("QuietForm Headphones", "Headphones", "Apex Audio", 24900, "Comfortable wireless headphones with focused, balanced sound."),
    ("Arc Mini Earbuds", "Earbuds", "Apex Audio", 8950, "Pocket-size earbuds with clear calls and dependable battery life."),
    ("Flux 65W Travel Charger", "Accessories", "Peak Accessories", 4950, "Fast charging for phones, tablets, and compatible laptops."),
    ("CinemaBeam Smart Projector", "Projectors", "Luma Home", 78500, "A compact full-HD smart projector for movies, games, and sport."),
]


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")


def _placeholder(label, width=900, height=900, background="f3f4f6"):
    text = str(label).replace(" ", "+")
    return f"https://placehold.co/{width}x{height}/{background}/111827?text={text}"


def _upsert(doctype, filters, values):
    name = frappe.db.get_value(doctype, filters, "name")
    if name:
        doc = frappe.get_doc(doctype, name)
        doc.update(values)
        doc.save(ignore_permissions=True)
        return doc
    doc = frappe.get_doc({"doctype": doctype, **values})
    doc.insert(ignore_permissions=True)
    return doc


def _ensure_categories(website_id):
    result = {}
    palette = ["fff1f2", "f5f3ff", "eff6ff", "ecfeff", "f0fdf4", "fffbeb"]
    for index, title in enumerate(CATEGORIES):
        slug = _slug(title)
        result[title] = _upsert(
            "Ecommerce Categories",
            {"website": website_id, "slug": slug},
            {
                "categories_name": title,
                "slug": slug,
                "website": website_id,
                "categories_logo": _placeholder(title, 600, 600, palette[index % len(palette)]),
            },
        )
    return result


def _ensure_brands(website_id):
    result = {}
    for title in BRANDS:
        slug = _slug(title)
        result[title] = _upsert(
            "Ecommerce Brand",
            {"website": website_id, "slug": slug},
            {
                "brand_name": title,
                "slug": slug,
                "website": website_id,
                "brand_logo": _placeholder(title, 480, 220, "ffffff"),
                "seo_title": f"{title} products",
                "seo_description": f"Browse products from {title}.",
            },
        )
    return result


def _ensure_products(website_id, categories, brands):
    result = {}
    palette = ["fff1f2", "f5f3ff", "eff6ff", "ecfeff", "f0fdf4", "fffbeb"]
    for index, (title, category, brand, price, description) in enumerate(PRODUCTS):
        slug = _slug(title)
        category_id = categories[category].name
        brand_id = brands[brand].name
        variant = {
            "variant_name": "Standard",
            "selling_price": price,
            "discounted_price": price,
            "cost_price": round(price * 0.78, 2),
            "quantity": 25,
            "sku": f"DEMO-{index + 1:03d}",
            "weight": 1,
            "volume": 1,
        }
        doc = _upsert(
            "Ecommerce Product",
            {"website": website_id, "slug": slug},
            {
                "product_name": title,
                "slug": slug,
                "website": website_id,
                "brand": brand_id,
                "catagories": category_id,
                "product_image": _placeholder(title, 900, 900, palette[index % len(palette)]),
                "gallery_images": json.dumps([]),
                "product_description": description,
                "long_description": f"{description} Includes local delivery support and straightforward product assistance.",
                "enable": 1,
                "continue_selling": 0,
                "varient": json.dumps([variant]),
            },
        )
        doc.set("categories", [])
        doc.append("categories", {"category": category_id})
        doc.set("variants", [])
        doc.append("variants", variant)
        doc.save(ignore_permissions=True)
        result[title] = doc
    return result


def _ensure_template(page):
    page_name = "Premium Commerce Home"
    existing = frappe.db.get_value("Ecommerce Template", {"page_name": page_name}, "name")
    source_data = None
    if page.template and page.template != existing:
        source_data = frappe.db.get_value("Ecommerce Template", page.template, "data_json")
    if not source_data and existing:
        source_data = frappe.db.get_value("Ecommerce Template", existing, "data_json")
    if not source_data:
        source_data = json.dumps({
            "title": "Premium Commerce Home",
            "fields": [
                {"label": "Header Blocks", "name": "header", "type": "draggable"},
                {"label": "Blocks", "name": "main", "type": "draggable"},
                {"label": "Footer Blocks", "name": "footer", "type": "draggable"},
            ],
        })
    if existing:
        template = frappe.get_doc("Ecommerce Template", existing)
        template.data_json = source_data
        template.template = TEMPLATE_HTML
        template.save(ignore_permissions=True)
        return template
    return frappe.get_doc({
        "doctype": "Ecommerce Template",
        "page_name": page_name,
        "data_json": source_data,
        "template": TEMPLATE_HTML,
    }).insert(ignore_permissions=True)


def _block_instance(block_name, values, instance_id):
    block = frappe.get_doc("Ecommerce Block", block_name)
    model = json.loads(block.model or "{}")
    for field in model.get("fields") or []:
        key = field.get("key") or field.get("name")
        if key in values:
            field["value"] = copy.deepcopy(values[key])
        elif "default" in field:
            field["value"] = copy.deepcopy(field["default"])
    return {
        "id": instance_id,
        "block_name": block_name,
        "name": block_name,
        "type": block.type,
        "block_details": {"name": block_name, "model": model},
    }


def _destination(entity_type, doc, label):
    return {"type": entity_type, "value": doc.name, "label": label}


def _homepage_value(website_id, categories, brands, products):
    category_items = [
        {
            "title": title,
            "image": categories[title].categories_logo,
            "destinations": [_destination("category", categories[title], title)],
        }
        for title in CATEGORIES
    ]
    brand_items = [
        {
            "title": title,
            "image": brands[title].brand_logo,
            "destinations": [_destination("brand", brands[title], title)],
        }
        for title in BRANDS
    ]
    product_ids = [products[title].name for title, *_ in PRODUCTS]
    nav_links = [
        {
            "keyword": title,
            "destinations": [_destination("category", categories[title], title)],
        }
        for title in ["Phones", "Laptops", "Cameras", "Audio"]
        if title in categories
    ]
    # Audio is represented by the Headphones category in the demo catalog.
    if len(nav_links) == 3:
        nav_links.append({
            "keyword": "Audio",
            "destinations": [_destination("category", categories["Headphones"], "Headphones")],
        })

    articles = [
        {
            "category": "Buying guide",
            "title": "How to choose headphones for work and travel",
            "description": "Compare comfort, battery life, microphones, and noise control before you buy.",
            "image": _placeholder("Headphone buying guide", 900, 720, "f1f5f9"),
            "date": "August 20, 2026",
            "link_label": "Read guide",
            "url": "#",
        },
        {
            "category": "Creator gear",
            "title": "A simple mobile video kit for new creators",
            "description": "Build a compact setup around clean audio, stable video, and portable power.",
            "image": _placeholder("Creator video kit", 900, 720, "e2e8f0"),
            "date": "August 18, 2026",
            "link_label": "Read guide",
            "url": "#",
        },
        {
            "category": "Home entertainment",
            "title": "Plan a better movie night at home",
            "description": "Balance screen size, room lighting, speakers, and seating for an immersive setup.",
            "image": f"{ASSET_ROOT}/home-theatre.png",
            "date": "August 16, 2026",
            "link_label": "Read guide",
            "url": "#",
        },
    ]

    header = [
        _block_instance("Navbar 1", {
            "email": "hello@novatech.example",
            "phone": "9800000000",
        }, "premium-contact"),
        _block_instance("Navbar 2", {
            "all_products": nav_links,
            "search_placeholder": "Search products",
            "wishlist": True,
            "cart": True,
            "menu_categories": [categories[title].name for title in CATEGORIES],
        }, "premium-navigation"),
    ]
    main = [
        _block_instance("Commerce Promo Hero", {
            "eyebrow": "Limited time collection",
            "heading": "Technology that fits your everyday",
            "description": "Discover thoughtful devices for work, creativity, entertainment, and life on the move.",
            "button_label": "Shop featured products",
            "button_url": f"/dashboard/store/{website_id}/category/phones",
            "image": f"{ASSET_ROOT}/hero-tech.png",
        }, "premium-hero"),
        _block_instance("Commerce Product Shelf", {
            "product_title": "Featured products",
            "product_description": "Popular picks selected across mobile, audio, cameras, and home entertainment.",
            "product_list": product_ids[:8],
        }, "premium-featured-products"),
        _block_instance("Commerce Article Grid", {
            "heading": "Latest guides",
            "view_all_label": "View all guides",
            "view_all_url": "#",
            "items": articles,
        }, "premium-articles"),
        _block_instance("Commerce Category Showcase", {
            "heading": "Browse categories",
            "items": category_items,
        }, "premium-categories"),
        _block_instance("Commerce Editorial Banner", {
            "eyebrow": "Nova Studio",
            "heading": "Bring cinema-level sound home",
            "description": "Pair a bright projector with room-filling audio for movies, music, games, and match day.",
            "button_label": "Explore home entertainment",
            "button_url": f"/dashboard/store/{website_id}/category/projectors",
            "image": f"{ASSET_ROOT}/home-theatre.png",
        }, "premium-editorial"),
        _block_instance("Commerce Product Shelf", {
            "product_title": "New arrivals",
            "product_description": "Fresh additions for creators, travellers, and connected homes.",
            "product_list": product_ids[4:],
        }, "premium-new-products"),
        _block_instance("Commerce Brand Showcase", {
            "heading": "Featured brands",
            "items": brand_items,
        }, "premium-brands"),
    ]
    footer = [
        _block_instance("Commerce Rich Footer", {
            "store_name": "Nova Tech Nepal",
            "description": "Original demo storefront for quality electronics, simple shopping, and dependable local support.",
            "email": "hello@novatech.example",
            "phone": "9800000000",
            "columns": [
                {"title": "Shop", "links": [{"label": "Phones", "url": f"/dashboard/store/{website_id}/category/phones"}, {"label": "Laptops", "url": f"/dashboard/store/{website_id}/category/laptops"}]},
                {"title": "Discover", "links": [{"label": "Cameras", "url": f"/dashboard/store/{website_id}/category/cameras"}, {"label": "Audio", "url": f"/dashboard/store/{website_id}/category/headphones"}]},
                {"title": "Help", "links": [{"label": "Delivery", "url": "#"}, {"label": "Contact", "url": "#"}]},
            ],
        }, "premium-footer"),
    ]
    return {
        "seo_title": "Nova Tech Nepal | Premium electronics",
        "seo_description": "Shop original demo electronics across mobile, audio, cameras, computing, and home entertainment.",
        "allow_indexing_search_engine": True,
        "header": header,
        "main": main,
        "footer": footer,
        "Page": {},
    }


def install(website_id, page_id=None):
    """Create the demo catalog and replace the selected homepage layout."""
    website_id = str(website_id)
    if not frappe.db.exists("Ecommerce Vendor Website", website_id):
        frappe.throw(f"Builder website {website_id} does not exist")

    from ecommerce.patches.add_premium_commerce_blocks import execute as ensure_blocks
    ensure_blocks()

    if page_id:
        page = frappe.get_doc("Ecommerce Page", str(page_id))
        if str(page.website_id) != website_id:
            frappe.throw("The selected page does not belong to this website")
    else:
        page_name = frappe.db.get_value(
            "Ecommerce Page",
            {"website_id": website_id},
            "name",
            order_by="creation asc",
        )
        if not page_name:
            frappe.throw(f"Builder website {website_id} has no pages")
        page = frappe.get_doc("Ecommerce Page", page_name)

    categories = _ensure_categories(website_id)
    brands = _ensure_brands(website_id)
    products = _ensure_products(website_id, categories, brands)
    template = _ensure_template(page)

    page.page = "Home"
    page.template = template.name
    page.field_value = json.dumps(_homepage_value(website_id, categories, brands, products))
    page.save(ignore_permissions=True)

    website = frappe.get_doc("Ecommerce Vendor Website", website_id)
    website.description = "Premium electronics for work, creativity, entertainment, and everyday life."
    website.canonical_url = None
    website.primary_color = "#ff4964"
    website.secondary_color = "#111827"
    website.additional_color1 = "#f5f5f5"
    website.additional_color2 = "#fbbf24"
    website.font = "Inter"
    website.template = template.name
    website.save(ignore_permissions=True)

    frappe.db.commit()
    from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
    _republish_website_pages(website_id)
    frappe.db.commit()

    return {
        "status": "success",
        "website": website_id,
        "page": page.name,
        "template": template.name,
        "categories": len(categories),
        "brands": len(brands),
        "products": len(products),
        "blocks": {"header": 2, "main": 7, "footer": 1},
    }

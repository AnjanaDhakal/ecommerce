import copy
import json

import frappe


TEMPLATE_PRESETS = {
    "Premium Commerce Home": {
        "description": "A complete commerce homepage with navigation, campaign, categories, editorial content, articles, and footer.",
        "header": ["Navbar 1", "Navbar 2"],
        "main": [
            "Commerce Promo Hero",
            "Commerce Product Shelf",
            "Commerce Category Showcase",
            "Commerce Editorial Banner",
            "Commerce Article Grid",
        ],
        "footer": ["Commerce Rich Footer"],
    },
    "Gallery Pages": {
        "description": "A visual page with navigation, an editable image gallery, and a ready-made footer.",
        "header": ["Navbar 2"],
        "main": ["Image Gallery"],
        "footer": ["Commerce Rich Footer"],
    },
    "Blank Page": {
        "description": "Start without preselected sections and build the page your way.",
        "header": [],
        "main": [],
        "footer": [],
    },
}


BLOCK_VALUE_OVERRIDES = {
    ("Premium Commerce Home", "Navbar 1"): {
        "email": "hello@yourstore.com",
        "phone": "+977 9800000000",
    },
    ("Premium Commerce Home", "Navbar 2"): {
        "logo": "https://placehold.co/250x100/111827/ffffff?text=YOUR+STORE",
        "all_products": [
            {"keyword": "New arrivals", "destinations": []},
            {"keyword": "Products", "destinations": []},
            {"keyword": "Collections", "destinations": []},
            {"keyword": "About", "destinations": []},
        ],
        "search_placeholder": "Search products",
        "wishlist": True,
        "cart": True,
    },
    ("Gallery Pages", "Navbar 2"): {
        "logo": "https://placehold.co/250x100/111827/ffffff?text=YOUR+STORE",
        "all_products": [
            {"keyword": "Gallery", "destinations": []},
            {"keyword": "Collections", "destinations": []},
            {"keyword": "About", "destinations": []},
        ],
        "search_placeholder": "Search",
        "wishlist": True,
        "cart": True,
    },
    ("Gallery Pages", "Image Gallery"): {
        "gallery_title": "Explore our collection",
        "gallery_description": "Replace these sample images with your own products, projects, or stories.",
        "image_list": [
            {
                "title": "Featured collection",
                "image": "https://placehold.co/900x720/f1f5f9/111827?text=Featured+collection",
                "alt_text": "Featured collection sample",
                "seo_keyword": "featured collection",
                "destinations": [],
            },
            {
                "title": "New arrivals",
                "image": "https://placehold.co/900x720/e2e8f0/111827?text=New+arrivals",
                "alt_text": "New arrivals sample",
                "seo_keyword": "new arrivals",
                "destinations": [],
            },
            {
                "title": "Customer favourites",
                "image": "https://placehold.co/900x720/cbd5e1/111827?text=Customer+favourites",
                "alt_text": "Customer favourites sample",
                "seo_keyword": "customer favourites",
                "destinations": [],
            },
        ],
    },
}


DEFAULT_PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ seo_title or doc.page }}</title>
  {% if seo_description %}<meta name="description" content="{{ seo_description }}">{% endif %}
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; color: #111827; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    img { max-width: 100%; }
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


def _fallback_blank_config():
    return {
        "title": "Blank Page",
        "tabs": [
            {
                "label": "SEO",
                "title": "SEO",
                "active": True,
                "sections": [
                    {
                        "label": "Search Engine Preview",
                        "fields": [
                            {
                                "label": "Title",
                                "type": "text",
                                "name": "seo_title",
                                "placeholder": "Enter SEO title",
                            },
                            {
                                "label": "Description",
                                "type": "textarea",
                                "name": "seo_description",
                                "placeholder": "Enter meta description",
                            },
                            {
                                "label": "Search Engine Visibility",
                                "type": "toggle",
                                "name": "allow_indexing_search_engine",
                                "default": True,
                            },
                        ],
                    }
                ],
            },
            {
                "label": "Configuration",
                "title": "Configuration",
                "active": False,
                "sections": [
                    {
                        "label": "Store settings",
                        "fields": [
                            {
                                "label": "Display Content",
                                "type": "toggle",
                                "name": "allow_indexing_social_1",
                                "default": True,
                            },
                            {
                                "label": "Enable Breadcrumbs",
                                "type": "toggle",
                                "name": "allow_indexing_social_2",
                                "default": True,
                            },
                        ],
                    }
                ],
            },
            {
                "label": "Page Info",
                "title": "Page Info",
                "active": False,
                "sections": [
                    {
                        "label": "Page details",
                        "fields": [
                            {
                                "label": "Thumbnail Image",
                                "type": "file",
                                "name": "thumnail_image",
                            },
                            {
                                "label": "Page Icon",
                                "type": "file",
                                "name": "page_image",
                            },
                        ],
                    }
                ],
            },
            {
                "label": "Content",
                "title": "Content",
                "active": False,
                "sections": [
                    {
                        "label": "Page content",
                        "fields": [
                            {
                                "label": "Summary",
                                "type": "editor",
                                "name": "page_summary",
                            }
                        ],
                    }
                ],
            },
            {
                "label": "Layout",
                "title": "Layout",
                "active": False,
                "sections": [
                    {
                        "fields": [
                            {
                                "label": "Header Blocks",
                                "name": "header",
                                "type": "draggable",
                            }
                        ]
                    },
                    {
                        "fields": [
                            {
                                "label": "Page Blocks",
                                "name": "main",
                                "type": "draggable",
                            }
                        ]
                    },
                    {
                        "fields": [
                            {
                                "label": "Footer Blocks",
                                "name": "footer",
                                "type": "draggable",
                            }
                        ]
                    },
                ],
            },
        ],
    }


def _blank_page_config_and_template():
    premium = frappe.db.get_value(
        "Ecommerce Template",
        {"page_name": "Premium Commerce Home"},
        ["data_json", "template"],
        as_dict=True,
    )
    if not premium:
        return _fallback_blank_config(), DEFAULT_PAGE_TEMPLATE

    try:
        config = json.loads(premium.data_json or "{}")
    except (TypeError, ValueError):
        config = _fallback_blank_config()
    return config, premium.template or DEFAULT_PAGE_TEMPLATE


def _block_instance(block_name, instance_id, values=None):
    if not frappe.db.exists("Ecommerce Block", block_name):
        return None

    block = frappe.get_doc("Ecommerce Block", block_name)
    try:
        model = json.loads(block.model or "{}")
    except (TypeError, ValueError):
        model = {}

    values = values or {}
    for field in model.get("fields") or []:
        field_name = field.get("name") or field.get("key")
        if field_name in values:
            field["value"] = copy.deepcopy(values[field_name])
        elif "default" in field and "value" not in field:
            field["value"] = copy.deepcopy(field["default"])

    return {
        "id": instance_id,
        "name": block.name,
        "block_name": block.block_name or block.name,
        "type": block.type,
        "is_template_starter": True,
        "block_details": {
            "name": block.name,
            "model": model,
        },
    }


def _configured_field_names(config):
    names = set()

    def visit(value):
        if isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            if value.get("type") and (value.get("name") or value.get("model")):
                names.add(value.get("name") or value.get("model"))
            for key in ("fields", "sections", "tabs"):
                visit(value.get(key))

    visit(config)
    return names


def execute():
    for page_name, preset in TEMPLATE_PRESETS.items():
        template_name = frappe.db.get_value(
            "Ecommerce Template", {"page_name": page_name}, "name"
        )
        if not template_name:
            continue

        template = frappe.get_doc("Ecommerce Template", template_name)
        try:
            config = json.loads(template.data_json or "{}")
        except (TypeError, ValueError):
            config = {}

        if page_name == "Blank Page":
            config, template_html = _blank_page_config_and_template()
            template.template = template_html

        # Older "Blank Page" records only contained SEO fields, which made it
        # impossible to add builder blocks after choosing the blank option.
        configured_fields = _configured_field_names(config)
        for area, label in (
            ("header", "Header Blocks"),
            ("main", "Page Blocks"),
            ("footer", "Footer Blocks"),
        ):
            if area not in configured_fields:
                config.setdefault("fields", []).append(
                    {"label": label, "name": area, "type": "draggable"}
                )

        starter_content = {
            "allow_indexing_search_engine": True,
            "header": [],
            "main": [],
            "footer": [],
            "Page": {},
        }
        for area in ("header", "main", "footer"):
            for index, block_name in enumerate(preset[area]):
                instance = _block_instance(
                    block_name,
                    f"starter-{page_name.lower().replace(' ', '-')}-{area}-{index + 1}",
                    BLOCK_VALUE_OVERRIDES.get((page_name, block_name)),
                )
                if instance:
                    starter_content[area].append(instance)

        config["template_description"] = preset["description"]
        config["default_page_title"] = page_name
        config["starter_content"] = starter_content
        template.data_json = json.dumps(config, indent=2)
        template.save(ignore_permissions=True)

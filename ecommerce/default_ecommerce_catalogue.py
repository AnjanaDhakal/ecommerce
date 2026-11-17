"""Portable starter catalogue used by new ecommerce websites and templates."""

import json

import frappe


ASSET_ROOT = "/assets/ecommerce/images/default-ecommerce-catalogue"

DEFAULT_BRAND = {
    "name": "Northstar",
    "slug": "ecommerce-default-northstar",
    "image": f"{ASSET_ROOT}/northstar.svg",
}

DEFAULT_CATEGORIES = [
    {
        "name": "Everyday Tech",
        "slug": "ecommerce-default-everyday-tech",
        "image": f"{ASSET_ROOT}/default-smartphone.jpg",
    },
    {
        "name": "Audio",
        "slug": "ecommerce-default-audio",
        "image": f"{ASSET_ROOT}/default-headphones.jpg",
    },
    {
        "name": "Workspace",
        "slug": "ecommerce-default-workspace",
        "image": f"{ASSET_ROOT}/default-laptop.jpg",
    },
]

DEFAULT_PRODUCTS = [
    {
        "name": "Default Product - Smartphone",
        "slug": "ecommerce-default-smartphone",
        "category": "ecommerce-default-everyday-tech",
        "image": f"{ASSET_ROOT}/default-smartphone.jpg",
        "price": 0,
        "description": "A dependable smartphone with a bright display and all-day battery.",
    },
    {
        "name": "Default Product - Headphones",
        "slug": "ecommerce-default-headphones",
        "category": "ecommerce-default-audio",
        "image": f"{ASSET_ROOT}/default-headphones.jpg",
        "price": 0,
        "description": "Comfortable wireless headphones with clear, balanced sound.",
    },
    {
        "name": "Default Product - Laptop",
        "slug": "ecommerce-default-laptop",
        "category": "ecommerce-default-workspace",
        "image": f"{ASSET_ROOT}/default-laptop.jpg",
        "price": 0,
        "description": "A slim everyday laptop for work, study, and travel.",
    },
    {
        "name": "Default Product - Camera",
        "slug": "ecommerce-default-camera",
        "category": "ecommerce-default-everyday-tech",
        "image": f"{ASSET_ROOT}/default-camera.jpg",
        "price": 0,
        "description": "A compact camera for sharp photos and easy everyday video.",
    },
    {
        "name": "Default Product - Speaker",
        "slug": "ecommerce-default-speaker",
        "category": "ecommerce-default-audio",
        "image": f"{ASSET_ROOT}/default-speaker.jpg",
        "price": 0,
        "description": "Portable room-filling sound in a durable compact design.",
    },
]

def _upsert(doctype, filters, values, refresh_existing=False):
    name = frappe.db.get_value(doctype, filters, "name")
    if name:
        doc = frappe.get_doc(doctype, name)
        if refresh_existing:
            doc.update(values)
            doc.save(ignore_permissions=True)
        return doc, False
    doc = frappe.get_doc({"doctype": doctype, **values})
    doc.insert(ignore_permissions=True)
    return doc, True


def ensure_default_ecommerce_catalogue(website_id, refresh_existing=False):
    """Create or refresh the app-owned five-product starter catalogue."""
    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["name", "type"],
        as_dict=True,
    )
    if not website or website.type != "Ecommerce":
        return {"products": [], "categories": [], "brands": [], "created": 0}

    created = 0
    brand, was_created = _upsert(
        "Ecommerce Brand",
        {"website": website_id, "slug": DEFAULT_BRAND["slug"]},
        {
            "brand_name": DEFAULT_BRAND["name"],
            "slug": DEFAULT_BRAND["slug"],
            "website": website_id,
            "brand_logo": DEFAULT_BRAND["image"],
            "publication_status": "Published",
            "seo_title": f"{DEFAULT_BRAND['name']} products",
            "seo_description": "Portable demo products included with Ecommerce.",
        },
        refresh_existing=refresh_existing,
    )
    created += int(was_created)

    categories_by_slug = {}
    categories = []
    for category_data in DEFAULT_CATEGORIES:
        category, was_created = _upsert(
            "Ecommerce Categories",
            {"website": website_id, "slug": category_data["slug"]},
            {
                "categories_name": category_data["name"],
                "slug": category_data["slug"],
                "website": website_id,
                "categories_logo": category_data["image"],
                "publication_status": "Published",
            },
            refresh_existing=refresh_existing,
        )
        created += int(was_created)
        categories.append(category)
        categories_by_slug[category_data["slug"]] = category

    products = []
    for index, product_data in enumerate(DEFAULT_PRODUCTS, start=1):
        category = categories_by_slug[product_data["category"]]
        variant = {
            "variant_name": "Standard",
            "selling_price": product_data["price"],
            "discounted_price": product_data["price"],
            "cost_price": round(product_data["price"] * 0.75, 2),
            "quantity": 25,
            "sku": f"LOGI360-DEMO-{index:03d}",
            "weight": 1,
            "volume": 1,
        }
        product, was_created = _upsert(
            "Ecommerce Product",
            {"website": website_id, "slug": product_data["slug"]},
            {
                "product_name": product_data["name"],
                "slug": product_data["slug"],
                "website": website_id,
                "brand": brand.name,
                "catagories": category.name,
                "product_image": product_data["image"],
                "gallery_images": json.dumps([]),
                "product_videos": json.dumps([]),
                "product_description": product_data["description"],
                "long_description": product_data["description"],
                "publication_status": "Published",
                "enable": 1,
                "continue_selling": 0,
                "varient": json.dumps([variant]),
            },
            refresh_existing=refresh_existing,
        )
        created += int(was_created)
        if was_created:
            product.append("categories", {"category": category.name})
            product.append("variants", variant)
            product.save(ignore_permissions=True)
        elif refresh_existing:
            product.set("categories", [])
            product.append("categories", {"category": category.name})
            product.set("variants", [])
            product.append("variants", variant)
            product.save(ignore_permissions=True)
        products.append(product)

    return {
        "products": products,
        "categories": categories,
        "brands": [brand],
        "created": created,
    }

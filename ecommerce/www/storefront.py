import json

import frappe

from ecommerce.api import (
    BUILDER_TAILWIND_HEAD_MARKUP,
    _builder_font_head_markup,
    _builder_inherit_published_layout,
    _ensure_builder_tailwind_runtime,
    _rewrite_storefront_links_for_custom_domain,
    get_storefront_entity,
)


no_cache = 1


def _builder_page_search_metadata(page):
    values = page.get("field_value") or {}
    if isinstance(values, str):
        try:
            values = json.loads(values)
        except (TypeError, ValueError):
            values = {}
    if not isinstance(values, dict):
        values = {}

    title = str(values.get("seo_title") or page.get("page") or "").strip()
    description = str(values.get("seo_description") or "").strip()
    keywords = values.get("seo_keywords") or values.get("meta_keywords") or ""
    if isinstance(keywords, list):
        keywords = ", ".join(
            str(value).strip() for value in keywords if str(value).strip()
        )
    else:
        keywords = str(keywords).strip()
    image = str(
        values.get("seo_image")
        or values.get("meta_image")
        or values.get("seo_logo")
        or ""
    ).strip()
    indexing_value = values.get("allow_indexing_search_engine", True)
    allow_indexing = indexing_value not in (
        False,
        0,
        "0",
        "false",
        "False",
        "no",
        "No",
    )
    metadata = {
        "title": title,
        "description": description,
        "robots": "index, follow" if allow_indexing else "noindex, nofollow",
    }
    if keywords:
        metadata["keywords"] = keywords
    if image:
        metadata["image"] = image
    return metadata


def get_context(context):
    website_id = frappe.form_dict.get("website_id")
    entity_type = frappe.form_dict.get("entity_type")
    entity_slug = frappe.form_dict.get("slug")

    website = (
        frappe.db.get_value(
            "Ecommerce Vendor Website",
            website_id,
            ["status", "favicon", "font"],
            as_dict=True,
        )
        if website_id
        else None
    )
    if not website or website.status != "Published":
        raise frappe.DoesNotExistError

    if website.favicon:
        context.favicon = website.favicon

    if entity_type == "page":
        page = frappe.db.get_value(
            "Ecommerce Page",
            {
                "website_id": website_id,
                "name": entity_slug,
                "page_status": ["!=", "Archived"],
            },
            [
                "name",
                "page",
                "parent1",
                "template",
                "field_value",
                "website_id",
                "block_render",
            ],
            as_dict=True,
        )
        if not page:
            raise frappe.DoesNotExistError
        search_metadata = _builder_page_search_metadata(page)
        context.title = search_metadata["title"]
        context.description = search_metadata["description"]
        context.metatags = frappe._dict(search_metadata)
        font_head_markup = _builder_font_head_markup(website.font)
        context.head_include = "\n".join(
            value
            for value in (
                context.get("head_include"),
                BUILDER_TAILWIND_HEAD_MARKUP,
                font_head_markup,
            )
            if value
        )
        context.builder_page = _ensure_builder_tailwind_runtime(
            _rewrite_storefront_links_for_custom_domain(
                _builder_inherit_published_layout(page),
                page.website_id,
            )
        )
        context.entity = None
        context.products = []
        return context

    response = get_storefront_entity(website_id, entity_type, entity_slug)
    if response.get("status") != "success":
        raise frappe.DoesNotExistError

    data = response["data"]
    context.title = data["entity"].get("title") or data["entity"].get("product_name")
    context.entity = data["entity"]
    context.products = data.get("products") or []
    context.builder_page = None
    return context

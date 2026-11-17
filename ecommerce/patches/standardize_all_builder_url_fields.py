"""Standardize builder URL fields to an internal link picker plus custom URL."""

import copy
import json
import re

import frappe


LINK_TYPES = {"commerce_link", "commerce_links"}
URL_FIELD_TYPES = {"normaltext", "text", "url"}


def _json_object(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError):
            return {}
    return {}


def _field_value(field):
    return copy.deepcopy(field.get("value", field.get("default")))


def _is_url_field(field):
    if not isinstance(field, dict) or field.get("type") not in URL_FIELD_TYPES:
        return False
    if field.get("external_url_only"):
        return False
    name = str(field.get("name") or "").strip().lower()
    label = str(field.get("label") or "").strip().lower()
    return name in {"url", "href", "link"} or name.endswith("_url") or "url" in label


def _name_tokens(name):
    return {
        token
        for token in re.split(r"[^a-z0-9]+", str(name or "").lower())
        if token and token not in {"custom", "destination", "destinations", "type"}
    }


def _related(link_field, url_field):
    if link_field.get("target_url_field") == url_field.get("name"):
        return True
    link_name = str(link_field.get("name") or "")
    url_name = str(url_field.get("name") or "")
    if link_name == "destinations" and url_name in {"url", "link", "href"}:
        return True
    link_tokens = _name_tokens(link_name)
    url_tokens = _name_tokens(url_name)
    return bool(link_tokens & url_tokens) or (
        link_name.startswith("link_") and url_name.startswith("link_")
    )


def _picker_name(url_name):
    if url_name in {"url", "href", "link"}:
        return "destinations"
    if url_name.endswith("_url"):
        return f"{url_name[:-4]}_destinations"
    return f"{url_name}_destinations"


def _friendly_labels(url_field):
    label = str(url_field.get("label") or "URL").strip()
    base = re.sub(r"\s*(?:custom\s+)?url\s*$", "", label, flags=re.IGNORECASE).strip()
    if not base or base.lower() == "link":
        return "Link", "Custom URL"
    return f"{base} link", f"{base} custom URL"


def _transform_fields(fields):
    fields = [copy.deepcopy(field) for field in fields or [] if isinstance(field, dict)]
    by_name = {field.get("name"): field for field in fields if field.get("name")}
    legacy_type_fields = {
        field.get("destination_type_field")
        for field in fields
        if field.get("type") == "commerce_link"
        and field.get("destination_type_field")
    }

    transformed = []
    for field in fields:
        name = field.get("name")
        if name in legacy_type_fields:
            continue

        if field.get("type") == "repeater":
            field["fields"] = _transform_fields(field.get("fields"))

        if field.get("type") == "commerce_link":
            type_field = by_name.get(field.get("destination_type_field")) or {}
            destination_type = _field_value(type_field)
            destination_id = _field_value(field)
            field["type"] = "commerce_links"
            field["multiple"] = False
            field.pop("destination_type_field", None)
            field.pop("value", None)
            field["default"] = []
            if destination_type and destination_id:
                field["value"] = [
                    {"type": destination_type, "value": destination_id}
                ]
            related_url = next(
                (candidate for candidate in fields if _is_url_field(candidate) and _related(field, candidate)),
                None,
            )
            if related_url:
                field["target_url_field"] = related_url.get("name")
            transformed.append(field)
            continue

        if not _is_url_field(field):
            transformed.append(field)
            continue

        related_picker = next(
            (
                candidate
                for candidate in [*transformed, *fields]
                if candidate is not field
                and candidate.get("type") in LINK_TYPES
                and _related(candidate, field)
            ),
            None,
        )
        picker_label, custom_label = _friendly_labels(field)
        if not related_picker:
            picker = {
                "label": picker_label,
                "type": "commerce_links",
                "name": _picker_name(str(name or "url")),
                "multiple": False,
                "target_url_field": name,
                "default": [],
            }
            transformed.append(picker)
        elif related_picker.get("type") == "commerce_links":
            related_picker["multiple"] = False
            related_picker["target_url_field"] = name
        field["label"] = custom_label
        transformed.append(field)
    return transformed


def _transform_model(model):
    model = copy.deepcopy(_json_object(model))
    if isinstance(model.get("fields"), list):
        model["fields"] = _transform_fields(model["fields"])
    for section in model.get("sections") or []:
        if isinstance(section, dict) and isinstance(section.get("fields"), list):
            section["fields"] = _transform_fields(section["fields"])
    for tab in model.get("tabs") or []:
        if not isinstance(tab, dict):
            continue
        if isinstance(tab.get("fields"), list):
            tab["fields"] = _transform_fields(tab["fields"])
        for section in tab.get("sections") or []:
            if isinstance(section, dict) and isinstance(section.get("fields"), list):
                section["fields"] = _transform_fields(section["fields"])
    return model


def _transform_block_instances(container):
    changed = False
    for section in ("header", "main", "footer"):
        for block in container.get(section) or []:
            if not isinstance(block, dict):
                continue
            details = block.get("block_details")
            if not isinstance(details, dict) or not details.get("model"):
                continue
            details["model"] = _transform_model(details["model"])
            changed = True
    return changed


def execute():
    for block_name in frappe.get_all("Ecommerce Block", pluck="name"):
        block = frappe.get_doc("Ecommerce Block", block_name)
        transformed_model = _transform_model(block.model)
        if transformed_model != _json_object(block.model):
            block.model = json.dumps(transformed_model)
            block.save(ignore_permissions=True)

    for page_name in frappe.get_all("Ecommerce Page", pluck="name"):
        page = frappe.get_doc("Ecommerce Page", page_name)
        field_value = _json_object(page.field_value)
        if _transform_block_instances(field_value):
            page.field_value = json.dumps(field_value)
            page.save(ignore_permissions=True)

    for template_name in frappe.get_all("Ecommerce Template", pluck="name"):
        template = frappe.get_doc("Ecommerce Template", template_name)
        data_json = _json_object(template.data_json)
        starter_content = data_json.get("starter_content")
        if isinstance(starter_content, dict) and _transform_block_instances(starter_content):
            template.data_json = json.dumps(data_json)
            template.save(ignore_permissions=True)

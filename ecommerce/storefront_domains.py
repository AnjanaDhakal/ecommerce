import re
from urllib.parse import urlparse

import frappe


DEFAULT_STOREFRONT_DOMAIN = "localhost"
RESERVED_SUBDOMAINS = {
    "admin",
    "api",
    "assets",
    "dashboard",
    "files",
    "private",
    "storefront",
    "www",
}


def storefront_base_domain():
    raw_value = str(
        frappe.conf.get("ecommerce_storefront_domain")
        or frappe.conf.get("host_name")
        or DEFAULT_STOREFRONT_DOMAIN
    ).strip()
    try:
        parsed = urlparse(raw_value if "://" in raw_value else f"//{raw_value}")
        return (parsed.hostname or DEFAULT_STOREFRONT_DOMAIN).lower().strip(".")
    except ValueError:
        return DEFAULT_STOREFRONT_DOMAIN


def storefront_url_scheme():
    value = str(frappe.conf.get("storefront_url_scheme") or "https").lower()
    return value if value in {"http", "https"} else "https"


def storefront_custom_domain_target():
    """Return the shared DNS endpoint advertised to custom-domain owners."""
    raw_value = str(
        frappe.conf.get("ecommerce_custom_domain_target")
        or storefront_base_domain()
    ).strip()
    try:
        parsed = urlparse(
            raw_value if "://" in raw_value else f"//{raw_value}",
        )
        host = (parsed.hostname or "").lower().strip(".")
    except ValueError:
        host = ""

    if not re.fullmatch(
        r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+",
        host,
    ):
        return storefront_base_domain()
    return host


def storefront_custom_domain_setup(value):
    """Describe the DNS record required for one configured custom hostname."""
    hostname = storefront_custom_domain(value)
    if not hostname:
        return None
    return {
        "hostname": hostname,
        "record_type": "CNAME",
        "target": storefront_custom_domain_target(),
        "proxy": "Proxied",
    }


def storefront_custom_domain(value):
    """Return the complete normalized hostname used as the routing key.

    Keep every DNS label, including ``www``. Custom storefront routing must
    distinguish hosts such as ``target.one.example`` and
    ``target.two.example`` even though their first label is the same.
    """
    raw_value = str(value or "").strip()
    if not raw_value or any(character.isspace() for character in raw_value):
        return None

    try:
        parsed = urlparse(
            raw_value if "://" in raw_value else f"//{raw_value}",
        )
        host = (parsed.hostname or "").lower().strip(".")
    except ValueError:
        return None

    if "." not in host:
        return None
    if not re.fullmatch(
        r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+",
        host,
    ):
        return None

    base_domain = storefront_base_domain()
    if host == base_domain or host.endswith(f".{base_domain}"):
        return None
    return host


def storefront_subdomain(value):
    custom_domain = storefront_custom_domain(value)
    # ``www`` is not useful in the generated storefront slug, but it remains part
    # of the exact custom-domain routing key above.
    slug_domain = (
        custom_domain[4:]
        if custom_domain and custom_domain.startswith("www.")
        else custom_domain
    )
    source = slug_domain.rsplit(".", 1)[0] if slug_domain else value
    slug = re.sub(r"[^a-z0-9]+", "-", str(source or "").lower()).strip("-")
    slug = slug[:63].rstrip("-")
    if not slug:
        frappe.throw("Website name must contain at least one letter or number.")
    if slug in RESERVED_SUBDOMAINS:
        frappe.throw("This website name is reserved. Please choose another name.")
    return slug


def _subdomain_is_used(subdomain, current_name=None):
    existing = frappe.db.get_value(
        "Ecommerce Vendor Website", {"subdomain": subdomain}, "name"
    )
    return bool(existing and str(existing) != str(current_name or ""))


def _subdomain_with_suffix(base, suffix):
    suffix = re.sub(r"[^a-z0-9]+", "-", str(suffix or "").lower()).strip("-")
    suffix = suffix or "vendor"
    available = 63 - len(suffix) - 1
    if available < 1:
        suffix = suffix[:61].rstrip("-")
        available = 63 - len(suffix) - 1
    return f"{base[:available].rstrip('-')}-{suffix}"


def available_storefront_subdomain(website_name, vendor_id, current_name=None):
    """Return a globally unique address while allowing names across vendors."""
    base = storefront_subdomain(website_name)
    if not _subdomain_is_used(base, current_name):
        return base

    vendor_suffix = re.sub(
        r"[^a-z0-9]+", "-", str(vendor_id or "vendor").lower()
    ).strip("-")
    candidate = _subdomain_with_suffix(base, vendor_suffix)
    if not _subdomain_is_used(candidate, current_name):
        return candidate

    number = 2
    while True:
        candidate = _subdomain_with_suffix(base, f"{vendor_suffix}-{number}")
        if not _subdomain_is_used(candidate, current_name):
            return candidate
        number += 1


def storefront_url(subdomain):
    return f"{storefront_url_scheme()}://{subdomain}.{storefront_base_domain()}"


def set_storefront_identity(doc):
    """Keep a website's public subdomain and canonical URL in sync with its name."""
    requested_custom_domain = str(doc.custom_domain or "").strip()
    doc.custom_domain = (
        storefront_custom_domain(requested_custom_domain)
        if requested_custom_domain
        else storefront_custom_domain(doc.website_link)
    )
    if requested_custom_domain and not doc.custom_domain:
        frappe.throw(
            "Custom domain must be a valid external hostname, such as example.com."
        )
    if not doc.is_new() and not doc.has_value_changed("website_link") and doc.subdomain:
        doc.canonical_url = storefront_url(doc.subdomain)
        return

    subdomain = available_storefront_subdomain(
        doc.website_link,
        doc.vendor_id,
        doc.name,
    )
    doc.subdomain = subdomain
    doc.canonical_url = storefront_url(subdomain)


def _storefront_subdomain_from_host(host):
    # Reverse proxies can append their own host to X-Forwarded-Host. The first
    # value is the hostname originally requested by the browser.
    host = str(host or "").split(",", 1)[0].strip().split(":", 1)[0]
    host = host.lower().strip(".")
    base_domain = storefront_base_domain()
    suffix = f".{base_domain}"
    if not host.endswith(suffix):
        return None
    subdomain = host[: -len(suffix)]
    return subdomain if subdomain and "." not in subdomain else None


def _storefront_request_subdomain(
    request_host, forwarded_host=None, original_host=None
):
    # Prefer the actual Host header. Some production proxies must rewrite Host
    # to the Frappe site name, so fall back to the standard forwarded/original
    # host headers to retain the public storefront hostname.
    for host in (request_host, forwarded_host, original_host):
        subdomain = _storefront_subdomain_from_host(host)
        if subdomain:
            return subdomain
    return None


def _request_subdomain():
    return _storefront_request_subdomain(
        frappe.request.host,
        frappe.get_request_header("X-Forwarded-Host"),
        frappe.get_request_header("X-Original-Host"),
    )


def _request_hosts():
    """Yield normalized request hosts in proxy-preference order."""
    seen = set()
    for value in (
        frappe.request.host,
        frappe.get_request_header("X-Forwarded-Host"),
        frappe.get_request_header("X-Original-Host"),
    ):
        host = str(value or "").split(",", 1)[0].strip().split(":", 1)[0]
        host = host.lower().strip(".")
        if host and host not in seen:
            seen.add(host)
            yield host


def _entity_from_path(path, home_page):
    clean_path = str(path or "/").strip("/")
    if not clean_path:
        return "page", home_page
    parts = clean_path.split("/", 1)
    if len(parts) != 2 or parts[0] not in {"page", "product", "category", "brand"}:
        return None, None
    return parts[0], parts[1]


def _serve_storefront_website(website, path):
    """Internally route a published website without changing the public host."""
    if not website:
        return False

    home_page = frappe.db.get_value(
        "Ecommerce Page",
        {
            "website_id": website.name,
            "page_status": ["!=", "Archived"],
        },
        "name",
        order_by="creation asc",
    )
    entity_type, entity_slug = _entity_from_path(path, home_page)
    if not entity_type or not entity_slug:
        return False

    frappe.form_dict.website_id = website.name
    frappe.form_dict.entity_type = entity_type
    frappe.form_dict.slug = entity_slug
    # Frappe resolves the request after before_request hooks have run.
    frappe.local.request.path = "/storefront"
    frappe.local.request.environ["PATH_INFO"] = "/storefront"
    return True


def route_wildcard_storefront():
    """Internally serve published storefronts on configured wildcard hosts."""
    subdomain = _request_subdomain()
    path = frappe.request.path or "/"
    if path.startswith(("/api/", "/assets/", "/files/", "/private/")):
        return

    if not subdomain:
        # Keep the site usable while new code is deployed ahead of `bench migrate`.
        # The website APIs still require migration before custom domains can be edited.
        if not frappe.db.has_column(
            "Ecommerce Vendor Website", "custom_domain"
        ):
            return
        for host in _request_hosts():
            custom_domain = storefront_custom_domain(host)
            if not custom_domain:
                continue
            website = frappe.db.get_value(
                "Ecommerce Vendor Website",
                {"custom_domain": custom_domain, "status": "Published"},
                ["name"],
                as_dict=True,
            )
            if _serve_storefront_website(website, path):
                return
        return

    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        {"subdomain": subdomain, "status": "Published"},
        ["name", "website_link"],
        as_dict=True,
    )
    if not website:
        # Never leak the main Frappe site's home/login page through a storefront
        # hostname. Let the storefront controller return a normal 404 instead.
        frappe.form_dict.website_id = None
        frappe.local.request.path = "/storefront"
        frappe.local.request.environ["PATH_INFO"] = "/storefront"
        return

    _serve_storefront_website(website, path)


def canonical_url_subdomain(value):
    """Extract a valid first label from an old canonical URL for migration."""
    try:
        host = (urlparse(str(value or "")).hostname or "").lower()
    except ValueError:
        return None
    suffix = f".{storefront_base_domain()}"
    if not host.endswith(suffix):
        return None
    candidate = host[: -len(suffix)]
    return candidate if re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", candidate) else None

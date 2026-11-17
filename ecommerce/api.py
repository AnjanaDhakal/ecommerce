import copy
import hashlib
import json
import frappe
from frappe import auth
from frappe import _
import base64
import binascii
import re
from urllib.parse import quote_plus, urlsplit
from uuid import uuid4
from datetime import timedelta
from decimal import Decimal
from html import escape
from jinja2 import Template
from frappe.utils import add_days, cint, get_datetime, getdate, now_datetime, nowdate

from ecommerce.storefront_domains import (
    storefront_base_domain,
    storefront_custom_domain_setup,
    storefront_custom_domain_target,
)


ECOMMERCE_FEATURE_DEFAULT_KEY = "ecommerce_ecommerce_enabled"

BUILDER_TAILWIND_HEAD_MARKUP = (
    '<script data-ecommerce-tailwind src="https://cdn.tailwindcss.com"></script>'
)


def _ensure_builder_tailwind_runtime(rendered_html):
    """Load Tailwind for a published builder document, not only its preview."""
    html = str(rendered_html or "")
    if re.search(
        r"<script\b(?=[^>]*\bdata-ecommerce-tailwind\b)[^>]*>",
        html,
        flags=re.IGNORECASE,
    ):
        return html
    if re.search(r"</head\s*>", html, flags=re.IGNORECASE):
        return re.sub(
            r"(</head\s*>)",
            rf"  {BUILDER_TAILWIND_HEAD_MARKUP}\n\1",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    return f"{BUILDER_TAILWIND_HEAD_MARKUP}\n{html}"

@frappe.whitelist()
def get_user_data():
    current_user = frappe.session.user
    user_data = frappe.db.get_value(
        "User",
        current_user,
        ["full_name", "user_image","email"],
        as_dict=True
    )

    return user_data


@frappe.whitelist(allow_guest=False)
def get_ecommerce_feature_status():
    """Return the signed-in user's opt-in state for the ECommerce workspace."""
    return {
        "status": "success",
        "data": {
            "enabled": bool(
                cint(
                    frappe.defaults.get_user_default(
                        ECOMMERCE_FEATURE_DEFAULT_KEY,
                        user=frappe.session.user,
                    )
                    or 0
                )
            )
        },
    }


def _unpublish_vendor_ecommerce_websites(vendor_id):
    """Take a vendor's published ECommerce storefronts offline without archiving them."""
    if not vendor_id:
        return 0

    website_names = frappe.get_all(
        "Ecommerce Vendor Website",
        filters={
            "vendor_id": vendor_id,
            "type": "Ecommerce",
            "status": "Published",
        },
        pluck="name",
    )
    for website_name in website_names:
        frappe.db.set_value(
            "Ecommerce Vendor Website",
            website_name,
            "status",
            "Draft",
            update_modified=True,
        )
    return len(website_names)


@frappe.whitelist(allow_guest=False)
def set_ecommerce_feature_status(enabled=None):
    """Enable or disable ECommerce for the signed-in user."""
    if frappe.request.method != "POST":
        frappe.local.response.http_status_code = 405
        return {
            "status": "error",
            "message": _("Invalid request method. Please use POST."),
        }

    request_data = frappe.request.get_json(silent=True) or {}
    enabled = request_data.get("enabled", enabled)
    enabled = enabled is True or str(enabled).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    unpublished_websites = 0
    if not enabled:
        vendor_info = get_vendor_id() or {}
        unpublished_websites = _unpublish_vendor_ecommerce_websites(
            vendor_info.get("vendor_id")
        )

    frappe.defaults.set_user_default(
        ECOMMERCE_FEATURE_DEFAULT_KEY,
        "1" if enabled else "0",
        user=frappe.session.user,
        parenttype="User",
    )
    frappe.db.commit()
    return {
        "status": "success",
        "message": _("ECommerce has been enabled.")
        if enabled
        else _("ECommerce has been disabled."),
        "data": {
            "enabled": enabled,
            "unpublished_websites": unpublished_websites,
        },
    }

@frappe.whitelist()
def get_vendor_id():
    """Use the signed-in Frappe user as the standalone store owner."""
    current_user = frappe.session.user
    if not current_user or current_user == "Guest":
        return {"status": "error", "message": "Authentication is required"}

    return {
        "status": "success",
        "vendor_id": current_user,
        "vendor_name": frappe.db.get_value("User", current_user, "full_name")
        or current_user,
    }


def _build_builder_preview_document(rendered_html):
    return f"""<!doctype html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="/">
    {BUILDER_TAILWIND_HEAD_MARKUP}
</head>
<body class="m-0 p-0 bg-gray-50">
{rendered_html}
</body>
</html>"""


def _rewrite_storefront_links_for_preview(rendered_html, website_id):
    """Keep storefront navigation inside the dashboard while previewing."""
    html = str(rendered_html or "")
    if not html or not website_id:
        return html

    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["canonical_url", "website_link"],
        as_dict=True,
    ) or {}
    public_urls = []
    for value in (website.get("canonical_url"), website.get("website_link")):
        value = str(value or "").strip().rstrip("/")
        if re.match(r"^https?://[^\s]+$", value, flags=re.IGNORECASE):
            public_urls.append(value)

    dashboard_base = f"/dashboard/store/{website_id}"
    home_page = frappe.db.get_value(
        "Ecommerce Page",
        {"website_id": website_id, "parent1": ["is", "not set"]},
        "name",
        order_by="creation asc",
    )

    for public_url in dict.fromkeys(public_urls):
        if home_page:
            home_url = f"{dashboard_base}/page/{home_page}"
            html = html.replace(f'href="{public_url}"', f'href="{home_url}"')
            html = html.replace(f"href='{public_url}'", f"href='{home_url}'")
        html = html.replace(f"{public_url}/", f"{dashboard_base}/")

    return html


BUILDER_GOOGLE_FONTS = {
    "Inter": ("Inter", "Inter:wght@300;400;500;600;700;800"),
    "Roboto": ("Roboto", "Roboto:wght@300;400;500;700;900"),
    "Outfit": ("Outfit", "Outfit:wght@300;400;500;600;700;800"),
    "Open Sans": ("Open Sans", "Open+Sans:wght@300;400;500;600;700;800"),
}


def _normalize_google_font_name(font_name):
    """Allow Google Font family names while rejecting CSS/HTML injection."""
    family = re.sub(r"\s+", " ", str(font_name or "").strip())
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .&+'-]{0,79}", family):
        return "Inter"
    return family

BUILDER_THEME_DEFAULTS = {
    "primary_color": "#ff4964",
    "secondary_color": "#111827",
    "additional_color1": "#111827",
    "additional_color2": "#ff4964",
    "font": "Inter",
}


def _builder_theme_values(website):
    """Return safe, consistently named theme values for builder/storefront clients."""
    values = website if isinstance(website, dict) else {}

    def color(field, fallback=None):
        value = str(values.get(field) or "").strip()
        return value if re.fullmatch(r"#[0-9a-fA-F]{6}", value) else (fallback or BUILDER_THEME_DEFAULTS[field])

    font = _normalize_google_font_name(
        values.get("font") or BUILDER_THEME_DEFAULTS["font"]
    )

    primary = color("primary_color")
    secondary = color("secondary_color")
    return {
        "primary_color": primary,
        "secondary_color": secondary,
        "additional_color_1": color("additional_color1", "#111827"),
        "additional_color_2": color("additional_color2", primary),
        "font": font,
    }


def _builder_theme_css(website):
    theme = _builder_theme_values(website)
    return """:root{{
  --store-primary:{primary};
  --store-secondary:{secondary};
  --store-additional-1:{additional_1};
  --store-additional-2:{additional_2};
  --store-surface:#f5f5f5;
  --store-action:var(--store-additional-1,#111827);
  --store-highlight:var(--store-additional-2,var(--store-primary));
  --store-ui-accent:var(--store-secondary,#2563eb);
  --store-role-60:var(--store-surface);
  --store-role-30:var(--store-secondary);
  --store-role-10:var(--store-primary);
  --store-font:"{font}",ui-sans-serif,system-ui,sans-serif;
}}
[data-theme-color="primary"]{{color:var(--store-primary)!important}}
[data-theme-bg="primary"]{{background-color:var(--store-primary)!important}}
[data-theme-color="secondary"]{{color:var(--store-secondary)!important}}
[data-theme-bg="secondary"]{{background-color:var(--store-secondary)!important}}
[data-theme-bg="surface"]{{background-color:var(--store-surface)!important}}
[data-theme-color="accent"]{{color:var(--store-highlight)!important}}
[data-theme-bg="accent"]{{background-color:var(--store-highlight)!important}}
[data-theme-bg="action"]{{background-color:var(--ecommerce-action-background,var(--store-action))!important}}
.ecommerce-theme-action-bg{{background-color:var(--ecommerce-action-background,var(--store-action))!important}}
.ecommerce-theme-secondary-bg{{background-color:var(--store-role-30,var(--store-secondary))!important}}
.rt-announcement a{{color:#fff!important}}
.rt-nav__actions span{{background-color:var(--store-ui-accent)!important}}
.rt-footer,.pc-footer{{background-color:var(--store-ui-accent)!important}}
""".format(
        primary=theme["primary_color"],
        secondary=theme["secondary_color"],
        additional_1=theme["additional_color_1"],
        additional_2=theme["additional_color_2"],
        font=escape(theme["font"], quote=True),
    )


def _builder_theme_head_markup(website):
    return f'<style data-ecommerce-theme>{_builder_theme_css(website)}</style>'


BUILDER_LEGACY_THEME_COLORS = {
    "#ff4964": "var(--store-primary)",
    "#7e51a2": "var(--store-primary)",
    "#e84cb0": "var(--store-primary)",
    "#111827": "var(--store-secondary)",
    "#0f172a": "var(--store-secondary)",
    "#d62b90": "var(--store-secondary)",
    "#f5f5f5": "var(--store-surface)",
    "#00ff00": "var(--store-surface)",
    "#fbbf24": "var(--store-accent)",
    "#ffa500": "var(--store-accent)",
}


def _builder_apply_theme_tokens(content):
    """Upgrade the original builder palette to live website theme variables."""
    themed = str(content or "")
    action_background = "var(--ecommerce-action-background,var(--store-action))"
    themed = re.sub(
        r"(background(?:-color)?\s*:\s*)#111827\b",
        rf"\1{action_background}",
        themed,
        flags=re.IGNORECASE,
    )
    themed = re.sub(
        r"bg-\[#111827\]",
        "ecommerce-theme-action-bg",
        themed,
        flags=re.IGNORECASE,
    )
    themed = re.sub(
        r"(?<![\w-])bg-(?:black|gray-900)(?![\w-])",
        "ecommerce-theme-action-bg",
        themed,
    )
    themed = re.sub(
        r"(background(?:-color)?\s*:\s*)#0f172a\b",
        r"\1var(--store-role-30,var(--store-secondary))",
        themed,
        flags=re.IGNORECASE,
    )
    themed = re.sub(
        r"bg-\[#0f172a\]|(?<![\w-])bg-slate-900(?![\w-])",
        "ecommerce-theme-secondary-bg",
        themed,
        flags=re.IGNORECASE,
    )
    for fixed_color, theme_token in BUILDER_LEGACY_THEME_COLORS.items():
        themed = re.sub(re.escape(fixed_color), theme_token, themed, flags=re.IGNORECASE)
    themed = re.sub(
        r"font-family\s*:\s*(?:Inter|Roboto|Outfit|[\"']?Open\s+Sans[\"']?)[^;}]*?(?=;|})",
        "font-family:var(--store-font)",
        themed,
        flags=re.IGNORECASE,
    )
    return themed


def _builder_font_head_markup(font_name):
    family = _normalize_google_font_name(font_name)
    query_family = quote_plus(family)
    stylesheet_url = (
        f"https://fonts.googleapis.com/css2?family={query_family}&display=swap"
    )
    safe_url = escape(stylesheet_url, quote=True)
    safe_family = escape(family, quote=True)
    return f"""<link data-ecommerce-font rel="preconnect" href="https://fonts.googleapis.com">
<link data-ecommerce-font rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link data-ecommerce-font rel="stylesheet" href="{safe_url}">
<style data-ecommerce-font>:root{{--font-stack:"{safe_family}",ui-sans-serif,system-ui,sans-serif}}html,body,button,input,select,textarea{{font-family:"{safe_family}",ui-sans-serif,system-ui,sans-serif}}</style>"""


def _apply_builder_head_metadata(
    rendered_html,
    field_value,
    page_title="",
    font_name="",
    website_theme=None,
):
    """Put builder Search Appearance values in the rendered document head."""
    html = rendered_html or ""
    values = field_value if isinstance(field_value, dict) else {}
    seo_title = str(values.get("seo_title") or page_title or "").strip()
    seo_description = str(values.get("seo_description") or "").strip()
    seo_keywords = values.get("seo_keywords") or values.get("meta_keywords") or ""
    if isinstance(seo_keywords, list):
        seo_keywords = ", ".join(str(value).strip() for value in seo_keywords if str(value).strip())
    else:
        seo_keywords = str(seo_keywords).strip()
    seo_image = str(
        values.get("seo_image")
        or values.get("meta_image")
        or values.get("seo_logo")
        or ""
    ).strip()
    indexing_value = values.get("allow_indexing_search_engine", True)
    allow_indexing = indexing_value not in (False, 0, "0", "false", "False", "no", "No")

    if not re.search(r"<head\b", html, flags=re.IGNORECASE):
        head = "<head></head>"
        if re.search(r"<html\b[^>]*>", html, flags=re.IGNORECASE):
            html = re.sub(
                r"(<html\b[^>]*>)",
                rf"\1{head}",
                html,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            html = f"<!doctype html><html>{head}<body>{html}</body></html>"

    title_tag = f"<title>{escape(seo_title)}</title>"
    if re.search(r"<title\b[^>]*>.*?</title\s*>", html, flags=re.IGNORECASE | re.DOTALL):
        html = re.sub(
            r"<title\b[^>]*>.*?</title\s*>",
            title_tag,
            html,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    else:
        html = re.sub(
            r"(<head\b[^>]*>)",
            rf"\1\n  {title_tag}",
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    def replace_meta(name, content):
        nonlocal html
        pattern = (
            r"<meta\b(?=[^>]*\bname\s*=\s*([\"'])"
            + re.escape(name)
            + r"\1)[^>]*>"
        )
        html = re.sub(pattern, "", html, flags=re.IGNORECASE)
        if content:
            meta_tag = (
                f'<meta name="{name}" content="{escape(str(content), quote=True)}">'
            )
            html = re.sub(
                r"(</head\s*>)",
                rf"  {meta_tag}\n\1",
                html,
                count=1,
                flags=re.IGNORECASE,
            )

    def replace_property(name, content):
        nonlocal html
        pattern = (
            r"<meta\b(?=[^>]*\bproperty\s*=\s*([\"'])"
            + re.escape(name)
            + r"\1)[^>]*>"
        )
        html = re.sub(pattern, "", html, flags=re.IGNORECASE)
        if content:
            meta_tag = (
                f'<meta property="{name}" content="{escape(str(content), quote=True)}">'
            )
            html = re.sub(
                r"(</head\s*>)",
                rf"  {meta_tag}\n\1",
                html,
                count=1,
                flags=re.IGNORECASE,
            )

    replace_meta("description", seo_description)
    replace_meta("keywords", seo_keywords)
    replace_meta("robots", "index, follow" if allow_indexing else "noindex, nofollow")
    replace_property("og:type", "website")
    replace_property("og:title", seo_title)
    replace_property("og:description", seo_description)
    replace_property("og:image", seo_image)
    replace_meta("twitter:card", "summary_large_image" if seo_image else "summary")
    replace_meta("twitter:title", seo_title)
    replace_meta("twitter:description", seo_description)
    replace_meta("twitter:image", seo_image)

    html = re.sub(
        r"<link\b(?=[^>]*\bdata-ecommerce-font\b)[^>]*>",
        "",
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<style\b(?=[^>]*\bdata-ecommerce-font\b)[^>]*>.*?</style\s*>",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r"<style\b(?=[^>]*\bdata-ecommerce-theme\b)[^>]*>.*?</style\s*>",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    font_markup = _builder_font_head_markup(font_name)
    theme_markup = _builder_theme_head_markup(website_theme or {"font": font_name})
    head_markup = "\n".join(value for value in (font_markup, theme_markup) if value)
    if head_markup:
        html = re.sub(
            r"(</head\s*>)",
            rf"  {head_markup}\n\1",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    return html


def _open_product_links_in_new_tab(rendered_html):
    """Keep a storefront listing or preview open when a product is selected."""
    if not rendered_html:
        return rendered_html
    return re.sub(
        r'<a(?![^>]*\btarget=)(?=[^>]*\bhref=["\'](?:/dashboard)?/store/[^"\']+/product/[^"\']+["\'])',
        '<a target="_blank" rel="noopener noreferrer"',
        rendered_html,
        flags=re.IGNORECASE,
    )


def _disable_empty_builder_links(rendered_html):
    """Make unset/placeholder builder links inert instead of navigating home.

    Several legacy blocks render missing destinations as ``href="#"`` or as
    fragment placeholders such as ``#shop``. In a preview these can jump to
    the dashboard route; on a published page they can unexpectedly navigate or
    scroll. Removing the href preserves the visual label without making it a
    route.
    """
    if not rendered_html:
        return rendered_html
    return re.sub(
        r"\s+href=(['\"])\s*(?:#[^'\"]*)?\1",
        ' aria-disabled="true" tabindex="-1"',
        rendered_html,
        flags=re.IGNORECASE,
    )


def _inject_storefront_cart_runtime(rendered_html, website_id):
    """Keep cart actions and header counts synchronized on builder pages."""
    html = rendered_html or ""
    has_add_to_cart = "ecommerce-add-to-cart" in html
    has_cart_link = bool(
        re.search(
            r"(?:<(?:a|button)\b[^>]*(?:data-storefront-cart|ecommerce-storefront-cart|href=['\"][^'\"]*/cart)|<path\b[^>]*d=['\"][^'\"]*(?:239\.89|120A16))",
            html,
            flags=re.IGNORECASE,
        )
    )
    if not has_add_to_cart and not has_cart_link:
        return rendered_html
    website_json = json.dumps(str(website_id or ""))
    has_add_to_cart_json = json.dumps(has_add_to_cart)
    return f"""{rendered_html}
<script>
(() => {{
  const storageKey = 'ecommerce_storefront_cart';
  const websiteId = {website_json};
  const hasAddToCart = {has_add_to_cart_json};

  const readCart = () => {{
    try {{ return JSON.parse(localStorage.getItem(storageKey) || '[]'); }}
    catch (_) {{ return []; }}
  }};
  const findCartLink = () => {{
    const explicitLink = document.querySelector(
      '[data-storefront-cart], .ecommerce-storefront-cart, a[href*="/cart"]'
    );
    if (explicitLink) return explicitLink;
    return Array.from(document.querySelectorAll('#list-action a, #list-action button')).find(link => {{
      const iconPath = link.querySelector('svg path')?.getAttribute('d') || '';
      return iconPath.includes('239.89') || iconPath.includes('120A16');
    }}) || null;
  }};
  const ensureCartLink = () => {{
    let cartLink = findCartLink();
    if (cartLink || !hasAddToCart) return cartLink;
    cartLink = document.createElement('a');
    cartLink.href = `/dashboard/store/${{encodeURIComponent(websiteId)}}/cart`;
    cartLink.target = '_blank';
    cartLink.rel = 'noopener noreferrer';
    cartLink.className = 'ecommerce-floating-cart';
    cartLink.style.cssText = 'position:fixed;right:20px;bottom:20px;z-index:9999;padding:12px 18px;border-radius:999px;background:#111827;color:white;text-decoration:none;font:600 14px system-ui;box-shadow:0 8px 24px #0003';
    document.body.appendChild(cartLink);
    return cartLink;
  }};
  const refreshCart = () => {{
    const count = readCart()
      .filter(item => String(item.website_id || '') === websiteId)
      .reduce((total, item) => total + Math.max(0, Number(item.quantity || 0)), 0);
    const cartLink = ensureCartLink();
    if (!cartLink) return;
    const cartUrl = `/dashboard/store/${{encodeURIComponent(websiteId)}}/cart`;
    if (cartLink.tagName === 'A') cartLink.setAttribute('href', cartUrl);
    else {{
      cartLink.setAttribute('role', 'link');
      if (!cartLink.dataset.cartNavigationBound) {{
        cartLink.addEventListener('click', () => {{ window.location.href = cartUrl; }});
        cartLink.dataset.cartNavigationBound = 'true';
      }}
    }}
    cartLink.removeAttribute('aria-disabled');
    cartLink.removeAttribute('tabindex');
    cartLink.removeAttribute('target');
    cartLink.removeAttribute('rel');
    if (cartLink.classList.contains('ecommerce-floating-cart')) {{
      cartLink.textContent = `View cart (${{count > 99 ? '99+' : count}})`;
      return;
    }}
    cartLink.classList.add('ecommerce-storefront-cart');
    cartLink.dataset.storefrontCart = 'true';
    cartLink.style.position = 'relative';
    cartLink.style.display = 'inline-flex';
    cartLink.style.alignItems = 'center';
    cartLink.style.justifyContent = 'center';
    cartLink.setAttribute('aria-label', `Cart, ${{count}} item${{count === 1 ? '' : 's'}}`);
    let badge = cartLink.querySelector('.ecommerce-cart-count, [data-cart-count]');
    if (!badge) {{
      badge = Array.from(cartLink.children).find(child =>
        child.tagName === 'SPAN' && /^\\s*\\d+\\s*$/.test(child.textContent || '')
      ) || null;
    }}
    if (!badge) {{
      badge = document.createElement('span');
      badge.setAttribute('aria-hidden', 'true');
      cartLink.appendChild(badge);
    }}
    badge.classList.add('ecommerce-cart-count');
    badge.dataset.cartCount = 'true';
    badge.textContent = count > 99 ? '99+' : String(count);
    badge.style.cssText = 'position:static;display:inline-grid;place-items:center;min-width:20px;height:20px;margin-left:6px;padding:0 5px;border:2px solid white;border-radius:9999px;background:var(--store-ui-accent,var(--store-secondary,#2563eb));color:white;font:700 11px/1 system-ui,sans-serif;box-sizing:border-box;';
  }};
  refreshCart();
  window.addEventListener('ecommerce:cart-updated', refreshCart);
  window.addEventListener('storage', event => {{
    if (!event.key || event.key === storageKey) refreshCart();
  }});
  window.addEventListener('focus', refreshCart);

  document.addEventListener('click', async (event) => {{
    const button = event.target.closest('.ecommerce-add-to-cart');
    if (!button) return;
    event.preventDefault();
    if (button.disabled) return;
    const originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = 'Adding…';
    try {{
      const match = String(button.dataset.productUrl || '').match(new RegExp('/store/([^/]+)/product/([^/?#]+)'));
      if (!match) throw new Error('Product link is unavailable');
      const params = new URLSearchParams({{ website_id: match[1], entity_type: 'product', slug: decodeURIComponent(match[2]) }});
      const response = await fetch(`/api/method/ecommerce.api.get_storefront_entity?${{params}}`);
      const body = await response.json();
      const product = body?.message?.data?.entity;
      if (!response.ok || !product) throw new Error(body?.message?.message || 'Unable to load product');
      const variants = product.variant || product.varient || [];
      const variant = variants[0] || null;
      if (variant && Number(variant.quantity || 0) <= 0 && !product.continue_selling) throw new Error('Out of stock');
      const discountedPrice = Number(variant?.discounted_price || 0);
      const price = variant
        ? Number(discountedPrice > 0 ? discountedPrice : (variant.selling_price ?? variant.cost_price ?? 0))
        : Number(product.price || 0);
      const variantName = variant?.variant_name || variant?.name || '';
      const key = `${{product.website}}:${{product.id}}:${{variantName}}`;
      const cart = readCart();
      const existing = cart.find(item => item.key === key);
      if (existing) existing.quantity += 1;
      else cart.push({{
        key,
        website_id: product.website,
        product_id: product.id,
        product_name: product.product_name,
        image: product.image || '',
        variant,
        price,
        quantity: 1,
      }});
      localStorage.setItem(storageKey, JSON.stringify(cart));
      window.dispatchEvent(new CustomEvent('ecommerce:cart-updated', {{ detail: {{ cart }} }}));
      button.textContent = 'Added to cart';
      refreshCart();
      setTimeout(() => {{ button.textContent = originalLabel; button.disabled = false; }}, 1200);
    }} catch (error) {{
      button.textContent = error?.message || 'Unable to add';
      setTimeout(() => {{ button.textContent = originalLabel; button.disabled = false; }}, 1800);
    }}
  }});
}})();
</script>"""


@frappe.whitelist(allow_guest=False)
def get_page_preview(page_name=None):
    """Return the rendered HTML for a builder page owned by the current vendor."""
    if frappe.request.method != "GET":
        return {
            "status": "error",
            "message": _("Invalid request method. Please use GET."),
        }

    page_name = page_name or (frappe.local.form_dict or {}).get("page_name")
    if not page_name:
        return {"status": "error", "message": _("Page name is required.")}

    vendor_info = get_vendor_id() or {}
    vendor_id = vendor_info.get("vendor_id")
    if not vendor_id:
        return {
            "status": "error",
            "message": vendor_info.get("message") or _("Vendor not found."),
        }

    page = frappe.db.get_value(
        "Ecommerce Page",
        page_name,
        [
            "name",
            "page",
            "parent1",
            "template",
            "field_value",
            "website_id",
            "website_name",
            "block_render",
        ],
        as_dict=True,
    )
    if not page:
        return {"status": "error", "message": _("Page not found.")}

    page_vendor_id = frappe.db.get_value(
        "Ecommerce Vendor Website",
        page.website_id,
        "vendor_id",
    )
    if not page_vendor_id or str(page_vendor_id) != str(vendor_id):
        frappe.local.response.http_status_code = 403
        return {"status": "error", "message": _("You cannot preview this page.")}

    rendered_html = _builder_inherit_published_layout(page)
    if not rendered_html:
        return {
            "status": "error",
            "message": _("No rendered preview is available. Save and publish the page first."),
        }

    preview_html = _build_builder_preview_document(
        _rewrite_storefront_links_for_preview(rendered_html, page.website_id)
    )

    return {
        "status": "success",
        "message": _("Page preview fetched successfully."),
        "data": {
            "name": page.name,
            "page": page.page,
            "website_name": page.website_name,
            "block_render": rendered_html,
            "preview": preview_html,
            "preview_url": f"/dashboard/store/{page.website_id}/page/{page.name}?preview=1",
        },
    }


def _extract_storefront_section(rendered_html, tag):
    """Extract a layout wrapper without confusing nested semantic elements.

    Builder blocks may contain their own ``header`` and ``footer`` elements.
    Track same-tag nesting so the first page header and last page footer are
    selected instead of an article card's internal markup.
    """
    html = rendered_html or ""
    normalized_tag = re.escape(str(tag or "").strip())
    if not html or not normalized_tag:
        return ""

    token_pattern = re.compile(
        rf"<\s*(/?)\s*{normalized_tag}\b[^>]*>",
        flags=re.IGNORECASE,
    )
    stack = []
    sections = []
    for token in token_pattern.finditer(html):
        if not token.group(1):
            stack.append(token.end())
            continue
        if not stack:
            continue
        content_start = stack.pop()
        if not stack:
            sections.append(html[content_start:token.start()].strip())

    if not sections:
        return ""
    return sections[-1] if str(tag).lower() == "footer" else sections[0]


def _replace_storefront_section(rendered_html, source_html, tag):
    """Replace a page's outer layout section with the root page section."""
    replacement = _extract_storefront_section(source_html, tag)
    if not replacement:
        return rendered_html or ""

    html = rendered_html or ""
    normalized_tag = re.escape(str(tag or "").strip())
    token_pattern = re.compile(
        rf"<\s*(/?)\s*{normalized_tag}\b[^>]*>",
        flags=re.IGNORECASE,
    )
    stack = []
    sections = []
    for token in token_pattern.finditer(html):
        if not token.group(1):
            stack.append(token.end())
            continue
        if not stack:
            continue
        content_start = stack.pop()
        if not stack:
            sections.append((content_start, token.start()))

    if not sections:
        return html
    content_start, content_end = (
        sections[-1] if str(tag).lower() == "footer" else sections[0]
    )
    return f"{html[:content_start]}{replacement}{html[content_end:]}"


def _builder_inherit_published_layout(page):
    """Use the root page's published header/footer for child storefront pages."""
    if isinstance(page, (str, int)):
        page = frappe.db.get_value(
            "Ecommerce Page",
            page,
            [
                "name",
                "parent1",
                "template",
                "field_value",
                "website_id",
                "block_render",
            ],
            as_dict=True,
        )
    if not page:
        return ""

    rendered_html = page.get("block_render") or ""
    if not rendered_html or not page.get("parent1"):
        return rendered_html

    root_page = _builder_root_page(page)
    if str(root_page.get("name")) == str(page.get("name")):
        return rendered_html

    root_render = frappe.db.get_value(
        "Ecommerce Page", root_page.get("name"), "block_render"
    ) or ""
    if not root_render:
        return rendered_html

    for section in ("header", "footer"):
        rendered_html = _replace_storefront_section(
            rendered_html,
            root_render,
            section,
        )
    return rendered_html


@frappe.whitelist(allow_guest=True)
def get_storefront_shell(website_id=None):
    """Return the published builder header/footer shared by storefront routes."""
    website_id = website_id or (frappe.local.form_dict or {}).get("website_id")
    if not website_id:
        return {"status": "error", "message": _("Website is required.")}

    website_theme = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        [
            "primary_color",
            "secondary_color",
            "additional_color1",
            "additional_color2",
            "font",
            "tawk_widget_id",
        ],
        as_dict=True,
    ) or {}
    theme = _builder_theme_values(website_theme)

    pages = frappe.get_all(
        "Ecommerce Page",
        filters={"website_id": website_id, "page_status": ["!=", "Archived"]},
        fields=["name", "page", "block_render", "creation"],
        order_by="creation asc",
    )
    published_pages = [page for page in pages if page.get("block_render")]
    if not published_pages:
        return {
            "status": "success",
            "data": {
                "header": "",
                "footer": "",
                "styles": "",
                "page_id": None,
                "theme": theme,
                "tawk_widget_id": website_theme.get("tawk_widget_id") or "",
            },
        }

    page = next(
        (
            item
            for item in published_pages
            if str(item.get("page") or "").strip().lower()
            in {"home", "home page", "homepage"}
        ),
        published_pages[0],
    )
    rendered_html = page.get("block_render") or ""
    # This endpoint powers the dashboard storefront routes (category, brand,
    # product, cart). Keep links in the shared header/footer inside that same
    # dashboard preview instead of sending them to the public domain.
    preview_html = _rewrite_storefront_links_for_preview(rendered_html, website_id)
    styles = "\n".join(
        match.strip()
        for match in re.findall(
            r"<style\b[^>]*>(.*?)</style>",
            rendered_html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match.strip()
    )
    return {
        "status": "success",
        "data": {
            "header": _extract_storefront_section(preview_html, "header"),
            "footer": _extract_storefront_section(preview_html, "footer"),
            "styles": styles,
            "page_id": page.name,
            "theme": theme,
            "tawk_widget_id": website_theme.get("tawk_widget_id") or "",
        },
    }




# def format_number_nepali(value):
#     """Return number with Nepali digits and Indian grouping (e.g., 20500 -> २०,५००)."""
#     nepali_digits = '०१२३४५६७८९'

#     def to_nepali_digits(s: str) -> str:
#         return ''.join(nepali_digits[int(ch)] if ch.isdigit() else ch for ch in s)

#     try:
#         num = float(value)
#     except (TypeError, ValueError):
#         return value

#     is_negative = num < 0
#     num = abs(num)

#     integer_part, dot, decimal_part = f"{num:.2f}".partition('.')
#     decimal_part = decimal_part.rstrip('0')

#     # Indian numbering grouping
#     if len(integer_part) > 3:
#         last3 = integer_part[-3:]
#         remaining = integer_part[:-3]
#         groups = []
#         while remaining:
#             groups.append(remaining[-2:])
#             remaining = remaining[:-2]
#         grouped_int = ','.join(reversed(groups)) + ',' + last3
#     else:
#         grouped_int = integer_part

#     nepali_int = to_nepali_digits(grouped_int)
#     nepali_dec = to_nepali_digits(decimal_part) if decimal_part else ''

#     result = nepali_int
#     if nepali_dec:
#         result += '.' + nepali_dec
#     if is_negative:
#         result = '-' + result
#     return result


def format_number_indian(value):
    """Return number with Indian grouping using English digits (e.g., 20500 -> '20,500')."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return value

    is_negative = num < 0
    num = abs(num)

    integer_part, dot, decimal_part = f"{num:.2f}".partition('.')
    decimal_part = decimal_part.rstrip('0')

    if len(integer_part) > 3:
        last3 = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while remaining:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        grouped_int = ','.join(reversed(groups)) + ',' + last3
    else:
        grouped_int = integer_part

    result = grouped_int
    if decimal_part:
        result += '.' + decimal_part
    if is_negative:
        result = '-' + result
    return result


def _copy_builder_catalogue(source_website, target_website, vendor_id):
    """Copy a vendor's catalogue to another website without duplicating slugs."""
    source_website = str(source_website or "")
    target_website = str(target_website or "")
    if not source_website or not target_website or source_website == target_website:
        return {"brands": 0, "categories": 0, "products": 0, "skipped": 0}

    website_vendors = frappe.db.get_values(
        "Ecommerce Vendor Website",
        {"name": ["in", [source_website, target_website]]},
        ["name", "vendor_id", "type"],
        as_dict=True,
    )
    vendor_by_website = {str(row.name): str(row.vendor_id or "") for row in website_vendors}
    type_by_website = {str(row.name): str(row.type or "") for row in website_vendors}
    expected_vendor = str(vendor_id or "")
    if (
        vendor_by_website.get(source_website) != expected_vendor
        or vendor_by_website.get(target_website) != expected_vendor
    ):
        frappe.throw(_("You can only copy a catalogue between your own websites."))
    if (
        type_by_website.get(source_website) != "Ecommerce"
        or type_by_website.get(target_website) != "Ecommerce"
    ):
        frappe.throw(_("Catalogues can only be copied between ecommerce websites."))

    counts = {"brands": 0, "categories": 0, "products": 0, "skipped": 0}

    target_brands = frappe.get_all(
        "Ecommerce Brand",
        filters={"website": target_website},
        fields=["name", "slug"],
    )
    target_brand_by_slug = {str(row.slug or ""): row.name for row in target_brands}
    brand_map = {}
    for source_name in frappe.get_all(
        "Ecommerce Brand",
        filters={"website": source_website},
        pluck="name",
        order_by="creation asc",
    ):
        source_doc = frappe.get_doc("Ecommerce Brand", source_name)
        slug = str(source_doc.slug or _builder_slug(source_doc.brand_name))
        existing_name = target_brand_by_slug.get(slug)
        if existing_name:
            brand_map[str(source_name)] = existing_name
            counts["skipped"] += 1
            continue
        copied_doc = frappe.copy_doc(source_doc)
        copied_doc.website = target_website
        copied_doc.insert(ignore_permissions=True)
        brand_map[str(source_name)] = copied_doc.name
        target_brand_by_slug[slug] = copied_doc.name
        counts["brands"] += 1

    target_categories = frappe.get_all(
        "Ecommerce Categories",
        filters={"website": target_website},
        fields=["name", "slug"],
    )
    target_category_by_slug = {
        str(row.slug or ""): row.name for row in target_categories
    }
    category_map = {}
    copied_categories = []
    source_categories = frappe.get_all(
        "Ecommerce Categories",
        filters={"website": source_website},
        pluck="name",
        order_by="creation asc",
    )
    for source_name in source_categories:
        source_doc = frappe.get_doc("Ecommerce Categories", source_name)
        slug = str(source_doc.slug or _builder_slug(source_doc.categories_name))
        existing_name = target_category_by_slug.get(slug)
        if existing_name:
            category_map[str(source_name)] = existing_name
            counts["skipped"] += 1
            continue
        copied_doc = frappe.copy_doc(source_doc)
        copied_doc.website = target_website
        copied_doc.parent_category = None
        copied_doc.insert(ignore_permissions=True)
        category_map[str(source_name)] = copied_doc.name
        target_category_by_slug[slug] = copied_doc.name
        copied_categories.append((source_doc, copied_doc))
        counts["categories"] += 1

    # Parents must be assigned after every category has a target ID.
    for source_doc, copied_doc in copied_categories:
        target_parent = category_map.get(str(source_doc.parent_category or ""))
        if target_parent:
            copied_doc.parent_category = target_parent
            copied_doc.save(ignore_permissions=True)

    target_products = frappe.get_all(
        "Ecommerce Product",
        filters={"website": target_website},
        fields=["name", "slug"],
    )
    target_product_slugs = {str(row.slug or "") for row in target_products}
    for source_name in frappe.get_all(
        "Ecommerce Product",
        filters={"website": source_website},
        pluck="name",
        order_by="creation asc",
    ):
        source_doc = frappe.get_doc("Ecommerce Product", source_name)
        slug = str(source_doc.slug or _builder_slug(source_doc.product_name))
        if slug in target_product_slugs:
            counts["skipped"] += 1
            continue

        copied_doc = frappe.copy_doc(source_doc)
        copied_doc.website = target_website
        copied_doc.brand = brand_map.get(str(source_doc.brand or ""))
        copied_doc.catagories = category_map.get(str(source_doc.catagories or ""))
        for category_row in copied_doc.get("categories") or []:
            category_row.category = category_map.get(str(category_row.category or ""))
        copied_doc.set(
            "categories",
            [row for row in (copied_doc.get("categories") or []) if row.category],
        )
        copied_doc.insert(ignore_permissions=True)
        target_product_slugs.add(slug)
        counts["products"] += 1

    return counts


def _apply_catalogue_template_defaults(
    field_value,
    products=None,
    categories=None,
    brands=None,
):
    """Populate fresh template blocks with the portable starter catalogue."""
    values = copy.deepcopy(_builder_json_object(field_value))
    products = list(products or [])[:5]
    categories = list(categories or [])[:3]
    brands = list(brands or [])[:1]
    product_ids = [row.get("name") for row in products if row.get("name")]
    category_ids = [row.get("name") for row in categories if row.get("name")]

    def linked_items(rows, entity_type, title_field, image_field, samples):
        items = []
        for index, row in enumerate(rows):
            sample = copy.deepcopy(samples[index]) if index < len(samples) else {}
            sample.update({
                "title": row.get(title_field) or row.get("name"),
                "destinations": [{
                    "type": entity_type,
                    "value": row.get("name"),
                    "label": row.get(title_field) or row.get("name"),
                }],
            })
            if row.get(image_field):
                sample["image"] = row.get(image_field)
            items.append(sample)
        return items

    def category_navigation_links(rows):
        return [
            {
                "label": row.get("categories_name") or row.get("name"),
                "destinations": [{
                    "type": "category",
                    "value": row.get("name"),
                    "label": row.get("categories_name") or row.get("name"),
                }],
                "url": "",
            }
            for row in rows
            if row.get("name")
        ]

    for section in ("header", "main", "footer"):
        for block in values.get(section) or []:
            if not isinstance(block, dict):
                continue
            details = block.get("block_details")
            details = details if isinstance(details, dict) else {}
            model = details.get("model") or block.get("model") or {}
            if isinstance(model, str):
                try:
                    model = json.loads(model)
                except (TypeError, ValueError):
                    model = {}
            if not isinstance(model, dict):
                continue

            model_name = str(model.get("block_name") or "").strip().lower()
            for field in _builder_model_fields(model):
                field_name = field.get("name") or field.get("key")
                field_type = str(field.get("type") or "").strip().lower()
                current_value = field.get("value")

                if field_type == "product" and product_ids:
                    field["value"] = copy.deepcopy(product_ids)
                elif (
                    field_type == "categories"
                    and category_ids
                    and current_value in (None, "", [])
                ):
                    field["value"] = copy.deepcopy(category_ids)
                elif field_name == "items" and categories and model_name in {
                    "commerce_category_showcase",
                    "retail_collection_mosaic",
                }:
                    samples = current_value or field.get("default") or []
                    field["value"] = linked_items(
                        categories,
                        "category",
                        "categories_name",
                        "categories_logo",
                        samples if isinstance(samples, list) else [],
                    )
                elif (
                    field_name == "items"
                    and brands
                    and model_name == "commerce_brand_showcase"
                ):
                    samples = current_value or field.get("default") or []
                    field["value"] = linked_items(
                        brands,
                        "brand",
                        "brand_name",
                        "brand_logo",
                        samples if isinstance(samples, list) else [],
                    )
                elif (
                    field_name == "links"
                    and categories
                    and model_name == "retail_navigation"
                ):
                    field["value"] = category_navigation_links(categories)

    return values


def _builder_catalogue_template_defaults(field_value, website_id):
    """Ensure and apply the portable app-owned starter catalogue."""
    if not website_id:
        return _builder_json_object(field_value)

    from ecommerce.default_ecommerce_catalogue import (
        ensure_default_ecommerce_catalogue,
    )

    catalogue = ensure_default_ecommerce_catalogue(website_id)
    return _apply_catalogue_template_defaults(
        field_value,
        products=catalogue.get("products"),
        categories=catalogue.get("categories"),
        brands=catalogue.get("brands"),
    )



@frappe.whitelist(allow_guest=False)
def create_website():
    import json

    if frappe.request.method != "POST":
        return {
            "status": "error",
            "message": _("Invalid request method. Please use POST.")
        }

    try:
        current_user = frappe.session.user
        user_roles = frappe.get_roles(current_user)

        result = get_vendor_id()
        vendor_ID = result.get("vendor_id")
        if not vendor_ID:
            return {
                "status": "error",
                "message": _("Vendor ID not found for the current user"),
            }

        data = json.loads(frappe.request.data or "{}")

        # ✅ Fields
        name = data.get("name")
        status = data.get("status")
        website_type = data.get("type")
        template = data.get("template") or "Default"
        description = data.get("description")
        canonical_url = data.get("canonical_url")
        custom_domain = data.get("custom_domain")
        primary_color = data.get("color")
        font = _normalize_google_font_name(data.get("font"))
        secondary_color = data.get("secondary_color")
        additional_color_1 = data.get("additional_color_1")
        additional_color_2 = data.get("additional_color_2")
        catalogue_source = data.get("catalogue_source")
        favicon = data.get("favicon")

        # ✅ Mandatory fields check (all except description & colors)
        missing_fields = []
        if not name:
            missing_fields.append("name")
        if not status:
            missing_fields.append("status")
        if not website_type:
            missing_fields.append("type")
        if missing_fields:
            return {
                "status": "error",
                "message": _("Missing required fields: {0}").format(", ".join(missing_fields))
            }

        # Default and Blank are built-in choices rather than linked Template
        # documents. If templates exist, Default uses the oldest configured
        # template; otherwise both choices safely create an untemplated page.
        page_template = template
        if template == "Default":
            page_template = frappe.db.get_value(
                "Ecommerce Template",
                {},
                "name",
                order_by="creation asc",
            )
        elif template == "Blank":
            page_template = None

        # ✅ Create website doc with colors + font
        new_doc = frappe.get_doc({
            "doctype": "Ecommerce Vendor Website",
            "vendor_id": vendor_ID,
            "website_link": name,
            "canonical_url": canonical_url,
            "custom_domain": custom_domain,
            "description": description,
            "type": website_type,
            "status": status,
            "template": page_template or template,
            "primary_color": primary_color,
            "font": font,
            "secondary_color": secondary_color,
            "additional_color1": additional_color_1,
            "additional_color2": additional_color_2
        })
        new_doc.insert(ignore_permissions=True)

        if favicon:
            new_doc.favicon = _save_builder_image(
                favicon,
                "Ecommerce Vendor Website",
                new_doc.name,
                "favicon",
                "favicon",
            )
            new_doc.save(ignore_permissions=True)

        catalogue_counts = _copy_builder_catalogue(
            catalogue_source,
            new_doc.name,
            vendor_ID,
        )

        # ✅ Create associated Home page
        new_page = frappe.get_doc({
            "doctype": "Ecommerce Page",
            "website_id": new_doc.name,
            "website_name": new_doc.website_link,
            "page": "Home",
            "template": page_template,
        })
        new_page.field_value = _builder_effective_field_value(new_page, {})
        new_page.field_value = _builder_catalogue_template_defaults(
            new_page.field_value,
            new_doc.name,
        )
        new_page.insert(ignore_permissions=True)
        _publish_initial_builder_page(new_page)

        frappe.db.commit()

        return {
            "status": "success",
            "message": _("Website and page created successfully"),
            "doc": new_doc,
            "page": new_page,
            "catalogue": catalogue_counts,
            "custom_domain_dns": storefront_custom_domain_setup(
                new_doc.custom_domain
            ),
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=str(e), title="Create Website API Error")
        return {
            "status": "error",
            "message": _("Error processing request: {0}").format(str(e))
        }



@frappe.whitelist(allow_guest=False)
def get_vendor_websites():
    try:
        current_user = frappe.session.user

        # Get vendor ID associated with the logged-in user
        result = get_vendor_id()
        vendor_id = result.get("vendor_id")

        if not vendor_id:
            return {
                "status": "error",
                "message": "Vendor ID not found for the current user"
            }

        # Fetch all websites belonging to the vendor
        websites = frappe.get_all(
            "Ecommerce Vendor Website",
            filters={
                "vendor_id": vendor_id,
                "status": ["in", ["Draft", "Published"]]
            },
            fields=["name", "website_link", "canonical_url", "custom_domain", "type", "description", "favicon", "status", "creation", "modified",
                    "template", "primary_color", "font", "secondary_color", "additional_color1", "additional_color2"]
        )

        # Append related pages for each website
        for website in websites:
            pages = frappe.get_all(
                "Ecommerce Page",
                filters={"website_id": website["name"]},
                fields=["name", "page", "page_status", "creation", "modified", "parent1","field_value","template","website_id","website_name"],
            )
            website["pages"] = pages
            website["custom_domain_target"] = storefront_custom_domain_target()
            website["custom_domain_dns"] = storefront_custom_domain_setup(
                website.get("custom_domain")
            )

        # Discarding an old design must not hide its catalogue from the import
        # selector. These websites stay out of the normal website table, but
        # remain available as catalogue sources for the same vendor.
        catalogue_sources = frappe.get_all(
            "Ecommerce Vendor Website",
            filters={"vendor_id": vendor_id, "type": "Ecommerce"},
            fields=["name", "website_link", "status", "modified"],
            order_by="modified desc",
        )
        for source in catalogue_sources:
            source["product_count"] = frappe.db.count(
                "Ecommerce Product", {"website": source.name}
            )

        return {
            "status": "success",
            "message": "Websites and pages fetched successfully",
            "data": websites,
            "catalogue_sources": catalogue_sources,
            "custom_domain_target": storefront_custom_domain_target(),
            "storefront_base_domain": storefront_base_domain(),
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Get Vendor Websites API Error")
        return {
            "status": "error",
            "message": f"Error fetching websites: {str(e)}"
        }


@frappe.whitelist(allow_guest=False)
def get_pages():
    try:
        # Templates are shared setup data. Requiring a vendor record here
        # prevents users from choosing a template before creating a website.
        templates = frappe.get_all(
            "Ecommerce Template",
            fields=["name", "page_name", "template", "creation", "data_json"],
            order_by="creation desc",
        )

        for template in templates:
            try:
                config = json.loads(template.get("data_json") or "{}")
            except (TypeError, ValueError):
                config = {}

            starter_content = config.get("starter_content") or {}
            block_names = []
            for area in ("header", "main", "footer"):
                for block in starter_content.get(area) or []:
                    block_name = block.get("block_name") or block.get("name")
                    if block_name and block_name not in block_names:
                        block_names.append(block_name)

            preview_by_name = {}
            if block_names:
                preview_by_name = {
                    row.name: row.block_image
                    for row in frappe.get_all(
                        "Ecommerce Block",
                        filters={"name": ["in", block_names]},
                        fields=["name", "block_image"],
                    )
                    if row.block_image
                }

            template["block_count"] = sum(
                len(starter_content.get(area) or [])
                for area in ("header", "main", "footer")
            )
            preview_images = []
            preview_details = {}
            # Lead with the page itself. Header screenshots tend to be short,
            # repetitive, and older records may point at private uploads that
            # an <img> in the chooser cannot display.
            for area in ("main", "footer", "header"):
                for starter_block in starter_content.get(area) or []:
                    block_name = starter_block.get("block_name") or starter_block.get("name")
                    model = (starter_block.get("block_details") or {}).get("model") or {}
                    model_values = {
                        field.get("name") or field.get("key"): field.get("value")
                        for field in model.get("fields") or []
                        if field.get("name") or field.get("key")
                    }

                    # Prefer the configured starter artwork to the reusable
                    # block screenshot. Template-specific aliases intentionally
                    # share their block implementation and block_image, so
                    # choosing block_image first made every template card look
                    # identical.
                    preview_image = next(
                        (
                            field.get("value")
                            for field in model.get("fields") or []
                            if field.get("type") == "file" and field.get("value")
                        ),
                        None,
                    )
                    if not preview_image:
                        preview_image = preview_by_name.get(block_name)
                    if str(preview_image or "").startswith("/private/"):
                        preview_image = None

                    if area == "main" and not preview_details and preview_image:
                        preview_details = {
                            "image": preview_image,
                            "layout": model_values.get("layout") or "image",
                            "heading": model_values.get("heading")
                            or config.get("default_page_title")
                            or template.get("page_name"),
                            "eyebrow": model_values.get("eyebrow")
                            or config.get("template_category")
                            or "Storefront",
                        }

                    if preview_image and preview_image not in preview_images:
                        preview_images.append(preview_image)

            template["preview_images"] = preview_images[:4]
            template["preview_image"] = preview_details.get("image")
            template["preview_layout"] = preview_details.get("layout", "image")
            template["preview_heading"] = preview_details.get("heading")
            template["preview_eyebrow"] = preview_details.get("eyebrow")
            template["description"] = config.get("template_description") or (
                "Start without preselected sections and build the page your way."
                if not template["block_count"]
                else "A ready-made layout with editable content and sections."
            )

        return {
            "status": "success",
            "message": "Page templates fetched successfully",
            "data": templates,
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Get Vendor pages API Error")
        return {
            "status": "error",
            "message": f"Error fetching page templates: {str(e)}",
            "data": [],
        }


def _builder_json_object(value):
    if isinstance(value, dict):
        return copy.deepcopy(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError):
            return {}
    return {}


def _builder_root_page(page):
    current = page
    visited = {str(current.get("name") or "")}
    while current.get("parent1"):
        parent_name = current.get("parent1")
        if str(parent_name) in visited:
            break
        visited.add(str(parent_name))
        parent = frappe.db.get_value(
            "Ecommerce Page",
            {
                "name": parent_name,
                "website_id": current.get("website_id"),
            },
            ["name", "parent1", "website_id", "template", "field_value"],
            as_dict=True,
        )
        if not parent:
            break
        current = parent
    return current


def _builder_template_starter_content(template_name):
    if not template_name:
        return {}
    raw_config = frappe.db.get_value(
        "Ecommerce Template", template_name, "data_json"
    )
    config = _builder_json_object(raw_config)
    starter_content = config.get("starter_content")
    return starter_content if isinstance(starter_content, dict) else {}


def _builder_layout_section(layout_values, layout_defaults, section):
    """Return a saved layout section, preserving an explicit empty list.

    A missing or malformed section may use the template starter content. An
    empty list is intentional: it means the user removed every block from that
    section and must not cause the template header/footer to reappear.
    """
    blocks = layout_values.get(section)
    if not isinstance(blocks, list):
        blocks = layout_defaults.get(section) or []
    return copy.deepcopy(blocks)


def _builder_effective_field_value(page, submitted_value=None):
    """Apply the shared root-page header/footer to a builder page.

    Child pages keep their own main content. Missing main content is initialized
    from the page's selected template. Root pages use their saved layout,
    falling back to their selected template when a header or footer is absent.
    """
    if isinstance(page, (str, int)):
        page = frappe.db.get_value(
            "Ecommerce Page",
            page,
            [
                "name",
                "parent1",
                "template",
                "field_value",
                "website_id",
            ],
            as_dict=True,
        )
    if not page:
        return _builder_json_object(submitted_value)

    values = _builder_json_object(
        submitted_value if submitted_value is not None else page.get("field_value")
    )
    root_page = _builder_root_page(page)
    inherits_layout = str(root_page.get("name")) != str(page.get("name"))
    layout_values = (
        _builder_json_object(root_page.get("field_value"))
        if inherits_layout
        else values
    )
    layout_defaults = _builder_template_starter_content(root_page.get("template"))

    # A newly-created standalone page has no submitted main key. Initialize it
    # from its selected template so Store Design matches Preview. Preserve an
    # explicit empty list because that means the user removed every section.
    if "main" not in values:
        page_defaults = _builder_template_starter_content(page.get("template"))
        values["main"] = copy.deepcopy(page_defaults.get("main") or [])

    for section in ("header", "footer"):
        values[section] = _builder_layout_section(
            layout_values, layout_defaults, section
        )

    return values


def _publish_initial_builder_page(page):
    """Compile template starter content when a builder page is first created."""
    if not page or not page.get("template"):
        return None

    result = update_publish_data(
        _page_name=page.name,
        _title=page.page,
        _field_value=page.field_value,
        _commit=False,
    )
    if not isinstance(result, dict) or result.get("status") != "success":
        frappe.throw(
            (result or {}).get("message")
            or _("Unable to render the selected page template.")
        )
    return result


@frappe.whitelist(allow_guest=False)
def post_page_data():
    try:
        data = frappe.local.form_dict

        title = data.get("title")
        website_name = data.get("website_name")
        route_page_name = data.get("route_page_name")
        main_page_name = data.get("main_page_name")
        field_value = data.get("field_value") or {}

        if not website_name:
            frappe.throw("Please select a website before creating a page.")

        if main_page_name:
            parent_page = frappe.db.get_value(
                "Ecommerce Page",
                main_page_name,
                ["name", "website_id", "page_status"],
                as_dict=True,
            )
            if not parent_page:
                frappe.throw("The selected parent page no longer exists.")
            if str(parent_page.website_id) != str(website_name):
                frappe.throw("The selected parent page belongs to another website.")
            if parent_page.page_status == "Archived":
                frappe.throw("An archived page cannot be used as a parent.")

        # Create new Ecommerce Page document
        new_doc = frappe.get_doc({
            "doctype": "Ecommerce Page",
            "page": title,
            "website_id": website_name,
            "parent1": main_page_name,
            "template": route_page_name,
            "page_status": "Active",
            "field_value": field_value
        })
        new_doc.field_value = _builder_effective_field_value(new_doc, field_value)
        if "main" not in _builder_json_object(field_value):
            new_doc.field_value = _builder_catalogue_template_defaults(
                new_doc.field_value,
                website_name,
            )

        # Insert the document (ignore_permissions if user doesn't have perm)
        new_doc.insert(ignore_permissions=True)
        _publish_initial_builder_page(new_doc)

        frappe.db.commit()  # ensure changes are saved

        return {
            "status": "success",
            "message": "New page created successfully",
            "data": {
                "name": new_doc.name,

            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error in post_page_data: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


def _builder_page_request_data():
    if frappe.request and frappe.request.data:
        try:
            return json.loads(frappe.request.data or "{}")
        except (TypeError, ValueError):
            pass
    return frappe.local.form_dict or {}


def _vendor_owned_builder_page(page_name):
    if not page_name or not frappe.db.exists("Ecommerce Page", page_name):
        return None, {"status": "error", "message": _("Page not found.")}

    page = frappe.get_doc("Ecommerce Page", page_name)
    vendor_info = get_vendor_id() or {}
    website_vendor = frappe.db.get_value(
        "Ecommerce Vendor Website", page.website_id, "vendor_id"
    )
    if not website_vendor or str(website_vendor) != str(vendor_info.get("vendor_id")):
        frappe.local.response.http_status_code = 403
        return None, {
            "status": "error",
            "message": _("You cannot manage this page."),
        }
    return page, None


def _builder_page_tree_names(page):
    rows = frappe.get_all(
        "Ecommerce Page",
        filters={"website_id": page.website_id},
        fields=["name", "parent1"],
    )
    children_by_parent = {}
    for row in rows:
        children_by_parent.setdefault(str(row.parent1 or ""), []).append(row.name)

    names = []
    visited = set()

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        names.append(name)
        for child_name in children_by_parent.get(str(name), []):
            visit(child_name)

    visit(page.name)
    return names


def _builder_page_ancestor_names(page):
    ancestors = []
    parent_name = page.parent1
    visited = {str(page.name)}
    while parent_name and str(parent_name) not in visited:
        visited.add(str(parent_name))
        parent = frappe.db.get_value(
            "Ecommerce Page",
            {"name": parent_name, "website_id": page.website_id},
            ["name", "parent1"],
            as_dict=True,
        )
        if not parent:
            break
        ancestors.insert(0, parent.name)
        parent_name = parent.parent1
    return ancestors


@frappe.whitelist(allow_guest=False)
def set_builder_page_archived():
    try:
        data = _builder_page_request_data()
        page, error = _vendor_owned_builder_page(data.get("page_name"))
        if error:
            return error

        archived = str(data.get("archived", "1")).lower() in {
            "1", "true", "yes", "on"
        }
        page_names = _builder_page_tree_names(page)
        status = "Archived" if archived else "Active"
        if not archived:
            page_names = list(
                dict.fromkeys(_builder_page_ancestor_names(page) + page_names)
            )
        for page_name in page_names:
            frappe.db.set_value(
                "Ecommerce Page",
                page_name,
                "page_status",
                status,
                update_modified=True,
            )
        frappe.db.commit()
        return {
            "status": "success",
            "message": (
                _("Page archived successfully.")
                if archived
                else _("Page restored successfully.")
            ),
            "data": {"page_names": page_names, "page_status": status},
        }
    except Exception as exc:
        frappe.log_error(
            title="Builder Page Archive Error", message=frappe.get_traceback()
        )
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def delete_builder_page():
    try:
        data = _builder_page_request_data()
        page, error = _vendor_owned_builder_page(data.get("page_name"))
        if error:
            return error

        page_names = _builder_page_tree_names(page)
        # Children must be removed before their parent Link field target.
        for page_name in reversed(page_names):
            frappe.delete_doc(
                "Ecommerce Page",
                page_name,
                ignore_permissions=True,
            )
        frappe.db.commit()
        return {
            "status": "success",
            "message": _("Page deleted permanently."),
            "data": {"page_names": page_names},
        }
    except Exception as exc:
        frappe.log_error(
            title="Builder Page Delete Error", message=frappe.get_traceback()
        )
        return {"status": "error", "message": str(exc)}


def _apply_builder_page_template(page, template):
    """Apply a template and synchronize a root page's shared child layout."""
    config = _builder_json_object(template.data_json)
    starter_content = copy.deepcopy(config.get("starter_content") or {})
    starter_content = _builder_catalogue_template_defaults(
        starter_content,
        page.get("website_id"),
    )
    previous = _builder_json_object(page.field_value)
    inherits_layout = bool(page.get("parent1"))
    replacement = copy.deepcopy(previous)
    replacement["main"] = copy.deepcopy(starter_content.get("main") or [])

    if inherits_layout:
        # Child pages own only their main section.
        current_content = _builder_effective_field_value(page, previous)
        replacement["header"] = copy.deepcopy(current_content.get("header") or [])
        replacement["footer"] = copy.deepcopy(current_content.get("footer") or [])
    else:
        # A root/parent page owns the shared website layout.
        replacement["header"] = copy.deepcopy(starter_content.get("header") or [])
        replacement["footer"] = copy.deepcopy(starter_content.get("footer") or [])

    # Preserve supported page metadata such as SEO values.
    for key in set(previous).intersection(starter_content):
        if key not in {"header", "main", "footer", "Page"}:
            replacement[key] = copy.deepcopy(previous[key])

    previous_template = page.template
    page.template = template.name
    page.field_value = _builder_effective_field_value(page, replacement)
    page.save(ignore_permissions=True)

    synced_children = []
    if not inherits_layout:
        # Persist the shared layout on descendants too. Effective layout
        # resolution already reads from the root, but synchronizing these
        # snapshots also keeps older APIs and saved previews consistent.
        root_value = _builder_json_object(page.field_value)
        for child_name in _builder_page_tree_names(page)[1:]:
            child = frappe.get_doc("Ecommerce Page", child_name)
            child_value = _builder_json_object(child.field_value)
            child_value["header"] = copy.deepcopy(root_value.get("header") or [])
            child_value["footer"] = copy.deepcopy(root_value.get("footer") or [])
            child.field_value = _builder_effective_field_value(child, child_value)
            child.save(ignore_permissions=True)
            synced_children.append(child.name)

    return {
        "page_name": page.name,
        "template": template.name,
        "template_label": template.page_name,
        "previous_template": previous_template,
        "inherits_layout": inherits_layout,
        "synced_children": synced_children,
        "field_value": page.field_value,
    }


@frappe.whitelist(allow_guest=False)
def change_builder_page_template():
    """Replace a root design or a child body without affecting sibling bodies."""
    try:
        data = _builder_page_request_data()
        page, error = _vendor_owned_builder_page(data.get("page_name"))
        if error:
            return error
        if page.page_status == "Archived":
            return {
                "status": "error",
                "message": _("Restore this page before changing its template."),
            }

        template = frappe.db.get_value(
            "Ecommerce Template",
            data.get("template_name"),
            ["name", "page_name", "data_json"],
            as_dict=True,
        )
        if not template:
            return {"status": "error", "message": _("Template not found.")}

        result = _apply_builder_page_template(page, template)
        frappe.db.commit()

        return {
            "status": "success",
            "message": _("Selected page template changed successfully."),
            "data": result,
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(
            title="Builder Page Template Change Error",
            message=frappe.get_traceback(),
        )
        return {"status": "error", "message": str(exc)}



# @frappe.whitelist(allow_guest=False)
# def get_pagetemplatedata():
#     import json, copy

#     try:
#         page_id = frappe.local.form_dict.get("page_id")
#         vendor_id = get_vendor_id().get("vendor_id")
#         if not vendor_id:
#             return {"status": "error", "message": "Vendor ID not found for the current user"}

#         # -----------------------------
#         # Helper: sanitize model
#         # --------------------------- --
#         def sanitize_model(model):
#             if not isinstance(model, dict):
#                 return {}
#             return {k: v for k, v in model.items() if k in {"block_name", "description", "fields"}}

#         # -----------------------------
#         # Helper: fetch a block by name/type
#         # -----------------------------
#         def get_block_details(block_name=None, block_type=None):
#             filters = {}
#             if block_name:
#                 filters["block_name"] = block_name
#             if block_type:
#                 filters["type"] = block_type

#             block = frappe.get_value(
#                 "Ecommerce Block",
#                 filters,
#                 ["name", "block_name", "block_image", "model", "type"],
#                 as_dict=True
#             )
#             if block:
#                 try:
#                     block["model"] = json.loads(block.get("model") or "{}")
#                 except Exception:
#                     block["model"] = {}
#                 block["model"] = sanitize_model(block["model"])
#             return block

#         # -----------------------------
#         # Recursive assign function
#         # -----------------------------
#         def assign_values(fields, field_value):
#             if not fields:
#                 return

#             for field in fields:
#                 key = field.get("key") or field.get("name")
#                 if key and key in field_value and key != "Page":  # ⛔ prevent Page duplication
#                     field["value"] = field_value[key]

#                 # 🔹 Handle draggable fields
#                 if field.get("type") == "draggable" and isinstance(field.get("value"), list):
#                     for block_instance in field["value"]:
#                         # If this block instance has a block_name but no block_details, fetch it
#                         if "block_name" in block_instance and "block_details" not in block_instance:
#                             block_template = get_block_details(block_name=block_instance["block_name"])
#                             if block_template:
#                                 block_instance["block_details"] = block_template

#                         # Now deep copy fields inside this block
#                         if block_instance.get("block_details") and block_instance["block_details"].get("model"):
#                             nested_fields = copy.deepcopy(block_instance["block_details"]["model"].get("fields", []))

#                             # Assign values from block_instance
#                             for nf in nested_fields:
#                                 nf_key = nf.get("key") or nf.get("name")
#                                 if nf_key and nf_key in block_instance and nf_key != "Page":
#                                     nf["value"] = block_instance[nf_key]

#                             block_instance["block_details"]["model"]["fields"] = nested_fields
#                             block_instance["block_details"]["model"] = sanitize_model(
#                                 block_instance["block_details"]["model"]
#                             )  # ✅ sanitize again

#                             # Recurse into nested draggables
#                             assign_values(nested_fields, block_instance)

#                 # 🔹 Recurse into sections
#                 if "sections" in field:
#                     for section in field.get("sections") or []:
#                         assign_values(section.get("fields"), field_value)

#                 # 🔹 Recurse into tabs
#                 if "tabs" in field:
#                     for tab in field.get("tabs") or []:
#                         for section in tab.get("sections") or []:
#                             assign_values(section.get("fields"), field_value)



#         # -----------------------------
#         # Fetch page with template and populate field values
#         # -----------------------------
#         def fetch_page_with_template(page_doc):
#             template = {}
#             if page_doc.get("template"):
#                 template = frappe.get_value(
#                     "Ecommerce Template",
#                     page_doc.get("template"),
#                     ["name", "data_json", "creation"],
#                     as_dict=True
#                 ) or {}

#             data_json = json.loads(template.get("data_json") or "{}")
#             field_value = json.loads(page_doc.get("field_value") or "{}")

#             # Assign top-level fields
#             assign_values(data_json.get("fields"), field_value)

#             # Assign fields for tabs → sections → fields
#             for tab in data_json.get("tabs") or []:
#                 for section in tab.get("sections") or []:
#                     assign_values(section.get("fields"), field_value)

#             return {
#                 "render_data": data_json,
#                 "page": page_doc.get("page"),
#                 "parent1": page_doc.get("parent1"),
#                 "template": page_doc.get("template"),
#                 "creation": page_doc.get("creation"),
#                 "name": page_doc.get("name"),
#             }

#         # -----------------------------
#         # Fetch single page
#         # -----------------------------
#         if page_id:
#             page = frappe.get_value(
#                 "Ecommerce Page",
#                 page_id,
#                 ["name", "page", "creation", "modified", "parent1", "field_value", "template"],
#                 as_dict=True
#             )
#             if not page:
#                 return {"status": "error", "message": f"No page found with ID {page_id}"}

#             return {
#                 "status": "success",
#                 "message": "Page fetched successfully",
#                 "data": fetch_page_with_template(page)
#             }

#         # -----------------------------
#         # Fetch all pages
#         # -----------------------------
#         pages = frappe.get_all(
#             "Ecommerce Page",
#             fields=["name", "page", "creation", "parent1", "field_value", "template"]
#         )
#         all_data = [fetch_page_with_template(p) for p in pages]

#         return {
#             "status": "success",
#             "message": "All pages fetched successfully",
#             "data": all_data
#         }

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Get Page Template Data Error")
#         return {"status": "error", "message": f"Error fetching page data: {str(e)}"}


# @frappe.whitelist(allow_guest=False)
# def get_pagetemplatedata():
#     import json, copy

#     try:
#         page_id = frappe.local.form_dict.get("page_id")
#         vendor_id = get_vendor_id().get("vendor_id")
#         if not vendor_id:
#             return {"status": "error", "message": "Vendor ID not found for the current user"}

#         # -----------------------------
#         # Helper: sanitize model
#         # -----------------------------
#         def sanitize_model(model):
#             if not isinstance(model, dict):
#                 return {}
#             return {k: v for k, v in model.items() if k in {"block_name", "description", "fields"}}

#         # -----------------------------
#         # Helper: fetch a block by name/type
#         # -----------------------------
#         def get_block_details(block_name=None, block_type=None):
#             filters = {}
#             if block_name:
#                 filters["block_name"] = block_name
#             if block_type:
#                 filters["type"] = block_type

#             block = frappe.get_value(
#                 "Ecommerce Block",
#                 filters,
#                 ["name", "block_name", "block_image", "model", "type"],
#                 as_dict=True
#             )
#             if block:
#                 try:
#                     block["model"] = json.loads(block.get("model") or "{}")
#                 except Exception:
#                     block["model"] = {}
#                 block["model"] = sanitize_model(block["model"])
#             return block

#         # -----------------------------
#         # Recursive assign function
#         # -----------------------------
#         def assign_values(fields, field_value):
#             if not fields:
#                 return

#             for field in fields:
#                 key = field.get("key") or field.get("name")
#                 if key and key in field_value and key != "Page":  # prevent Page duplication
#                     field["value"] = field_value[key]

#                 # 🔹 Handle draggable fields
#                 if field.get("type") == "draggable" and isinstance(field.get("value"), list):
#                     for block_instance in field["value"]:
#                         # Fetch template if missing
#                         if "block_name" in block_instance and "block_details" not in block_instance:
#                             block_template = get_block_details(block_name=block_instance["block_name"])
#                             if block_template:
#                                 block_instance["block_details"] = block_template

#                         # Merge template fields with saved values
#                         if block_instance.get("block_details"):
#                             # Always fetch the latest template fields from DB
#                             fresh_template = get_block_details(block_name=block_instance["block_name"])
#                             template_fields = copy.deepcopy(
#                                 fresh_template.get("model", {}).get("fields", [])
#                             )


#                             # Collect saved values (from previous model.fields)
#                             saved_values = {}
#                             old_fields = block_instance.get("block_details", {}).get("model", {}).get("fields", [])
#                             for ef in old_fields:
#                                 ef_key = ef.get("key") or ef.get("name")
#                                 if ef_key and "value" in ef:
#                                     saved_values[ef_key] = ef["value"]

#                             merged_fields = []
#                             for tf in template_fields:
#                                 tf_key = tf.get("key") or tf.get("name")
#                                 if tf_key in saved_values:
#                                     tf["value"] = saved_values[tf_key]
#                                 elif tf_key in block_instance and tf_key != "Page":  # legacy support
#                                     tf["value"] = block_instance[tf_key]
#                                 else:
#                                     tf.setdefault("value", "")
#                                 merged_fields.append(tf)

#                             # ✅ Always overwrite with merged template
#                             block_instance["block_details"]["model"]["fields"] = merged_fields
#                             block_instance["block_details"]["model"] = sanitize_model(
#                                 block_instance["block_details"]["model"]
#                             )

#                             # Recurse into nested draggables
#                             assign_values(merged_fields, block_instance)

#                 # 🔹 Recurse into sections
#                 if "sections" in field:
#                     for section in field.get("sections") or []:
#                         assign_values(section.get("fields"), field_value)

#                 # 🔹 Recurse into tabs
#                 if "tabs" in field:
#                     for tab in field.get("tabs") or []:
#                         for section in tab.get("sections") or []:
#                             assign_values(section.get("fields"), field_value)



#         # -----------------------------
#         # Fetch page with template and populate field values
#         # -----------------------------
#         def fetch_page_with_template(page_doc):
#             template = {}
#             if page_doc.get("template"):
#                 template = frappe.get_value(
#                     "Ecommerce Template",
#                     page_doc.get("template"),
#                     ["name", "data_json", "creation"],
#                     as_dict=True
#                 ) or {}

#             data_json = json.loads(template.get("data_json") or "{}")
#             field_value = json.loads(page_doc.get("field_value") or "{}")

#             # Assign top-level fields
#             assign_values(data_json.get("fields"), field_value)

#             # Assign fields for tabs → sections → fields
#             for tab in data_json.get("tabs") or []:
#                 for section in tab.get("sections") or []:
#                     assign_values(section.get("fields"), field_value)

#             return {
#                 "render_data": data_json,
#                 "page": page_doc.get("page"),
#                 "parent1": page_doc.get("parent1"),
#                 "template": page_doc.get("template"),
#                 "creation": page_doc.get("creation"),
#                 "name": page_doc.get("name"),
#             }

#         # -----------------------------
#         # Fetch single page
#         # -----------------------------
#         if page_id:
#             page = frappe.get_value(
#                 "Ecommerce Page",
#                 page_id,
#                 ["name", "page", "creation", "modified", "parent1", "field_value", "template"],
#                 as_dict=True
#             )
#             if not page:
#                 return {"status": "error", "message": f"No page found with ID {page_id}"}

#             return {
#                 "status": "success",
#                 "message": "Page fetched successfully",
#                 "data": fetch_page_with_template(page)
#             }

#         # -----------------------------
#         # Fetch all pages
#         # -----------------------------
#         pages = frappe.get_all(
#             "Ecommerce Page",
#             fields=["name", "page", "creation", "parent1", "field_value", "template"]
#         )
#         all_data = [fetch_page_with_template(p) for p in pages]

#         return {
#             "status": "success",
#             "message": "All pages fetched successfully",
#             "data": all_data
#         }

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Get Page Template Data Error")
#         return {"status": "error", "message": f"Error fetching page data: {str(e)}"}



# @frappe.whitelist(allow_guest=False)
# def get_pagetemplatedata():
#     import json, copy

#     try:
#         page_id = frappe.local.form_dict.get("page_id")
#         vendor_id = get_vendor_id().get("vendor_id")
#         if not vendor_id:
#             return {"status": "error", "message": "Vendor ID not found for the current user"}

#         # -----------------------------
#         # Helper: sanitize model
#         # -----------------------------
#         def sanitize_model(model):
#             if not isinstance(model, dict):
#                 return {}
#             return {k: v for k, v in model.items() if k in {"block_name", "description", "fields", "tabs"}}


#         # -----------------------------
#         # Helper: fetch a block by name/type
#         # -----------------------------
#         def get_block_details(block_name=None, block_type=None):
#             filters = {}
#             if block_name:
#                 filters["block_name"] = block_name
#             if block_type:
#                 filters["type"] = block_type

#             block = frappe.get_value(
#                 "Ecommerce Block",
#                 filters,
#                 ["name", "block_name", "block_image", "model", "type"],
#                 as_dict=True
#             )
#             if block:
#                 try:
#                     model_data = json.loads(block.get("model") or "{}")
#                 except Exception:
#                     model_data = {}

#                 # Always sanitize but now includes tabs
#                 block["model"] = sanitize_model(model_data)
#             return block



#         # -----------------------------
#         # Recursive assign function
#         # -----------------------------
#         def assign_values(fields, field_value):
#             if not fields:
#                 return

#             for field in fields:
#                 key = field.get("key") or field.get("name")

#                 # Assign simple field value
#                 if key and key in field_value and key != "Page":
#                     field["value"] = field_value[key]

#                 # 🔹 Handle draggable (blocks)
#                 if field.get("type") == "draggable" and isinstance(field.get("value"), list):
#                     for block_instance in field["value"]:
#                         # Try to detect block_name at multiple levels
#                         block_name = (
#                             block_instance.get("block_name")
#                             or block_instance.get("name")
#                             or block_instance.get("block_details", {}).get("model", {}).get("block_name")
#                         )

#                         if not block_name:
#                             continue  # skip if still missing

#                         # Ensure block_details exists
#                         if "block_details" not in block_instance or not block_instance["block_details"].get("model", {}).get("fields"):
#                             block_template = get_block_details(block_name=block_name)
#                             if block_template:
#                                 block_instance["block_details"] = block_template



#                         # Proceed if block_details exists
#                         if block_instance.get("block_details"):
#                             fresh_template = get_block_details(block_name=block_instance["block_name"])
#                             model = fresh_template.get("model", {})

#                             # Deep copy fields and tabs from template
#                             template_fields = copy.deepcopy(model.get("fields", []))
#                             template_tabs = copy.deepcopy(model.get("tabs", []))

#                             # Collect saved values (from previous block_details.model.fields)
#                             saved_values = {}
#                             old_fields = block_instance.get("block_details", {}).get("model", {}).get("fields", [])
#                             for ef in old_fields:
#                                 ef_key = ef.get("key") or ef.get("name")
#                                 if ef_key and "value" in ef:
#                                     saved_values[ef_key] = ef["value"]

#                             # Merge template fields with saved values
#                             merged_fields = []
#                             for tf in template_fields:
#                                 tf_key = tf.get("key") or tf.get("name")
#                                 if tf_key in saved_values:
#                                     tf["value"] = saved_values[tf_key]
#                                 elif tf_key in block_instance and tf_key != "Page":  # legacy support
#                                     tf["value"] = block_instance[tf_key]
#                                 else:
#                                     tf.setdefault("value", "")
#                                 merged_fields.append(tf)

#                             # ✅ Assign merged fields back
#                             block_instance["block_details"]["model"]["fields"] = merged_fields

#                             # ✅ Handle nested tabs inside block templates
#                             if template_tabs:
#                                 for tab in template_tabs:
#                                     for section in tab.get("sections") or []:
#                                         assign_values(section.get("fields"), block_instance)

#                                 block_instance["block_details"]["model"]["tabs"] = template_tabs

#                             # ✅ Re-sanitize and recurse further
#                             block_instance["block_details"]["model"] = sanitize_model(
#                                 block_instance["block_details"]["model"]
#                             )

#                             assign_values(merged_fields, block_instance)

#                 # 🔹 Recurse into nested sections
#                 if "sections" in field:
#                     for section in field.get("sections") or []:
#                         assign_values(section.get("fields"), field_value)

#                 # 🔹 Recurse into tabs (global or within model)
#                 tabs = field.get("tabs") or field.get("model", {}).get("tabs")
#                 if tabs:
#                     for tab in tabs:
#                         for section in tab.get("sections") or []:
#                             assign_values(section.get("fields"), field_value)




#         # -----------------------------
#         # Fetch page with template and populate field values
#         # -----------------------------
#         def fetch_page_with_template(page_doc):
#             template = {}
#             if page_doc.get("template"):
#                 template = frappe.get_value(
#                     "Ecommerce Template",
#                     page_doc.get("template"),
#                     ["name", "data_json", "creation"],
#                     as_dict=True
#                 ) or {}

#             data_json = json.loads(template.get("data_json") or "{}")
#             field_value = json.loads(page_doc.get("field_value") or "{}")

#             # Assign top-level fields
#             assign_values(data_json.get("fields"), field_value)

#             # --- Merge Tabs from Template and Page ---
#             template_tabs = data_json.get("tabs") or []
#             saved_tabs = field_value.get("tabs") or []

#             # Convert saved tabs into a dict by label/name
#             saved_tabs_dict = {t.get("label") or t.get("name"): t for t in saved_tabs if t.get("label") or t.get("name")}

#             merged_tabs = []
#             for tab in template_tabs:
#                 tab_label = tab.get("label") or tab.get("name")
#                 saved_tab = saved_tabs_dict.get(tab_label)

#                 if saved_tab:
#                     # Merge tab sections
#                     for section in tab.get("sections") or []:
#                         assign_values(section.get("fields"), saved_tab)

#                 merged_tabs.append(tab)

#             # Add any extra tabs that exist only in saved data (not in template)
#             for label, saved_tab in saved_tabs_dict.items():
#                 if not any(t.get("label") == label for t in merged_tabs):
#                     merged_tabs.append(saved_tab)

#             # Assign back merged tabs
#             data_json["tabs"] = merged_tabs

#             # Run assignment inside tabs → sections → fields
#             for tab in data_json.get("tabs") or []:
#                 for section in tab.get("sections") or []:
#                     assign_values(section.get("fields"), field_value)

#             return {
#                 "render_data": data_json,
#                 "page": page_doc.get("page"),
#                 "parent1": page_doc.get("parent1"),
#                 "template": page_doc.get("template"),
#                 "creation": page_doc.get("creation"),
#                 "name": page_doc.get("name"),
#             }

#         # -----------------------------
#         # Fetch single page
#         # -----------------------------
#         if page_id:
#             page = frappe.get_value(
#                 "Ecommerce Page",
#                 page_id,
#                 ["name", "page", "creation", "modified", "parent1", "field_value", "template"],
#                 as_dict=True
#             )
#             if not page:
#                 return {"status": "error", "message": f"No page found with ID {page_id}"}

#             return {
#                 "status": "success",
#                 "message": "Page fetched successfully",
#                 "data": fetch_page_with_template(page)
#             }

#         # -----------------------------
#         # Fetch all pages
#         # -----------------------------
#         pages = frappe.get_all(
#             "Ecommerce Page",
#             fields=["name", "page", "creation", "parent1", "field_value", "template"]
#         )
#         all_data = [fetch_page_with_template(p) for p in pages]

#         return {
#             "status": "success",
#             "message": "All pages fetched successfully",
#             "data": all_data
#         }

#     except Exception as e:
#         frappe.log_error(message=str(e), title="Get Page Template Data Error")
#         return {"status": "error", "message": f"Error fetching page data: {str(e)}"}




@frappe.whitelist(allow_guest=False)
def get_pagetemplatedata():
    import json, copy

    try:
        form = frappe.local.form_dict or {}
        page_id = form.get("page_id")
        vendor_info = get_vendor_id() or {}
        vendor_id = vendor_info.get("vendor_id")
        if not vendor_id:
            return {
                "status": "error",
                "message": vendor_info.get("message") or "Vendor ID not found for the current user",
            }

        # -----------------------------
        # Helper: sanitize model
        # -----------------------------
        def sanitize_model(model):
            if not isinstance(model, dict):
                return {}
            return {k: v for k, v in model.items() if k in {"block_name", "description", "fields", "tabs"}}


        # -----------------------------
        # Helper: fetch a block by name/type
        # -----------------------------
        def get_block_details(block_name=None, block_type=None):
            filters = {}
            if block_name:
                filters["block_name"] = block_name
            if block_type:
                filters["type"] = block_type

            block = frappe.get_value(
                "Ecommerce Block",
                filters,
                ["name", "block_name", "block_image", "model", "type"],
                as_dict=True
            )
            if block:
                try:
                    model_data = json.loads(block.get("model") or "{}")
                except Exception:
                    model_data = {}

                # Always sanitize but now includes tabs
                block["model"] = sanitize_model(model_data)
            return block



        # -----------------------------
        # Recursive assign function
        # -----------------------------
        def assign_values(fields, field_value):
            if not isinstance(fields, list):
                return

            for field in fields:
                key = field.get("key") or field.get("name")

                # Assign simple field value
                if key and key in field_value and key != "Page":
                    field["value"] = field_value[key]

                # 🔹 Handle draggable (blocks)
                if field.get("type") == "draggable" and isinstance(field.get("value"), list):
                    for block_instance in field["value"]:
                        # Try to detect block_name at multiple levels
                        block_name = (
                            block_instance.get("block_name")
                            or block_instance.get("name")
                            or block_instance.get("block_details", {}).get("model", {}).get("block_name")
                        )

                        if not block_name:
                            continue  # skip if still missing

                        # Ensure block_details exists
                        if "block_details" not in block_instance or not block_instance["block_details"].get("model", {}).get("fields"):
                            block_template = get_block_details(block_name=block_name)
                            if block_template:
                                block_instance["block_details"] = block_template



                        # Proceed if block_details exists
                        if block_instance.get("block_details"):
                            block_name_for_template = (
                                block_instance.get("block_name")
                                or block_instance.get("name")
                                or block_instance.get("block_details", {}).get("model", {}).get("block_name")
                            )
                            fresh_template = get_block_details(block_name=block_name_for_template)
                            if not fresh_template:
                                continue
                            model = fresh_template.get("model", {})

                            # Deep copy fields and tabs from template
                            template_fields = copy.deepcopy(model.get("fields", []))
                            template_tabs = copy.deepcopy(model.get("tabs", []))

                            old_fields = block_instance.get("block_details", {}).get("model", {}).get("fields", [])
                            merged_fields = _merge_builder_template_fields(
                                template_fields,
                                old_fields,
                                block_instance,
                            )

                            # ✅ Assign merged fields back
                            block_instance["block_details"]["model"]["fields"] = merged_fields

                            # ✅ Handle nested tabs inside block templates
                            if template_tabs:
                                for tab in template_tabs:
                                    for section in tab.get("sections") or []:
                                        assign_values(section.get("fields"), block_instance)

                                block_instance["block_details"]["model"]["tabs"] = template_tabs

                            # ✅ Re-sanitize and recurse further
                            block_instance["block_details"]["model"] = sanitize_model(
                                block_instance["block_details"]["model"]
                            )

                            assign_values(merged_fields, block_instance)

                # 🔹 Recurse into nested sections
                if "sections" in field:
                    for section in field.get("sections") or []:
                        assign_values(section.get("fields"), field_value)

                # 🔹 Recurse into tabs (global or within model)
                # tabs = field.get("tabs") or field.get("model", {}).get("tabs")
                # if tabs:
                #     for tab in tabs:
                #         for section in tab.get("sections") or []:
                #             assign_values(section.get("fields"), field_value)
                # 🔹 Recurse into tabs (global or inside model)
                tabs = None

                if isinstance(field, dict):
                    if isinstance(field.get("tabs"), list):
                        tabs = field.get("tabs")
                    elif isinstance(field.get("model"), dict) and isinstance(field["model"].get("tabs"), list):
                        tabs = field["model"].get("tabs")

                # 🔥 Only loop if tabs is list
                if isinstance(tabs, list):
                    for tab in tabs:
                        for section in tab.get("sections") or []:
                            assign_values(section.get("fields"), field_value)





        # -----------------------------
        # Fetch page with template and populate field values
        # -----------------------------
        def fetch_page_with_template(page_doc):
            template = {}
            if page_doc.get("template"):
                template = frappe.get_value(
                    "Ecommerce Template",
                    page_doc.get("template"),
                    ["name", "data_json", "creation"],
                    as_dict=True
                ) or {}

            data_json = json.loads(template.get("data_json") or "{}")
            field_value = _builder_effective_field_value(page_doc)

            # # Assign top-level fields
            # assign_values(data_json.get("fields"), field_value)

            # # --- Merge Tabs from Template and Page ---
            # template_tabs = data_json.get("tabs") or []
            # saved_tabs = field_value.get("tabs") or []
            # Assign top-level fields
            assign_values(data_json.get("fields"), field_value)

            # --- Merge tabs ---
            template_tabs = data_json.get("tabs") or []
            saved_tabs = field_value.get("tabs") or []

            # Convert saved tabs into a dict by label/name
            saved_tabs_dict = {t.get("label") or t.get("name"): t for t in saved_tabs if t.get("label") or t.get("name")}

            merged_tabs = []
            for tab in template_tabs:
                tab_label = tab.get("label") or tab.get("name")
                saved_tab = saved_tabs_dict.get(tab_label)

                if saved_tab:
                    # Merge tab sections
                    for section in tab.get("sections") or []:
                        assign_values(section.get("fields"), saved_tab)

                merged_tabs.append(tab)

            # Add any extra tabs that exist only in saved data (not in template)
            for label, saved_tab in saved_tabs_dict.items():
                if not any(t.get("label") == label for t in merged_tabs):
                    merged_tabs.append(saved_tab)

            # Assign back merged tabs
            data_json["tabs"] = merged_tabs

            # # Run assignment inside tabs → sections → fields
            # for tab in data_json.get("tabs") or []:
            #     for section in tab.get("sections") or []:
            #         assign_values(section.get("fields"), field_value)

            # Run assignment inside tabs
            for tab in data_json.get("tabs") or []:
                for section in tab.get("sections") or []:
                    assign_values(section.get("fields"), field_value)

            # 🔥 NEW — Merge for NO-TABS JSON PAGES
            for field in (data_json.get("fields") or []):
                key = field.get("key") or field.get("name") or field.get("model")
                if key and key in field_value and key != "Page":
                    field["value"] = field_value[key]

            return {
                "render_data": data_json,
                "page": page_doc.get("page"),
                "parent1": page_doc.get("parent1"),
                "template": page_doc.get("template"),
                "field_value": field_value,
                "inherits_layout": bool(page_doc.get("parent1")),
                "layout_source": _builder_root_page(page_doc).get("name"),
                "creation": page_doc.get("creation"),
                "name": page_doc.get("name"),
            }

        # -----------------------------
        # Fetch single page
        # -----------------------------
        if page_id:
            page = frappe.get_value(
                "Ecommerce Page",
                page_id,
                [
                    "name",
                    "page",
                    "creation",
                    "modified",
                    "parent1",
                    "field_value",
                    "template",
                    "website_id",
                ],
                as_dict=True
            )
            if not page:
                return {"status": "error", "message": f"No page found with ID {page_id}"}

            return {
                "status": "success",
                "message": "Page fetched successfully",
                "data": fetch_page_with_template(page)
            }

        # -----------------------------
        # Fetch all pages
        # -----------------------------
        pages = frappe.get_all(
            "Ecommerce Page",
            fields=[
                "name",
                "page",
                "creation",
                "parent1",
                "field_value",
                "template",
                "website_id",
            ]
        )
        all_data = [fetch_page_with_template(p) for p in pages]

        return {
            "status": "success",
            "message": "All pages fetched successfully",
            "data": all_data
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Get Page Template Data Error")
        return {"status": "error", "message": f"Error fetching page data: {str(e)}"}





# @frappe.whitelist(allow_guest=False)
# def update_page_data():
#     try:
#         data = frappe.local.form_dict

#         page_name = data.get("name")   # 🔑 Existing page identifier
#         title = data.get("title")
#         field_value = data.get("field_value") or {}

#         if not page_name:
#             return {
#                 "status": "error",
#                 "message": "Page name is required to update"
#             }

#         # Fetch the existing doc
#         doc = frappe.get_doc("Ecommerce Page", page_name)

#         # Update fields
#         if title:
#             doc.page = title
#         if field_value:
#             doc.field_value = field_value

#         # Save changes
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Page updated successfully",
#             "data": {
#                 "name": doc.name,
#             }
#         }

#     except Exception as e:
#         frappe.log_error(f"Error in update_page_data: {str(e)}")
#         return {
#             "status": "error",
#             "message": str(e)
#         }
@frappe.whitelist(allow_guest=False)
def update_page_data():
    try:
        data = frappe.local.form_dict

        page_name = data.get("name")   # 🔑 Existing page identifier
        title = data.get("title")
        field_value = data.get("field_value") or {}
        website_id = data.get("website_id") or data.get("website_name")
        parent1 = data.get("parent1") or data.get("main_page_name")

        if not page_name:
            return {
                "status": "error",
                "message": "Page name is required to update"
            }

        # Fetch the existing doc
        doc = frappe.get_doc("Ecommerce Page", page_name)

        # Update fields
        if title:
            doc.page = title
        if website_id:
            doc.website_id = website_id
        if parent1:
            doc.parent1 = parent1
        if field_value:
            doc.field_value = _builder_effective_field_value(doc, field_value)

        # Save changes
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Page updated successfully",
            "data": {
                "name": doc.name,
                "title": doc.page,
                "website_id": doc.website_id,
                "parent1": doc.parent1,
            }
        }

    except Exception as e:
        frappe.log_error(f"Error in update_page_data: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }



import base64
import mimetypes
import os
from urllib.parse import unquote


_BUILDER_PREVIEW_LAYOUTS = {
    "contact_info_header": "announcement",
    "header_navigation": "navigation",
    "product": "shelf",
    "image_gallery": "collection",
    "commerce_promo_hero": "hero",
    "retail_announcement": "announcement",
    "retail_navigation": "navigation",
    "retail_campaign_hero": "hero",
    "retail_collection_mosaic": "collection",
    "retail_story_split": "story",
    "retail_value_icons": "benefits",
    "retail_quote_wall": "reviews",
    "retail_newsletter_footer": "footer",
    "commerce_product_shelf": "shelf",
    "commerce_category_showcase": "collection",
    "commerce_editorial_banner": "story",
    "commerce_brand_showcase": "benefits",
    "commerce_article_grid": "collection",
    "commerce_rich_footer": "footer",
}

_BUILDER_BASE_BLOCKS = {
    "retail_announcement": "Retail Announcement Bar",
    "retail_navigation": "Retail Studio Navigation",
    "retail_campaign_hero": "Retail Campaign Hero",
    "retail_collection_mosaic": "Retail Collection Mosaic",
    "retail_story_split": "Retail Story Split",
    "retail_value_icons": "Retail Value Icons",
    "retail_quote_wall": "Retail Quote Wall",
    "retail_newsletter_footer": "Retail Newsletter Footer",
    "commerce_product_shelf": "Commerce Product Shelf",
}

def _builder_block_model_name(block):
    try:
        model = json.loads(block.get("model") or "{}")
    except (TypeError, ValueError):
        return ""
    return str(model.get("block_name") or "")


def _builder_block_generated_preview(block):
    """Return a lightweight visual preview when a block has no real screenshot."""
    layout = _BUILDER_PREVIEW_LAYOUTS.get(_builder_block_model_name(block))
    if not layout:
        return None

    label = escape(str(block.get("block_name") or block.get("name") or "Section"))
    palette = ("#7c3aed", "#db2777", "#ea580c", "#0891b2", "#16a34a", "#2563eb")
    accent = palette[sum(ord(char) for char in label) % len(palette)]
    pale = f"{accent}18"

    layouts = {
        "announcement": f'''<rect x="42" y="146" width="876" height="72" rx="12" fill="{accent}"/><rect x="258" y="174" width="330" height="14" rx="7" fill="white" opacity=".92"/><rect x="618" y="174" width="92" height="14" rx="7" fill="white" opacity=".68"/>''',
        "navigation": f'''<rect x="42" y="125" width="876" height="116" rx="14" fill="white" stroke="#dbe1e8"/><rect x="76" y="158" width="126" height="24" rx="7" fill="{accent}"/><rect x="405" y="164" width="72" height="12" rx="6" fill="#64748b"/><rect x="499" y="164" width="72" height="12" rx="6" fill="#64748b"/><rect x="593" y="164" width="72" height="12" rx="6" fill="#64748b"/><circle cx="842" cy="170" r="18" fill="{pale}" stroke="{accent}"/>''',
        "hero": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="white" stroke="#dbe1e8"/><rect x="558" y="104" width="360" height="264" rx="16" fill="{pale}"/><circle cx="738" cy="236" r="72" fill="{accent}" opacity=".38"/><rect x="86" y="158" width="108" height="12" rx="6" fill="{accent}"/><rect x="86" y="188" width="360" height="31" rx="8" fill="#172033"/><rect x="86" y="234" width="294" height="13" rx="6" fill="#94a3b8"/><rect x="86" y="258" width="250" height="13" rx="6" fill="#cbd5e1"/><rect x="86" y="302" width="132" height="38" rx="9" fill="{accent}"/>''',
        "collection": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="white" stroke="#dbe1e8"/><rect x="76" y="136" width="250" height="23" rx="7" fill="#172033"/><rect x="76" y="182" width="378" height="150" rx="13" fill="{accent}" opacity=".82"/><rect x="470" y="182" width="198" height="150" rx="13" fill="{pale}"/><rect x="684" y="182" width="198" height="150" rx="13" fill="{accent}" opacity=".45"/>''',
        "story": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="white" stroke="#dbe1e8"/><rect x="42" y="104" width="438" height="264" rx="16" fill="{pale}"/><circle cx="260" cy="236" r="76" fill="{accent}" opacity=".34"/><rect x="536" y="153" width="102" height="12" rx="6" fill="{accent}"/><rect x="536" y="184" width="300" height="28" rx="7" fill="#172033"/><rect x="536" y="230" width="318" height="12" rx="6" fill="#94a3b8"/><rect x="536" y="254" width="260" height="12" rx="6" fill="#cbd5e1"/><rect x="536" y="299" width="118" height="13" rx="6" fill="{accent}"/>''',
        "benefits": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="white" stroke="#dbe1e8"/><rect x="354" y="134" width="252" height="24" rx="8" fill="#172033"/>{''.join(f'<rect x="{x}" y="190" width="242" height="132" rx="14" fill="{pale}"/><circle cx="{x + 121}" cy="224" r="21" fill="{accent}" opacity=".8"/><rect x="{x + 58}" y="260" width="126" height="13" rx="6" fill="#475569"/><rect x="{x + 76}" y="286" width="90" height="10" rx="5" fill="#94a3b8"/>' for x in (76, 359, 642))}''',
        "reviews": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="#172033"/><rect x="350" y="134" width="260" height="24" rx="8" fill="white"/>{''.join(f'<rect x="{x}" y="188" width="370" height="132" rx="14" fill="#253149"/><rect x="{x + 28}" y="216" width="88" height="12" rx="6" fill="{accent}"/><rect x="{x + 28}" y="248" width="286" height="12" rx="6" fill="white" opacity=".82"/><rect x="{x + 28}" y="274" width="226" height="10" rx="5" fill="white" opacity=".45"/>' for x in (76, 514))}''',
        "footer": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="#111827"/><rect x="76" y="148" width="310" height="27" rx="8" fill="white"/><rect x="76" y="195" width="384" height="12" rx="6" fill="#64748b"/><rect x="535" y="150" width="314" height="48" rx="8" fill="#1f2937" stroke="#64748b"/><rect x="773" y="150" width="76" height="48" rx="8" fill="{accent}"/><line x1="76" y1="286" x2="884" y2="286" stroke="#374151"/><rect x="76" y="316" width="126" height="10" rx="5" fill="#64748b"/><rect x="686" y="316" width="198" height="10" rx="5" fill="#64748b"/>''',
        "shelf": f'''<rect x="42" y="104" width="876" height="264" rx="16" fill="white" stroke="#dbe1e8"/><rect x="76" y="132" width="224" height="24" rx="8" fill="#172033"/>{''.join(f'<rect x="{x}" y="182" width="176" height="150" rx="13" fill="#f8fafc" stroke="#dbe1e8"/><rect x="{x + 18}" y="198" width="140" height="78" rx="10" fill="{pale}"/><circle cx="{x + 88}" cy="237" r="28" fill="{accent}" opacity=".{opacity}"/><rect x="{x + 18}" y="290" width="104" height="11" rx="5" fill="#475569"/><rect x="{x + 18}" y="311" width="66" height="10" rx="5" fill="{accent}"/>' for x, opacity in ((76, 80), (286, 62), (496, 46), (706, 32)))}''',
    }

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="430" viewBox="0 0 960 430"><rect width="960" height="430" rx="22" fill="#f1f5f9"/><text x="42" y="58" fill="#172033" font-family="Arial, sans-serif" font-size="23" font-weight="700">{label}</text><text x="918" y="57" fill="{accent}" text-anchor="end" font-family="Arial, sans-serif" font-size="13" font-weight="700">{layout.upper()}</text>{layouts[layout]}</svg>'''
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _builder_block_is_template_alias(block):
    model_name = _builder_block_model_name(block)
    base_name = _BUILDER_BASE_BLOCKS.get(model_name)
    return bool(base_name and block.get("block_name") != base_name)


def _builder_block_preview_data_uri(block_doc):
    image_url = unquote(str(getattr(block_doc, "block_image", "") or "").split("?", 1)[0])
    if not image_url:
        return None

    file_name = frappe.db.get_value("File", {"file_url": image_url}, "name")
    if not file_name:
        return None

    file_path = frappe.get_doc("File", file_name).get_full_path()
    if not os.path.exists(file_path):
        return None

    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    return f"data:{mime_type};base64,{encoded}"


def _builder_value_has_content(value):
    if value is None or value == "":
        return False
    if isinstance(value, (list, tuple, set)):
        return any(_builder_value_has_content(item) for item in value)
    if isinstance(value, dict):
        return any(_builder_value_has_content(item) for item in value.values())
    return True


def _builder_block_has_user_content(block):
    if not isinstance(block, dict):
        return False

    # Starter-template blocks are intentional page content even when their
    # editable values still match the block schema's defaults.
    if block.get("is_template_starter"):
        return True

    block_details = block.get("block_details")
    block_details = block_details if isinstance(block_details, dict) else {}
    model = block_details.get("model") or block.get("model") or {}
    if isinstance(model, str):
        try:
            model = json.loads(model)
        except (TypeError, ValueError):
            model = {}

    fields = _builder_model_fields(model)

    for field in fields:
        value = field.get("value")
        if not _builder_value_has_content(value):
            continue
        if "default" in field and value == field.get("default"):
            continue
        return True
    return False


def _builder_model_fields(model):
    """Flatten every field location supported by a builder block model."""
    if not isinstance(model, dict):
        return []

    fields = _builder_dict_items(model.get("fields"))
    for section in _builder_dict_items(model.get("sections")):
        fields.extend(_builder_dict_items(section.get("fields")))
    for tab in _builder_dict_items(model.get("tabs")):
        fields.extend(_builder_dict_items(tab.get("fields")))
        for section in _builder_dict_items(tab.get("sections")):
            fields.extend(_builder_dict_items(section.get("fields")))
    return fields


def _builder_dict_items(values):
    """Return only object entries from a saved builder list.

    Some legacy pages contain JSON ``null`` placeholders after blocks or
    repeater rows were removed. Published rendering must ignore those stale
    entries instead of allowing one page to break every automatic republish.
    """
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, dict)]


def _builder_configured_field_value(field):
    """Use an untouched field's default without overriding an explicit value."""
    if not isinstance(field, dict):
        return None
    source = field.get("value") if "value" in field else field.get("default")
    if source is None and "default" in field:
        source = field.get("default")
    return copy.deepcopy(source)


def _builder_block_render_mode(block, preview_only=False):
    """Render every added block from its configured values in every surface."""
    return "configured"


def _merge_builder_template_fields(template_fields, saved_fields=None, block_instance=None):
    """Merge saved block values onto a fresh template without losing defaults."""
    saved_values = {}
    for field in _builder_dict_items(saved_fields):
        key = field.get("key") or field.get("name")
        if key and "value" in field and field.get("value") is not None:
            saved_values[key] = field["value"]

    merged_fields = copy.deepcopy(_builder_dict_items(template_fields))
    for field in merged_fields:
        key = field.get("key") or field.get("name")
        if key in saved_values:
            field["value"] = saved_values[key]
        elif key and key in (block_instance or {}) and key != "Page":
            field["value"] = block_instance[key]
        elif "value" not in field:
            field["value"] = copy.deepcopy(field.get("default", ""))
    return merged_fields


def _builder_effective_block_model(block, template_model):
    """Merge saved values onto the latest block schema and its defaults."""
    if not isinstance(block, dict):
        block = {}
    block_details = block.get("block_details")
    block_details = block_details if isinstance(block_details, dict) else {}
    saved_model = block_details.get("model") or block.get("model") or {}
    if isinstance(saved_model, str):
        try:
            saved_model = json.loads(saved_model)
        except (TypeError, ValueError):
            saved_model = {}
    if isinstance(template_model, str):
        try:
            template_model = json.loads(template_model)
        except (TypeError, ValueError):
            template_model = {}

    saved_model = saved_model if isinstance(saved_model, dict) else {}
    template_model = template_model if isinstance(template_model, dict) else {}
    if not template_model:
        return copy.deepcopy(saved_model)

    merged = copy.deepcopy(template_model)
    merged["fields"] = _merge_builder_template_fields(
        template_model.get("fields"), saved_model.get("fields"), block
    )

    saved_sections = _builder_dict_items(saved_model.get("sections"))
    merged["sections"] = _builder_dict_items(merged.get("sections"))
    for index, section in enumerate(merged["sections"]):
        saved_section = saved_sections[index] if index < len(saved_sections) else {}
        section["fields"] = _merge_builder_template_fields(
            section.get("fields"), saved_section.get("fields"), block
        )

    saved_tabs = _builder_dict_items(saved_model.get("tabs"))
    merged["tabs"] = _builder_dict_items(merged.get("tabs"))
    for tab_index, tab in enumerate(merged["tabs"]):
        saved_tab = saved_tabs[tab_index] if tab_index < len(saved_tabs) else {}
        tab["fields"] = _merge_builder_template_fields(
            tab.get("fields"), saved_tab.get("fields"), block
        )
        saved_tab_sections = _builder_dict_items(saved_tab.get("sections"))
        tab["sections"] = _builder_dict_items(tab.get("sections"))
        for section_index, section in enumerate(tab["sections"]):
            saved_section = (
                saved_tab_sections[section_index]
                if section_index < len(saved_tab_sections)
                else {}
            )
            section["fields"] = _merge_builder_template_fields(
                section.get("fields"), saved_section.get("fields"), block
            )

    return merged


def _render_empty_block_preview(block_doc, block_name):
    safe_name = escape(str(block_name or "Block"))
    normalized_name = str(block_name or "").lower()
    block_type = str(getattr(block_doc, "type", "") or "").lower()

    if "navbar 1" in normalized_name or "contact" in normalized_name:
        return """
<section data-ecommerce-demo-content="1" style="padding:10px clamp(18px,4vw,64px);background:linear-gradient(90deg,#111827,#334155);color:#fff;font:500 14px Inter,Arial,sans-serif">
  <div style="display:flex;justify-content:flex-end;gap:24px;max-width:1440px;margin:auto"><span>hello@yourstore.com</span><span>+977 9800000000</span></div>
</section>"""

    if "navbar" in normalized_name or block_type == "header":
        return """
<section data-ecommerce-demo-content="1" style="padding:18px clamp(18px,4vw,64px);background:#fff;border-bottom:1px solid #e5e7eb;font-family:Inter,Arial,sans-serif">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:28px;max-width:1440px;margin:auto">
    <strong style="font-size:22px;letter-spacing:-.04em;color:#111827">YOUR STORE</strong>
    <nav style="display:flex;gap:24px;color:#374151;font-size:14px"><span>New arrivals</span><span>Products</span><span>Collections</span><span>About</span></nav>
    <div style="display:flex;align-items:center;gap:16px"><span style="padding:10px 18px;border:1px solid #d1d5db;border-radius:999px;color:#6b7280">Search products</span><span style="font-size:20px">♡</span><span style="font-size:20px">♧</span></div>
  </div>
</section>"""

    if "product" in normalized_name:
        cards = "".join(
            f"""<article><div style="aspect-ratio:1;background:{color};border-radius:18px;display:grid;place-items:center;color:#475569;font-size:42px">{icon}</div><p style="margin:14px 0 5px;color:#64748b;font-size:12px">{brand}</p><h3 style="margin:0 0 8px;font-size:16px">{title}</h3><strong>Rs {price}</strong></article>"""
            for color, icon, brand, title, price in [
                ("#eef2ff", "◉", "Northstar", "Everyday Smartphone", "49,999"),
                ("#fef3c7", "⌁", "Apex Audio", "Wireless Headphones", "12,900"),
                ("#ecfeff", "▣", "Orbit Gear", "Lightweight Laptop", "89,500"),
                ("#fce7f3", "◇", "FrameLab", "Pocket Camera", "38,000"),
            ]
        )
        return f"""
<section data-ecommerce-demo-content="1" style="padding:64px clamp(18px,4vw,64px);font-family:Inter,Arial,sans-serif;color:#111827">
  <div style="max-width:1440px;margin:auto"><h2 style="margin:0;font-size:36px">Featured products</h2><p style="color:#64748b">A sample collection appears here until products are added.</p><div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px;margin-top:28px">{cards}</div></div>
</section>"""

    if "gallery" in normalized_name:
        tiles = "".join(
            f'<article style="min-height:360px;border-radius:20px;background:{color};display:flex;align-items:flex-end;padding:24px"><strong style="font-size:20px">{title}</strong></article>'
            for color, title in [
                ("linear-gradient(145deg,#dbeafe,#93c5fd)", "Featured collection"),
                ("linear-gradient(145deg,#fce7f3,#f9a8d4)", "New arrivals"),
                ("linear-gradient(145deg,#dcfce7,#86efac)", "Customer favourites"),
            ]
        )
        return f"""
<section data-ecommerce-demo-content="1" style="padding:64px clamp(18px,4vw,64px);font-family:Inter,Arial,sans-serif;color:#111827;text-align:center">
  <h2 style="margin:0;font-size:36px">Explore our collection</h2><p style="color:#64748b">Add your own images and links when you are ready.</p><div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-top:30px;text-align:left">{tiles}</div>
</section>"""

    if block_type == "footer" or "footer" in normalized_name:
        return """
<footer data-ecommerce-demo-content="1" style="padding:56px clamp(18px,4vw,64px) 24px;background:#0f172a;color:#fff;font-family:Inter,Arial,sans-serif">
  <div style="display:grid;grid-template-columns:2fr repeat(3,1fr);gap:36px;max-width:1440px;margin:auto"><div><h2>Your Store</h2><p style="max-width:420px;color:#94a3b8;line-height:1.7">Quality products, straightforward shopping, and dependable local support.</p></div><div><strong>Shop</strong><p style="color:#cbd5e1">All products</p><p style="color:#cbd5e1">New arrivals</p></div><div><strong>Help</strong><p style="color:#cbd5e1">Delivery</p><p style="color:#cbd5e1">Contact</p></div><div><strong>Company</strong><p style="color:#cbd5e1">About</p><p style="color:#cbd5e1">Privacy</p></div></div>
</footer>"""

    try:
        image_uri = _builder_block_preview_data_uri(block_doc)
    except Exception:
        frappe.log_error(
            title=f"Builder preview image failed: {block_name}",
            message=frappe.get_traceback(),
        )
        image_uri = None

    if image_uri:
        return f'<section data-ecommerce-demo-content="1" style="padding:24px;background:#fff"><img src="{image_uri}" alt="{safe_name} preview" style="display:block;width:100%;max-height:620px;object-fit:contain;object-position:top" /></section>'

    return f"""
<section data-ecommerce-demo-content="1" style="padding:80px clamp(18px,8vw,120px);background:#f8fafc;font-family:Inter,Arial,sans-serif;color:#111827">
  <p style="margin:0;color:#64748b;text-transform:uppercase;letter-spacing:.14em;font-size:12px">Sample section</p><h2 style="margin:10px 0;font-size:42px">{safe_name}</h2><p style="max-width:620px;color:#64748b;line-height:1.7">Your content will appear here. Open this section in the editor to customize its text, imagery, and links.</p>
</section>"""


def _builder_preview_products():
    from ecommerce.default_ecommerce_catalogue import (
        DEFAULT_BRAND,
        DEFAULT_PRODUCTS,
    )

    return [
        {
            "name": f"preview-product-{index}",
            "product_name": product["name"],
            "brand_name": DEFAULT_BRAND["name"],
            "price": product["price"],
            "selling_price": product["price"],
            "discounted_price": product["price"],
            "product_image": product["image"],
            "url": "#",
            "show_add_to_cart": True,
        }
        for index, product in enumerate(DEFAULT_PRODUCTS, start=1)
    ]

@frappe.whitelist(allow_guest=False)
def get_block():
    try:
        blocks = frappe.get_all(
            "Ecommerce Block",
            fields=["name", "block_name", "block_image", "model", "type"]
        )

        # Return template aliases as well as their base blocks. The page editor
        # uses the current template's starter block names to keep only the
        # relevant aliases, while still showing base blocks for layouts the
        # template does not provide. Removing aliases here made starter
        # sections visible on the page but impossible to add again.

        # Convert image paths to Base64
        for block in blocks:
            block["model_name"] = _builder_block_model_name(block)
            block["is_template_alias"] = _builder_block_is_template_alias(block)
            if block.get("block_image"):
                try:
                    # Resolve through the File DocType so public/private paths
                    # use Frappe's own safe path handling.
                    image_url = unquote(str(block["block_image"]).split("?", 1)[0])
                    file_name = frappe.db.get_value(
                        "File", {"file_url": image_url}, "name"
                    )
                    if not file_name:
                        # Builder-provided previews live in this app's public
                        # assets and do not need a File record or base64 copy.
                        if image_url.startswith("/assets/ecommerce/"):
                            block["block_image_base64"] = image_url
                            continue
                        raise FileNotFoundError(f"File record not found: {image_url}")
                    file_path = frappe.get_doc("File", file_name).get_full_path()

                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            encoded = base64.b64encode(f.read()).decode("utf-8")

                        mime_type = (
                            mimetypes.guess_type(file_path)[0]
                            or "application/octet-stream"
                        )

                        block["block_image_base64"] = f"data:{mime_type};base64,{encoded}"
                    else:
                        block["block_image_base64"] = None
                except Exception as img_err:
                    frappe.log_error(f"Error encoding image for {block['name']}: {str(img_err)}")
                    block["block_image_base64"] = None

            if not block.get("block_image_base64"):
                block["block_image_base64"] = _builder_block_generated_preview(block)

        return {
            "status": "success",
            "message": "Blocks fetched successfully",
            "data": blocks
        }

    except Exception as e:
        frappe.log_error(f"Error in get_block: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist(allow_guest=False)
def preview_builder_block(block_name=None, website_id=None, values=None):
    """Render one unsaved builder block for the visual section editor."""
    try:
        request_body = getattr(getattr(frappe, "local", None), "request", None)
        request_body = getattr(request_body, "data", None)
        request_data = json.loads(request_body or "{}")
        payload = request_data.get("doc", request_data)
        if isinstance(payload, str):
            payload = json.loads(payload)
        payload = payload if isinstance(payload, dict) else {}

        block_name = block_name or payload.get("block_name")
        if not block_name or not frappe.db.exists("Ecommerce Block", block_name):
            return {"status": "error", "message": _("Section not found.")}

        website_id = website_id or payload.get("website_id")
        values = values if values is not None else payload.get("values") or {}
        if isinstance(values, str):
            values = json.loads(values)
        if not isinstance(values, dict):
            values = {}

        block = frappe.get_doc("Ecommerce Block", block_name)
        try:
            block_model = json.loads(block.model or "{}")
        except (TypeError, ValueError):
            block_model = {}

        sample_logo_svg = base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="240" height="80" viewBox="0 0 240 80"><rect width="240" height="80" rx="12" fill="#ecfdf5"/><path d="M34 52V28h8l10 13 10-13h8v24h-8V40L52 52 42 40v12z" fill="#169b62"/><text x="82" y="47" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#1f2937">Your logo</text></svg>'
        ).decode("ascii")
        sample_values = {}
        for field in block_model.get("fields") or []:
            key = field.get("key") or field.get("name")
            if not key or _builder_value_has_content(values.get(key)):
                continue
            if key == "logo":
                sample_values[key] = f"data:image/svg+xml;base64,{sample_logo_svg}"
            elif key == "all_products":
                sample_values[key] = [
                    {"keyword": _("All products"), "destination_url": "#"},
                    {"keyword": _("About us"), "destination_url": "#"},
                    {"keyword": _("Shop"), "destination_url": "#"},
                ]
            elif key == "search_placeholder":
                sample_values[key] = _("Search products")
            elif _builder_value_has_content(field.get("default")):
                sample_values[key] = copy.deepcopy(field["default"])
            elif field.get("type") == "email":
                sample_values[key] = "hello@yourstore.com"
            elif field.get("type") == "phone":
                sample_values[key] = "9800000000"
            elif field.get("type") == "toggle":
                sample_values[key] = field.get("default", True)

        render_values = {
            key: value for key, value in values.items()
            if _builder_value_has_content(value)
        }
        context = {
            **sample_values,
            **render_values,
            "vendor_website_id": website_id,
            "vendor_website_url": _get_vendor_fixed_url(website_id) if website_id else "",
            "store_categories": _get_storefront_category_tree(website_id) if website_id else [],
            "storefront_all_products_url": _storefront_all_products_url(website_id),
        }
        if block_name == "Navbar 2":
            menu_category_ids = values.get("menu_categories") or []
            context["store_categories"] = _get_storefront_category_tree(
                website_id,
                menu_category_ids,
            ) if website_id else []
            context["storefront_all_products_url"] = _storefront_all_products_url(
                website_id,
                menu_category_ids,
            )

        product_ids = values.get("product_list")
        if isinstance(product_ids, list):
            context["product_list"] = _resolve_builder_products(product_ids)

        preview_theme = frappe.db.get_value(
            "Ecommerce Vendor Website",
            website_id,
            [
                "primary_color",
                "secondary_color",
                "additional_color1",
                "additional_color2",
                "font",
            ],
            as_dict=True,
        ) if website_id else {}

        return {
            "status": "success",
            "data": {
                "html": _builder_apply_theme_tokens(
                    Template(block.block or "").render(**context)
                ),
                "style": "\n".join((
                    _builder_theme_css(preview_theme or {}),
                    _builder_apply_theme_tokens(block.style or ""),
                )),
                "sample_values": sample_values,
            },
        }
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "Builder Block Preview Failed")
        return {"status": "error", "message": str(exc)}








# @frappe.whitelist(allow_guest=False)
# def update_publish_data():
#     try:
#         import json
#         from jinja2 import Template

#         # --- Parse request data ---
#         data = json.loads(frappe.request.data) if frappe.request.data else frappe.local.form_dict
#         page_name = data.get("name")
#         title = data.get("title")
#         field_value = data.get("field_value") or {}

#         if not page_name:
#             return {"status": "error", "message": "Page name is required"}

#         # --- Deep-clean unwanted "null" keys ---
#         def clean_null_keys(d):
#             if isinstance(d, dict):
#                 return {k: clean_null_keys(v) for k, v in d.items() if k != "null"}
#             elif isinstance(d, list):
#                 return [clean_null_keys(i) for i in d]
#             return d

#         field_value = clean_null_keys(field_value)

#         # --- Helper: replace product_list IDs with actual product docs ---
#         def resolve_products(val):
#             products = []
#             for pid in val:
#                 try:
#                     prod = frappe.get_doc("Ecommerce Product", pid)
#                     products.append({
#                         "id": prod.name,
#                         "product_name": prod.product_name,
#                         "product_description": prod.product_description,
#                         "price": prod.price,
#                         "product_image": prod.product_image,
#                     })
#                 except frappe.DoesNotExistError:
#                     frappe.log_error(f"Product {pid} not found")
#             return products

#         # --- Update any product_list fields globally inside field_value ---
#         def traverse_and_update(d):
#             if isinstance(d, dict):
#                 new_d = {}
#                 for k, v in d.items():
#                     if k == "product_list" and isinstance(v, list):
#                         new_d[k] = resolve_products(v)
#                     else:
#                         new_d[k] = traverse_and_update(v)
#                 return new_d
#             elif isinstance(d, list):
#                 return [traverse_and_update(i) for i in d]
#             return d

#         field_value = traverse_and_update(field_value)

#         # --- Fetch Page ---
#         doc = frappe.get_doc("Ecommerce Page", page_name)
#         if title:
#             doc.page = title
#         if field_value:
#             doc.field_value = field_value

#         # --- Render Blocks (HTML + Script + Style) ---
#         def render_blocks(section):
#             html = ""
#             scripts = []
#             styles = []

#             blocks = field_value.get(section) or []
#             for block in blocks:
#                 block_name = block.get("block_name") or block.get("name")
#                 if not block_name:
#                     continue
#                 try:
#                     block_doc = frappe.get_doc("Ecommerce Block", block_name)
#                     block_html = block_doc.block or ""
#                     model = block.get("block_details", {}).get("model", {})

#                     # --- Build context ---
#                     context = {}
#                     for f in model.get("fields") or []:
#                         key = f.get("key") or f.get("name")
#                         val = f.get("value")

#                         if key == "product_list" and isinstance(val, list):
#                             val = resolve_products(val)

#                         context[key] = val

#                         # Collect block field-level script/style
#                         if key == "script" and val:
#                             scripts.append(val)
#                         if key == "style" and val:
#                             styles.append(val)

#                     # Merge direct keys from model
#                     for k, v in model.items():
#                         if k not in context:
#                             if k == "product_list" and isinstance(v, list):
#                                 context[k] = resolve_products(v)
#                             else:
#                                 context[k] = v

#                     # Collect block-level script/style from Block Doc itself
#                     if getattr(block_doc, "script", None):
#                         scripts.append(block_doc.script)
#                     if getattr(block_doc, "style", None):
#                         styles.append(block_doc.style)

#                     # Render the block HTML
#                     block_tpl = Template(block_html)
#                     html += block_tpl.render(**context) + "\n"

#                 except frappe.DoesNotExistError:
#                     frappe.log_error(f"Builder Block {block_name} not found")

#             return html, scripts, styles

#         # --- Render each section ---
#         header_html, header_scripts, header_styles = render_blocks("header")
#         main_html, main_scripts, main_styles = render_blocks("main")
#         footer_html, footer_scripts, footer_styles = render_blocks("footer")

#         def unique_list(lst):
#             seen = set()
#             result = []
#             for i in lst:
#                 if i not in seen:
#                     seen.add(i)
#                     result.append(i)
#             return result

#         all_scripts = "\n".join(unique_list(header_scripts + main_scripts + footer_scripts))
#         all_styles = "\n".join(unique_list(header_styles + main_styles + footer_styles))


#         # # Merge all scripts/styles
#         # all_scripts = "\n".join(header_scripts + main_scripts + footer_scripts)
#         # all_styles = "\n".join(header_styles + main_styles + footer_styles)

#         # --- Get Page Template ---
#         template_name = getattr(doc, "template", None)
#         if not template_name:
#             return {"status": "error", "message": "No template linked to this page"}

#         try:
#             template_doc = frappe.get_doc("Ecommerce Template", template_name)
#             template_html = template_doc.template or ""
#         except frappe.DoesNotExistError:
#             return {"status": "error", "message": f"Template {template_name} not found"}

#         # --- Render Page Template ---
#         page_tpl = Template(template_html)

#         # Safe field_value (remove block sections)
#         safe_field_value = dict(field_value)
#         for section in ["header", "main", "footer"]:
#             safe_field_value.pop(section, None)

#         page_html = page_tpl.render(
#             **safe_field_value,
#             header=header_html,
#             main=main_html,
#             footer=footer_html,
#             blockscript=all_scripts,
#             blockstyle=all_styles,
#             doc=doc
#         )

#         # --- Save final output ---
#         doc.block_render = page_html
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Page updated & published successfully",
#             "data": {
#                 "name": doc.name,
#                 "block_render": doc.block_render,
#                 "field_value": doc.field_value
#             }
#         }

#     except Exception as e:
#         frappe.log_error(title="Update Publish Data Error", message=frappe.get_traceback())
#         return {"status": "error", "message": str(e)}




# @frappe.whitelist(allow_guest=False)
# def update_publish_data():
#     try:
#         import json
#         from jinja2 import Template

#         # --- Parse request data ---
#         data = json.loads(frappe.request.data) if frappe.request.data else frappe.local.form_dict
#         page_name = data.get("name")
#         title = data.get("title")
#         field_value = data.get("field_value") or {}

#         if not page_name:
#             return {"status": "error", "message": "Page name is required"}

#         # --- Deep-clean unwanted "null" keys ---
#         def clean_null_keys(d):
#             if isinstance(d, dict):
#                 return {k: clean_null_keys(v) for k, v in d.items() if k != "null"}
#             elif isinstance(d, list):
#                 return [clean_null_keys(i) for i in d]
#             return d

#         field_value = clean_null_keys(field_value)

#         # --- Helper: unwrap nested {"value": ...} keys ---
#         def unwrap_value(v):
#             """Recursively unwraps {'value': X} structures to X."""
#             if isinstance(v, dict):
#                 if set(v.keys()) == {"value"}:
#                     return unwrap_value(v["value"])
#                 else:
#                     return {k: unwrap_value(sub_v) for k, sub_v in v.items()}
#             elif isinstance(v, list):
#                 return [unwrap_value(i) for i in v]
#             return v

#         # --- Normalize repeater fields ---
#         def parse_repeater_field(field):
#             """
#             Converts repeater field into a list of dicts using its nested fields definition.
#             """
#             if not field or "fields" not in field:
#                 return field.get("value", []) if isinstance(field, dict) else field

#             items = []
#             inner_fields = field.get("fields", [])
#             for val_obj in field.get("value", []):
#                 if isinstance(val_obj, dict) and "value" in val_obj and len(inner_fields) == 1:
#                     # Simple repeater: one field only
#                     items.append({inner_fields[0].get("name"): val_obj.get("value")})
#                 elif isinstance(val_obj, dict):
#                     # Complex repeater (multi-field entries)
#                     item_data = {}
#                     for inner_field in inner_fields:
#                         key = inner_field.get("name")
#                         if key in val_obj:
#                             item_data[key] = val_obj[key]
#                         elif "value" in val_obj:
#                             item_data[key] = val_obj["value"]
#                     items.append(item_data)
#             return items

#         def normalize_repeaters(value):
#             """Recursively normalizes any repeater-type fields."""
#             value = unwrap_value(value)  # ✅ NEW: unwraps nested value objects first

#             if isinstance(value, dict) and "fields" in value and "value" in value:
#                 return parse_repeater_field(value)
#             elif isinstance(value, dict):
#                 return {k: normalize_repeaters(v) for k, v in value.items()}
#             elif isinstance(value, list):
#                 return [normalize_repeaters(v) for v in value]
#             return value

#         # --- Helper: replace product_list IDs with actual product docs ---
#         def resolve_products(val):
#             products = []
#             for pid in val:
#                 try:
#                     prod = frappe.get_doc("Ecommerce Product", pid)
#                     products.append({
#                         "id": prod.name,
#                         "product_name": prod.product_name,
#                         "product_description": prod.product_description,
#                         "price": prod.price,
#                         "product_image": prod.product_image,
#                     })
#                 except frappe.DoesNotExistError:
#                     frappe.log_error(f"Product {pid} not found")
#             return products

#         # --- Update any product_list fields globally inside field_value ---
#         def traverse_and_update(d):
#             if isinstance(d, dict):
#                 new_d = {}
#                 for k, v in d.items():
#                     if k == "product_list" and isinstance(v, list):
#                         new_d[k] = resolve_products(v)
#                     else:
#                         new_d[k] = traverse_and_update(v)
#                 return new_d
#             elif isinstance(d, list):
#                 return [traverse_and_update(i) for i in d]
#             return d

#         field_value = traverse_and_update(field_value)

#         # --- Fetch Page ---
#         doc = frappe.get_doc("Ecommerce Page", page_name)
#         if title:
#             doc.page = title
#         if field_value:
#             doc.field_value = field_value

#         # --- Render Blocks (HTML + Script + Style) ---
#         def render_blocks(section):
#             html = ""
#             scripts = []
#             styles = []

#             blocks = field_value.get(section) or []
#             for block in blocks:
#                 block_name = block.get("block_name") or block.get("name")
#                 if not block_name:
#                     continue
#                 try:
#                     block_doc = frappe.get_doc("Ecommerce Block", block_name)
#                     block_html = block_doc.block or ""
#                     model = block.get("block_details", {}).get("model", {})

#                     # --- Build context ---
#                     context = {}
#                     for f in model.get("fields") or []:
#                         key = f.get("key") or f.get("name")
#                         val = f.get("value")

#                         if key == "product_list" and isinstance(val, list):
#                             val = resolve_products(val)

#                         val = normalize_repeaters(val)
#                         context[key] = val

#                         if key == "script" and val:
#                             scripts.append(val)
#                         if key == "style" and val:
#                             styles.append(val)

#                     # Merge direct keys from model
#                     for k, v in model.items():
#                         if k not in context:
#                             if k == "product_list" and isinstance(v, list):
#                                 context[k] = resolve_products(v)
#                             else:
#                                 context[k] = normalize_repeaters(v)

#                     # Collect block-level script/style from Block Doc itself
#                     if getattr(block_doc, "script", None):
#                         scripts.append(block_doc.script)
#                     if getattr(block_doc, "style", None):
#                         styles.append(block_doc.style)

#                     # Render the block HTML safely
#                     block_tpl = Template(block_html)
#                     html += block_tpl.render(**context) + "\n"

#                 except frappe.DoesNotExistError:
#                     frappe.log_error(f"Builder Block {block_name} not found")

#             return html, scripts, styles

#         # --- Render each section ---
#         header_html, header_scripts, header_styles = render_blocks("header")
#         main_html, main_scripts, main_styles = render_blocks("main")
#         footer_html, footer_scripts, footer_styles = render_blocks("footer")

#         def unique_list(lst):
#             seen = set()
#             result = []
#             for i in lst:
#                 if i not in seen:
#                     seen.add(i)
#                     result.append(i)
#             return result

#         all_scripts = "\n".join(unique_list(header_scripts + main_scripts + footer_scripts))
#         all_styles = "\n".join(unique_list(header_styles + main_styles + footer_styles))

#         # --- Get Page Template ---
#         template_name = getattr(doc, "template", None)
#         if not template_name:
#             return {"status": "error", "message": "No template linked to this page"}

#         try:
#             template_doc = frappe.get_doc("Ecommerce Template", template_name)
#             template_html = template_doc.template or ""
#         except frappe.DoesNotExistError:
#             return {"status": "error", "message": f"Template {template_name} not found"}

#         # --- Render Page Template ---
#         page_tpl = Template(template_html)

#         # Safe field_value (remove block sections)
#         safe_field_value = dict(field_value)
#         for section in ["header", "main", "footer"]:
#             safe_field_value.pop(section, None)

#         page_html = page_tpl.render(
#             **safe_field_value,
#             header=header_html,
#             main=main_html,
#             footer=footer_html,
#             blockscript=all_scripts,
#             blockstyle=all_styles,
#             doc=doc
#         )

#         # --- Save final output ---
#         doc.block_render = page_html
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Page updated & published successfully",
#             "data": {
#                 "name": doc.name,
#                 "block_render": doc.block_render,
#                 "field_value": doc.field_value
#             }
#         }

#     except Exception as e:
#         frappe.log_error(title="Update Publish Data Error", message=frappe.get_traceback())
#         return {"status": "error", "message": str(e)}



@frappe.whitelist(allow_guest=False)
def update_publish_data(
    _page_name=None,
    _title=None,
    _field_value=None,
    _preview_only=None,
    _commit=True,
):
    try:
        import json
        from jinja2 import Template

        # --- Parse request data ---
        if _page_name is None:
            data = json.loads(frappe.request.data) if frappe.request.data else frappe.local.form_dict
            page_name = data.get("name")
            title = data.get("title")
            field_value = data.get("field_value") or {}
            preview_only = str(data.get("preview_only") or "").lower() in {
                "1", "true", "yes", "on"
            }
        else:
            page_name = _page_name
            title = _title
            field_value = _builder_json_object(_field_value)
            preview_only = bool(_preview_only)

        if not page_name:
            return {"status": "error", "message": "Page name is required"}

        # --- Deep-clean unwanted "null" keys ---
        def clean_null_keys(d):
            if isinstance(d, dict):
                return {k: clean_null_keys(v) for k, v in d.items() if k != "null"}
            elif isinstance(d, list):
                return [clean_null_keys(i) for i in d]
            return d

        field_value = clean_null_keys(field_value)

        # --- Helper: unwrap nested {"value": ...} keys ---
        def unwrap_value(v):
            """Recursively unwraps {'value': X} structures to X."""
            if isinstance(v, dict):
                if set(v.keys()) == {"value"}:
                    return unwrap_value(v["value"])
                else:
                    return {k: unwrap_value(sub_v) for k, sub_v in v.items()}
            elif isinstance(v, list):
                return [unwrap_value(i) for i in v]
            return v

        # --- Normalize repeater fields ---
        def parse_repeater_field(field):
            """
            Converts repeater field into a list of dicts using its nested fields definition.
            """
            if not field or "fields" not in field:
                return field.get("value", []) if isinstance(field, dict) else field

            items = []
            inner_fields = _builder_dict_items(field.get("fields"))
            for val_obj in field.get("value", []):
                if isinstance(val_obj, dict) and "value" in val_obj and len(inner_fields) == 1:
                    # Simple repeater: one field only
                    items.append({inner_fields[0].get("name"): val_obj.get("value")})
                elif isinstance(val_obj, dict):
                    # Complex repeater (multi-field entries)
                    item_data = {}
                    for inner_field in inner_fields:
                        key = inner_field.get("name")
                        if key in val_obj:
                            item_data[key] = val_obj[key]
                        elif "value" in val_obj:
                            item_data[key] = val_obj["value"]
                    items.append(item_data)
            return items

        def normalize_repeaters(value):
            """Recursively normalizes any repeater-type fields."""
            value = unwrap_value(value)  # ✅ NEW: unwraps nested value objects first

            if isinstance(value, dict) and "fields" in value and "value" in value:
                return parse_repeater_field(value)
            elif isinstance(value, dict):
                return {k: normalize_repeaters(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [normalize_repeaters(v) for v in value]
            return value

        # --- Helper: replace product_list IDs with actual product docs ---
        def resolve_products(val):
            return _resolve_builder_products(val)

        def normalize_css_color(value):
            value = str(value or "").strip()
            if re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", value):
                return value
            return None

        def normalize_theme_color(value):
            tokens = {
                "primary": "var(--store-primary)",
                "secondary": "var(--store-secondary)",
                "additional_1": "var(--store-additional-1)",
                "additional_2": "var(--store-additional-2)",
            }
            return tokens.get(str(value or "").strip())

        def normalize_css_length(value, allow_multiple=False, allow_auto=False):
            value = str(value or "").strip().lower()
            if not value:
                return None

            values = value.split()
            if not allow_multiple and len(values) != 1:
                return None
            if allow_multiple and not 1 <= len(values) <= 4:
                return None

            normalized = []
            for item in values:
                if allow_auto and item == "auto":
                    normalized.append(item)
                    continue
                if re.fullmatch(r"-?\d+(?:\.\d+)?", item):
                    normalized.append(f"{item}px")
                    continue
                if re.fullmatch(r"-?\d+(?:\.\d+)?(?:px|rem|em|%|vh|vw)", item):
                    normalized.append(item)
                    continue
                return None

            return " ".join(normalized)

        def get_block_style_attributes(style_values):
            if not isinstance(style_values, dict):
                return "", ""

            background_type = str(style_values.get("background_type") or "").strip()
            background = None
            if background_type == "gradient":
                gradient_from = (
                    normalize_theme_color(style_values.get("gradient_from_theme"))
                    or normalize_css_color(style_values.get("gradient_from"))
                )
                gradient_to = (
                    normalize_theme_color(style_values.get("gradient_to_theme"))
                    or normalize_css_color(style_values.get("gradient_to"))
                )
                allowed_directions = {
                    "to right", "to left", "to bottom", "to top",
                    "to bottom right", "to bottom left",
                }
                gradient_direction = str(
                    style_values.get("gradient_direction") or "to right"
                ).strip().lower()
                if gradient_direction not in allowed_directions:
                    gradient_direction = "to right"
                if gradient_from and gradient_to:
                    background = (
                        f"linear-gradient({gradient_direction}, "
                        f"{gradient_from}, {gradient_to})"
                    )
            elif background_type == "solid" or not background_type:
                # The empty type keeps compatibility with solid colors saved
                # before background modes were introduced.
                background = (
                    normalize_theme_color(style_values.get("background_theme"))
                    or normalize_css_color(style_values.get("background_color"))
                )
            text_color = (
                normalize_theme_color(style_values.get("text_theme"))
                or normalize_css_color(style_values.get("text_color"))
            )
            action_background = (
                normalize_theme_color(style_values.get("action_theme"))
                or normalize_css_color(style_values.get("action_color"))
            )
            font_size = normalize_css_length(style_values.get("font_size"))
            margin = normalize_css_length(
                style_values.get("margin"), allow_multiple=True, allow_auto=True
            )
            padding = normalize_css_length(
                style_values.get("padding"), allow_multiple=True
            )
            margin_sides = {
                side: normalize_css_length(
                    style_values.get(f"margin_{side}"), allow_auto=True
                )
                for side in ("top", "right", "bottom", "left")
            }
            padding_sides = {
                side: normalize_css_length(style_values.get(f"padding_{side}"))
                for side in ("top", "right", "bottom", "left")
            }

            classes = ["ecommerce-builder-block"]
            variables = []
            if background:
                classes.append("ecommerce-custom-background")
                variables.append(f"--ecommerce-block-background:{background}")
            if text_color:
                classes.append("ecommerce-custom-text")
                variables.append(f"--ecommerce-block-text:{text_color}")
            if action_background:
                classes.append("ecommerce-custom-action")
                variables.append(f"--ecommerce-action-background:{action_background}")
            if font_size:
                classes.append("ecommerce-custom-font-size")
                variables.append(f"--ecommerce-block-font-size:{font_size}")
            if margin or any(margin_sides.values()):
                classes.append("ecommerce-custom-margin")
                if margin:
                    variables.append(f"margin:{margin}")
                variables.extend(
                    f"margin-{side}:{value}"
                    for side, value in margin_sides.items()
                    if value
                )
            if padding or any(padding_sides.values()):
                classes.append("ecommerce-custom-padding")
                if padding:
                    variables.append(f"padding:{padding}")
                variables.extend(
                    f"padding-{side}:{value}"
                    for side, value in padding_sides.items()
                    if value
                )

            if len(classes) == 1:
                return "", ""

            style_attribute = ";".join(variables)
            return " ".join(classes), style_attribute

        def apply_block_style(rendered_html, style_values):
            style_class, style_attribute = get_block_style_attributes(style_values)
            if not style_class:
                return rendered_html

            return (
                f'<div class="{style_class}" style="{style_attribute}">'
                f"{rendered_html}</div>"
            )

        def add_product_styles(products, style_values, product_settings):
            if not isinstance(products, list):
                return products

            if not isinstance(style_values, dict):
                style_values = {}
            if not isinstance(product_settings, dict):
                product_settings = {}

            for product in products:
                if not isinstance(product, dict):
                    continue
                product_id = str(product.get("id") or product.get("name") or "")
                style_class, style_attribute = get_block_style_attributes(
                    style_values.get(product_id) or {}
                )
                product["builder_style_class"] = style_class
                product["builder_style_attribute"] = style_attribute
                settings = product_settings.get(product_id) or {}
                if not isinstance(settings, dict):
                    settings = {}
                product["show_add_to_cart"] = settings.get(
                    "show_add_to_cart", True
                )
                action_class, action_attribute = get_block_style_attributes(
                    settings.get("add_to_cart_style") or {}
                )
                product["add_to_cart_style_class"] = action_class
                product["add_to_cart_style_attribute"] = action_attribute
            return products

        # --- Update any product_list fields globally inside field_value ---
        def traverse_and_update(d):
            if isinstance(d, dict):
                new_d = {}
                for k, v in d.items():
                    if k == "product_list" and isinstance(v, list):
                        new_d[k] = resolve_products(v)
                    else:
                        new_d[k] = traverse_and_update(v)
                return new_d
            elif isinstance(d, list):
                return [traverse_and_update(i) for i in d]
            return d

        # --- Fetch Page ---
        doc = frappe.get_doc("Ecommerce Page", page_name)
        if preview_only:
            vendor_info = get_vendor_id() or {}
            page_vendor_id = frappe.db.get_value(
                "Ecommerce Vendor Website",
                doc.website_id,
                "vendor_id",
            )
            if not page_vendor_id or str(page_vendor_id) != str(vendor_info.get("vendor_id")):
                frappe.local.response.http_status_code = 403
                return {
                    "status": "error",
                    "message": _("You cannot preview this page."),
                }
        if title:
            doc.page = title
        field_value = _builder_effective_field_value(doc, field_value)
        doc.field_value = field_value

        # Keep the saved builder configuration as product IDs. Use a separate
        # expanded copy only while rendering the published HTML.
        render_field_value = traverse_and_update(field_value)

        # Older drafts may have been created before starter content was added
        # to their selected template. Fill only the missing preview areas from
        # the latest template definition; never persist this fallback data.
        preview_starter_content = {}
        if preview_only and doc.template:
            try:
                template_config = json.loads(
                    frappe.db.get_value(
                        "Ecommerce Template", doc.template, "data_json"
                    )
                    or "{}"
                )
                preview_starter_content = (
                    template_config.get("starter_content") or {}
                )
            except (TypeError, ValueError):
                preview_starter_content = {}

        # --- Render Blocks (HTML + Script + Style) ---
        def render_blocks(section):
            html = ""
            scripts = []
            styles = []

            blocks = render_field_value.get(section)
            # A non-blank template must render the same starter blocks in the
            # public page as it does in preview only when that section is
            # missing from an older draft. An explicit empty list means the
            # merchant removed every block and must remain empty.
            if not isinstance(blocks, list):
                blocks = copy.deepcopy(preview_starter_content.get(section) or [])
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                block_name = block.get("block_name") or block.get("name")
                if not block_name:
                    continue
                try:
                    block_doc = frappe.get_doc("Ecommerce Block", block_name)
                    block_html = block_doc.block or ""
                    model = _builder_effective_block_model(block, block_doc.model)

                    if _builder_block_render_mode(block, preview_only) != "configured":
                        continue


                    # --- Build context ---
                    context = {
                        "vendor_website_url": _get_vendor_fixed_url(doc.website_id),
                        "vendor_website_id": doc.website_id,
                        "vendor_website_name": doc.website_name,
                        "store_categories": _get_storefront_category_tree(doc.website_id),
                        "storefront_all_products_url": _storefront_all_products_url(
                            doc.website_id
                        ),
                    }
                    destination_url_overrides = {}
                    for f in _builder_model_fields(model):
                        key = f.get("key") or f.get("name")
                        val = _builder_configured_field_value(f)

                        if f.get("type") == "commerce_link" and key:
                            type_field_name = (
                                f.get("destination_type_field") or "destination_type"
                            )
                            type_field = next(
                                (
                                    candidate
                                    for candidate in _builder_model_fields(model)
                                    if (candidate.get("key") or candidate.get("name"))
                                    == type_field_name
                                ),
                                None,
                            )
                            destination_type = (
                                _builder_configured_field_value(type_field)
                                if type_field
                                else None
                            )
                            context[f"{key}_url"] = (
                                _resolve_commerce_destination(
                                    doc.website_id,
                                    destination_type,
                                    val,
                                )
                                if destination_type and val
                                else None
                            )

                        if f.get("type") in {
                            "product",
                            "repeatable",
                            "repeater",
                            "draggable",
                            "commerce_links",
                            "categories",
                        } and not isinstance(val, list):
                            val = []

                        # unwrap nested 'value' objects
                        val = normalize_repeaters(val)

                        if f.get("type") == "commerce_links" and key:
                            resolved_destinations = _resolve_commerce_destinations(
                                doc.website_id,
                                val,
                            )
                            context[f"{key}_links"] = resolved_destinations
                            context[f"{key}_url"] = (
                                resolved_destinations[0].get("url")
                                if resolved_destinations
                                else None
                            )
                            target_url_field = f.get("target_url_field")
                            if target_url_field and resolved_destinations:
                                destination_url_overrides[target_url_field] = (
                                    resolved_destinations[0].get("url")
                                )

                        # Product fields store selected Product document IDs in
                        # their value. Jinja needs the complete product records,
                        # not those numeric IDs, to render image/name/price/etc.
                        if key == "product_list" and isinstance(val, list):
                            val = resolve_products(val)
                            if preview_only and not val:
                                val = _builder_preview_products()
                            val = add_product_styles(
                                val,
                                block.get("product_styles") or {},
                                block.get("product_settings") or {},
                            )

                        if key == "grid_num":
                            try:
                                val = max(1, min(4, int(val)))
                            except (TypeError, ValueError):
                                val = 3

                        # handle nested repeater value (like sections)
                        if f.get("type") == "repeater" and isinstance(val, list):
                            context[key] = []
                            for repeater_item in val:
                                if not isinstance(repeater_item, dict):
                                    continue
                                item_ctx = {}
                                # If it has nested fields (like links)
                                for sub_field in _builder_dict_items(f.get("fields")):
                                    sub_key = sub_field.get("name")
                                    sub_val = repeater_item.get(sub_key)
                                    # recursively normalize nested repeater inside repeater
                                    item_ctx[sub_key] = normalize_repeaters(sub_val)
                                if item_ctx.get("destination_type") and item_ctx.get("destination"):
                                    destination_type = item_ctx.get("destination_type")
                                    destination_id = item_ctx.get("destination")
                                    item_ctx["destination_url"] = (
                                        _product_category_destination(
                                            doc.website_id,
                                            destination_id,
                                        )
                                        if key == "image_list" and destination_type == "product"
                                        else None
                                    ) or _resolve_commerce_destination(
                                        doc.website_id,
                                        destination_type,
                                        destination_id,
                                    )
                                item_ctx = _resolve_nested_commerce_destinations(
                                    doc.website_id,
                                    item_ctx,
                                    prefer_product_category=(key == "image_list"),
                                )
                                context[key].append(item_ctx)
                        else:
                            context[key] = val

                        # special cases for script and style
                        if key == "script" and val:
                            scripts.append(val)
                        if key == "style" and val:
                            styles.append(_builder_apply_theme_tokens(val))

                    for target_url_field, internal_url in destination_url_overrides.items():
                        context[target_url_field] = internal_url

                    if block_name == "Navbar 2":
                        menu_category_ids = context.get("menu_categories") or []
                        context["store_categories"] = _get_storefront_category_tree(
                            doc.website_id,
                            menu_category_ids,
                        )
                        context["storefront_all_products_url"] = (
                            _storefront_all_products_url(
                                doc.website_id,
                                menu_category_ids,
                            )
                        )

                    # Merge direct keys from model
                    for k, v in model.items():
                        if k not in context:
                            value = normalize_repeaters(v)
                            if k == "product_list" and isinstance(value, list):
                                value = resolve_products(value)
                                value = add_product_styles(
                                    value,
                                    block.get("product_styles") or {},
                                    block.get("product_settings") or {},
                                )
                            context[k] = value

                    # 🔥 Ensure Jinja context naming matches template expectations
                    # e.g. footer_sections = sections for convenience
                    if "sections" in context:
                        context["footer_sections"] = context["sections"]

                    # Optional style targets inside a block, such as the
                    # Product Card's Add to Cart button.
                    element_styles = block.get("element_styles") or {}
                    if isinstance(element_styles, dict):
                        for element_key, element_style in element_styles.items():
                            style_class, style_attribute = get_block_style_attributes(
                                element_style
                            )
                            context[f"{element_key}_style_class"] = style_class
                            context[f"{element_key}_style_attribute"] = style_attribute


                    # Collect block-level script/style from Block Doc itself
                    if getattr(block_doc, "script", None):
                        scripts.append(block_doc.script)
                    if getattr(block_doc, "style", None):
                        styles.append(_builder_apply_theme_tokens(block_doc.style))

                    # Render block HTML
                    block_tpl = Template(block_html)
                    rendered_block = _builder_apply_theme_tokens(
                        block_tpl.render(**context)
                    )
                    html += apply_block_style(
                        rendered_block,
                        block.get("block_style") or {},
                    ) + "\n"


                except frappe.DoesNotExistError:
                    frappe.log_error(f"Builder Block {block_name} not found")

            return html, scripts, styles

        # --- Render each section ---
        header_html, header_scripts, header_styles = render_blocks("header")
        main_html, main_scripts, main_styles = render_blocks("main")
        footer_html, footer_scripts, footer_styles = render_blocks("footer")

        def unique_list(lst):
            seen = set()
            result = []
            for i in lst:
                if i not in seen:
                    seen.add(i)
                    result.append(i)
            return result

        all_scripts = "\n".join(unique_list(header_scripts + main_scripts + footer_scripts))
        runtime_grid_styles = r"""
@media (min-width: 768px) {
  .md\:grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
  .md\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .md\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}

.ecommerce-custom-background {
  background: var(--ecommerce-block-background) !important;
}
.ecommerce-custom-background > :first-child,
.ecommerce-custom-background > :first-child > :first-child {
  background: var(--ecommerce-block-background) !important;
  background-image: none !important;
}
.ecommerce-product-style.ecommerce-custom-background {
  background: transparent !important;
  background-image: none !important;
}
.ecommerce-product-style.ecommerce-custom-background > :first-child > :first-child {
  background: transparent !important;
  background-image: none !important;
}
.ecommerce-product-style.ecommerce-custom-background > :first-child {
  overflow: hidden !important;
  border-radius: 1rem !important;
}
.ecommerce-custom-text,
.ecommerce-custom-text * {
  color: var(--ecommerce-block-text) !important;
}
.ecommerce-custom-font-size,
.ecommerce-custom-font-size * {
  font-size: var(--ecommerce-block-font-size) !important;
}
.ecommerce-custom-margin > :first-child,
.ecommerce-custom-margin > :first-child > :first-child {
  margin: 0 !important;
}
.ecommerce-custom-padding > :first-child,
.ecommerce-custom-padding > :first-child > :first-child {
  padding: 0 !important;
}
"""
        all_styles = "\n".join(
            unique_list(
                header_styles
                + main_styles
                + footer_styles
                + [runtime_grid_styles]
            )
        )

        # --- Get Page Template ---
        template_name = getattr(doc, "template", None)
        if not template_name:
            return {"status": "error", "message": "No template linked to this page"}

        try:
            template_doc = frappe.get_doc("Ecommerce Template", template_name)
            template_html = template_doc.template or ""
        except frappe.DoesNotExistError:
            return {"status": "error", "message": f"Template {template_name} not found"}

        # --- Render Page Template ---
        page_tpl = Template(template_html)

        # Safe field_value (remove block sections)
        safe_field_value = dict(render_field_value)
        for section in ["header", "main", "footer"]:
            safe_field_value.pop(section, None)

        page_html = page_tpl.render(
            **safe_field_value,
            header=header_html,
            main=main_html,
            footer=footer_html,
            blockscript=all_scripts,
            blockstyle=all_styles,
            doc=doc
        )
        website_theme = frappe.db.get_value(
            "Ecommerce Vendor Website",
            doc.website_id,
            [
                "font",
                "primary_color",
                "secondary_color",
                "additional_color1",
                "additional_color2",
            ],
            as_dict=True,
        ) or {}
        page_html = _apply_builder_head_metadata(
            page_html,
            safe_field_value,
            getattr(doc, "page", ""),
            website_theme.get("font"),
            website_theme,
        )
        page_html = _disable_empty_builder_links(page_html)
        page_html = _open_product_links_in_new_tab(page_html)
        page_html = _inject_storefront_cart_runtime(page_html, doc.website_id)

        if preview_only:
            return {
                "status": "success",
                "message": _("Page preview rendered successfully."),
                "data": {
                    "name": doc.name,
                    "block_render": page_html,
                    "preview": _build_builder_preview_document(
                        _rewrite_storefront_links_for_preview(
                            page_html, doc.website_id
                        )
                    ),
                    "preview_url": f"/dashboard/store/{doc.website_id}/page/{doc.name}?preview=1",
                    "field_value": field_value,
                },
            }

        # --- Save final output ---
        doc.block_render = page_html
        doc.save(ignore_permissions=True)
        if _commit:
            frappe.db.commit()

        return {
            "status": "success",
            "message": "Page updated & published successfully",
            "data": {
                "name": doc.name,
                "block_render": doc.block_render,
                "field_value": doc.field_value
            }
        }

    except Exception as e:
        frappe.log_error(title="Update Publish Data Error", message=frappe.get_traceback())
        return {"status": "error", "message": str(e)}





def _builder_media_url(value):
    """Return an existing local or HTTP(S) media URL, if ``value`` is one."""
    if not isinstance(value, str):
        return None

    value = value.strip()
    if value.startswith(("/files/", "/private/files/", "/assets/")):
        return value

    parsed = urlsplit(value)
    if parsed.scheme.lower() in {"http", "https"} and parsed.netloc:
        return value
    return None


def _save_builder_image(data_url, doctype, document_name, fieldname, suffix):
    """Save a base64 image and attach it to a builder document."""
    if not data_url:
        return None

    existing_url = _builder_media_url(data_url)
    if existing_url:
        return existing_url

    if not isinstance(data_url, str) or not data_url.startswith("data:image/"):
        frappe.throw(_("Invalid image data for {0}").format(fieldname))

    try:
        header, encoded_content = data_url.split(",", 1)
        image_type = header.split("/", 1)[1].split(";", 1)[0].lower()
        extension_map = {
            "jpeg": "jpg",
            "jpg": "jpg",
            "png": "png",
            "gif": "gif",
            "webp": "webp",
        }
        extension = extension_map.get(image_type)
        if not extension:
            frappe.throw(_("Unsupported image type for {0}").format(fieldname))

        content = base64.b64decode(encoded_content, validate=True)
        max_size = int(frappe.local.conf.get("max_file_size", 5 * 1024 * 1024))
        if len(content) > max_size:
            frappe.throw(_("The image for {0} is too large").format(fieldname))

        from frappe.utils.file_manager import save_file

        saved_file = save_file(
            f"{document_name}-{suffix}.{extension}",
            content,
            doctype,
            document_name,
            is_private=0,
            df=fieldname,
        )
        return saved_file.file_url
    except (ValueError, TypeError, binascii.Error):
        frappe.throw(_("Unable to decode the image for {0}").format(fieldname))


def _save_builder_video(data_url, doctype, document_name, fieldname, suffix):
    """Save a supported base64 video and attach it to a builder document."""
    if not data_url:
        return None
    existing_url = _builder_media_url(data_url)
    if existing_url:
        return existing_url
    if not isinstance(data_url, str) or not data_url.startswith("data:video/"):
        frappe.throw(_("Invalid video data for {0}").format(fieldname))

    try:
        header, encoded_content = data_url.split(",", 1)
        video_type = header.split("/", 1)[1].split(";", 1)[0].lower()
        extension_map = {
            "mp4": "mp4",
            "webm": "webm",
            "ogg": "ogv",
            "quicktime": "mov",
            "x-m4v": "m4v",
        }
        extension = extension_map.get(video_type)
        if not extension:
            frappe.throw(_("Unsupported video type for {0}").format(fieldname))

        content = base64.b64decode(encoded_content, validate=True)
        max_size = int(frappe.local.conf.get("max_file_size", 5 * 1024 * 1024))
        if len(content) > max_size:
            frappe.throw(_("The video for {0} is too large").format(fieldname))

        from frappe.utils.file_manager import save_file

        saved_file = save_file(
            f"{document_name}-{suffix}.{extension}",
            content,
            doctype,
            document_name,
            is_private=0,
            df=fieldname,
        )
        return saved_file.file_url
    except (ValueError, TypeError, binascii.Error):
        frappe.throw(_("Unable to decode the video for {0}").format(fieldname))


def _assign_builder_variant_images(product, variant_values):
    """Link variant rows to their selected image after product media is saved."""
    raw_gallery_images = product.get("gallery_images")
    if isinstance(raw_gallery_images, str):
        try:
            raw_gallery_images = frappe.parse_json(raw_gallery_images) or []
        except (TypeError, ValueError):
            raw_gallery_images = []
    if not isinstance(raw_gallery_images, list):
        raw_gallery_images = []
    product_images = [product.get("product_image"), *raw_gallery_images]
    product_images = [image for image in product_images if image]

    for row, value in zip(product.get("variants") or [], variant_values or []):
        if not isinstance(value, dict):
            continue
        image_index = value.get("variant_image_index")
        try:
            image_index = int(image_index) if image_index is not None else None
        except (TypeError, ValueError):
            image_index = None
        if image_index is not None and 0 <= image_index < len(product_images):
            row.variant_image = product_images[image_index]
        else:
            variant_image = value.get("variant_image") or value.get("image")
            row.variant_image = (
                variant_image
                if isinstance(variant_image, str) and variant_image.startswith("/files/")
                else None
            )


def _get_builder_product_price(product):
    """Return a display price from a product or its first usable variant."""
    direct_price = product.get("price") if hasattr(product, "get") else None
    if direct_price not in (None, "", 0, 0.0, "0", "0.0"):
        return direct_price

    variants = _get_builder_product_variants(product)

    for variant in variants if isinstance(variants, list) else []:
        if not isinstance(variant, dict):
            continue
        discounted_price = variant.get("discounted_price")
        try:
            if discounted_price not in (None, "") and float(discounted_price) > 0:
                return discounted_price
        except (TypeError, ValueError):
            pass

        for price_field in ("selling_price", "cost_price"):
            price = variant.get(price_field)
            if price not in (None, ""):
                return price

    return 0


def _get_builder_product_variants(product):
    """Return structured variants, falling back to the legacy JSON field."""
    product_name = product.get("name") if hasattr(product, "get") else None
    if product_name and frappe.get_meta("Ecommerce Product").has_field("variants"):
        child_variants = frappe.get_all(
            "Ecommerce Product Variant",
            filters={"parent": product_name, "parentfield": "variants"},
            fields=[
                "variant_name", "discounted_price", "selling_price",
                "cost_price", "weight", "volume", "quantity", "sku", "variant_image",
            ],
            order_by="idx asc",
        )
        if child_variants:
            return [
                {
                    "name": row.variant_name,
                    "variant_name": row.variant_name,
                    "image": row.variant_image,
                    "variant_image": row.variant_image,
                    "discounted_price": row.discounted_price,
                    "selling_price": row.selling_price,
                    "cost_price": row.cost_price,
                    "weight": row.weight,
                    "volume": row.volume,
                    "volumne": row.volume,
                    "quantity": row.quantity,
                    "sku": row.sku,
                }
                for row in child_variants
            ]

    raw_variants = product.get("varient") if hasattr(product, "get") else None
    try:
        variants = frappe.parse_json(raw_variants) if raw_variants else []
    except (TypeError, ValueError):
        variants = []

    if isinstance(variants, dict):
        return [variants]
    return variants if isinstance(variants, list) else []


STOREFRONT_STATUSES = {"Published", "Hidden", "Archived"}


def _storefront_status(value):
    value = str(value or "Published").strip().title()
    return value if value in STOREFRONT_STATUSES else "Published"


@frappe.whitelist(allow_guest=False)
def update_storefront_item_status():
    """Update the lifecycle status of one vendor-owned catalogue item."""
    try:
        request_data = frappe.request.get_json(silent=True) or {}
        item_type = str(request_data.get("item_type") or "").strip().lower()
        item_name = request_data.get("name")
        publication_status = str(
            request_data.get("publication_status") or ""
        ).strip().title()

        doctype_by_type = {
            "product": "Ecommerce Product",
            "category": "Ecommerce Categories",
            "brand": "Ecommerce Brand",
        }
        doctype = doctype_by_type.get(item_type)
        if not doctype or not item_name:
            return {"status": "error", "message": _("Invalid storefront item")}
        if publication_status not in STOREFRONT_STATUSES:
            return {"status": "error", "message": _("Invalid publication status")}
        if not frappe.db.exists(doctype, item_name):
            return {"status": "error", "message": _("Storefront item not found")}

        doc = frappe.get_doc(doctype, item_name)
        vendor_info = get_vendor_id() or {}
        website_vendor = frappe.db.get_value(
            "Ecommerce Vendor Website", doc.website, "vendor_id"
        )
        if not website_vendor or str(website_vendor) != str(
            vendor_info.get("vendor_id")
        ):
            frappe.local.response.http_status_code = 403
            return {
                "status": "error",
                "message": _("You cannot edit this storefront item"),
            }

        doc.publication_status = publication_status
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
        _republish_website_pages(doc.website)

        return {
            "status": "success",
            "message": _("Storefront status updated successfully"),
            "data": {
                "name": doc.name,
                "publication_status": doc.publication_status,
            },
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Storefront Status Update Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def get_ecommerce_archive():
    """Return every archived ecommerce record owned by the current vendor."""
    try:
        vendor_info = get_vendor_id() or {}
        vendor_id = vendor_info.get("vendor_id")
        if not vendor_id:
            return {"status": "error", "message": _("Vendor not found"), "data": []}

        websites = frappe.get_all(
            "Ecommerce Vendor Website",
            filters={"vendor_id": vendor_id},
            fields=["name", "website_link", "status", "type", "modified"],
            order_by="modified desc",
        )
        website_ids = [row.name for row in websites]
        website_labels = {str(row.name): row.website_link for row in websites}
        archived = []

        for row in websites:
            if row.status == "Discarded":
                archived.append({
                    "type": "website",
                    "name": row.name,
                    "title": row.website_link or row.name,
                    "subtitle": row.type or _("Website"),
                    "modified": row.modified,
                    "image": None,
                })

        if website_ids:
            page_rows = frappe.get_all(
                "Ecommerce Page",
                filters={
                    "website_id": ["in", website_ids],
                    "page_status": "Archived",
                },
                fields=["name", "page", "website_id", "modified"],
                order_by="modified desc",
            )
            for row in page_rows:
                archived.append({
                    "type": "page",
                    "name": row.name,
                    "title": row.page or row.name,
                    "subtitle": website_labels.get(str(row.website_id), _("Website page")),
                    "modified": row.modified,
                    "image": None,
                })

            catalogue_specs = (
                ("product", "Ecommerce Product", "product_name", "product_image"),
                ("category", "Ecommerce Categories", "categories_name", "categories_logo"),
                ("brand", "Ecommerce Brand", "brand_name", "brand_logo"),
            )
            for item_type, doctype, title_field, image_field in catalogue_specs:
                rows = frappe.get_all(
                    doctype,
                    filters={
                        "website": ["in", website_ids],
                        "publication_status": "Archived",
                    },
                    fields=[
                        "name", title_field, image_field, "website", "modified"
                    ],
                    order_by="modified desc",
                )
                for row in rows:
                    archived.append({
                        "type": item_type,
                        "name": row.name,
                        "title": row.get(title_field) or row.name,
                        "subtitle": website_labels.get(str(row.website), _("ECommerce")),
                        "modified": row.modified,
                        "image": row.get(image_field),
                    })

        archived.sort(
            key=lambda row: str(row.get("modified") or ""), reverse=True
        )
        return {
            "status": "success",
            "message": _("Archive fetched successfully"),
            "data": archived,
        }
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "Fetch ECommerce Archive Failed")
        return {"status": "error", "message": str(exc), "data": []}


@frappe.whitelist(allow_guest=False)
def restore_ecommerce_archive_item():
    """Restore one archived record without making catalogue items public."""
    try:
        request_data = frappe.request.get_json(silent=True) or {}
        item_type = str(request_data.get("item_type") or "").strip().lower()
        item_name = request_data.get("name")
        if not item_name:
            return {"status": "error", "message": _("Archive item is required")}

        vendor_info = get_vendor_id() or {}
        vendor_id = vendor_info.get("vendor_id")
        if not vendor_id:
            return {"status": "error", "message": _("Vendor not found")}

        restored_status = ""
        website_id = None
        if item_type == "website":
            doc = frappe.get_doc("Ecommerce Vendor Website", item_name)
            if str(doc.vendor_id or "") != str(vendor_id):
                frappe.local.response.http_status_code = 403
                return {"status": "error", "message": _("You cannot restore this website")}
            doc.status = "Draft"
            doc.save(ignore_permissions=True)
            restored_status = "Draft"
            website_id = doc.name
        elif item_type == "page":
            page, error = _vendor_owned_builder_page(item_name)
            if error:
                return error
            page_names = list(
                dict.fromkeys(
                    _builder_page_ancestor_names(page) + _builder_page_tree_names(page)
                )
            )
            for page_name in page_names:
                frappe.db.set_value(
                    "Ecommerce Page",
                    page_name,
                    "page_status",
                    "Active",
                    update_modified=True,
                )
            restored_status = "Active"
            website_id = page.website_id
        else:
            doctype_by_type = {
                "product": "Ecommerce Product",
                "category": "Ecommerce Categories",
                "brand": "Ecommerce Brand",
            }
            doctype = doctype_by_type.get(item_type)
            if not doctype or not frappe.db.exists(doctype, item_name):
                return {"status": "error", "message": _("Archive item not found")}
            doc = frappe.get_doc(doctype, item_name)
            website_id = doc.website
            website_vendor = frappe.db.get_value(
                "Ecommerce Vendor Website", website_id, "vendor_id"
            )
            if str(website_vendor or "") != str(vendor_id):
                frappe.local.response.http_status_code = 403
                return {"status": "error", "message": _("You cannot restore this item")}
            doc.publication_status = "Hidden"
            doc.save(ignore_permissions=True)
            restored_status = "Hidden"

        if website_id:
            from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
            _republish_website_pages(website_id)
        frappe.db.commit()
        return {
            "status": "success",
            "message": _("Item restored successfully"),
            "data": {"name": item_name, "type": item_type, "status": restored_status},
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Restore ECommerce Archive Item Failed")
        return {"status": "error", "message": str(exc)}


def _category_is_storefront_visible(category):
    """A subcategory is public only while every ancestor is also published."""
    category_id = category.get("name") if hasattr(category, "get") else category
    visited = set()
    while category_id and category_id not in visited:
        visited.add(category_id)
        row = frappe.db.get_value(
            "Ecommerce Categories",
            category_id,
            ["parent_category", "publication_status"],
            as_dict=True,
        )
        if not row or _storefront_status(row.publication_status) != "Published":
            return False
        category_id = row.parent_category
    return not category_id


def _builder_product_categories(product, storefront_only=False):
    product_name = product.get("name") if hasattr(product, "get") else None
    category_ids = []
    if product_name and frappe.get_meta("Ecommerce Product").has_field("categories"):
        category_ids = frappe.get_all(
            "Ecommerce Product Category",
            filters={"parent": product_name, "parentfield": "categories"},
            pluck="category",
            order_by="idx asc",
        )
    legacy_category = product.get("catagories") if hasattr(product, "get") else None
    if legacy_category and legacy_category not in category_ids:
        category_ids.insert(0, legacy_category)

    categories = []
    for category_id in category_ids:
        row = frappe.db.get_value(
            "Ecommerce Categories",
            category_id,
            ["name", "categories_name", "slug", "categories_logo"],
            as_dict=True,
        )
        if row:
            if storefront_only:
                status = frappe.db.get_value(
                    "Ecommerce Categories", category_id, "publication_status"
                )
                if (
                    _storefront_status(status) != "Published"
                    or not _category_is_storefront_visible(category_id)
                ):
                    continue
            categories.append(row)
    return categories


def _builder_slug(value, fallback="item"):
    normalized = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return normalized or fallback


def _request_custom_storefront_base_url(custom_domain):
    """Return the current custom-domain origin when it owns this request."""
    from ecommerce.storefront_domains import storefront_custom_domain

    expected_host = storefront_custom_domain(custom_domain)
    request = getattr(frappe.local, "request", None)
    if not expected_host or not request:
        return None

    for value in (
        getattr(request, "host", None),
        frappe.get_request_header("X-Forwarded-Host"),
        frappe.get_request_header("X-Original-Host"),
    ):
        request_host = str(value or "").split(",", 1)[0].strip().split(":", 1)[0]
        request_host = request_host.lower().strip(".")
        if storefront_custom_domain(request_host) != expected_host:
            continue
        forwarded_scheme = str(
            frappe.get_request_header("X-Forwarded-Proto") or ""
        ).split(",", 1)[0].strip().lower()
        request_scheme = str(getattr(request, "scheme", "") or "").lower()
        scheme = forwarded_scheme if forwarded_scheme in {"http", "https"} else request_scheme
        if scheme not in {"http", "https"}:
            scheme = "https"
        return f"{scheme}://{request_host}"
    return None


def _storefront_public_base_url(website):
    website_row = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website,
        ["canonical_url", "custom_domain"],
        as_dict=True,
    ) or {}
    return (
        _request_custom_storefront_base_url(website_row.get("custom_domain"))
        or str(website_row.get("canonical_url") or "").rstrip("/")
        or None
    )


def _rewrite_storefront_links_for_custom_domain(rendered_html, website_id):
    """Keep links on the custom host while serving pre-rendered builder HTML."""
    html = str(rendered_html or "")
    if not html or not website_id:
        return html

    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["canonical_url", "custom_domain"],
        as_dict=True,
    ) or {}
    custom_base = _request_custom_storefront_base_url(website.get("custom_domain"))
    canonical_base = str(website.get("canonical_url") or "").rstrip("/")
    if not custom_base or not canonical_base or custom_base == canonical_base:
        return html
    return html.replace(canonical_base, custom_base)


def _storefront_url(website, entity_type, entity_slug):
    if not website or not entity_slug:
        return None
    raw_entity_slug = entity_slug
    public_url = _storefront_public_base_url(website)
    if public_url:
        public_url = str(public_url).rstrip("/")
        entity_type = _builder_slug(entity_type)
        entity_slug = _builder_slug(entity_slug)
        if entity_type == "page":
            home_page = frappe.db.get_value(
                "Ecommerce Page",
                {"website_id": website, "name": raw_entity_slug},
                "name",
            )
            if home_page:
                first_page = frappe.db.get_value(
                    "Ecommerce Page",
                    {"website_id": website},
                    "name",
                    order_by="creation asc",
                )
                if str(first_page) == str(home_page):
                    return public_url
        return f"{public_url}/{entity_type}/{entity_slug}"
    return "/dashboard/store/{}/{}/{}".format(
        website,
        _builder_slug(entity_type),
        _builder_slug(entity_slug),
    )


def _storefront_category_ids(value):
    if value in (None, ""):
        return None
    if isinstance(value, str):
        try:
            value = frappe.parse_json(value)
        except (TypeError, ValueError):
            value = value.split(",")
    if not isinstance(value, (list, tuple, set)):
        value = [value]
    return list(dict.fromkeys(str(item) for item in value if item not in (None, "")))


def _storefront_all_products_url(website_id, category_ids=None):
    url = _storefront_url(website_id, "category", "all-products")
    category_ids = _storefront_category_ids(category_ids)
    if category_ids:
        url += "?categories=" + quote_plus(json.dumps(category_ids, separators=(",", ":")))
    return url


def _product_category_destination(website_id, product_id):
    """Return the first assigned category page for a gallery-linked product."""
    category_id = frappe.db.get_value(
        "Ecommerce Product Category",
        {
            "parent": product_id,
            "parenttype": "Ecommerce Product",
            "parentfield": "categories",
        },
        "category",
        order_by="idx asc",
    )
    if not category_id:
        category_id = frappe.db.get_value(
            "Ecommerce Product",
            {"name": product_id, "website": website_id},
            "catagories",
        )
    if not category_id:
        return _storefront_url(website_id, "category", "all-products")
    category_slug = frappe.db.get_value(
        "Ecommerce Categories",
        {"name": category_id, "website": website_id},
        "slug",
    )
    return _storefront_url(website_id, "category", category_slug or category_id)


def _get_vendor_fixed_url(website_id):
    """Return the single fixed website target used by editable SEO keywords."""
    if not website_id:
        return "#"
    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["website_link", "canonical_url"],
        as_dict=True,
    )
    if not website:
        return "#"
    for value in (website.canonical_url, website.website_link):
        value = str(value or "").strip()
        if re.match(r"^https?://[^\s]+$", value, flags=re.IGNORECASE):
            return value
    home_page = frappe.db.get_value(
        "Ecommerce Page",
        {"website_id": website_id},
        "name",
        order_by="creation asc",
    )
    return _storefront_url(website_id, "page", home_page) if home_page else "#"


def _resolve_commerce_destination(website_id, entity_type, entity_id):
    entity_type = str(entity_type or "").strip().lower()
    mapping = {
        "brand": ("Ecommerce Brand", "slug"),
        "category": ("Ecommerce Categories", "slug"),
        "product": ("Ecommerce Product", "slug"),
    }
    if entity_type == "page":
        page_exists = frappe.db.exists(
            "Ecommerce Page", {"name": entity_id, "website_id": website_id}
        )
        return _storefront_url(website_id, "page", entity_id) if page_exists else None
    if entity_type not in mapping:
        return None
    doctype, slug_field = mapping[entity_type]
    if entity_type in {"brand", "category", "product"}:
        status = frappe.db.get_value(
            doctype, {"name": entity_id, "website": website_id}, "publication_status"
        )
        if _storefront_status(status) != "Published":
            return None
        if entity_type == "category" and not _category_is_storefront_visible(entity_id):
            return None
    value = frappe.db.get_value(
        doctype,
        {"name": entity_id, "website": website_id},
        slug_field,
    )
    return _storefront_url(website_id, entity_type, value) if value else None


def _resolve_commerce_destinations(
    website_id,
    destinations,
    prefer_product_category=False,
):
    """Resolve multiple image relationships with a predictable primary-link order."""
    if not isinstance(destinations, list):
        return []
    label_fields = {
        "brand": ("Ecommerce Brand", "brand_name"),
        "category": ("Ecommerce Categories", "categories_name"),
        "product": ("Ecommerce Product", "product_name"),
        "page": ("Ecommerce Page", "page"),
    }
    priority = {"product": 0, "category": 1, "brand": 2, "page": 3}
    resolved = []
    seen = set()
    for destination in destinations:
        if not isinstance(destination, dict):
            continue
        entity_type = str(destination.get("type") or "").strip().lower()
        entity_id = destination.get("value") or destination.get("id")
        key = (entity_type, str(entity_id))
        if entity_type not in label_fields or not entity_id or key in seen:
            continue
        url = None
        if prefer_product_category and entity_type == "product":
            url = _product_category_destination(website_id, entity_id)
        url = url or _resolve_commerce_destination(website_id, entity_type, entity_id)
        if not url:
            continue
        doctype, label_field = label_fields[entity_type]
        label = destination.get("label") or frappe.db.get_value(
            doctype, entity_id, label_field
        )
        resolved.append({
            "type": entity_type,
            "value": entity_id,
            "label": label or str(entity_id),
            "url": url,
        })
        seen.add(key)
    return sorted(resolved, key=lambda item: priority.get(item["type"], 99))


def _resolve_nested_commerce_destinations(
    website_id,
    value,
    prefer_product_category=False,
):
    """Resolve destination lists at any depth inside builder repeater values."""
    if isinstance(value, list):
        return [
            _resolve_nested_commerce_destinations(
                website_id,
                item,
                prefer_product_category=prefer_product_category,
            )
            for item in value
        ]
    if not isinstance(value, dict):
        return value

    resolved_value = {
        key: _resolve_nested_commerce_destinations(
            website_id,
            item,
            prefer_product_category=prefer_product_category,
        )
        for key, item in value.items()
    }
    destinations = value.get("destinations")
    if isinstance(destinations, list):
        resolved_destinations = _resolve_commerce_destinations(
            website_id,
            destinations,
            prefer_product_category=prefer_product_category,
        )
        resolved_value["destination_links"] = resolved_destinations
        if resolved_destinations:
            resolved_value["destination_url"] = resolved_destinations[0].get("url")
            if "url" in resolved_value:
                resolved_value["url"] = resolved_destinations[0].get("url")

    for key, destinations in value.items():
        if key == "destinations" or not key.endswith("_destinations"):
            continue
        if not isinstance(destinations, list):
            continue
        resolved_destinations = _resolve_commerce_destinations(
            website_id,
            destinations,
            prefer_product_category=prefer_product_category,
        )
        resolved_value[f"{key}_links"] = resolved_destinations
        if resolved_destinations:
            target_url_field = f"{key[:-len('_destinations')]}_url"
            resolved_value[target_url_field] = resolved_destinations[0].get("url")
    return resolved_value


def _serialize_builder_product(product, storefront_only=False):
    """Convert a Builder Product document into template/API-ready data."""
    product_name = product.get("name")
    brand = product.get("brand")
    category = product.get("catagories")
    categories = _builder_product_categories(product, storefront_only=storefront_only)
    variants = _get_builder_product_variants(product)
    product_slug = product.get("slug") or _builder_slug(product.get("product_name"), str(product_name))
    website = product.get("website")
    product_image = product.get("product_image")
    raw_gallery_images = product.get("gallery_images")
    if isinstance(raw_gallery_images, str):
        try:
            raw_gallery_images = frappe.parse_json(raw_gallery_images) or []
        except (TypeError, ValueError):
            raw_gallery_images = []
    if not isinstance(raw_gallery_images, list):
        raw_gallery_images = []
    product_images = []
    for image_url in [product_image, *raw_gallery_images]:
        image_url = str(image_url or "").strip()
        if image_url and image_url not in product_images:
            product_images.append(image_url)
    raw_product_videos = product.get("product_videos")
    if isinstance(raw_product_videos, str):
        try:
            raw_product_videos = frappe.parse_json(raw_product_videos) or []
        except (TypeError, ValueError):
            raw_product_videos = []
    if not isinstance(raw_product_videos, list):
        raw_product_videos = []
    product_videos = [
        str(video_url).strip()
        for video_url in raw_product_videos
        if str(video_url or "").strip()
    ]
    serialized_categories = [
        {
            "id": row.name,
            "name": row.name,
            "categories_name": row.categories_name,
            "slug": row.slug,
            "image": row.categories_logo,
            "url": _storefront_url(website, "category", row.slug or row.name),
        }
        for row in categories
    ]

    def optional_text(value):
        text = str(value or "").strip()
        return "" if text.lower() in {"none", "null", "undefined"} else text

    product_description = optional_text(product.get("product_description"))
    long_description = optional_text(product.get("long_description"))

    return {
        "type": "product",
        "id": product_name,
        "name": product_name,
        "product_name": product.get("product_name"),
        "slug": product_slug,
        "website": website,
        "home_url": _get_vendor_fixed_url(website),
        "url": _storefront_url(website, "product", product_slug),
        "product_description": product_description,
        "description": product_description,
        "long_description": long_description,
        "price": _get_builder_product_price(product),
        "product_image": product_image,
        "image": product_image,
        "images": product_images,
        "videos": product_videos,
        "product_videos": product_videos,
        "brand": brand,
        "brand_name": (
            frappe.db.get_value("Ecommerce Brand", brand, "brand_name")
            if brand
            else None
        ),
        "catagories": category,
        "category": category,
        "category_name": (
            frappe.db.get_value(
                "Ecommerce Categories", category, "categories_name"
            )
            if category
            else None
        ),
        "categories": serialized_categories,
        "category_ids": [row.name for row in categories],
        "enable": product.get("enable"),
        "continue_selling": product.get("continue_selling"),
        "publication_status": _storefront_status(product.get("publication_status")),
        "varient": variants,
        "variant": variants,
    }


def _resolve_builder_products(values):
    """Fetch selected Builder Product IDs and preserve their selected order."""
    if isinstance(values, str):
        try:
            values = frappe.parse_json(values)
        except (TypeError, ValueError):
            values = [values]

    if not isinstance(values, (list, tuple)):
        values = [values]

    products = []
    for selected_value in values:
        product_id = selected_value
        if isinstance(selected_value, dict):
            product_id = (
                selected_value.get("id")
                or selected_value.get("name")
                or selected_value.get("value")
            )

        if product_id in (None, ""):
            continue

        try:
            product = frappe.get_doc("Ecommerce Product", str(product_id))
            if _storefront_status(product.get("publication_status")) == "Published":
                products.append(_serialize_builder_product(product, storefront_only=True))
        except frappe.DoesNotExistError:
            frappe.log_error(
                f"Builder Product {product_id} not found",
                "Builder Product Resolution",
            )

    return products


@frappe.whitelist(allow_guest=False)
def add_brand():
    try:
        doc_data = frappe.local.form_dict.get("doc")
        if not doc_data:
            request_data = json.loads(frappe.request.data or "{}")
            doc_data = request_data.get("doc", request_data)

        if isinstance(doc_data, str):
            doc_data = json.loads(doc_data)

        if not isinstance(doc_data, dict):
            return {"status": "error", "message": _("Invalid brand data")}

        brand_name = (doc_data.get("brand_name") or doc_data.get("name") or "").strip()
        if not brand_name:
            return {"status": "error", "message": _("Brand Name is required")}

        brand = frappe.get_doc({
            "doctype": "Ecommerce Brand",
            "brand_name": brand_name,
            "slug": (doc_data.get("slug") or _builder_slug(brand_name)).strip(),
            "website": doc_data.get("website") or doc_data.get("website_id"),
            "publication_status": _storefront_status(
                doc_data.get("publication_status")
            ),
            "seo_title": doc_data.get("seo_title"),
            "seo_description": doc_data.get("seo_description"),
        })
        brand.insert(ignore_permissions=True)

        brand_logo = _save_builder_image(
            doc_data.get("brand_logo") or doc_data.get("logo"),
            "Ecommerce Brand",
            brand.name,
            "brand_logo",
            "brand-logo",
        )
        seo_logo = _save_builder_image(
            doc_data.get("seo_logo"),
            "Ecommerce Brand",
            brand.name,
            "seo_logo",
            "seo-logo",
        )

        if brand_logo:
            brand.brand_logo = brand_logo
        if seo_logo:
            brand.seo_logo = seo_logo
        if brand_logo or seo_logo:
            brand.save(ignore_permissions=True)

        frappe.db.commit()
        return {
            "status": "success",
            "message": _("Brand created successfully"),
            "data": {
                "name": brand.name,
                "brand_name": brand.brand_name,
                "slug": brand.slug,
                "website": brand.website,
                "publication_status": brand.publication_status,
                "brand_logo": brand.brand_logo,
                "seo_title": brand.seo_title,
                "seo_description": brand.seo_description,
                "seo_logo": brand.seo_logo,
            },
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Brand Creation Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def update_brand():
    """Update a vendor-owned storefront brand."""
    try:
        doc_data = frappe.local.form_dict.get("doc")
        if not doc_data:
            request_data = json.loads(frappe.request.data or "{}")
            doc_data = request_data.get("doc", request_data)
        if isinstance(doc_data, str):
            doc_data = json.loads(doc_data)
        if not isinstance(doc_data, dict):
            return {"status": "error", "message": _("Invalid brand data")}

        brand_id = doc_data.get("name") or doc_data.get("id")
        if not brand_id or not frappe.db.exists("Ecommerce Brand", brand_id):
            return {"status": "error", "message": _("Brand not found")}

        brand = frappe.get_doc("Ecommerce Brand", brand_id)
        vendor_info = get_vendor_id() or {}
        website_vendor = frappe.db.get_value(
            "Ecommerce Vendor Website", brand.website, "vendor_id"
        )
        if not website_vendor or str(website_vendor) != str(vendor_info.get("vendor_id")):
            frappe.local.response.http_status_code = 403
            return {"status": "error", "message": _("You cannot edit this brand")}

        brand_name = str(doc_data.get("brand_name") or "").strip()
        if not brand_name:
            return {"status": "error", "message": _("Brand Name is required")}

        brand.brand_name = brand_name
        brand.slug = str(doc_data.get("slug") or _builder_slug(brand_name)).strip()
        brand.seo_title = doc_data.get("seo_title") or None
        brand.seo_description = doc_data.get("seo_description") or None
        brand.publication_status = _storefront_status(
            doc_data.get("publication_status") or brand.publication_status
        )

        if doc_data.get("brand_logo"):
            brand.brand_logo = _save_builder_image(
                doc_data.get("brand_logo"),
                "Ecommerce Brand",
                brand.name,
                "brand_logo",
                "brand-logo",
            )
        if doc_data.get("seo_logo"):
            brand.seo_logo = _save_builder_image(
                doc_data.get("seo_logo"),
                "Ecommerce Brand",
                brand.name,
                "seo_logo",
                "seo-logo",
            )

        brand.save(ignore_permissions=True)
        frappe.db.commit()
        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
        _republish_website_pages(brand.website)
        return {
            "status": "success",
            "message": _("Brand updated successfully"),
            "data": {
                "name": brand.name,
                "brand_name": brand.brand_name,
                "slug": brand.slug,
                "website": brand.website,
                "publication_status": brand.publication_status,
                "brand_logo": brand.brand_logo,
                "seo_title": brand.seo_title,
                "seo_description": brand.seo_description,
                "seo_logo": brand.seo_logo,
            },
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Brand Update Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def get_brands(website_id=None):
    try:
        website_id = website_id or (frappe.local.form_dict or {}).get("website_id")
        filters = {"website": website_id} if website_id else {}
        filters["publication_status"] = ["!=", "Archived"]
        brands = frappe.get_all(
            "Ecommerce Brand",
            filters=filters,
            fields=[
                "name",
                "brand_name",
                "slug",
                "website",
                "publication_status",
                "brand_logo",
                "seo_title",
                "seo_description",
                "seo_logo",
                "creation",
                "modified",
            ],
            order_by="creation desc",
        )
        return {
            "status": "success",
            "message": _("Brands fetched successfully"),
            "data": brands,
        }
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "Fetch Brands Failed")
        return {"status": "error", "message": str(exc), "data": []}


@frappe.whitelist(allow_guest=False)
def add_category():
    try:
        doc_data = frappe.local.form_dict.get("doc")
        if not doc_data:
            request_data = json.loads(frappe.request.data or "{}")
            doc_data = request_data.get("doc", request_data)
        if isinstance(doc_data, str):
            doc_data = json.loads(doc_data)
        if not isinstance(doc_data, dict):
            return {"status": "error", "message": _("Invalid category data")}

        category_name = (
            doc_data.get("categories_name") or doc_data.get("name") or ""
        ).strip()
        if not category_name:
            return {"status": "error", "message": _("Category Name is required")}

        category = frappe.get_doc({
            "doctype": "Ecommerce Categories",
            "categories_name": category_name,
            "slug": (doc_data.get("slug") or _builder_slug(category_name)).strip(),
            "website": doc_data.get("website") or doc_data.get("website_id"),
            "parent_category": doc_data.get("parent_category") or None,
            "publication_status": _storefront_status(
                doc_data.get("publication_status")
            ),
        })
        _validate_category_parent(category)
        category.insert(ignore_permissions=True)

        category_logo = _save_builder_image(
            doc_data.get("categories_logo") or doc_data.get("icon"),
            "Ecommerce Categories",
            category.name,
            "categories_logo",
            "category-logo",
        )
        if category_logo:
            category.categories_logo = category_logo
            category.save(ignore_permissions=True)

        frappe.db.commit()
        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
        _republish_website_pages(category.website)
        return {
            "status": "success",
            "message": _("Category created successfully"),
            "data": {
                "name": category.name,
                "categories_name": category.categories_name,
                "categories_logo": category.categories_logo,
                "slug": category.slug,
                "website": category.website,
                "parent_category": category.parent_category,
                "publication_status": category.publication_status,
            },
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Category Creation Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def update_category():
    """Update a vendor-owned storefront category."""
    try:
        doc_data = frappe.local.form_dict.get("doc")
        if not doc_data:
            request_data = json.loads(frappe.request.data or "{}")
            doc_data = request_data.get("doc", request_data)
        if isinstance(doc_data, str):
            doc_data = json.loads(doc_data)
        if not isinstance(doc_data, dict):
            return {"status": "error", "message": _("Invalid category data")}

        category_id = doc_data.get("name") or doc_data.get("id")
        if not category_id or not frappe.db.exists("Ecommerce Categories", category_id):
            return {"status": "error", "message": _("Category not found")}

        category = frappe.get_doc("Ecommerce Categories", category_id)
        vendor_info = get_vendor_id() or {}
        website_vendor = frappe.db.get_value(
            "Ecommerce Vendor Website", category.website, "vendor_id"
        )
        if not website_vendor or str(website_vendor) != str(vendor_info.get("vendor_id")):
            frappe.local.response.http_status_code = 403
            return {"status": "error", "message": _("You cannot edit this category")}

        category_name = str(doc_data.get("categories_name") or "").strip()
        if not category_name:
            return {"status": "error", "message": _("Category Name is required")}

        category.categories_name = category_name
        category.slug = str(doc_data.get("slug") or _builder_slug(category_name)).strip()
        category.parent_category = doc_data.get("parent_category") or None
        category.publication_status = _storefront_status(
            doc_data.get("publication_status") or category.publication_status
        )
        _validate_category_parent(category)
        if doc_data.get("categories_logo"):
            category.categories_logo = _save_builder_image(
                doc_data.get("categories_logo"),
                "Ecommerce Categories",
                category.name,
                "categories_logo",
                "category-logo",
            )

        category.save(ignore_permissions=True)
        frappe.db.commit()
        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
        _republish_website_pages(category.website)
        return {
            "status": "success",
            "message": _("Category updated successfully"),
            "data": {
                "name": category.name,
                "categories_name": category.categories_name,
                "categories_logo": category.categories_logo,
                "slug": category.slug,
                "website": category.website,
                "parent_category": category.parent_category,
                "publication_status": category.publication_status,
            },
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Category Update Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def get_categories(website_id=None, include_archived=False):
    try:
        website_id = website_id or (frappe.local.form_dict or {}).get("website_id")
        filters = {"website": website_id} if website_id else {}
        include_archived = include_archived is True or str(include_archived).lower() in {
            "1", "true", "yes"
        }
        if not include_archived:
            filters["publication_status"] = ["!=", "Archived"]
        categories = frappe.get_all(
            "Ecommerce Categories",
            filters=filters,
            fields=[
                "name",
                "categories_name",
                "categories_logo",
                "slug",
                "website",
                "parent_category",
                "publication_status",
                "creation",
                "modified",
            ],
            order_by="creation desc",
        )
        category_names = {row.name: row.categories_name for row in categories}
        for row in categories:
            row["parent_category_name"] = category_names.get(row.parent_category)
        return {
            "status": "success",
            "message": _("Categories fetched successfully"),
            "data": categories,
        }
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "Fetch Categories Failed")
        return {"status": "error", "message": str(exc), "data": []}


def _validate_category_parent(category):
    """Keep category trees inside one website and prevent loops."""
    parent_name = category.get("parent_category")
    if not parent_name:
        return
    if parent_name == category.name:
        frappe.throw(_("A category cannot be its own parent."))

    parent = frappe.db.get_value(
        "Ecommerce Categories",
        parent_name,
        ["name", "website", "parent_category"],
        as_dict=True,
    )
    if not parent or str(parent.website) != str(category.website):
        frappe.throw(_("Parent category must belong to the same website."))

    visited = {category.name}
    current = parent
    while current:
        if current.name in visited:
            frappe.throw(_("This parent selection would create a category loop."))
        visited.add(current.name)
        if not current.parent_category:
            break
        current = frappe.db.get_value(
            "Ecommerce Categories",
            current.parent_category,
            ["name", "website", "parent_category"],
            as_dict=True,
        )


def _get_storefront_category_tree(website_id, selected_ids=None):
    rows = frappe.get_all(
        "Ecommerce Categories",
        filters={"website": website_id},
        fields=["name", "categories_name", "slug", "parent_category", "publication_status"],
        order_by="categories_name asc",
    )
    rows = [
        row for row in rows
        if _storefront_status(row.publication_status) == "Published"
        and _category_is_storefront_visible(row.name)
    ]
    items = {
        row.name: {
            "id": row.name,
            "title": row.categories_name,
            "slug": row.slug,
            "url": _storefront_url(website_id, "category", row.slug or row.name),
            "parent_category": row.parent_category,
            "publication_status": row.publication_status,
            "children": [],
        }
        for row in rows
    }
    roots = []
    for item in items.values():
        parent = items.get(item["parent_category"])
        if parent:
            parent["children"].append(item)
        else:
            roots.append(item)
    if selected_ids is not None:
        selected = {str(value) for value in selected_ids if value not in (None, "")}
        filtered_roots = []
        for root in roots:
            if str(root["id"]) in selected:
                filtered_roots.append(root)
                continue
            selected_children = [
                child for child in root["children"]
                if str(child["id"]) in selected
            ]
            if selected_children:
                filtered_roots.append({**root, "children": selected_children})
        roots = filtered_roots
    return roots


@frappe.whitelist(allow_guest=False)
def add_product():
    try:
        doc_json = frappe.local.form_dict.get("doc")
        if not doc_json:
            request_data = json.loads(frappe.request.data or "{}")
            doc_json = request_data.get("doc", request_data)

        if isinstance(doc_json, str):
            product_data = json.loads(doc_json)
        else:
            product_data = doc_json
        if not isinstance(product_data, dict):
            return {"status": "error", "message": _("Invalid product data")}

        product_name = (
            product_data.get("product_name") or product_data.get("name") or ""
        ).strip()
        if not product_name:
            return {"status": "error", "message": _("Product Name is required")}

        doc = frappe.get_doc({
            "doctype": "Ecommerce Product",
            "product_name": product_name,
            "slug": product_data.get("slug") or _builder_slug(product_name),
            "website": product_data.get("website") or product_data.get("website_id"),
            "brand": product_data.get("brand"),
            "catagories": product_data.get("catagories") or product_data.get("category"),
            "product_description": product_data.get("product_description")
                or product_data.get("description"),
            "long_description": product_data.get("long_description"),
            "enable": 1 if product_data.get("enable") else 0,
            "continue_selling": 1 if product_data.get("continue_selling") else 0,
            "publication_status": _storefront_status(
                product_data.get("publication_status")
            ),
            "varient": json.dumps(product_data.get("varient") or []),
        })
        category_values = product_data.get("categories") or [
            product_data.get("catagories") or product_data.get("category")
        ]
        for category_value in category_values:
            category_id = category_value.get("name") if isinstance(category_value, dict) else category_value
            if category_id:
                doc.append("categories", {"category": category_id})
        for variant in product_data.get("variants") or product_data.get("varient") or []:
            if not isinstance(variant, dict):
                continue
            doc.append("variants", {
                "variant_name": variant.get("variant_name") or variant.get("name"),
                "variant_image": variant.get("variant_image") or variant.get("image"),
                "discounted_price": variant.get("discounted_price"),
                "selling_price": variant.get("selling_price"),
                "cost_price": variant.get("cost_price"),
                "weight": variant.get("weight"),
                "volume": variant.get("volume") or variant.get("volumne"),
                "quantity": variant.get("quantity"),
                "sku": variant.get("sku"),
            })
        doc.insert(ignore_permissions=True)

        product_image = _save_builder_image(
            product_data.get("product_image") or product_data.get("image"),
            "Ecommerce Product",
            doc.name,
            "product_image",
            "product-image",
        )
        if product_image:
            doc.product_image = product_image

        gallery_images = []
        for index, gallery_image_data in enumerate(
            product_data.get("gallery_images") or [],
            start=1,
        ):
            gallery_image = _save_builder_image(
                gallery_image_data,
                "Ecommerce Product",
                doc.name,
                "product_image",
                f"gallery-{index}",
            )
            if gallery_image:
                gallery_images.append(gallery_image)
        if gallery_images:
            doc.gallery_images = json.dumps(gallery_images)

        _assign_builder_variant_images(
            doc,
            product_data.get("variants") or product_data.get("varient") or [],
        )

        product_videos = []
        for index, video_data in enumerate(
            product_data.get("product_videos") or [],
            start=1,
        ):
            product_video = _save_builder_video(
                video_data,
                "Ecommerce Product",
                doc.name,
                "product_videos",
                f"product-video-{index}",
            )
            if product_video:
                product_videos.append(product_video)
        if product_videos:
            doc.product_videos = json.dumps(product_videos)

        if product_image or gallery_images or product_videos:
            doc.save(ignore_permissions=True)

        frappe.db.commit()
        return {
            "status": "success",
            "message": _("Product created successfully"),
            "data": {
                "name": doc.name,
                "product_name": doc.product_name,
                "slug": doc.slug,
                "website": doc.website,
                "product_image": doc.product_image,
                "gallery_images": gallery_images,
                "product_videos": product_videos,
                "brand": doc.brand,
                "catagories": doc.catagories,
                "product_description": doc.product_description,
                "long_description": doc.long_description,
                "enable": doc.enable,
                "continue_selling": doc.continue_selling,
                "publication_status": doc.publication_status,
                "varient": doc.varient,
            },
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Product Creation Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def update_product():
    """Update a Builder Product, replacing its categories and variant inventory."""
    try:
        doc_json = frappe.local.form_dict.get("doc")
        if not doc_json:
            request_data = json.loads(frappe.request.data or "{}")
            doc_json = request_data.get("doc", request_data)
        product_data = json.loads(doc_json) if isinstance(doc_json, str) else doc_json
        if not isinstance(product_data, dict):
            return {"status": "error", "message": _("Invalid product data")}

        product_id = product_data.get("name") or product_data.get("id")
        if not product_id or not frappe.db.exists("Ecommerce Product", product_id):
            return {"status": "error", "message": _("Product not found")}

        doc = frappe.get_doc("Ecommerce Product", product_id)
        vendor_info = get_vendor_id() or {}
        website_vendor = frappe.db.get_value(
            "Ecommerce Vendor Website",
            doc.website,
            "vendor_id",
        )
        if not website_vendor or str(website_vendor) != str(vendor_info.get("vendor_id")):
            frappe.local.response.http_status_code = 403
            return {"status": "error", "message": _("You cannot edit this product")}
        product_name = str(product_data.get("product_name") or "").strip()
        if not product_name:
            return {"status": "error", "message": _("Product Name is required")}

        old_name = doc.product_name
        target_website = product_data.get("website") or product_data.get("website_id") or doc.website
        target_vendor = frappe.db.get_value(
            "Ecommerce Vendor Website",
            target_website,
            "vendor_id",
        )
        if str(target_vendor or "") != str(vendor_info.get("vendor_id") or ""):
            frappe.local.response.http_status_code = 403
            return {"status": "error", "message": _("You cannot move this product to that website")}

        doc.product_name = product_name
        doc.website = target_website
        doc.brand = product_data.get("brand") or None
        doc.product_description = product_data.get("product_description") or None
        doc.long_description = product_data.get("long_description") or None
        doc.enable = 1 if product_data.get("enable") else 0
        doc.continue_selling = 1 if product_data.get("continue_selling") else 0
        doc.publication_status = _storefront_status(
            product_data.get("publication_status") or doc.publication_status
        )
        if product_name != old_name and not product_data.get("slug"):
            doc.slug = None
        elif product_data.get("slug"):
            doc.slug = product_data.get("slug")

        doc.set("categories", [])
        category_values = product_data.get("categories") or []
        if not category_values and product_data.get("catagories"):
            category_values = [product_data.get("catagories")]
        category_ids = []
        for category_value in category_values:
            category_id = (
                category_value.get("name") or category_value.get("id")
                if isinstance(category_value, dict)
                else category_value
            )
            if category_id:
                doc.append("categories", {"category": category_id})
                category_ids.append(category_id)
        doc.catagories = category_ids[0] if category_ids else None

        doc.set("variants", [])
        variants = product_data.get("variants") or product_data.get("varient") or []
        doc.varient = json.dumps(variants)
        for variant in variants:
            if not isinstance(variant, dict):
                continue
            doc.append("variants", {
                "variant_name": variant.get("variant_name") or variant.get("name"),
                "variant_image": variant.get("variant_image") or variant.get("image"),
                "discounted_price": variant.get("discounted_price"),
                "selling_price": variant.get("selling_price"),
                "cost_price": variant.get("cost_price"),
                "weight": variant.get("weight"),
                "volume": variant.get("volume") or variant.get("volumne"),
                "quantity": variant.get("quantity"),
                "sku": variant.get("sku"),
            })

        product_image_data = product_data.get("product_image")
        gallery_image_data = product_data.get("gallery_images")
        product_video_data = product_data.get("product_videos")
        if product_image_data:
            product_image = _save_builder_image(
                product_image_data,
                "Ecommerce Product",
                doc.name,
                "product_image",
                "product-image",
            )
            if product_image:
                doc.product_image = product_image
        if isinstance(gallery_image_data, list):
            gallery_images = []
            for index, image_data in enumerate(gallery_image_data, start=1):
                gallery_image = _save_builder_image(
                    image_data,
                    "Ecommerce Product",
                    doc.name,
                    "product_image",
                    f"gallery-{index}",
                )
                if gallery_image:
                    gallery_images.append(gallery_image)
            doc.gallery_images = json.dumps(gallery_images)
        if isinstance(product_video_data, list):
            product_videos = []
            for index, video_data in enumerate(product_video_data, start=1):
                product_video = _save_builder_video(
                    video_data,
                    "Ecommerce Product",
                    doc.name,
                    "product_videos",
                    f"product-video-{index}",
                )
                if product_video:
                    product_videos.append(product_video)
            doc.product_videos = json.dumps(product_videos)

        _assign_builder_variant_images(doc, variants)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
        _republish_website_pages(doc.website)

        return {
            "status": "success",
            "message": _("Product updated successfully"),
            "data": _serialize_builder_product(doc),
        }
    except Exception as exc:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Product Update Failed")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist(allow_guest=False)
def get_products(
    product_ids=None,
    website_id=None,
    brand=None,
    category=None,
    storefront_only=False,
    include_archived=False,
):
    try:
        storefront_only = storefront_only is True or str(storefront_only).lower() in {
            "1", "true", "yes"
        }
        include_archived = include_archived is True or str(include_archived).lower() in {
            "1", "true", "yes"
        }
        product_ids = product_ids or (frappe.local.form_dict or {}).get("product_ids")
        if product_ids:
            products = _resolve_builder_products(product_ids)
            return {
                "status": "success",
                "message": _("Products fetched successfully"),
                "data": products,
            }

        form_dict = frappe.local.form_dict or {}
        website_id = website_id or form_dict.get("website_id")
        brand = brand or form_dict.get("brand")
        category = category or form_dict.get("category")
        filters = {}
        if website_id:
            filters["website"] = website_id
        if brand:
            filters["brand"] = brand
        if storefront_only:
            filters["publication_status"] = "Published"
        elif not include_archived:
            filters["publication_status"] = ["!=", "Archived"]
        products = frappe.get_all(
            "Ecommerce Product",
            filters=filters,
            fields=[
                "name",
                "product_name",
                "slug",
                "website",
                "product_description",
                "long_description",
                "brand",
                "catagories",
                "product_image",
                "gallery_images",
                "product_videos",
                "enable",
                "continue_selling",
                "publication_status",
                "varient",
                "creation",
                "modified",
            ],
            order_by="creation desc",
        )
        products = [
            _serialize_builder_product(product, storefront_only=storefront_only)
            for product in products
        ]
        if category:
            products = [
                product for product in products
                if str(category) in {str(value) for value in product.get("category_ids") or []}
            ]

        return {
            "status": "success",
            "message": _("Products fetched successfully"),
            "data": products,
        }

    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "Fetch Products Failed")
        return {"status": "error", "message": str(exc), "data": []}


@frappe.whitelist(allow_guest=False)
def get_commerce_link_options(website_id=None):
    """Return all valid Image Gallery destinations for the selected website."""
    website_id = website_id or (frappe.local.form_dict or {}).get("website_id")
    filters = {"website": website_id} if website_id else {}
    brands = frappe.get_all(
        "Ecommerce Brand",
        filters={**filters, "publication_status": "Published"},
        fields=["name", "brand_name", "slug", "website", "publication_status"],
        order_by="brand_name asc",
    )
    categories = frappe.get_all(
        "Ecommerce Categories",
        filters={**filters, "publication_status": "Published"},
        fields=["name", "categories_name", "slug", "website", "publication_status"],
        order_by="categories_name asc",
    )
    categories = [
        row for row in categories if _category_is_storefront_visible(row.name)
    ]
    products = get_products(
        website_id=website_id, storefront_only=True
    ).get("data") or []
    page_filters = {"page_status": ["!=", "Archived"]}
    if website_id:
        page_filters["website_id"] = website_id
    pages = frappe.get_all(
        "Ecommerce Page", filters=page_filters,
        fields=["name", "page", "website_id"], order_by="page asc",
    )
    return {
        "status": "success",
        "data": {
            "brand": [{"value": row.name, "label": row.brand_name, "url": _storefront_url(row.website, "brand", row.slug or row.name)} for row in brands],
            "category": [{"value": row.name, "label": row.categories_name, "url": _storefront_url(row.website, "category", row.slug or row.name)} for row in categories],
            "product": [{"value": row["name"], "label": row["product_name"], "url": row.get("url")} for row in products],
            "page": [{"value": row.name, "label": row.page, "url": _storefront_url(row.website_id, "page", row.name)} for row in pages],
        },
    }


@frappe.whitelist(allow_guest=True)
def get_storefront_entity(
    website_id=None,
    entity_type=None,
    slug=None,
    category_ids=None,
):
    """Public data source for brand, category and product storefront pages."""
    form_dict = frappe.local.form_dict or {}
    website_id = website_id or form_dict.get("website_id")
    entity_type = (entity_type or form_dict.get("entity_type") or "").lower()
    slug = slug or form_dict.get("slug")
    category_ids = _storefront_category_ids(
        category_ids if category_ids is not None else form_dict.get("category_ids")
    )
    if not website_id or entity_type not in {"brand", "category", "product"} or not slug:
        return {"status": "error", "message": _("Invalid storefront destination")}

    mapping = {
        "brand": ("Ecommerce Brand", "brand_name"),
        "category": ("Ecommerce Categories", "categories_name"),
        "product": ("Ecommerce Product", "product_name"),
    }
    if entity_type == "category" and slug == "all-products":
        products = get_products(
            website_id=website_id, storefront_only=True
        ).get("data") or []
        if category_ids:
            valid_categories = frappe.get_all(
                "Ecommerce Categories",
                filters={"website": website_id},
                fields=["name", "parent_category", "publication_status"],
            )
            valid_by_id = {
                str(row.name): row for row in valid_categories
                if _storefront_status(row.publication_status) == "Published"
                and _category_is_storefront_visible(row.name)
            }
            allowed_ids = {
                category_id for category_id in category_ids
                if category_id in valid_by_id
            }
            changed = True
            while changed:
                changed = False
                for category_id, row in valid_by_id.items():
                    if (
                        str(row.parent_category or "") in allowed_ids
                        and category_id not in allowed_ids
                    ):
                        allowed_ids.add(category_id)
                        changed = True
            products = [
                product for product in products
                if allowed_ids.intersection(
                    str(value) for value in product.get("category_ids") or []
                )
            ]
        return {
            "status": "success",
            "data": {
                "entity": {
                    "id": "all-products",
                    "type": "category",
                    "title": _("All Products"),
                    "slug": "all-products",
                    "image": None,
                },
                "products": products,
            },
        }
    doctype, title_field = mapping[entity_type]
    entity = frappe.db.get_value(
        doctype, {"website": website_id, "slug": slug}, "*", as_dict=True
    )
    if not entity:
        return {"status": "error", "message": _("Storefront item not found")}
    if entity_type in {"brand", "category", "product"} and _storefront_status(
        entity.get("publication_status")
    ) != "Published":
        return {"status": "error", "message": _("Storefront item not found")}
    if entity_type == "category" and not _category_is_storefront_visible(entity):
        return {"status": "error", "message": _("Storefront item not found")}

    if entity_type == "product":
        product = _serialize_builder_product(entity, storefront_only=True)
        return {"status": "success", "data": {"entity": product, "products": [product]}}

    product_filters = {"website_id": website_id}
    product_filters[entity_type] = entity.name
    products = get_products(
        **product_filters, storefront_only=True
    ).get("data") or []
    if entity_type == "category":
        child_ids = frappe.get_all(
            "Ecommerce Categories",
            filters={
                "website": website_id,
                "parent_category": entity.name,
                "publication_status": "Published",
            },
            pluck="name",
        )
        if child_ids:
            all_products = get_products(
                website_id=website_id, storefront_only=True
            ).get("data") or []
            allowed_ids = {str(entity.name), *(str(value) for value in child_ids)}
            products = [
                product for product in all_products
                if allowed_ids.intersection(
                    str(value) for value in product.get("category_ids") or []
                )
            ]
    return {
        "status": "success",
        "data": {
            "entity": {
                "id": entity.name,
                "type": entity_type,
                "title": entity.get(title_field),
                "slug": entity.slug,
                "image": entity.get("brand_logo") or entity.get("categories_logo"),
                "publication_status": _storefront_status(
                    entity.get("publication_status")
                ) if entity_type in {"brand", "category"} else None,
            },
            "products": products,
        },
    }


def _storefront_request_value(value, default=None):
    if value in (None, ""):
        return default
    if isinstance(value, str):
        try:
            return frappe.parse_json(value)
        except (TypeError, ValueError):
            return value
    return value


def _storefront_money(value):
    try:
        return Decimal(str(value or 0))
    except (TypeError, ValueError, ArithmeticError):
        return Decimal("0")


def _storefront_variant_price(variant):
    discounted = _storefront_money(variant.get("discounted_price"))
    if discounted > 0:
        return discounted
    selling = _storefront_money(variant.get("selling_price"))
    if selling > 0:
        return selling
    return _storefront_money(variant.get("cost_price"))


def _storefront_error(message, status_code=400):
    frappe.local.response.http_status_code = status_code
    return {"status": "error", "message": _(message)}


@frappe.whitelist(allow_guest=True)
def get_storefront_checkout_options(website_id=None):
    """Return public delivery destinations for an ecommerce storefront."""
    website_id = website_id or (frappe.local.form_dict or {}).get("website_id")
    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["name", "type", "status"],
        as_dict=True,
    )
    if not website or website.type != "Ecommerce" or website.status == "Discarded":
        return _storefront_error("Storefront not found.", 404)

    return {
        "status": "success",
        "data": {
            "branches": [
                {
                    "value": "standard",
                    "label": _("Standard delivery"),
                    "city": "",
                    "district": "",
                    "municipality": "",
                    "areas": [],
                }
            ]
        },
    }


@frappe.whitelist(allow_guest=True)
def get_storefront_delivery_quote(website_id=None, destination_branch=None, city_area=None, address=None, items=None):
    """Return the same server-calculated delivery charge used at order creation."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)

    request_data = frappe.request.get_json(silent=True) or {}
    website_id = website_id or request_data.get("website_id")
    destination_branch = str(
        destination_branch or request_data.get("destination_branch") or ""
    ).strip()
    city_area = str(city_area or request_data.get("city_area") or "").strip()
    address = str(address or request_data.get("address") or "").strip()
    items = _storefront_request_value(items or request_data.get("items"), [])

    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["name", "vendor_id", "type", "status"],
        as_dict=True,
    )
    if not website or website.type != "Ecommerce" or website.status == "Discarded":
        return _storefront_error("Storefront not found.", 404)
    if not website.vendor_id:
        return _storefront_error("This storefront is not connected to a vendor.")
    destination_branch = destination_branch or "standard"
    if not isinstance(items, list) or not items or len(items) > 50:
        return _storefront_error("Your cart is empty or contains too many products.")

    package_weight = Decimal("0")
    package_quantity = 0
    try:
        for requested_item in items:
            if not isinstance(requested_item, dict):
                raise ValueError(_("Invalid cart product."))
            product_id = str(requested_item.get("product_id") or "").strip()
            quantity = int(requested_item.get("quantity") or 0)
            if not product_id or quantity < 1 or quantity > 999:
                raise ValueError(_("Invalid product quantity."))

            product = frappe.db.get_value(
                "Ecommerce Product",
                {"name": product_id, "website": website.name},
                ["name", "enable"],
                as_dict=True,
            )
            if not product:
                raise ValueError(_("A product in your cart is no longer available."))

            if product.enable:
                requested_variant = requested_item.get("variant") or {}
                variant_name = str(
                    requested_variant.get("variant_name")
                    or requested_variant.get("name")
                    or requested_item.get("variant_name")
                    or ""
                ).strip()
                variant = frappe.db.get_value(
                    "Ecommerce Product Variant",
                    {
                        "parent": product.name,
                        "parenttype": "Ecommerce Product",
                        "parentfield": "variants",
                        "variant_name": variant_name,
                    },
                    ["weight"],
                    as_dict=True,
                )
                if not variant:
                    raise ValueError(_("A selected product variant is unavailable."))
                package_weight += _storefront_money(variant.weight) * quantity
            package_quantity += quantity

        # Delivery pricing is intentionally local to this app. A future carrier
        # adapter can replace this default without requiring another app.
        delivery_amount = Decimal("0")
        return {
            "status": "success",
            "data": {
                "delivery_amount": float(delivery_amount),
                "pickup_branch": "",
                "destination_branch": destination_branch,
                "package_weight": float(package_weight),
                "package_qty": package_quantity,
            },
        }
    except (TypeError, ValueError) as error:
        return _storefront_error(str(error))


@frappe.whitelist(allow_guest=True)
def place_storefront_order(website_id=None, customer=None, items=None):
    """Create a server-validated COD order from a public storefront checkout."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)

    request_data = frappe.request.get_json(silent=True) or {}
    website_id = website_id or request_data.get("website_id")
    customer = _storefront_request_value(customer or request_data.get("customer"), {})
    items = _storefront_request_value(items or request_data.get("items"), [])
    if not isinstance(customer, dict) or not isinstance(items, list):
        return _storefront_error("Invalid checkout information.")

    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["name", "vendor_id", "type", "status"],
        as_dict=True,
    )
    if not website or website.type != "Ecommerce" or website.status == "Discarded":
        return _storefront_error("Storefront not found.", 404)
    if not website.vendor_id:
        return _storefront_error("This storefront is not connected to a vendor.")

    customer_name = str(customer.get("name") or "").strip()
    phone = re.sub(r"\D", "", str(customer.get("phone") or ""))
    address = str(customer.get("address") or "").strip()
    city_area = str(customer.get("city_area") or "").strip()
    delivery_location = address
    destination_branch = str(customer.get("destination_branch") or "").strip()
    instruction = str(customer.get("instruction") or "").strip()
    if not customer_name:
        return _storefront_error("Full name is required.")
    if len(phone) != 10:
        return _storefront_error("Enter a valid 10-digit phone number.")
    if not address:
        return _storefront_error("Delivery address is required.")
    if not city_area:
        return _storefront_error("City or area is required.")
    destination_branch = destination_branch or "standard"
    if not items or len(items) > 50:
        return _storefront_error("Your cart is empty or contains too many products.")

    order_lines = []
    subtotal = Decimal("0")
    package_weight = Decimal("0")
    package_quantity = 0

    try:
        for requested_item in items:
            if not isinstance(requested_item, dict):
                raise ValueError(_("Invalid cart product."))
            product_id = str(requested_item.get("product_id") or "").strip()
            quantity = int(requested_item.get("quantity") or 0)
            if not product_id or quantity < 1 or quantity > 999:
                raise ValueError(_("Invalid product quantity."))

            product = frappe.db.get_value(
                "Ecommerce Product",
                {"name": product_id, "website": website.name},
                ["name", "product_name", "continue_selling", "enable"],
                as_dict=True,
            )
            if not product:
                raise ValueError(_("A product in your cart is no longer available."))

            requested_variant = requested_item.get("variant") or {}
            variant_name = str(
                requested_variant.get("variant_name")
                or requested_variant.get("name")
                or requested_item.get("variant_name")
                or ""
            ).strip()
            variant = None
            if product.enable:
                if not variant_name:
                    raise ValueError(_("Select a variant for {0}.").format(product.product_name))
                rows = frappe.db.sql(
                    """
                    SELECT name, variant_name, discounted_price, selling_price,
                           cost_price, quantity, weight, sku
                    FROM `tabEcommerce Product Variant`
                    WHERE parent = %s AND parenttype = 'Ecommerce Product'
                          AND parentfield = 'variants' AND variant_name = %s
                    LIMIT 1 FOR UPDATE
                    """,
                    (product.name, variant_name),
                    as_dict=True,
                )
                variant = rows[0] if rows else None
                if not variant:
                    raise ValueError(_("The selected variant for {0} is unavailable.").format(product.product_name))
                available = _storefront_money(variant.quantity)
                if available < quantity and not product.continue_selling:
                    raise ValueError(_("Only {0} units of {1} are available.").format(
                        max(0, available), product.product_name
                    ))
                price = _storefront_variant_price(variant)
                package_weight += _storefront_money(variant.weight) * quantity
            else:
                price = _storefront_money(_get_builder_product_price(product))

            if price <= 0:
                raise ValueError(_("{0} does not have a valid selling price.").format(product.product_name))

            line_total = price * quantity
            subtotal += line_total
            package_quantity += quantity
            order_lines.append({
                "product_id": product.name,
                "product": product.product_name,
                "variant": variant_name,
                "variant_id": variant.get("name") if variant else "",
                "sku": variant.get("sku") if variant else "",
                "quantity": quantity,
                "unit_price": float(price),
                "line_total": float(line_total),
                "weight": float(_storefront_money(variant.get("weight"))) if variant else 0,
            })

        delivery_amount = Decimal("0")
        grand_total = subtotal + delivery_amount
        ecommerce_order = frappe.get_doc({
            "doctype": "Ecommerce Ecommerce Order",
            "website": website.name,
            "vendor_id": website.vendor_id,
            "customer_name": customer_name,
            "phone": phone,
            "city_area": city_area,
            "delivery_address": address,
            "destination_branch": destination_branch,
            "pickup_branch": "",
            "order_note": instruction,
            "subtotal": float(subtotal),
            "delivery_amount": float(delivery_amount),
            "grand_total": float(grand_total),
            "package_weight": float(package_weight),
            "package_qty": package_quantity,
            "payment_method": "Cash on Delivery",
            "status": "Pending",
        })
        for line in order_lines:
            ecommerce_order.append("items", {
                "product_id": line["product_id"],
                "product_name": line["product"],
                "variant_name": line["variant"],
                "variant_id": line["variant_id"],
                "sku": line["sku"],
                "quantity": line["quantity"],
                "unit_price": line["unit_price"],
                "line_total": line["line_total"],
                "weight": line["weight"],
            })
        ecommerce_order.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": _("Order received and waiting for the store to pack it."),
            "data": {
                "order_id": ecommerce_order.name,
                "status": ecommerce_order.status,
                "subtotal": float(subtotal),
                "delivery_amount": float(delivery_amount),
                "total": float(grand_total),
                "payment_method": "Cash on Delivery",
            },
        }
    except (ValueError, TypeError) as exc:
        frappe.db.rollback()
        return _storefront_error(str(exc))
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Storefront COD Order Failed")
        return _storefront_error("Unable to place your order. Please try again.", 500)


def _ecommerce_vendor_id():
    if frappe.session.user == "Guest":
        return None
    result = get_vendor_id() or {}
    return result.get("vendor_id") if result.get("status") == "success" else None


def _analytics_change(current, previous):
    current = float(current or 0)
    previous = float(previous or 0)
    if not previous:
        value = 0 if not current else 100
    else:
        value = ((current - previous) / previous) * 100
    return f"{value:+.2f}%" if value else "0.00%"


def _normalize_tawk_widget_id(value):
    widget_id = str(value or "").strip()
    if not widget_id:
        return ""
    embedded_path = re.search(
        r"https?://(?:embed\.tawk\.to|tawk\.to/chat)/([A-Za-z0-9_-]{4,100}/[A-Za-z0-9_-]{1,100})",
        widget_id,
        flags=re.IGNORECASE,
    )
    if embedded_path:
        widget_id = embedded_path.group(1)
    else:
        widget_id = widget_id.strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_-]{4,100}/[A-Za-z0-9_-]{1,100}", widget_id):
        raise ValueError(
            _("Paste the Tawk.to Widget Code, Direct Chat Link, embed URL, or property-id/widget-id.")
        )
    return widget_id


@frappe.whitelist(allow_guest=False)
def get_ecommerce_plugin_settings(website_id=None):
    """Return ecommerce websites and the selected website's plugin settings."""
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)
    websites = frappe.get_all(
        "Ecommerce Vendor Website",
        filters={
            "vendor_id": vendor_id,
            "type": "Ecommerce",
            "status": ["!=", "Discarded"],
        },
        fields=["name", "website_link", "status", "tawk_widget_id"],
        order_by="modified desc",
    )
    requested_id = str(
        website_id or (frappe.local.form_dict or {}).get("website_id") or ""
    ).strip()
    selected = next(
        (row for row in websites if str(row.name) == requested_id),
        websites[0] if websites else None,
    )
    return {
        "status": "success",
        "data": {
            "websites": websites,
            "selected_website": str(selected.name) if selected else "",
            "tawk_widget_id": selected.tawk_widget_id if selected else "",
        },
    }


@frappe.whitelist(allow_guest=False)
def set_ecommerce_tawk_widget(website_id=None, widget_id=None):
    """Add or remove the Tawk.to widget for one vendor ecommerce website."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)
    request_data = frappe.request.get_json(silent=True) or {}
    website_id = str(website_id or request_data.get("website_id") or "").strip()
    widget_id = widget_id if widget_id is not None else request_data.get("widget_id")
    if not website_id or not frappe.db.exists(
        "Ecommerce Vendor Website",
        {"name": website_id, "vendor_id": vendor_id, "type": "Ecommerce"},
    ):
        return _storefront_error("Ecommerce website not found.", 404)
    try:
        normalized_widget_id = _normalize_tawk_widget_id(widget_id)
    except ValueError as error:
        return _storefront_error(str(error))
    frappe.db.set_value(
        "Ecommerce Vendor Website",
        website_id,
        "tawk_widget_id",
        normalized_widget_id,
        update_modified=True,
    )
    frappe.db.commit()
    return {
        "status": "success",
        "message": _("Tawk.to widget added.") if normalized_widget_id else _("Tawk.to widget removed."),
        "data": {
            "website_id": website_id,
            "tawk_widget_id": normalized_widget_id,
        },
    }


@frappe.whitelist(allow_guest=True)
def track_storefront_visit(website_id=None, visitor_id=None, path=None, source=None):
    """Record one anonymous visitor per storefront per day and count page views."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)

    request_data = frappe.request.get_json(silent=True) or {}
    website_id = website_id or request_data.get("website_id")
    visitor_id = str(visitor_id or request_data.get("visitor_id") or "").strip()[:200]
    path = str(path or request_data.get("path") or "").strip()[:140]
    source = str(source or request_data.get("source") or "Direct").strip()[:140] or "Direct"
    if not visitor_id:
        return _storefront_error("Anonymous visitor ID is required.")

    website = frappe.db.get_value(
        "Ecommerce Vendor Website",
        website_id,
        ["name", "vendor_id", "type", "status"],
        as_dict=True,
    )
    if not website or website.type != "Ecommerce" or website.status != "Published":
        return _storefront_error("Storefront not found.", 404)

    visit_date = nowdate()
    visitor_hash = hashlib.sha256(
        f"{website.name}:{visitor_id}".encode("utf-8")
    ).hexdigest()
    visit_key = hashlib.sha256(
        f"{website.name}:{visitor_hash}:{visit_date}".encode("utf-8")
    ).hexdigest()
    product_view = int("/product/" in path)
    cart_view = int(path.rstrip("/").endswith("/cart"))
    checkout_view = int(path.rstrip("/").endswith("/checkout"))

    if frappe.db.exists("Ecommerce Storefront Visit", visit_key):
        frappe.db.sql(
            """
            UPDATE `tabEcommerce Storefront Visit`
               SET page_views = page_views + 1,
                   product_views = product_views + %s,
                   cart_views = cart_views + %s,
                   checkout_views = checkout_views + %s,
                   source = COALESCE(NULLIF(source, ''), %s),
                   last_path = %s,
                   modified = %s
             WHERE name = %s
            """,
            (product_view, cart_view, checkout_view, source, path, now_datetime(), visit_key),
        )
    else:
        try:
            frappe.get_doc({
                "doctype": "Ecommerce Storefront Visit",
                "visit_key": visit_key,
                "website": website.name,
                "vendor_id": website.vendor_id,
                "visitor_hash": visitor_hash,
                "visit_date": visit_date,
                "page_views": 1,
                "product_views": product_view,
                "cart_views": cart_view,
                "checkout_views": checkout_view,
                "source": source,
                "last_path": path,
            }).insert(ignore_permissions=True)
        except frappe.DuplicateEntryError:
            frappe.db.sql(
                """
                UPDATE `tabEcommerce Storefront Visit`
                   SET page_views = page_views + 1,
                       product_views = product_views + %s,
                       cart_views = cart_views + %s,
                       checkout_views = checkout_views + %s,
                       source = COALESCE(NULLIF(source, ''), %s),
                       last_path = %s,
                       modified = %s
                 WHERE name = %s
                """,
                (product_view, cart_view, checkout_view, source, path, now_datetime(), visit_key),
            )
    frappe.db.commit()
    return {"status": "success"}


@frappe.whitelist(allow_guest=False)
def get_ecommerce_analytics(website_id=None):
    """Return live storefront analytics for the signed-in vendor."""
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)

    website_id = str(
        website_id or (frappe.local.form_dict or {}).get("website_id") or ""
    ).strip()
    if website_id and not frappe.db.exists(
        "Ecommerce Vendor Website",
        {"name": website_id, "vendor_id": vendor_id, "type": "Ecommerce"},
    ):
        return _storefront_error("Ecommerce website not found.", 404)

    order_where = ["o.vendor_id = %s"]
    order_values = [vendor_id]
    visit_where = ["v.vendor_id = %s"]
    visit_values = [vendor_id]
    if website_id:
        order_where.append("o.website = %s")
        order_values.append(website_id)
        visit_where.append("v.website = %s")
        visit_values.append(website_id)
    order_clause = " AND ".join(order_where)
    visit_clause = " AND ".join(visit_where)

    today = getdate(nowdate())
    week_start = add_days(today, -today.weekday())
    previous_week_start = add_days(week_start, -7)
    next_week_start = add_days(week_start, 7)

    totals = frappe.db.sql(
        f"""
        SELECT COUNT(*) AS total_orders,
               COALESCE(SUM(CASE WHEN o.status = 'Confirmed' THEN o.grand_total ELSE 0 END), 0) AS total_sales,
               SUM(CASE WHEN o.creation >= %s AND o.creation < %s THEN 1 ELSE 0 END) AS current_orders,
               SUM(CASE WHEN o.creation >= %s AND o.creation < %s THEN 1 ELSE 0 END) AS previous_orders,
               COALESCE(SUM(CASE WHEN o.status = 'Confirmed' AND o.creation >= %s AND o.creation < %s THEN o.grand_total ELSE 0 END), 0) AS current_sales,
               COALESCE(SUM(CASE WHEN o.status = 'Confirmed' AND o.creation >= %s AND o.creation < %s THEN o.grand_total ELSE 0 END), 0) AS previous_sales
          FROM `tabEcommerce Ecommerce Order` o
         WHERE {order_clause}
        """,
        [
            week_start, next_week_start,
            previous_week_start, week_start,
            week_start, next_week_start,
            previous_week_start, week_start,
        ] + order_values,
        as_dict=True,
    )[0]

    visitors = frappe.db.sql(
        f"""
        SELECT COUNT(DISTINCT v.visitor_hash) AS total_visitors,
               COUNT(DISTINCT CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.visitor_hash END) AS current_visitors,
               COUNT(DISTINCT CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.visitor_hash END) AS previous_visitors,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.page_views ELSE 0 END), 0) AS current_page_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.page_views ELSE 0 END), 0) AS previous_page_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.product_views ELSE 0 END), 0) AS current_product_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.product_views ELSE 0 END), 0) AS previous_product_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.cart_views ELSE 0 END), 0) AS current_cart_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.cart_views ELSE 0 END), 0) AS previous_cart_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.checkout_views ELSE 0 END), 0) AS current_checkout_views,
               COALESCE(SUM(CASE WHEN v.visit_date >= %s AND v.visit_date < %s THEN v.checkout_views ELSE 0 END), 0) AS previous_checkout_views
          FROM `tabEcommerce Storefront Visit` v
         WHERE {visit_clause}
        """,
        [
            week_start, next_week_start, previous_week_start, week_start,
            week_start, next_week_start, previous_week_start, week_start,
            week_start, next_week_start, previous_week_start, week_start,
            week_start, next_week_start, previous_week_start, week_start,
            week_start, next_week_start, previous_week_start, week_start,
        ] + visit_values,
        as_dict=True,
    )[0]

    chart_start = add_days(today, -7)
    daily_rows = frappe.db.sql(
        f"""
        SELECT DATE(o.creation) AS order_date,
               COALESCE(SUM(CASE WHEN o.status = 'Confirmed' THEN o.grand_total ELSE 0 END), 0) AS revenue,
               COUNT(*) AS orders
          FROM `tabEcommerce Ecommerce Order` o
         WHERE {order_clause} AND o.creation >= %s
         GROUP BY DATE(o.creation)
        """,
        order_values + [chart_start],
        as_dict=True,
    )
    daily_map = {str(row.order_date): row for row in daily_rows}
    revenue_points = []
    for offset in range(8):
        date_value = add_days(chart_start, offset)
        row = daily_map.get(str(date_value))
        revenue_points.append({
            "date": date_value.strftime("%d %b"),
            "revenue": float(row.revenue if row else 0),
            "order": int(row.orders if row else 0),
        })

    month_start = today.replace(day=1)
    monthly_revenue = frappe.db.sql(
        f"""
        SELECT COALESCE(SUM(o.grand_total), 0)
          FROM `tabEcommerce Ecommerce Order` o
         WHERE {order_clause} AND o.status = 'Confirmed' AND o.creation >= %s
        """,
        order_values + [month_start],
    )[0][0]
    target_filters = {
        "vendor_id": vendor_id,
        "type": "Ecommerce",
        "status": ["!=", "Discarded"],
    }
    if website_id:
        target_filters["name"] = website_id
    monthly_target = sum(
        float(value or 0)
        for value in frappe.get_all(
            "Ecommerce Vendor Website",
            filters=target_filters,
            pluck="monthly_sales_target",
        )
    )
    target_percentage = (
        round((float(monthly_revenue or 0) / monthly_target) * 100, 2)
        if monthly_target > 0 else 0
    )
    if not monthly_target:
        target_status = "No target configured"
        target_message = "Select a website and set its monthly sales target."
    elif target_percentage >= 100:
        target_status = "Target achieved"
        target_message = "Confirmed storefront revenue has reached this month's goal."
    else:
        target_status = "In progress"
        target_message = f"NPR {max(monthly_target - float(monthly_revenue or 0), 0):,.2f} remaining this month."

    category_rows = frappe.db.sql(
        f"""
        SELECT COALESCE(NULLIF(c.categories_name, ''), NULLIF(p.catagories, ''), 'Uncategorized') AS category,
               COALESCE(SUM(i.line_total), 0) AS sales
          FROM `tabEcommerce Ecommerce Order` o
          JOIN `tabEcommerce Ecommerce Order Item` i ON i.parent = o.name
          LEFT JOIN `tabEcommerce Product` p ON p.name = i.product_id
          LEFT JOIN `tabEcommerce Categories` c ON c.name = p.catagories
         WHERE {order_clause} AND o.status = 'Confirmed'
         GROUP BY COALESCE(NULLIF(c.categories_name, ''), NULLIF(p.catagories, ''), 'Uncategorized')
         ORDER BY sales DESC
         LIMIT 4
        """,
        order_values,
        as_dict=True,
    )

    recent_rows = frappe.db.sql(
        f"""
        SELECT o.name, o.customer_name, o.grand_total, o.status, o.creation,
               COALESCE(SUM(i.quantity), 0) AS quantity,
               GROUP_CONCAT(i.product_name ORDER BY i.idx SEPARATOR ', ') AS products
          FROM `tabEcommerce Ecommerce Order` o
          LEFT JOIN `tabEcommerce Ecommerce Order Item` i ON i.parent = o.name
         WHERE {order_clause}
         GROUP BY o.name
         ORDER BY o.creation DESC
         LIMIT 20
        """,
        order_values,
        as_dict=True,
    )
    recent_orders = [
        {
            "no": index,
            "orderId": row.name,
            "customer": row.customer_name,
            "product": row.products or "—",
            "qty": int(row.quantity or 0),
            "total": float(row.grand_total or 0),
            "status": row.status,
        }
        for index, row in enumerate(recent_rows, start=1)
    ]
    recent_activity = [
        {
            "timestamp": get_datetime(row.creation).strftime("%d %b, %I:%M %p"),
            "message": f"{row.customer_name}'s order {row.name} is {str(row.status).lower()} (NPR {float(row.grand_total or 0):,.2f}).",
        }
        for row in recent_rows[:8]
    ]

    location_rows = frappe.db.sql(
        f"""
        SELECT COALESCE(NULLIF(o.city_area, ''), 'Unknown') AS location,
               COUNT(*) AS orders
          FROM `tabEcommerce Ecommerce Order` o
         WHERE {order_clause} AND o.status != 'Cancelled'
         GROUP BY COALESCE(NULLIF(o.city_area, ''), 'Unknown')
         ORDER BY orders DESC
         LIMIT 6
        """,
        order_values,
        as_dict=True,
    )
    location_total = sum(int(row.orders or 0) for row in location_rows)
    locations = [
        {
            "name": row.location,
            "percentage": round((int(row.orders or 0) / location_total) * 100, 1)
            if location_total else 0,
        }
        for row in location_rows
    ]

    source_rows = frappe.db.sql(
        f"""
        SELECT COALESCE(NULLIF(v.source, ''), 'Direct') AS source,
               COUNT(DISTINCT v.visitor_hash) AS visitors
          FROM `tabEcommerce Storefront Visit` v
         WHERE {visit_clause}
         GROUP BY COALESCE(NULLIF(v.source, ''), 'Direct')
         ORDER BY visitors DESC
         LIMIT 5
        """,
        visit_values,
        as_dict=True,
    )
    source_total = sum(int(row.visitors or 0) for row in source_rows)
    traffic_sources = [
        {
            "name": row.source,
            "percentage": round((int(row.visitors or 0) / source_total) * 100, 1)
            if source_total else 0,
        }
        for row in source_rows
    ]

    websites = frappe.get_all(
        "Ecommerce Vendor Website",
        filters={"vendor_id": vendor_id, "type": "Ecommerce", "status": ["!=", "Discarded"]},
        fields=["name", "website_link", "status"],
        order_by="modified desc",
    )
    return {
        "status": "success",
        "data": {
            "websites": websites,
            "selectedWebsite": website_id,
            "summary": {
                "totalSales": {
                    "value": float(totals.total_sales or 0),
                    "change": _analytics_change(totals.current_sales, totals.previous_sales),
                    "comparisonText": "vs last week",
                },
                "totalOrders": {
                    "value": int(totals.total_orders or 0),
                    "change": _analytics_change(totals.current_orders, totals.previous_orders),
                    "comparisonText": "vs last week",
                },
                "totalVisitors": {
                    "value": int(visitors.total_visitors or 0),
                    "change": _analytics_change(visitors.current_visitors, visitors.previous_visitors),
                    "comparisonText": "vs last week",
                },
            },
            "revenueAnalytics": {"period": "Last 8 Days", "dataPoints": revenue_points},
            "monthlyTarget": {
                "percentage": target_percentage,
                "status": target_status,
                "message": target_message,
                "target": monthly_target,
                "revenue": float(monthly_revenue or 0),
                "canEdit": bool(website_id),
            },
            "topCategories": {
                "categories": [
                    {"name": row.category, "value": float(row.sales or 0)}
                    for row in category_rows
                ]
            },
            "activeUser": {
                "total": int(visitors.current_visitors or 0),
                "change": _analytics_change(visitors.current_visitors, visitors.previous_visitors),
                "comparisonText": "vs last week",
                "countries": locations,
            },
            "conversionRate": {
                "period": "This Week",
                "metrics": [
                    {"name": "Storefront Views", "value": int(visitors.current_page_views or 0), "change": _analytics_change(visitors.current_page_views, visitors.previous_page_views)},
                    {"name": "Product Views", "value": int(visitors.current_product_views or 0), "change": _analytics_change(visitors.current_product_views, visitors.previous_product_views)},
                    {"name": "Cart Visits", "value": int(visitors.current_cart_views or 0), "change": _analytics_change(visitors.current_cart_views, visitors.previous_cart_views)},
                    {"name": "Checkout Visits", "value": int(visitors.current_checkout_views or 0), "change": _analytics_change(visitors.current_checkout_views, visitors.previous_checkout_views)},
                    {"name": "Orders Placed", "value": int(totals.current_orders or 0), "change": _analytics_change(totals.current_orders, totals.previous_orders)},
                ],
            },
            "trafficSources": {"sources": traffic_sources},
            "recentOrders": recent_orders,
            "recentActivity": recent_activity,
        },
    }


@frappe.whitelist(allow_guest=False)
def set_ecommerce_monthly_target(website_id=None, target=None):
    """Set the monthly confirmed-sales target for one vendor ecommerce website."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)

    request_data = frappe.request.get_json(silent=True) or {}
    website_id = str(website_id or request_data.get("website_id") or "").strip()
    target = target if target is not None else request_data.get("target")
    if not website_id or not frappe.db.exists(
        "Ecommerce Vendor Website",
        {"name": website_id, "vendor_id": vendor_id, "type": "Ecommerce"},
    ):
        return _storefront_error("Ecommerce website not found.", 404)
    try:
        target_value = Decimal(str(target or 0))
    except (ArithmeticError, TypeError, ValueError):
        return _storefront_error("Enter a valid monthly sales target.")
    if target_value < 0:
        return _storefront_error("Monthly sales target cannot be negative.")

    frappe.db.set_value(
        "Ecommerce Vendor Website",
        website_id,
        "monthly_sales_target",
        float(target_value),
        update_modified=True,
    )
    frappe.db.commit()
    return {
        "status": "success",
        "message": _("Monthly sales target updated."),
        "data": {"website_id": website_id, "target": float(target_value)},
    }


def _serialize_ecommerce_order(order):
    return {
        "name": order.name,
        "website": order.website,
        "status": order.status,
        "system_order": order.system_order or "",
        "customer_name": order.customer_name,
        "phone": order.phone,
        "city_area": order.city_area,
        "delivery_address": order.delivery_address,
        "destination_branch": order.destination_branch,
        "order_note": order.order_note or "",
        "subtotal": float(order.subtotal or 0),
        "delivery_amount": float(order.delivery_amount or 0),
        "grand_total": float(order.grand_total or 0),
        "payment_method": order.payment_method,
        "creation": str(order.creation),
        "packed_at": str(order.packed_at) if order.packed_at else "",
        "confirmed_at": str(order.confirmed_at) if order.confirmed_at else "",
        "items": [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "variant_name": row.variant_name or "",
                "sku": row.sku or "",
                "quantity": int(row.quantity or 0),
                "unit_price": float(row.unit_price or 0),
                "line_total": float(row.line_total or 0),
            }
            for row in order.items
        ],
    }


CONFIRMABLE_ECOMMERCE_ORDER_STATUSES = frozenset({"Pending", "Packed"})
CANCELLABLE_ECOMMERCE_ORDER_STATUSES = frozenset({"Pending", "Packed"})


def _can_confirm_ecommerce_order(status):
    return str(status or "") in CONFIRMABLE_ECOMMERCE_ORDER_STATUSES


def _can_cancel_ecommerce_order(status):
    return str(status or "") in CANCELLABLE_ECOMMERCE_ORDER_STATUSES


@frappe.whitelist()
def get_ecommerce_orders(status=None, search=None, page=1, page_length=25):
    """Return one searchable, paginated page of the signed-in vendor's orders."""
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)

    allowed_statuses = ("Pending", "Packed", "Confirmed", "Cancelled")
    status = str(status or "All").strip().title()
    if status not in ("All", *allowed_statuses):
        return _storefront_error("Invalid ecommerce order status.")

    search = str(search or "").strip()[:100]
    try:
        page = max(int(page or 1), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        page_length = min(max(int(page_length or 25), 10), 100)
    except (TypeError, ValueError):
        page_length = 25

    search_filters = None
    if search:
        search_term = f"%{search}%"
        search_filters = {
            "name": ["like", search_term],
            "customer_name": ["like", search_term],
            "phone": ["like", search_term],
            "system_order": ["like", search_term],
            "destination_branch": ["like", search_term],
        }

    def order_count(order_status=None):
        count_filters = {"vendor_id": vendor_id}
        if order_status:
            count_filters["status"] = order_status
        rows = frappe.get_all(
            "Ecommerce Ecommerce Order",
            filters=count_filters,
            or_filters=search_filters,
            fields=["count(name) as total"],
            limit_page_length=1,
        )
        return int(rows[0].total or 0) if rows else 0

    status_counts = {order_status: order_count(order_status) for order_status in allowed_statuses}
    status_counts["All"] = sum(status_counts.values())
    total = status_counts[status]
    total_pages = max((total + page_length - 1) // page_length, 1)
    page = min(page, total_pages)

    filters = {"vendor_id": vendor_id}
    if status != "All":
        filters["status"] = status
    names = frappe.get_all(
        "Ecommerce Ecommerce Order",
        filters=filters,
        or_filters=search_filters,
        pluck="name",
        order_by="creation desc",
        start=(page - 1) * page_length,
        page_length=page_length,
    )
    return {
        "status": "success",
        "data": [_serialize_ecommerce_order(frappe.get_doc("Ecommerce Ecommerce Order", name)) for name in names],
        "status_counts": status_counts,
        "pagination": {
            "page": page,
            "page_length": page_length,
            "total": total,
            "pages": total_pages,
        },
    }


@frappe.whitelist()
def update_ecommerce_order_status(order_id=None, status=None):
    """Cancel a pending or legacy packed order before confirmation."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)
    try:
        locked = frappe.db.sql(
            "SELECT name FROM `tabEcommerce Ecommerce Order` WHERE name = %s FOR UPDATE",
            order_id,
            as_dict=True,
        )
        if not locked:
            return _storefront_error("Ecommerce order not found.", 404)
        order = frappe.get_doc("Ecommerce Ecommerce Order", order_id)
        if order.vendor_id != vendor_id:
            return _storefront_error("Ecommerce order not found.", 404)
        target = str(status or "").strip()
        if target != "Cancelled" or not _can_cancel_ecommerce_order(order.status):
            return _storefront_error(
                f"Cannot change an order from {order.status} to {target}."
            )
        order.status = target
        order.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "status": "success",
            "message": _("Order updated."),
            "data": _serialize_ecommerce_order(order),
        }
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Update Ecommerce Order Status Failed")
        return _storefront_error("Unable to update this ecommerce order.", 500)


@frappe.whitelist()
def confirm_ecommerce_order(order_id=None):
    """Confirm a pending standalone ecommerce order and reserve its stock."""
    if frappe.request.method != "POST":
        return _storefront_error("Invalid request method. Please use POST.", 405)
    vendor_id = _ecommerce_vendor_id()
    if not vendor_id:
        return _storefront_error("Vendor account could not be identified.", 403)

    try:
        locked = frappe.db.sql(
            "SELECT name FROM `tabEcommerce Ecommerce Order` WHERE name = %s FOR UPDATE",
            order_id,
            as_dict=True,
        )
        if not locked:
            return _storefront_error("Ecommerce order not found.", 404)
        ecommerce_order = frappe.get_doc("Ecommerce Ecommerce Order", order_id)
        if ecommerce_order.vendor_id != vendor_id:
            return _storefront_error("Ecommerce order not found.", 404)
        if ecommerce_order.system_order:
            return {
                "status": "success",
                "message": _("This order is already confirmed."),
                "data": _serialize_ecommerce_order(ecommerce_order),
            }
        if not _can_confirm_ecommerce_order(ecommerce_order.status):
            return _storefront_error(
                f"Cannot confirm an order with status {ecommerce_order.status}."
            )

        website = frappe.get_doc("Ecommerce Vendor Website", ecommerce_order.website)

        stock_updates = []
        for item in ecommerce_order.items:
            product = frappe.db.get_value(
                "Ecommerce Product",
                {"name": item.product_id, "website": website.name},
                ["name", "product_name", "enable", "continue_selling"],
                as_dict=True,
            )
            if not product:
                raise ValueError(_("{0} is no longer available.").format(item.product_name))
            if product.enable:
                rows = frappe.db.sql(
                    """
                    SELECT name, quantity FROM `tabEcommerce Product Variant`
                    WHERE name = %s AND parent = %s AND parenttype = 'Ecommerce Product'
                    LIMIT 1 FOR UPDATE
                    """,
                    (item.variant_id, product.name),
                    as_dict=True,
                )
                if not rows:
                    raise ValueError(_("The selected variant for {0} is unavailable.").format(item.product_name))
                available = _storefront_money(rows[0].quantity)
                quantity = int(item.quantity or 0)
                if available < quantity and not product.continue_selling:
                    raise ValueError(_("Only {0} units of {1} are available.").format(max(0, available), item.product_name))
                stock_updates.append((rows[0].name, max(Decimal("0"), available - quantity)))
        for variant_id, remaining_quantity in stock_updates:
            frappe.db.set_value(
                "Ecommerce Product Variant",
                variant_id,
                "quantity",
                float(remaining_quantity),
                update_modified=False,
            )
        ecommerce_order.status = "Confirmed"
        ecommerce_order.system_order = ecommerce_order.name
        ecommerce_order.confirmed_at = now_datetime()
        ecommerce_order.save(ignore_permissions=True)
        frappe.db.commit()
        return {
            "status": "success",
            "message": _("Ecommerce order confirmed successfully."),
            "data": _serialize_ecommerce_order(ecommerce_order),
        }
    except (ValueError, TypeError) as exc:
        frappe.db.rollback()
        return _storefront_error(str(exc))
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Confirm Ecommerce Order Failed")
        return _storefront_error("Unable to confirm this ecommerce order.", 500)


import frappe
from frappe.utils.file_manager import save_file


@frappe.whitelist(allow_guest=False)
def upload_file():
    try:
        if 'file' not in frappe.request.files:
            return {"status": "error", "message": "No file found in request"}

        file = frappe.request.files['file']
        content = file.stream.read()
        form_data = frappe.local.form_dict or {}
        is_builder_logo = str(form_data.get("is_builder_logo") or "").lower() in {
            "1", "true", "yes"
        }
        page_name = form_data.get("page_name")

        # 🧩 Safely ensure max_file_size is int
        try:
            max_size = int(frappe.local.conf.get("max_file_size", 5242880))
        except Exception:
            max_size = 5242880

        if len(content) > max_size:
            return {"status": "error", "message": _("File too large.")}

        extension = os.path.splitext(os.path.basename(file.filename or ""))[1].lower()
        upload_filename = f"{uuid4().hex}{extension}"
        attached_doctype = None
        attached_name = None

        if is_builder_logo:
            if not page_name:
                return {
                    "status": "error",
                    "message": _("Page name is required when uploading a logo."),
                }

            page = frappe.db.get_value(
                "Ecommerce Page",
                page_name,
                ["name", "website_id"],
                as_dict=True,
            )
            if not page:
                return {"status": "error", "message": _("Page not found.")}

            vendor_info = get_vendor_id() or {}
            vendor_id = vendor_info.get("vendor_id")
            page_vendor_id = frappe.db.get_value(
                "Ecommerce Vendor Website",
                page.website_id,
                "vendor_id",
            )
            if not vendor_id or str(page_vendor_id) != str(vendor_id):
                frappe.local.response.http_status_code = 403
                return {
                    "status": "error",
                    "message": _("You cannot upload a logo for this page."),
                }

            allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
            if extension not in allowed_extensions:
                return {
                    "status": "error",
                    "message": _("Please upload a supported logo image."),
                }
            attached_doctype = "Ecommerce Page"
            attached_name = page.name

        saved_file = save_file(
            upload_filename,
            content,
            attached_doctype,
            attached_name,
            is_private=0,
        )
        file_url = frappe.utils.get_url(saved_file.file_url)

        return {
            "status": "success",
            "file_url": file_url,
            "file_name": saved_file.file_name,
            "file_id": saved_file.name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Upload File API Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=False)
def update_website():
    import json
    data = json.loads(frappe.request.data or "{}")

    website_id = data.get("name")  # must exist
    if not website_id:
        return {"status": "error", "message": "Website ID is required"}

    try:
        doc = frappe.get_doc("Ecommerce Vendor Website", website_id)
        vendor_info = get_vendor_id() or {}
        vendor_id = vendor_info.get("vendor_id")
        if not vendor_id or str(doc.vendor_id or "") != str(vendor_id):
            frappe.local.response.http_status_code = 403
            return {"status": "error", "message": _("You cannot edit this website")}

        requested_template = data.get("template") if "template" in data else doc.template
        template = None
        if requested_template:
            template = frappe.db.get_value(
                "Ecommerce Template",
                requested_template,
                ["name", "page_name", "data_json"],
                as_dict=True,
            )
            if not template:
                return {"status": "error", "message": _("Template not found.")}

        # update fields
        fields = [
            "website_link", "custom_domain", "status", "type", "description", "template",
            "font", "primary_color", "secondary_color",
            "additional_color2"
        ]
        for field in fields:
            if field in data:
                value = (
                    _normalize_google_font_name(data[field])
                    if field == "font"
                    else data[field]
                )
                setattr(doc, field, value)
        if "additional_color_1" in data:
            doc.additional_color1 = data["additional_color_1"]
        if "additional_color_2" in data:
            doc.additional_color2 = data["additional_color_2"]
        if "favicon" in data:
            doc.favicon = (
                _save_builder_image(
                    data.get("favicon"),
                    "Ecommerce Vendor Website",
                    doc.name,
                    "favicon",
                    "favicon",
                )
                if data.get("favicon")
                else None
            )

        doc.save(ignore_permissions=True)
        template_result = None
        if template:
            website_pages = frappe.get_all(
                "Ecommerce Page",
                filters={"website_id": doc.name},
                fields=["name", "page", "parent1", "template"],
                order_by="creation asc",
            )
            root_pages = [page for page in website_pages if not page.parent1]
            root_page = next(
                (page for page in root_pages if page.page == "Home"),
                root_pages[0] if root_pages else None,
            )
            if not root_page:
                raise ValueError(_("This website does not have a root page to update."))
            if root_page.template != template.name:
                template_result = _apply_builder_page_template(
                    frappe.get_doc("Ecommerce Page", root_page.name),
                    template,
                )

        catalogue_counts = _copy_builder_catalogue(
            data.get("catalogue_source"),
            doc.name,
            vendor_id,
        )
        # Published HTML contains the same theme tokens for iframe/public previews.
        # Refresh it now so an edited theme is visible without manually publishing
        # every page again.
        from ecommerce.patches.ensure_unique_product_slugs import _republish_website_pages
        _republish_website_pages(doc.name)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Website updated successfully",
            "doc": doc,
            "catalogue": catalogue_counts,
            "template": template_result,
            "custom_domain_dns": storefront_custom_domain_setup(
                doc.custom_domain
            ),
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=str(e), title="Update Website Error")
        return {
            "status": "error",
            "message": f"Error updating website: {str(e)}"
        }

@frappe.whitelist(allow_guest=False)
def delete_website():
    import json
    data = json.loads(frappe.request.data or "{}")
    website_id = data.get("name")  # must exist

    if not website_id:
        return {"status": "error", "message": "Website ID is required"}

    try:
        doc = frappe.get_doc("Ecommerce Vendor Website", website_id)
        doc.status = "Discarded"  # ✅ properly mark as discarded
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "message": "Website deleted successfully"}
    except Exception as e:
        frappe.log_error(message=str(e), title="Delete Website Error")
        return {"status": "error", "message": f"Error deleting website: {str(e)}"}

"""Install ten editable ecommerce starter templates and their shared blocks.

The collection deliberately uses a small set of flexible, well-scoped blocks.
Each template supplies a different content model and layout variant, while
merchants can still add, remove, reorder, and restyle every section in Builder.
"""

import copy
import json

import frappe


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ seo_title or doc.page }}</title>
  {% if seo_description %}<meta name="description" content="{{ seo_description }}">{% endif %}
  <style>
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:var(--store-role-30,#171717);font-family:var(--store-font,Inter),ui-sans-serif,system-ui,sans-serif}img{max-width:100%}a{color:inherit}body>header{position:relative;z-index:20}{{ blockstyle | safe }}
  </style>
</head>
<body>
  <header>{{ header | safe }}</header>
  <main>{{ main | safe }}</main>
  <footer>{{ footer | safe }}</footer>
  {% if blockscript %}<script>{{ blockscript | safe }}</script>{% endif %}
</body>
</html>"""


def field(label, kind, name, default=None, **extra):
    result = {"label": label, "type": kind, "name": name, **extra}
    if default is not None:
        result["default"] = default
    return result


def destination_fields(label, name):
    """Use the shared tabbed internal destination picker plus URL fallback."""
    return [
        field(
            f"{label} link",
            "commerce_links",
            f"{name}_destination",
            [],
            multiple=False,
            target_url_field=f"{name}_url",
        ),
    ]


BLOCKS = [
    {
        "name": "Retail Announcement Bar",
        "type": "Header",
        "model": {"block_name": "retail_announcement", "fields": [
            field("Message", "text", "message", "Free delivery on qualifying orders"),
            field("Link label", "text", "link_label", "Shop now"),
            *destination_fields("Link", "link"),
            field("Link URL", "normaltext", "link_url", ""),
        ]},
        "html": """<div class="rt-announcement"><span>{{ message }}</span>{% if link_label %}<a href="{{ link_destination_url or link_url or '#' }}">{{ link_label }} →</a>{% endif %}</div>""",
        "style": """.rt-announcement{display:flex;justify-content:center;align-items:center;gap:1.25rem;min-height:38px;padding:.45rem 1rem;background:var(--store-role-30,#171717);color:#fff;font-size:.78rem;letter-spacing:.04em}.rt-announcement a{color:var(--store-highlight,var(--store-role-10,#f59e0b));font-weight:750;text-decoration:none}@media(max-width:560px){.rt-announcement{justify-content:space-between;font-size:.7rem}}""",
    },
    {
        "name": "Retail Studio Navigation",
        "type": "Header",
        "model": {"block_name": "retail_navigation", "fields": [
            field("Store name", "text", "store_name", "STUDIO STORE"),
            field("Tagline", "text", "tagline", "Goods for better living"),
            field("Links", "repeater", "links", [], fields=[field("Label", "text", "label"), field("Link", "commerce_links", "destinations", [], multiple=False), field("Custom URL", "normaltext", "url")]),
            field("Show search", "toggle", "show_search", True),
            field("Show cart", "toggle", "show_cart", True),
        ]},
        "html": """<nav class="rt-nav"><a class="rt-brand" href="#"><strong>{{ store_name }}</strong>{% if tagline %}<small>{{ tagline }}</small>{% endif %}</a><div class="rt-nav__links">{% set navigation_links = links if links else store_categories[:3] %}{% for link in navigation_links %}<a href="{{ link.destination_url or link.url or '#' }}">{{ link.label or link.title }}</a>{% endfor %}</div><div class="rt-nav__actions">{% if show_search %}<a href="#search" aria-label="Search">⌕</a>{% endif %}{% if show_cart %}<a href="/storefront/cart" aria-label="Cart">Bag <span class="ecommerce-cart-count" data-cart-count aria-hidden="true">0</span></a>{% endif %}</div></nav>""",
        "style": """.rt-nav{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:2rem;min-height:82px;padding:1rem clamp(1.1rem,4vw,4.5rem);border-bottom:1px solid #e7e5e4;background:#fff}.rt-brand{display:flex;flex-direction:column;width:max-content;text-decoration:none;line-height:1}.rt-brand strong{font-size:1.05rem;letter-spacing:.12em}.rt-brand small{margin-top:.35rem;color:#78716c;font-size:.65rem;letter-spacing:.04em}.rt-nav__links{display:flex;align-items:center;gap:clamp(1.1rem,2.5vw,2.5rem)}.rt-nav__links a{text-decoration:none;font-size:.86rem;font-weight:650}.rt-nav__actions{display:flex;justify-content:flex-end;align-items:center;gap:1.1rem}.rt-nav__actions a{text-decoration:none;font-size:.82rem;font-weight:700}.rt-nav__actions a:first-child{font-size:1.6rem;font-weight:400}.rt-nav__actions span{display:inline-grid;place-items:center;width:20px;height:20px;margin-left:.25rem;border-radius:50%;background:var(--store-role-10,#f59e0b);color:#fff;font-size:.65rem}@media(max-width:800px){.rt-nav{grid-template-columns:1fr auto;min-height:70px}.rt-nav__links{display:none}.rt-brand small{display:none}}""",
    },
    {
        "name": "Retail Campaign Hero",
        "type": "Main",
        "model": {"block_name": "retail_campaign_hero", "fields": [
            field("Layout", "select", "layout", "split", options=[{"label": "Split", "value": "split"}, {"label": "Image overlay", "value": "overlay"}, {"label": "Editorial", "value": "editorial"}]),
            field("Eyebrow", "text", "eyebrow", "The new collection"), field("Heading", "text", "heading", "Objects worth keeping"),
            field("Description", "textarea", "description", "Considered essentials, made for how you live now."),
            field("Primary button", "text", "button_label", "Explore collection"),
            *destination_fields("Primary button", "button"),
            field("Primary custom URL", "normaltext", "button_url", ""),
            field("Secondary button", "text", "secondary_label", "Our story"),
            *destination_fields("Secondary button", "secondary"),
            field("Secondary custom URL", "normaltext", "secondary_url", ""),
            field("Hero image", "file", "image", "https://placehold.co/1400x1100/e7e5e4/292524?text=New+collection"),
        ]},
        "html": """<section class="rt-hero rt-hero--{{ layout or 'split' }}">{% if image %}<img class="rt-hero__image" src="{{ image }}" alt="{{ heading }}">{% endif %}<div class="rt-hero__copy">{% if eyebrow %}<p class="rt-kicker">{{ eyebrow }}</p>{% endif %}<h1>{{ heading }}</h1>{% if description %}<p class="rt-hero__desc">{{ description }}</p>{% endif %}<div class="rt-buttons"><a class="rt-button" href="{{ button_destination_url or button_url or '#' }}">{{ button_label }}</a>{% if secondary_label %}<a class="rt-text-link" href="{{ secondary_destination_url or secondary_url or '#' }}">{{ secondary_label }} →</a>{% endif %}</div></div></section>""",
        "style": """.rt-hero{position:relative;min-height:clamp(540px,72vw,760px);background:var(--store-role-60,#f5f5f4);overflow:hidden}.rt-hero__image{width:100%;height:100%;object-fit:cover}.rt-hero__copy{padding:clamp(2rem,7vw,7rem)}.rt-kicker{margin:0 0 1rem;color:var(--store-role-10,#b45309);font-size:.74rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase}.rt-hero h1{max-width:800px;margin:0;font-family:Georgia,serif;font-size:clamp(3rem,7vw,7.5rem);font-weight:500;letter-spacing:-.055em;line-height:.92}.rt-hero__desc{max-width:550px;margin:1.5rem 0 0;color:#57534e;font-size:clamp(1rem,1.4vw,1.2rem);line-height:1.7}.rt-buttons{display:flex;align-items:center;gap:1.4rem;margin-top:2rem}.rt-button{display:inline-flex;padding:.95rem 1.4rem;background:var(--ecommerce-action-background,var(--store-role-30,#171717));color:#fff;text-decoration:none;font-weight:750}.rt-text-link{font-size:.88rem;font-weight:750;text-decoration:none}.rt-hero--split{display:grid;grid-template-columns:minmax(0,.92fr) minmax(0,1.08fr)}.rt-hero--split .rt-hero__image{grid-column:2;grid-row:1;min-height:620px}.rt-hero--split .rt-hero__copy{grid-column:1;grid-row:1;display:flex;flex-direction:column;justify-content:center}.rt-hero--overlay{display:grid;color:#fff}.rt-hero--overlay>*{grid-area:1/1}.rt-hero--overlay:after{content:"";grid-area:1/1;background:linear-gradient(90deg,rgba(0,0,0,.72),rgba(0,0,0,.08));pointer-events:none}.rt-hero--overlay .rt-hero__copy{z-index:1;align-self:end;padding-bottom:clamp(3rem,8vw,7rem)}.rt-hero--overlay .rt-hero__desc{color:#e7e5e4}.rt-hero--overlay .rt-button{background:#fff;color:#171717}.rt-hero--editorial{display:grid;grid-template-columns:1.35fr .65fr;background:#fff}.rt-hero--editorial .rt-hero__image{grid-column:1;grid-row:1;min-height:680px}.rt-hero--editorial .rt-hero__copy{grid-column:2;grid-row:1;align-self:center}.rt-hero--editorial h1{font-size:clamp(2.8rem,5vw,5.8rem)}@media(max-width:800px){.rt-hero--split,.rt-hero--editorial{display:flex;flex-direction:column}.rt-hero--split .rt-hero__image,.rt-hero--editorial .rt-hero__image{min-height:360px;max-height:55vh}.rt-hero__copy{padding:2.75rem 1.35rem}.rt-hero--overlay .rt-hero__copy{align-self:end}.rt-buttons{flex-wrap:wrap}}""",
    },
    {
        "name": "Retail Collection Mosaic",
        "type": "Main",
        "model": {"block_name": "retail_collection_mosaic", "fields": [
            field("Layout", "select", "layout", "mosaic", options=[{"label": "Mosaic", "value": "mosaic"}, {"label": "Equal cards", "value": "cards"}, {"label": "Compact circles", "value": "circles"}]),
            field("Heading", "text", "heading", "Shop by collection"), field("Description", "textarea", "description", "Find your new favourites."),
            field("Collections", "repeater", "items", [], fields=[field("Title", "text", "title"), field("Caption", "text", "caption"), field("Image", "file", "image"), field("Link", "commerce_links", "destinations")]),
        ]},
        "html": """<section class="rt-section rt-collections rt-collections--{{ layout or 'mosaic' }}"><header class="rt-section__header"><p class="rt-kicker">Curated for you</p><h2>{{ heading }}</h2>{% if description %}<p>{{ description }}</p>{% endif %}</header><div class="rt-collections__grid">{% for item in items %}<a class="rt-collection" href="{{ item.destination_url or '#' }}">{% if item.image %}<img src="{{ item.image }}" alt="{{ item.title }}">{% endif %}<span><strong>{{ item.title }}</strong>{% if item.caption %}<small>{{ item.caption }}</small>{% endif %}</span></a>{% endfor %}</div></section>""",
        "style": """.rt-section{padding:clamp(3.5rem,7vw,7rem) clamp(1.1rem,4vw,4.5rem)}.rt-section__header{max-width:680px;margin-bottom:2.4rem}.rt-section__header h2{margin:.25rem 0;font-family:Georgia,serif;font-size:clamp(2.2rem,4vw,4.2rem);font-weight:500;letter-spacing:-.04em}.rt-section__header>p:last-child{color:#78716c;line-height:1.6}.rt-collections__grid{display:grid;grid-template-columns:repeat(12,1fr);gap:1rem}.rt-collection{position:relative;grid-column:span 4;min-height:440px;overflow:hidden;background:#e7e5e4;color:#fff;text-decoration:none}.rt-collection img{position:absolute;width:100%;height:100%;object-fit:cover;transition:transform .5s}.rt-collection:after{content:"";position:absolute;inset:30% 0 0;background:linear-gradient(transparent,rgba(0,0,0,.72))}.rt-collection:hover img{transform:scale(1.035)}.rt-collection span{position:absolute;z-index:1;right:1.4rem;bottom:1.4rem;left:1.4rem}.rt-collection strong,.rt-collection small{display:block}.rt-collection strong{font-family:Georgia,serif;font-size:1.7rem}.rt-collection small{margin-top:.3rem;color:#e7e5e4}.rt-collections--mosaic .rt-collection:first-child{grid-column:span 7}.rt-collections--mosaic .rt-collection:nth-child(2){grid-column:span 5}.rt-collections--mosaic .rt-collection:nth-child(n+3){grid-column:span 4;min-height:330px}.rt-collections--cards .rt-collection{min-height:380px}.rt-collections--circles .rt-collections__grid{grid-template-columns:repeat(5,1fr)}.rt-collections--circles .rt-collection{grid-column:auto;min-height:0;aspect-ratio:1;border-radius:50%}.rt-collections--circles .rt-collection strong{font-family:inherit;font-size:1rem}.rt-collections--circles .rt-collection small{display:none}@media(max-width:800px){.rt-collections__grid,.rt-collections--circles .rt-collections__grid{grid-template-columns:repeat(2,1fr)}.rt-collection,.rt-collections--mosaic .rt-collection:first-child,.rt-collections--mosaic .rt-collection:nth-child(2),.rt-collections--mosaic .rt-collection:nth-child(n+3){grid-column:auto;min-height:300px}.rt-collections--circles .rt-collection{min-height:0}}@media(max-width:500px){.rt-collections__grid{grid-template-columns:1fr}.rt-collections--circles .rt-collections__grid{grid-template-columns:repeat(2,1fr)}}""",
    },
    {
        "name": "Retail Story Split",
        "type": "Main",
        "model": {"block_name": "retail_story_split", "fields": [
            field("Image position", "select", "image_position", "left", options=[{"label": "Left", "value": "left"}, {"label": "Right", "value": "right"}]),
            field("Eyebrow", "text", "eyebrow", "Made with intention"), field("Heading", "text", "heading", "A better way to choose"),
            field("Story", "textarea", "description", "We bring together thoughtful products, clear information, and warm service."),
            field("Link label", "text", "link_label", "Learn about us"),
            *destination_fields("Story button", "link"),
            field("Link custom URL", "normaltext", "link_url", ""),
            field("Image", "file", "image", "https://placehold.co/1200x1000/d6d3d1/292524?text=Our+story"),
            *destination_fields("Story image", "image_link"),
            field("Image custom URL", "normaltext", "image_url", ""),
        ]},
        "html": """<section class="rt-story rt-story--{{ image_position or 'left' }}"><div class="rt-story__media">{% if image %}{% if image_link_destination_url or image_url %}<a href="{{ image_link_destination_url or image_url }}">{% endif %}<img src="{{ image }}" alt="{{ heading }}">{% if image_link_destination_url or image_url %}</a>{% endif %}{% endif %}</div><div class="rt-story__copy"><p class="rt-kicker">{{ eyebrow }}</p><h2>{{ heading }}</h2><p>{{ description }}</p>{% if link_label %}<a href="{{ link_destination_url or link_url or '#' }}">{{ link_label }} →</a>{% endif %}</div></section>""",
        "style": """.rt-story{display:grid;grid-template-columns:1fr 1fr;background:var(--store-role-60,#f5f5f4)}.rt-story__media{min-height:560px}.rt-story__media>a{display:block;width:100%;height:100%}.rt-story__media img{width:100%;height:100%;object-fit:cover}.rt-story__copy{display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:clamp(3rem,8vw,8rem)}.rt-story__copy h2{max-width:650px;margin:.25rem 0 1.25rem;font-family:Georgia,serif;font-size:clamp(2.5rem,5vw,5rem);font-weight:500;letter-spacing:-.045em;line-height:1}.rt-story__copy>p:not(.rt-kicker){max-width:540px;color:#57534e;line-height:1.8}.rt-story__copy a{margin-top:1.25rem;font-size:.88rem;font-weight:800;text-decoration:none;border-bottom:1px solid;padding-bottom:.25rem}.rt-story--right .rt-story__media{grid-column:2;grid-row:1}.rt-story--right .rt-story__copy{grid-column:1;grid-row:1}@media(max-width:760px){.rt-story{display:flex;flex-direction:column}.rt-story--right .rt-story__media{order:0}.rt-story__media{min-height:360px}.rt-story__copy{padding:3.5rem 1.35rem}}""",
    },
    {
        "name": "Retail Value Icons",
        "type": "Main",
        "model": {"block_name": "retail_value_icons", "fields": [
            field("Heading", "text", "heading", "Why shop with us"),
            field("Benefits", "repeater", "items", [
                {"icon": "✦", "title": "Selected with care", "description": "Only products we would choose ourselves."},
                {"icon": "↗", "title": "Fast local delivery", "description": "Clear tracking from checkout to your door."},
                {"icon": "♡", "title": "Human support", "description": "Helpful answers before and after your order."},
            ], fields=[field("Icon", "text", "icon"), field("Title", "text", "title"), field("Description", "textarea", "description")]),
        ]},
        "html": """<section class="rt-values"><h2>{{ heading }}</h2><div>{% for item in items %}<article><i>{{ item.icon }}</i><h3>{{ item.title }}</h3><p>{{ item.description }}</p></article>{% endfor %}</div></section>""",
        "style": """.rt-values{padding:clamp(3rem,6vw,5.5rem) clamp(1.1rem,4vw,4.5rem);border-block:1px solid #e7e5e4}.rt-values>h2{margin:0 0 2.25rem;font-family:Georgia,serif;font-size:clamp(2rem,3vw,3rem);font-weight:500;text-align:center}.rt-values>div{display:grid;grid-template-columns:repeat(3,1fr);max-width:1200px;margin:auto}.rt-values article{padding:1rem clamp(1rem,4vw,4rem);text-align:center;border-right:1px solid #e7e5e4}.rt-values article:last-child{border:0}.rt-values i{display:grid;place-items:center;width:48px;height:48px;margin:0 auto 1rem;border-radius:50%;background:var(--store-role-60,#f5f5f4);color:var(--store-role-10,#b45309);font-style:normal;font-size:1.25rem}.rt-values h3{margin:.4rem 0;font-size:1rem}.rt-values p{margin:.5rem 0 0;color:#78716c;font-size:.86rem;line-height:1.6}@media(max-width:650px){.rt-values>div{grid-template-columns:1fr}.rt-values article{border-right:0;border-bottom:1px solid #e7e5e4;padding:1.5rem}}""",
    },
    {
        "name": "Retail Quote Wall",
        "type": "Main",
        "model": {"block_name": "retail_quote_wall", "fields": [
            field("Eyebrow", "text", "eyebrow", "Loved by our community"), field("Heading", "text", "heading", "The feeling is mutual"),
            field("Reviews", "repeater", "items", [
                {"quote": "Beautifully packed, exactly as described, and delivered sooner than expected.", "name": "Maya K.", "detail": "Verified customer"},
                {"quote": "The kind of shop you recommend to a friend without thinking twice.", "name": "Aarav S.", "detail": "Verified customer"},
            ], fields=[field("Quote", "textarea", "quote"), field("Name", "text", "name"), field("Detail", "text", "detail")]),
        ]},
        "html": """<section class="rt-quotes"><header><p class="rt-kicker">{{ eyebrow }}</p><h2>{{ heading }}</h2></header><div>{% for item in items %}<figure><div aria-label="5 stars">★★★★★</div><blockquote>“{{ item.quote }}”</blockquote><figcaption><strong>{{ item.name }}</strong><span>{{ item.detail }}</span></figcaption></figure>{% endfor %}</div></section>""",
        "style": """.rt-quotes{padding:clamp(4rem,8vw,8rem) clamp(1.1rem,4vw,4.5rem);background:var(--store-role-30,#171717);color:#fff}.rt-quotes header{text-align:center}.rt-quotes h2{margin:.3rem 0 3rem;font-family:Georgia,serif;font-size:clamp(2.5rem,4vw,4.5rem);font-weight:500}.rt-quotes>div{display:grid;grid-template-columns:repeat(2,1fr);gap:1.25rem;max-width:1200px;margin:auto}.rt-quotes figure{margin:0;padding:clamp(1.7rem,4vw,3.5rem);border:1px solid rgba(255,255,255,.18)}.rt-quotes figure>div{color:var(--store-highlight,var(--store-role-10,#f59e0b));letter-spacing:.2em}.rt-quotes blockquote{margin:1.5rem 0;font-family:Georgia,serif;font-size:clamp(1.35rem,2.2vw,2rem);line-height:1.45}.rt-quotes figcaption span,.rt-quotes figcaption strong{display:block}.rt-quotes figcaption span{margin-top:.25rem;color:#a8a29e;font-size:.78rem}@media(max-width:650px){.rt-quotes>div{grid-template-columns:1fr}}""",
    },
    {
        "name": "Retail Newsletter Footer",
        "type": "Footer",
        "model": {"block_name": "retail_newsletter_footer", "fields": [
            field("Store name", "text", "store_name", "STUDIO STORE"), field("Heading", "text", "heading", "Good things, occasionally"),
            field("Description", "textarea", "description", "New arrivals, useful guides, and private offers—sent with restraint."),
            field("Email placeholder", "text", "placeholder", "Email address"), field("Button label", "text", "button_label", "Join us"),
            field("Links", "repeater", "links", [{"label": "Shipping", "url": ""}, {"label": "Returns", "url": ""}, {"label": "Contact", "url": ""}, {"label": "Instagram", "url": ""}], fields=[field("Label", "text", "label"), field("Link", "commerce_links", "destinations", [], multiple=False), field("Custom URL", "normaltext", "url")]),
        ]},
        "html": """<footer class="rt-footer"><div class="rt-footer__newsletter"><div><p>{{ store_name }}</p><h2>{{ heading }}</h2><span>{{ description }}</span></div><form onsubmit="return false"><label class="sr-only" for="rt-email">Email</label><input id="rt-email" type="email" placeholder="{{ placeholder }}" required><button type="submit">{{ button_label }} →</button></form></div><div class="rt-footer__bottom"><span>© {{ store_name }}</span><nav>{% for link in links %}<a href="{{ link.destination_url or link.url or '#' }}">{{ link.label }}</a>{% endfor %}</nav></div></footer>""",
        "style": """.rt-footer{padding:clamp(3.5rem,7vw,7rem) clamp(1.1rem,4vw,4.5rem) 1.5rem;background:var(--store-ui-accent,var(--store-secondary,#111));color:#fff}.rt-footer__newsletter{display:grid;grid-template-columns:1fr 1fr;gap:clamp(2rem,8vw,8rem);align-items:end;padding-bottom:4rem}.rt-footer__newsletter p{color:#fff;font-size:.75rem;font-weight:800;letter-spacing:.18em}.rt-footer__newsletter h2{margin:.4rem 0;font-family:Georgia,serif;font-size:clamp(2.5rem,4.5vw,5rem);font-weight:500;line-height:1}.rt-footer__newsletter span{display:block;max-width:560px;margin-top:1rem;color:#e2e8f0;line-height:1.7}.rt-footer form{display:flex;border-bottom:1px solid rgba(255,255,255,.55)}.rt-footer input{flex:1;min-width:0;padding:1rem 0;border:0;outline:0;background:transparent;color:#fff;font:inherit}.rt-footer button{border:0;background:transparent;color:#fff;font-weight:750;cursor:pointer}.rt-footer__bottom{display:flex;justify-content:space-between;gap:2rem;padding-top:1.5rem;border-top:1px solid rgba(255,255,255,.28);color:#e2e8f0;font-size:.78rem}.rt-footer nav{display:flex;flex-wrap:wrap;gap:1.5rem}.rt-footer a{text-decoration:none}@media(max-width:700px){.rt-footer__newsletter{grid-template-columns:1fr}.rt-footer__bottom{flex-direction:column}}""",
    },
]


IMG = {
    "fashion": "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1600&q=85",
    "gadgets": "https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=1600&q=85",
    "jewelry": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1600&q=85",
    "cosmetics": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=1600&q=85",
    "grocery": "https://images.unsplash.com/photo-1543168256-418811576931?auto=format&fit=crop&w=1600&q=85",
    "home": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1600&q=85",
    "kids": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&w=1600&q=85",
    "sports": "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?auto=format&fit=crop&w=1600&q=85",
    "books": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=1600&q=85",
    "pets": "https://images.unsplash.com/photo-1450778869180-41d0601e046e?auto=format&fit=crop&w=1600&q=85",
}


TEMPLATES = [
    ("Loom & Line Fashion", "Fashion", "split", "A quieter kind of confidence", "Modern layers and everyday tailoring, selected to work harder in your wardrobe.", ["New season", "Everyday layers", "Accessories"], "The edit behind the edit"),
    ("Circuit Modern Gadgets", "Gadgets", "overlay", "Tomorrow, switched on", "Smart technology with clean design, useful features, and support that speaks human.", ["Mobile", "Audio", "Smart home", "Work setup"], "Technology that earns its place"),
    ("Aurum Jewelry Atelier", "Jewelry", "editorial", "Made to become yours", "Fine details, luminous materials, and pieces created for stories still unfolding.", ["Rings", "Necklaces", "Earrings"], "Small objects, lasting meaning"),
    ("Petal Lab Cosmetics", "Cosmetics", "split", "Your ritual, refined", "Skin-loving formulas and expressive colour for routines that feel entirely your own.", ["Skincare", "Makeup", "Body", "Sets"], "Beauty with nothing to hide"),
    ("Daily Basket Grocery", "Grocery", "overlay", "Freshness at your doorstep", "Market-fresh produce, pantry staples, and neighbourhood favourites delivered simply.", ["Fresh produce", "Bakery", "Pantry", "Drinks"], "Good food starts closer to home"),
    ("Still House Living", "Home", "editorial", "Room to live beautifully", "Warm, useful pieces that make everyday spaces feel considered and unmistakably yours.", ["Living", "Dining", "Bedroom"], "A home collected over time"),
    ("Tiny Trails Kids", "Kids", "split", "Big joy for little days", "Playful, practical finds for curious kids and the grown-ups cheering them on.", ["Play", "Wear", "Learn", "Nursery"], "Designed for real family life"),
    ("Peak Motion Sports", "Sports", "overlay", "Built for the next move", "Performance gear and everyday essentials that meet you wherever progress happens.", ["Training", "Running", "Outdoor"], "Purpose in every detail"),
    ("Page & Pine Books", "Books", "editorial", "Find your next world", "Stories to disappear into, ideas to return to, and editions worth keeping close.", ["New fiction", "Ideas", "Children", "Beautiful books"], "Independent minds, thoughtfully shelved"),
    ("Paw & Parcel Pets", "Pets", "split", "For very good company", "Food, play, comfort, and care essentials chosen for happier days together.", ["Dogs", "Cats", "Walk", "Wellness"], "Care made joyful"),
]


BASE_BLOCK_NAMES = (
    "Retail Announcement Bar",
    "Retail Studio Navigation",
    "Retail Campaign Hero",
    "Retail Collection Mosaic",
    "Retail Story Split",
    "Retail Value Icons",
    "Retail Quote Wall",
    "Retail Newsletter Footer",
    "Commerce Product Shelf",
)

BLOCK_IMAGES = {
    "Retail Announcement Bar": "/assets/ecommerce/images/builder-block-previews/retail-announcement-bar.png",
    "Retail Studio Navigation": "/assets/ecommerce/images/builder-block-previews/retail-studio-navigation.png",
    "Retail Campaign Hero": "/assets/ecommerce/images/builder-block-previews/retail-campaign-hero.png",
    "Retail Collection Mosaic": "/assets/ecommerce/images/builder-block-previews/retail-collection-mosaic.png",
    "Retail Story Split": "/assets/ecommerce/images/builder-block-previews/retail-story-split.png",
    "Retail Value Icons": "/assets/ecommerce/images/builder-block-previews/retail-value-icons.png",
    "Retail Quote Wall": "/assets/ecommerce/images/builder-block-previews/retail-quote-wall.png",
    "Retail Newsletter Footer": "/assets/ecommerce/images/builder-block-previews/retail-newsletter-footer.png",
}


BASE_CONFIG = {
    "tabs": [
        {
            "label": "SEO",
            "title": "SEO",
            "active": True,
            "sections": [{
                "label": "Search preview",
                "fields": [
                    field("SEO title", "text", "seo_title"),
                    field("SEO description", "textarea", "seo_description"),
                    field("Allow search indexing", "toggle", "allow_indexing_search_engine", True),
                ],
            }],
        },
        {
            "label": "Configuration",
            "title": "Configuration",
            "active": False,
            "sections": [{
                "label": "Store settings",
                "fields": [
                    field("Display Content", "toggle", "allow_indexing_social_1", True),
                    field("Enable Breadcrumbs", "toggle", "allow_indexing_social_2", True),
                ],
            }],
        },
        {
            "label": "Page Info",
            "title": "Page Info",
            "active": False,
            "sections": [{
                "label": "Page details",
                "fields": [
                    field("Thumbnail Image", "file", "thumnail_image"),
                    field("Page Icon", "file", "page_image"),
                ],
            }],
        },
        {
            "label": "Content",
            "title": "Content",
            "active": False,
            "sections": [{
                "label": "Page content",
                "fields": [field("Summary", "editor", "page_summary")],
            }],
        },
        {
            "label": "Layout",
            "title": "Layout",
            "active": False,
            "sections": [
                {"fields": [field("Header blocks", "draggable", "header")]},
                {"fields": [field("Page blocks", "draggable", "main")]},
                {"fields": [field("Footer blocks", "draggable", "footer")]},
            ],
        },
    ]
}


def block_instance(block_name, instance_id, values=None):
    doc = frappe.get_doc("Ecommerce Block", block_name)
    model = json.loads(doc.model or "{}")
    values = values or {}
    for item in model.get("fields") or []:
        key = item.get("name") or item.get("key")
        if key in values:
            item["value"] = copy.deepcopy(values[key])
        elif "default" in item:
            item["value"] = copy.deepcopy(item["default"])
    return {"id": instance_id, "name": doc.name, "block_name": doc.block_name or doc.name, "type": doc.type, "is_template_starter": True, "block_details": {"name": doc.name, "model": model}}


def migrate_page_block_names(template_name, block_aliases, starter_content):
    """Rename old generic starter instances while preserving edited values."""
    name_map = dict(zip(BASE_BLOCK_NAMES, block_aliases))
    placeholder_routes = {
        "#", "#shop", "#about", "#new", "#collections", "#search"
    }

    def clear_placeholder_routes(value, field_name=None):
        changed = False
        if isinstance(value, dict):
            configured_name = value.get("name") or value.get("key") or field_name
            if configured_name in {
                "url", "link", "link_url", "button_url",
                "secondary_url", "image_url",
            }:
                for value_key in ("value", "default"):
                    configured_value = value.get(value_key)
                    if (
                        isinstance(configured_value, str)
                        and configured_value.strip().lower() in placeholder_routes
                    ):
                        value[value_key] = ""
                        changed = True
            for key, item in list(value.items()):
                if (
                    key in {
                        "url", "link", "link_url", "button_url",
                        "secondary_url", "image_url",
                    }
                    and isinstance(item, str)
                    and item.strip().lower() in placeholder_routes
                ):
                    value[key] = ""
                    changed = True
                elif clear_placeholder_routes(item, key):
                    changed = True
        elif isinstance(value, list):
            for item in value:
                if clear_placeholder_routes(item, field_name):
                    changed = True
        return changed

    def starter_family(instances):
        families = set()
        for instance in instances or []:
            parts = str(instance.get("id") or "").split("-")
            if len(parts) < 3 or parts[0] != "retail" or not parts[1].isdigit():
                return None
            families.add(parts[1])
        return next(iter(families)) if len(families) == 1 else None

    pages = frappe.get_all(
        "Ecommerce Page",
        filters={"template": template_name},
        fields=["name", "parent1", "field_value"],
    )
    for page in pages:
        values = json.loads(page.field_value or "{}")
        changed = False

        # Repair root layouts saved by the earlier body-only implementation.
        # Replace them only when both sides are untouched retail starter sets
        # and their template-family ids prove that they came from another
        # template. Custom layouts are never overwritten by this migration.
        if not page.parent1:
            for layout_section in ("header", "footer"):
                current_family = starter_family(values.get(layout_section))
                expected_family = starter_family(starter_content.get(layout_section))
                if current_family and expected_family and current_family != expected_family:
                    values[layout_section] = copy.deepcopy(
                        starter_content.get(layout_section) or []
                    )
                    changed = True

        sections = ("main",) if page.parent1 else ("header", "main", "footer")
        for section in sections:
            for instance in values.get(section) or []:
                old_name = instance.get("block_name") or instance.get("name")
                alias_name = name_map.get(old_name)
                if alias_name:
                    instance["name"] = alias_name
                    instance["block_name"] = alias_name
                    details = instance.setdefault("block_details", {})
                    details["name"] = alias_name
                    changed = True
                if clear_placeholder_routes(instance):
                    changed = True
        if changed:
            frappe.db.set_value(
                "Ecommerce Page",
                page.name,
                "field_value",
                json.dumps(values),
                update_modified=False,
            )


def collection_items(category, names):
    colors = ["d6d3d1", "e7e5e4", "f5f5f4", "d4d4d8"]
    return [{"title": name, "caption": f"Shop {name.lower()}", "image": f"https://placehold.co/900x1100/{colors[index % len(colors)]}/292524?text={name.replace(' ', '+')}", "destinations": []} for index, name in enumerate(names)]


def execute():
    for definition in BLOCKS:
        values = {
            "type": definition["type"],
            "model": json.dumps(definition["model"]),
            "block": definition["html"],
            "style": definition["style"],
            "block_image": BLOCK_IMAGES.get(definition["name"]),
        }
        if frappe.db.exists("Ecommerce Block", definition["name"]):
            doc = frappe.get_doc("Ecommerce Block", definition["name"])
            doc.update(values)
            doc.save(ignore_permissions=True)
        else:
            frappe.get_doc({"doctype": "Ecommerce Block", "block_name": definition["name"], **values}).insert(ignore_permissions=True)

    for index, (name, category, layout, heading, description, collections, story_heading) in enumerate(TEMPLATES, 1):
        key = category.lower()
        # Templates share the same block definitions. Their distinct wording,
        # imagery, layout, and colors live in each starter block instance.
        announcement_name, nav_name, hero_name, mosaic_name, story_name, values_name, quotes_name, footer_name, shelf_name = BASE_BLOCK_NAMES
        hero = block_instance(hero_name, f"retail-{index}-hero", {"layout": layout, "eyebrow": f"{category} · New collection", "heading": heading, "description": description, "image": IMG[key]})
        mosaic = block_instance(mosaic_name, f"retail-{index}-collections", {"layout": "circles" if category in ("Grocery", "Kids", "Pets") else ("cards" if category in ("Cosmetics", "Gadgets") else "mosaic"), "heading": f"Shop {category.lower()}", "description": "Curated categories to help customers find the right product faster.", "items": collection_items(category, collections)})
        story = block_instance(story_name, f"retail-{index}-story", {"image_position": "right" if index % 2 == 0 else "left", "eyebrow": "Our point of view", "heading": story_heading, "description": description, "image": IMG[key]})
        nav = block_instance(nav_name, f"retail-{index}-nav", {"store_name": name.split(" ")[0].upper(), "tagline": f"Modern {category.lower()}, thoughtfully chosen"})
        announcement = block_instance(announcement_name, f"retail-{index}-announcement", {"message": "Free local delivery · Easy returns · Secure checkout", "link_label": "Discover the collection"})
        values = block_instance(values_name, f"retail-{index}-values")
        quotes = block_instance(quotes_name, f"retail-{index}-quotes", {"heading": f"Why customers choose our {category.lower()} edit"})
        footer = block_instance(footer_name, f"retail-{index}-footer", {"store_name": name.split(" ")[0].upper(), "description": f"Fresh {category.lower()} arrivals, useful advice, and private offers."})
        product_shelf = block_instance(shelf_name, f"retail-{index}-products", {"product_title": "Just in", "product_description": f"The latest {category.lower()} products, ready to make your own.", "grid_num": 4}) if frappe.db.exists("Ecommerce Block", shelf_name) else None

        main = [hero, mosaic]
        if product_shelf:
            main.append(product_shelf)
        main.extend([story, values])
        if index in (1, 3, 4, 6, 9):
            main.append(quotes)

        config = copy.deepcopy(BASE_CONFIG)
        starter_content = {"seo_title": name, "seo_description": description, "allow_indexing_search_engine": True, "header": [announcement, nav], "main": main, "footer": [footer], "Page": {}}
        config.update({
            "title": name,
            "default_page_title": name,
            "template_description": f"A responsive {category.lower()} storefront with a {layout} hero, collection navigation, product merchandising, brand story, trust content, and email capture.",
            "template_category": category,
            "starter_content": starter_content,
        })
        existing = frappe.db.get_value("Ecommerce Template", {"page_name": name}, "name")
        if existing:
            template = frappe.get_doc("Ecommerce Template", existing)
            template.data_json = json.dumps(config, indent=2)
            template.template = PAGE_TEMPLATE
            template.save(ignore_permissions=True)
        else:
            frappe.get_doc({"doctype": "Ecommerce Template", "page_name": name, "data_json": json.dumps(config, indent=2), "template": PAGE_TEMPLATE}).insert(ignore_permissions=True)

        template_name = existing or frappe.db.get_value(
            "Ecommerce Template", {"page_name": name}, "name"
        )
        migrate_page_block_names(template_name, BASE_BLOCK_NAMES, starter_content)

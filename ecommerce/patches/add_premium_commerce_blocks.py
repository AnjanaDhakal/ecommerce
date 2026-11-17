import json

import frappe


BLOCKS = [
    {
        "name": "Commerce Promo Hero",
        "type": "Main",
        "model": {
            "block_name": "commerce_promo_hero",
            "fields": [
                {"label": "Eyebrow", "type": "text", "name": "eyebrow", "default": "Limited time offer"},
                {"label": "Heading", "type": "text", "name": "heading", "default": "Upgrade your everyday"},
                {"label": "Description", "type": "textarea", "name": "description", "default": "Discover new arrivals and customer favourites selected for your store."},
                {"label": "Button label", "type": "text", "name": "button_label", "default": "Shop now"},
                {"label": "Button link", "type": "commerce_links", "name": "button_destinations", "multiple": False},
                {"label": "Button custom URL", "type": "normaltext", "name": "button_url", "default": ""},
                {"label": "Hero image", "type": "file", "name": "image", "default": "https://placehold.co/1600x760/f3f4f6/111827?text=Hero+campaign"},
            ],
        },
        "html": '''<section class="pc-hero">
  <div class="pc-hero__copy">
    {% if eyebrow %}<p class="pc-eyebrow">{{ eyebrow }}</p>{% endif %}
    {% if heading %}<h1>{{ heading }}</h1>{% endif %}
    {% if description %}<p class="pc-hero__description">{{ description }}</p>{% endif %}
    {% if button_label %}<a class="pc-button" href="{{ button_destinations_url or button_url or '#' }}">{{ button_label }}</a>{% endif %}
  </div>
  {% if image %}<img src="{{ image }}" alt="{{ heading or 'Store campaign' }}">{% endif %}
</section>''',
        "style": '''.pc-hero{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);min-height:520px;background:var(--store-role-60,#f5f5f5);overflow:hidden}.pc-hero__copy{display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:clamp(2rem,6vw,6rem)}.pc-hero h1{max-width:680px;margin:.3rem 0 1rem;color:var(--store-role-30,#111827);font-size:clamp(2.5rem,5vw,5.2rem);line-height:.98;letter-spacing:-.05em}.pc-eyebrow{margin:0;text-transform:uppercase;letter-spacing:.18em;font-size:.78rem;font-weight:700;color:var(--store-role-10,#ff4964)}.pc-hero__description{max-width:560px;color:#64748b;line-height:1.7}.pc-hero img{width:100%;height:100%;min-height:520px;object-fit:cover}.pc-button{display:inline-flex;margin-top:1.25rem;padding:.9rem 1.4rem;border-radius:.55rem;background:var(--ecommerce-action-background,var(--store-action,#111827));color:#fff;text-decoration:none;font-weight:700}@media(max-width:800px){.pc-hero{grid-template-columns:1fr}.pc-hero img{min-height:320px}.pc-hero__copy{padding:2.5rem 1.5rem}}''',
    },
    {
        "name": "Commerce Product Shelf",
        "type": "Main",
        "model": {"block_name": "commerce_product_shelf", "fields": [
            {"label": "Heading", "type": "text", "name": "product_title", "default": "Featured products"},
            {"label": "Description", "type": "textarea", "name": "product_description", "default": "Popular picks from our collection."},
            {"label": "Products per row", "type": "text", "name": "grid_num", "default": 4},
            {"label": "Products", "type": "product", "name": "product_list"},
        ]},
        "html": '''<section class="pc-section">
  <header class="pc-section__header"><div>{% if product_title %}<h2>{{ product_title }}</h2>{% endif %}{% if product_description %}<p>{{ product_description }}</p>{% endif %}</div></header>
  {% if product_list %}<div class="pc-products" data-columns="{{ grid_num or 4 }}" style="--pc-product-columns:{{ grid_num or 4 }}">{% for product in product_list %}
    <article class="pc-product">
      <a class="pc-product__image" href="{{ product.url or '#' }}">{% if product.product_image %}<img src="{{ product.product_image }}" alt="{{ product.product_name }}">{% endif %}</a>
      <div class="pc-product__body">{% if product.brand_name %}<small>{{ product.brand_name }}</small>{% endif %}<a href="{{ product.url or '#' }}"><h3>{{ product.product_name }}</h3></a><strong>Rs {{ product.price }}</strong></div>
    </article>{% endfor %}</div>{% endif %}
</section>''',
        "style": '''.pc-section{padding:clamp(2.5rem,6vw,6rem) clamp(1rem,4vw,4rem)}.pc-section__header{display:flex;justify-content:space-between;align-items:end;margin-bottom:2rem}.pc-section__header h2{margin:0;font-size:clamp(2rem,3vw,3rem)}.pc-section__header p{margin:.6rem 0 0;color:#64748b}.pc-products{display:grid;grid-template-columns:repeat(var(--pc-product-columns,4),minmax(0,1fr));gap:1.25rem}.pc-product{min-width:0}.pc-product__image{display:grid;place-items:center;aspect-ratio:1/1;background:#f5f5f5;border-radius:1rem;overflow:hidden}.pc-product__image img{width:100%;height:100%;object-fit:contain;padding:1rem;box-sizing:border-box;transition:transform .25s}.pc-product:hover img{transform:scale(1.04)}.pc-product__body{padding:1rem .25rem}.pc-product__body small{color:#64748b}.pc-product__body a{color:inherit;text-decoration:none}.pc-product__body h3{min-height:2.8em;margin:.4rem 0;line-height:1.4}.pc-product__body strong{font-size:1.05rem}@media(max-width:1000px){.pc-products{grid-template-columns:repeat(2,minmax(0,1fr))}.pc-products[data-columns="1"]{grid-template-columns:1fr}}@media(max-width:560px){.pc-products{grid-template-columns:1fr}}''',
    },
    {
        "name": "Commerce Category Showcase",
        "type": "Main",
        "model": {"block_name": "commerce_category_showcase", "fields": [
            {"label": "Heading", "type": "text", "name": "heading", "default": "Browse categories"},
            {"label": "Categories", "type": "repeater", "name": "items", "fields": [
                {"label": "Category name", "type": "text", "name": "title"},
                {"label": "Image", "type": "file", "name": "image"},
                {"label": "Link", "type": "commerce_links", "name": "destinations"},
            ], "default": [
                {"title": "Phones", "image": "https://placehold.co/600x600/f4f4f5/111827?text=Phones", "destinations": []},
                {"title": "Computers", "image": "https://placehold.co/600x600/f4f4f5/111827?text=Computers", "destinations": []},
                {"title": "Audio", "image": "https://placehold.co/600x600/f4f4f5/111827?text=Audio", "destinations": []},
                {"title": "Cameras", "image": "https://placehold.co/600x600/f4f4f5/111827?text=Cameras", "destinations": []},
            ]},
        ]},
        "html": '''<section class="pc-section">{% if heading %}<h2 class="pc-heading">{{ heading }}</h2>{% endif %}{% if items %}<div class="pc-categories">{% for item in items %}<a href="{{ item.destination_url or '#' }}" class="pc-category">{% if item.image %}<img src="{{ item.image }}" alt="{{ item.title }}">{% endif %}{% if item.title %}<span>{{ item.title }}</span>{% endif %}</a>{% endfor %}</div>{% endif %}</section>''',
        "style": '''.pc-section{padding:clamp(2.5rem,6vw,6rem) clamp(1rem,4vw,4rem)}.pc-heading{margin:0 0 2rem;font-size:clamp(2rem,3vw,3rem)}.pc-categories{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:1rem}.pc-category{color:#111827;text-decoration:none;text-align:center;font-weight:650}.pc-category img{display:block;width:100%;aspect-ratio:1/1;object-fit:contain;padding:1rem;box-sizing:border-box;background:#f5f5f5;border-radius:50%;margin-bottom:.8rem}@media(max-width:1000px){.pc-categories{grid-template-columns:repeat(3,1fr)}}@media(max-width:560px){.pc-categories{grid-template-columns:repeat(2,1fr)}}''',
    },
    {
        "name": "Commerce Editorial Banner",
        "type": "Main",
        "model": {"block_name": "commerce_editorial_banner", "fields": [
            {"label": "Eyebrow", "type": "text", "name": "eyebrow", "default": "Designed for your lifestyle"},
            {"label": "Heading", "type": "text", "name": "heading", "default": "Build your perfect setup"},
            {"label": "Description", "type": "textarea", "name": "description", "default": "Combine products that work beautifully together, backed by local service and support."},
            {"label": "Button label", "type": "text", "name": "button_label", "default": "Explore collection"},
            {"label": "Button link", "type": "commerce_links", "name": "button_destinations", "multiple": False},
            {"label": "Button custom URL", "type": "normaltext", "name": "button_url", "default": ""},
            {"label": "Image", "type": "file", "name": "image", "default": "https://placehold.co/1400x900/111827/ffffff?text=Editorial+story"},
        ]},
        "html": '''<section class="pc-editorial">{% if image %}<img src="{{ image }}" alt="{{ heading }}">{% endif %}<div>{% if eyebrow %}<p>{{ eyebrow }}</p>{% endif %}{% if heading %}<h2>{{ heading }}</h2>{% endif %}{% if description %}<span>{{ description }}</span>{% endif %}{% if button_label %}<a href="{{ button_destinations_url or button_url or '#' }}">{{ button_label }}</a>{% endif %}</div></section>''',
        "style": '''.pc-editorial{display:grid;grid-template-columns:1.15fr .85fr;background:var(--store-role-30,#111827);color:#fff}.pc-editorial>img{width:100%;height:600px;object-fit:cover}.pc-editorial>div{display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:clamp(2rem,6vw,6rem)}.pc-editorial p{color:var(--store-highlight,var(--store-role-10,#ff4964));text-transform:uppercase;letter-spacing:.15em;font-size:.75rem;font-weight:700}.pc-editorial h2{margin:.5rem 0 1rem;font-size:clamp(2.2rem,4vw,4.5rem);line-height:1}.pc-editorial span{color:#cbd5e1;line-height:1.7}.pc-editorial a{margin-top:1.5rem;padding:.9rem 1.2rem;border-radius:.55rem;background:var(--ecommerce-action-background,var(--store-action,#111827));color:#fff;text-decoration:none;font-weight:700}@media(max-width:800px){.pc-editorial{grid-template-columns:1fr}.pc-editorial>img{height:360px}}''',
    },
    {
        "name": "Commerce Brand Showcase",
        "type": "Main",
        "model": {"block_name": "commerce_brand_showcase", "fields": [
            {"label": "Heading", "type": "text", "name": "heading", "default": "Featured brands"},
            {"label": "Brands", "type": "repeater", "name": "items", "fields": [
                {"label": "Brand name", "type": "text", "name": "title"},
                {"label": "Logo", "type": "file", "name": "image"},
                {"label": "Link", "type": "commerce_links", "name": "destinations"},
            ], "default": [{"title": "Brand one", "image": "https://placehold.co/360x180/ffffff/111827?text=Brand+1", "destinations": []},{"title": "Brand two", "image": "https://placehold.co/360x180/ffffff/111827?text=Brand+2", "destinations": []},{"title": "Brand three", "image": "https://placehold.co/360x180/ffffff/111827?text=Brand+3", "destinations": []}]},
        ]},
        "html": '''<section class="pc-section">{% if heading %}<h2 class="pc-heading">{{ heading }}</h2>{% endif %}{% if items %}<div class="pc-brands">{% for item in items %}<a href="{{ item.destination_url or '#' }}">{% if item.image %}<img src="{{ item.image }}" alt="{{ item.title }}">{% else %}{{ item.title }}{% endif %}</a>{% endfor %}</div>{% endif %}</section>''',
        "style": '''.pc-section{padding:clamp(2.5rem,6vw,6rem) clamp(1rem,4vw,4rem)}.pc-heading{margin:0 0 2rem;font-size:clamp(2rem,3vw,3rem)}.pc-brands{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));border:1px solid #e5e7eb}.pc-brands a{display:grid;place-items:center;min-height:150px;padding:1rem;border-right:1px solid #e5e7eb;color:#111827;text-decoration:none}.pc-brands img{width:100%;height:80px;object-fit:contain}@media(max-width:800px){.pc-brands{grid-template-columns:repeat(2,1fr)}}''',
    },
    {
        "name": "Commerce Article Grid",
        "type": "Main",
        "model": {"block_name": "commerce_article_grid", "fields": [
            {"label": "Heading", "type": "text", "name": "heading", "default": "Stories and guides"},
            {"label": "View all label", "type": "text", "name": "view_all_label", "default": "View all articles"},
            {"label": "View all link", "type": "commerce_links", "name": "view_all_destinations", "multiple": False},
            {"label": "View all custom URL", "type": "normaltext", "name": "view_all_url", "default": ""},
            {"label": "Articles", "type": "repeater", "name": "items", "fields": [
                {"label": "Category", "type": "text", "name": "category", "default": "Article"},
                {"label": "Title", "type": "text", "name": "title", "default": "New article"},
                {"label": "Summary", "type": "textarea", "name": "description", "default": "Add a short summary for this article."},
                {"label": "Image", "type": "file", "name": "image", "default": "https://placehold.co/900x720/e2e8f0/111827?text=New+article"},
                {"label": "Date", "type": "normaltext", "name": "date", "default": "Publication date"},
                {"label": "Link label", "type": "text", "name": "link_label", "default": "Read article"},
                {"label": "Link", "type": "commerce_links", "name": "destinations", "multiple": False},
                {"label": "Custom URL", "type": "normaltext", "name": "url", "default": ""},
            ], "default": [
                {"category": "Buying guides", "title": "How to choose the right headphones", "description": "Key features to consider for the perfect sound, comfort, and everyday use.", "image": "https://placehold.co/900x720/f1f5f9/111827?text=Headphones", "date": "May 14, 2024", "link_label": "Read article", "url": "#"},
                {"category": "Workspace", "title": "Create a workspace that inspires", "description": "Simple upgrades and smart layouts to boost focus and productivity.", "image": "https://placehold.co/900x720/e2e8f0/111827?text=Workspace", "date": "May 7, 2024", "link_label": "Read article", "url": "#"},
                {"category": "Gear & tech", "title": "The best compact cameras for travel", "description": "Lightweight picks that deliver stunning photos, wherever you go.", "image": "https://placehold.co/900x720/cbd5e1/111827?text=Camera", "date": "Apr 30, 2024", "link_label": "Read article", "url": "#"},
            ]},
        ]},
        "html": '''<section class="pc-article-section">
  <header class="pc-article-header">
    {% if heading %}<h2>{{ heading }}</h2>{% endif %}
    {% if view_all_label %}<a href="{{ view_all_destinations_url or view_all_url or '#' }}">{{ view_all_label }} <span aria-hidden="true">→</span></a>{% endif %}
  </header>
  {% if items %}<div class="pc-articles">{% for item in items %}
    <article class="pc-article-card">
      <a class="pc-article-image" href="{{ item.destination_url or item.url or '#' }}">{% if item.image %}<img src="{{ item.image }}" alt="{{ item.title }}">{% else %}<span></span>{% endif %}</a>
      <p class="pc-article-category">{{ item.category or '' }}</p>
      <h3><a href="{{ item.destination_url or item.url or '#' }}">{{ item.title or '' }}</a></h3>
      <p class="pc-article-description">{{ item.description or '' }}</p>
      <footer><span>{{ item.date or '' }}</span><i></i><a href="{{ item.destination_url or item.url or '#' }}">{{ item.link_label or '' }} <span aria-hidden="true">→</span></a></footer>
    </article>
  {% endfor %}</div>{% endif %}
</section>''',
        "style": '''.pc-article-section{padding:clamp(2.5rem,6vw,5.5rem) clamp(1rem,4vw,4rem);color:#111827;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.pc-article-header{display:flex;align-items:center;justify-content:space-between;gap:1.5rem;margin-bottom:2rem}.pc-article-header h2{margin:0;font-size:clamp(2rem,3vw,3.25rem);line-height:1.05;letter-spacing:-.035em}.pc-article-header a{color:#ff4964;text-decoration:none;font-size:.9rem;font-weight:600}.pc-article-header a span,.pc-article-card footer a span{display:inline-block;margin-left:.55rem;font-size:1.25em}.pc-articles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.5rem}.pc-article-card{min-width:0}.pc-article-image{display:block;overflow:hidden;border-radius:.4rem;background:#f1f5f9}.pc-article-image img,.pc-article-image>span{display:block;width:100%;aspect-ratio:1.22/1;object-fit:cover}.pc-article-card:hover img{transform:scale(1.025)}.pc-article-image img{transition:transform .25s ease}.pc-article-category{margin:1.15rem 0 .7rem;color:#ff4964;font-size:.72rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase}.pc-article-card h3{margin:0;font-size:1.22rem;line-height:1.3;letter-spacing:-.015em}.pc-article-card h3 a{color:inherit;text-decoration:none}.pc-article-description{min-height:3em;margin:.75rem 0 0;color:#6b7280;line-height:1.55}.pc-article-card footer{display:flex;align-items:center;gap:1rem;margin-top:1.35rem;color:#6b7280;font-size:.82rem}.pc-article-card footer i{display:block;width:1px;height:1rem;background:#9ca3af}.pc-article-card footer a{color:#ff4964;text-decoration:none;font-weight:600}@media(max-width:800px){.pc-articles{grid-template-columns:1fr}.pc-article-header{align-items:flex-start}.pc-article-description{min-height:0}}''',
    },
    {
        "name": "Commerce Rich Footer",
        "type": "Footer",
        "model": {"block_name": "commerce_rich_footer", "fields": [
            {"label": "Store name", "type": "text", "name": "store_name", "default": "Your Store"},
            {"label": "Short description", "type": "textarea", "name": "description", "default": "Quality products, straightforward shopping, and dependable local support."},
            {"label": "Email", "type": "email", "name": "email", "default": "hello@yourstore.com"},
            {"label": "Phone", "type": "phone", "name": "phone", "default": "+977 9800000000"},
            {"label": "Link columns", "type": "repeater", "name": "columns", "fields": [
                {"label": "Heading", "type": "text", "name": "title"},
                {"label": "Links", "type": "repeater", "name": "links", "fields": [{"label": "Label", "type": "text", "name": "label"},{"label": "Link", "type": "commerce_links", "name": "destinations", "multiple": False},{"label": "Custom URL", "type": "normaltext", "name": "url"}]},
            ], "default": [{"title": "Shop", "links": [{"label": "All products", "url": "#"},{"label": "New arrivals", "url": "#"}]},{"title": "Help", "links": [{"label": "Contact", "url": "#"},{"label": "Delivery", "url": "#"}]},{"title": "Company", "links": [{"label": "About", "url": "#"},{"label": "Privacy", "url": "#"}]}]},
        ]},
        "html": '''<footer class="pc-footer"><div class="pc-footer__main"><div>{% if store_name %}<h2>{{ store_name }}</h2>{% endif %}{% if description %}<p>{{ description }}</p>{% endif %}{% if email %}<a href="mailto:{{ email }}">{{ email }}</a>{% endif %}{% if phone %}<a href="tel:{{ phone }}">{{ phone }}</a>{% endif %}</div>{% for column in columns %}<nav><h3>{{ column.title }}</h3>{% for link in column.links %}<a href="{{ link.destination_url or link.url or '#' }}">{{ link.label }}</a>{% endfor %}</nav>{% endfor %}</div><div class="pc-footer__bottom">© {{ store_name }}. All rights reserved.</div></footer>''',
        "style": '''.pc-footer{padding:4rem clamp(1rem,4vw,4rem) 1.5rem;background:var(--store-role-30,var(--store-secondary));color:#fff}.pc-footer__main{display:grid;grid-template-columns:2fr repeat(3,1fr);gap:3rem}.pc-footer h2,.pc-footer h3{margin-top:0}.pc-footer p{max-width:480px;color:#94a3b8;line-height:1.7}.pc-footer a{display:block;margin:.65rem 0;color:#cbd5e1;text-decoration:none}.pc-footer a:hover{color:var(--store-highlight,#fff)}.pc-footer__bottom{margin-top:3rem;padding-top:1.5rem;border-top:1px solid color-mix(in srgb,currentColor 25%,transparent);color:#94a3b8;font-size:.85rem}@media(max-width:800px){.pc-footer__main{grid-template-columns:1fr 1fr}}''',
    },
]


BLOCK_IMAGES = {
    "Commerce Promo Hero": "/assets/ecommerce/images/builder-block-previews/commerce-promo-hero.png",
    "Commerce Product Shelf": "/assets/ecommerce/images/builder-block-previews/commerce-product-shelf.png",
    "Commerce Category Showcase": "/assets/ecommerce/images/builder-block-previews/commerce-category-showcase.png",
    "Commerce Editorial Banner": "/assets/ecommerce/images/builder-block-previews/commerce-editorial-banner.png",
    "Commerce Brand Showcase": "/assets/ecommerce/images/builder-block-previews/commerce-brand-showcase.png",
    "Commerce Article Grid": "/assets/ecommerce/images/builder-block-previews/commerce-article-grid.png",
    "Commerce Rich Footer": "/assets/ecommerce/images/builder-block-previews/commerce-rich-footer.png",
}


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
            frappe.get_doc({
                "doctype": "Ecommerce Block",
                "block_name": definition["name"],
                **values,
            }).insert(ignore_permissions=True)

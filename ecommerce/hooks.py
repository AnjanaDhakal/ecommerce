app_name = "ecommerce"
app_title = "Ecommerce"
app_publisher = "Anjana Dhakal"
app_description = "Independent ecommerce builder and storefront"
app_email = ""
app_license = "MIT"
app_home = "/ecommerce"

add_to_apps_screen = [
    {
        "name": "ecommerce",
        "title": "Ecommerce",
        "route": "/ecommerce",
    }
]

before_request = ["ecommerce.storefront_domains.route_wildcard_storefront"]

fixtures = [
    {"dt": "Ecommerce Block"},
    {"dt": "Ecommerce Template"},
]

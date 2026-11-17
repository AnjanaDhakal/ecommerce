from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from ecommerce.api import (
    _rewrite_storefront_links_for_custom_domain,
    _storefront_url,
)
from ecommerce.storefront_domains import (
    _storefront_request_subdomain,
    _storefront_subdomain_from_host,
    available_storefront_subdomain,
    route_wildcard_storefront,
    storefront_custom_domain,
    storefront_custom_domain_setup,
    storefront_custom_domain_target,
    storefront_subdomain,
)


class TestStorefrontDomains(TestCase):
    @patch("ecommerce.storefront_domains.frappe")
    def test_custom_domains_share_configured_cname_target(self, frappe_mock):
        frappe_mock.conf.get.return_value = "https://connect.pnd.bz/"

        self.assertEqual(storefront_custom_domain_target(), "connect.pnd.bz")
        self.assertEqual(
            storefront_custom_domain_setup("https://shop.example.com/path"),
            {
                "hostname": "shop.example.com",
                "record_type": "CNAME",
                "target": "connect.pnd.bz",
                "proxy": "Proxied",
            },
        )

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    @patch("ecommerce.api.frappe")
    def test_custom_domain_links_keep_current_browser_host(self, frappe_mock, _base_domain):
        frappe_mock.local = SimpleNamespace(
            request=SimpleNamespace(
                host="abc.dhakalanjana.com.np",
                scheme="https",
            )
        )
        frappe_mock.get_request_header.return_value = None
        frappe_mock.db.get_value.return_value = {
            "canonical_url": "https://data.pnd.bz",
            "custom_domain": "abc.dhakalanjana.com.np",
        }

        self.assertEqual(
            _storefront_url("WEB-1", "product", "Phone"),
            "https://abc.dhakalanjana.com.np/product/phone",
        )
        self.assertEqual(
            _rewrite_storefront_links_for_custom_domain(
                '<a href="https://data.pnd.bz/category/new">New</a>',
                "WEB-1",
            ),
            '<a href="https://abc.dhakalanjana.com.np/category/new">New</a>',
        )

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    def test_domain_like_name_uses_domain_without_tld(self, _base_domain):
        self.assertEqual(storefront_subdomain("oliz.com"), "oliz")
        self.assertEqual(
            storefront_subdomain("https://www.zuwa-cosmetic.com/products"),
            "zuwa-cosmetic",
        )

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    def test_extracts_custom_domain_alias(self, _base_domain):
        self.assertEqual(
            storefront_custom_domain("www.oliz.com"),
            "www.oliz.com",
        )
        self.assertEqual(
            storefront_custom_domain("https://www.anjana1.com/store"),
            "www.anjana1.com",
        )
        self.assertIsNone(storefront_custom_domain("oliz.shops.example.com"))
        self.assertIsNone(storefront_custom_domain("My Shop"))

    @patch("ecommerce.storefront_domains.frappe")
    def test_custom_domain_lookup_uses_complete_hostname(self, frappe_mock):
        frappe_mock.request = SimpleNamespace(
            host="target.dhakalanjana.com.np",
            path="/",
            query_string=b"",
            environ={"PATH_INFO": "/"},
        )
        frappe_mock.local.request = frappe_mock.request
        frappe_mock.form_dict = SimpleNamespace()
        frappe_mock.get_request_header.return_value = None
        frappe_mock.db.has_column.return_value = True
        frappe_mock.db.get_value.side_effect = [
            SimpleNamespace(name="WEB-TARGET"),
            "HOME-TARGET",
        ]

        route_wildcard_storefront()

        self.assertEqual(
            frappe_mock.db.get_value.call_args_list[0].args,
            (
                "Ecommerce Vendor Website",
                {
                    "custom_domain": "target.dhakalanjana.com.np",
                    "status": "Published",
                },
                ["name"],
            ),
        )
        self.assertEqual(frappe_mock.form_dict.website_id, "WEB-TARGET")

    @patch("ecommerce.storefront_domains.frappe")
    def test_published_custom_domain_serves_storefront_without_redirect(
        self, frappe_mock
    ):
        frappe_mock.request = SimpleNamespace(
            host="oliz.com",
            path="/product/phone",
            query_string=b"color=black",
            environ={"PATH_INFO": "/product/phone"},
        )
        frappe_mock.local.request = frappe_mock.request
        frappe_mock.form_dict = SimpleNamespace()
        frappe_mock.get_request_header.return_value = None
        frappe_mock.db.get_value.side_effect = [
            SimpleNamespace(name="WEB-1"),
            "HOME-1",
        ]

        route_wildcard_storefront()

        self.assertEqual(frappe_mock.db.get_value.call_args_list[0].args, (
            "Ecommerce Vendor Website",
            {"custom_domain": "oliz.com", "status": "Published"},
            ["name"],
        ))
        self.assertEqual(frappe_mock.form_dict.website_id, "WEB-1")
        self.assertEqual(frappe_mock.form_dict.entity_type, "product")
        self.assertEqual(frappe_mock.form_dict.slug, "phone")
        self.assertEqual(frappe_mock.request.path, "/storefront")
        self.assertEqual(frappe_mock.request.environ["PATH_INFO"], "/storefront")

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    def test_extracts_dynamic_storefront_subdomain(self, _base_domain):
        self.assertEqual(
            _storefront_subdomain_from_host("dhakal.shops.example.com"),
            "dhakal",
        )

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    def test_accepts_forwarded_host_with_port_and_proxy_chain(self, _base_domain):
        self.assertEqual(
            _storefront_request_subdomain(
                "mysite.com",
                "dhakal.shops.example.com:443, internal-proxy",
            ),
            "dhakal",
        )

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    def test_prefers_public_request_host(self, _base_domain):
        self.assertEqual(
            _storefront_request_subdomain(
                "dhakal.shops.example.com",
                "different-store.shops.example.com",
            ),
            "dhakal",
        )

    @patch("ecommerce.storefront_domains.storefront_base_domain", return_value="shops.example.com")
    def test_rejects_nested_or_unrelated_domains(self, _base_domain):
        self.assertIsNone(
            _storefront_subdomain_from_host("nested.dhakal.shops.example.com")
        )
        self.assertIsNone(
            _storefront_subdomain_from_host("dhakal.example.com")
        )

    @patch("ecommerce.storefront_domains._subdomain_is_used")
    def test_reuses_display_name_with_vendor_specific_address(self, is_used):
        is_used.side_effect = [True, False]

        self.assertEqual(
            available_storefront_subdomain("My Shop", "Vendor-00002"),
            "my-shop-vendor-00002",
        )

    @patch("ecommerce.storefront_domains._subdomain_is_used")
    def test_keeps_plain_address_when_name_is_available(self, is_used):
        is_used.return_value = False

        self.assertEqual(
            available_storefront_subdomain("My Shop", "Vendor-00001"),
            "my-shop",
        )

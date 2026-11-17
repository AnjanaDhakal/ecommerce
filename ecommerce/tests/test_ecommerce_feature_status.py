from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import call, patch

from ecommerce.api import set_ecommerce_feature_status as _feature_status_endpoint


set_ecommerce_feature_status = getattr(
    _feature_status_endpoint, "__wrapped__", _feature_status_endpoint
)


class TestEcommerceFeatureStatus(TestCase):
    @patch("ecommerce.api.get_vendor_id")
    @patch("ecommerce.api.frappe")
    def test_disabling_ecommerce_unpublishes_all_live_vendor_websites(
        self, frappe_mock, get_vendor_id_mock
    ):
        frappe_mock.request.method = "POST"
        frappe_mock.request.get_json.return_value = {"enabled": False}
        frappe_mock.session.user = "vendor@example.com"
        frappe_mock.get_all.return_value = ["WEB-1", "WEB-2"]
        get_vendor_id_mock.return_value = {"vendor_id": "VENDOR-1"}

        with patch("ecommerce.api._", side_effect=lambda value: value):
            result = set_ecommerce_feature_status()

        frappe_mock.get_all.assert_called_once_with(
            "Ecommerce Vendor Website",
            filters={
                "vendor_id": "VENDOR-1",
                "type": "Ecommerce",
                "status": "Published",
            },
            pluck="name",
        )
        self.assertEqual(
            frappe_mock.db.set_value.call_args_list,
            [
                call(
                    "Ecommerce Vendor Website",
                    "WEB-1",
                    "status",
                    "Draft",
                    update_modified=True,
                ),
                call(
                    "Ecommerce Vendor Website",
                    "WEB-2",
                    "status",
                    "Draft",
                    update_modified=True,
                ),
            ],
        )
        frappe_mock.defaults.set_user_default.assert_called_once_with(
            "ecommerce_ecommerce_enabled",
            "0",
            user="vendor@example.com",
            parenttype="User",
        )
        frappe_mock.db.commit.assert_called_once_with()
        self.assertFalse(result["data"]["enabled"])
        self.assertEqual(result["data"]["unpublished_websites"], 2)

    @patch("ecommerce.api.get_vendor_id")
    @patch("ecommerce.api.frappe")
    def test_enabling_ecommerce_does_not_publish_websites(
        self, frappe_mock, get_vendor_id_mock
    ):
        frappe_mock.request.method = "POST"
        frappe_mock.request.get_json.return_value = {"enabled": True}
        frappe_mock.session.user = "vendor@example.com"

        with patch("ecommerce.api._", side_effect=lambda value: value):
            result = set_ecommerce_feature_status()

        get_vendor_id_mock.assert_not_called()
        frappe_mock.get_all.assert_not_called()
        frappe_mock.db.set_value.assert_not_called()
        self.assertTrue(result["data"]["enabled"])
        self.assertEqual(result["data"]["unpublished_websites"], 0)

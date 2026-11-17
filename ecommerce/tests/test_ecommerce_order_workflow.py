from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

import frappe

from ecommerce.api import (
    _can_cancel_ecommerce_order,
    _can_confirm_ecommerce_order,
    confirm_ecommerce_order,
    update_ecommerce_order_status,
)


class TestEcommerceOrderWorkflow(TestCase):
    def setUp(self):
        frappe.local.flags = SimpleNamespace(in_test=True)

    def test_pending_order_can_be_confirmed_directly(self):
        self.assertTrue(_can_confirm_ecommerce_order("Pending"))

    def test_legacy_packed_order_remains_confirmable(self):
        self.assertTrue(_can_confirm_ecommerce_order("Packed"))

    def test_terminal_orders_cannot_be_confirmed_again(self):
        self.assertFalse(_can_confirm_ecommerce_order("Confirmed"))
        self.assertFalse(_can_confirm_ecommerce_order("Cancelled"))

    def test_only_unconfirmed_orders_can_be_cancelled(self):
        self.assertTrue(_can_cancel_ecommerce_order("Pending"))
        self.assertTrue(_can_cancel_ecommerce_order("Packed"))
        self.assertFalse(_can_cancel_ecommerce_order("Confirmed"))
        self.assertFalse(_can_cancel_ecommerce_order("Cancelled"))

    @patch("ecommerce.api._serialize_ecommerce_order")
    @patch("ecommerce.api._", side_effect=lambda message: message)
    @patch("ecommerce.api.now_datetime", return_value="2026-11-17 00:00:00")
    @patch("ecommerce.api._ecommerce_vendor_id", return_value="VENDOR-1")
    @patch("ecommerce.api.frappe")
    def test_pending_confirmation_deducts_stock_and_confirms_local_order(
        self, frappe_mock, _vendor_id_mock, _now_mock, _translate_mock, serialize_mock
    ):
        frappe_mock.request.method = "POST"
        item = SimpleNamespace(
            product_id="PRODUCT-1",
            product_name="Example product",
            variant_id="VARIANT-1",
            variant_name="Standard",
            quantity=2,
            unit_price=100,
        )
        ecommerce_order = MagicMock(
            vendor_id="VENDOR-1",
            system_order="",
            status="Pending",
            website="WEBSITE-1",
            pickup_branch="BRANCH-1",
            items=[item],
            customer_name="Customer",
            phone="9800000000",
            city_area="Kathmandu",
            delivery_address="Delivery address",
            destination_branch="BRANCH-2",
            order_note="",
            grand_total=250,
            delivery_amount=50,
            package_weight=1,
            package_qty=1,
            name="ECO-1",
        )
        ecommerce_order.name = "ECO-1"
        website = SimpleNamespace(name="WEBSITE-1")
        def get_doc(doctype, name=None):
            return {
                "Ecommerce Ecommerce Order": ecommerce_order,
                "Ecommerce Vendor Website": website,
            }[doctype]

        frappe_mock.get_doc.side_effect = get_doc
        frappe_mock.db.sql.side_effect = [
            [SimpleNamespace(name="ECO-1")],
            [SimpleNamespace(name="VARIANT-1", quantity=5)],
        ]
        frappe_mock.db.get_value.return_value = SimpleNamespace(
            name="PRODUCT-1",
            product_name="Example product",
            enable=True,
            continue_selling=False,
        )
        serialize_mock.return_value = {"name": "ECO-1"}

        result = confirm_ecommerce_order(order_id="ECO-1")

        self.assertEqual(result["status"], "success")
        frappe_mock.db.set_value.assert_called_once_with(
            "Ecommerce Product Variant",
            "VARIANT-1",
            "quantity",
            3.0,
            update_modified=False,
        )
        self.assertEqual(ecommerce_order.status, "Confirmed")
        self.assertEqual(ecommerce_order.system_order, "ECO-1")
        ecommerce_order.save.assert_called_once_with(ignore_permissions=True)
        frappe_mock.db.commit.assert_called_once()

    @patch("ecommerce.api._serialize_ecommerce_order")
    @patch("ecommerce.api._", side_effect=lambda message: message)
    @patch("ecommerce.api._ecommerce_vendor_id", return_value="VENDOR-1")
    @patch("ecommerce.api.frappe")
    def test_confirm_is_idempotent_when_system_order_already_exists(
        self, frappe_mock, _vendor_id_mock, _translate_mock, serialize_mock
    ):
        frappe_mock.request.method = "POST"
        ecommerce_order = MagicMock(
            vendor_id="VENDOR-1",
            system_order="SYSTEM-ORDER-1",
            status="Confirmed",
        )
        frappe_mock.db.sql.return_value = [SimpleNamespace(name="ECO-1")]
        frappe_mock.get_doc.return_value = ecommerce_order
        serialize_mock.return_value = {"name": "ECO-1"}

        result = confirm_ecommerce_order(order_id="ECO-1")

        self.assertEqual(result["status"], "success")
        self.assertIn("already confirmed", result["message"])
        frappe_mock.db.set_value.assert_not_called()
        frappe_mock.db.commit.assert_not_called()

    @patch("ecommerce.api._storefront_error")
    @patch("ecommerce.api._ecommerce_vendor_id", return_value="VENDOR-1")
    @patch("ecommerce.api.frappe")
    def test_pending_order_cannot_move_to_packed(
        self, frappe_mock, _vendor_id_mock, storefront_error_mock
    ):
        frappe_mock.request.method = "POST"
        frappe_mock.db.sql.return_value = [SimpleNamespace(name="ECO-1")]
        order = MagicMock(vendor_id="VENDOR-1", status="Pending")
        frappe_mock.get_doc.return_value = order
        storefront_error_mock.side_effect = lambda message, status_code=400: {
            "status": "error",
            "message": message,
            "status_code": status_code,
        }

        result = update_ecommerce_order_status("ECO-1", "Packed")

        self.assertEqual(result["status"], "error")
        self.assertIn("Pending to Packed", result["message"])
        order.save.assert_not_called()
        sql = frappe_mock.db.sql.call_args.args[0]
        self.assertIn("FOR UPDATE", sql)

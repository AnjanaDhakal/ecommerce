from datetime import datetime
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order import (
    EcommerceEcommerceOrder,
)


class TestEcommerceOrderNaming(TestCase):
    @patch(
        "ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order.now_datetime",
        return_value=datetime(2026, 10, 4),
    )
    @patch(
        "ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order.getseries",
        return_value="1",
    )
    @patch(
        "ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order.frappe"
    )
    def test_first_order_uses_owner_token_and_compact_date(
        self, frappe_mock, _series, _now
    ):
        order = SimpleNamespace(vendor_id="Test-TR")

        EcommerceEcommerceOrder.autoname(order)

        self.assertEqual(order.name, "E-Test-TR-261004")

    @patch(
        "ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order.now_datetime",
        return_value=datetime(2026, 10, 4),
    )
    @patch(
        "ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order.getseries",
        return_value="2",
    )
    @patch(
        "ecommerce.ecommerce.doctype.ecommerce_ecommerce_order.ecommerce_ecommerce_order.frappe"
    )
    def test_later_same_day_orders_receive_unique_suffix(
        self, frappe_mock, _series, _now
    ):
        order = SimpleNamespace(vendor_id="Test / TR")

        EcommerceEcommerceOrder.autoname(order)

        self.assertEqual(order.name, "E-Test-TR-261004-2")

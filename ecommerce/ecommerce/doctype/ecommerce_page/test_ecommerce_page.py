# Copyright (c) 2025, Ecommerce contributors
# See license.txt

import json
from unittest.mock import Mock, patch

import frappe
from frappe.tests.utils import FrappeTestCase
from ecommerce.api import (
	_apply_builder_page_template,
	_apply_catalogue_template_defaults,
	_builder_block_has_user_content,
	_builder_value_has_content,
	_extract_storefront_section,
	_merge_builder_template_fields,
)


class TestEcommercePage(FrappeTestCase):
	def test_catalogue_defaults_populate_fresh_template_blocks(self):
		field_value = {
			"header": [{
				"block_details": {"model": {
					"block_name": "header_navigation",
					"fields": [{"name": "menu_categories", "type": "categories", "value": []}],
				}},
			}],
			"main": [
				{"block_details": {"model": {
					"block_name": "commerce_product_shelf",
					"fields": [{"name": "product_list", "type": "product"}],
				}}},
				{"block_details": {"model": {
					"block_name": "commerce_category_showcase",
					"fields": [{
						"name": "items",
						"type": "repeater",
						"value": [{"title": "Sample", "image": "sample-category.png"}],
					}],
				}}},
				{"block_details": {"model": {
					"block_name": "commerce_brand_showcase",
					"fields": [{"name": "items", "type": "repeater", "value": []}],
				}}},
			],
			"footer": [],
		}
		products = [frappe._dict(name=f"PRODUCT-{index}") for index in range(1, 7)]
		categories = [
			frappe._dict(
				name=f"CATEGORY-{index}",
				categories_name=f"Category {index}",
				categories_logo=None,
			)
			for index in range(1, 5)
		]
		brands = [
			frappe._dict(name="BRAND-1", brand_name="Brand One", brand_logo="brand.png"),
			frappe._dict(name="BRAND-2", brand_name="Brand Two", brand_logo=None),
		]

		result = _apply_catalogue_template_defaults(
			field_value,
			products=products,
			categories=categories,
			brands=brands,
		)

		header_field = result["header"][0]["block_details"]["model"]["fields"][0]
		product_field = result["main"][0]["block_details"]["model"]["fields"][0]
		category_field = result["main"][1]["block_details"]["model"]["fields"][0]
		brand_field = result["main"][2]["block_details"]["model"]["fields"][0]
		self.assertEqual(header_field["value"], ["CATEGORY-1", "CATEGORY-2", "CATEGORY-3"])
		self.assertEqual(product_field["value"], [
			"PRODUCT-1", "PRODUCT-2", "PRODUCT-3", "PRODUCT-4", "PRODUCT-5",
		])
		self.assertEqual(
			[item["title"] for item in category_field["value"]],
			["Category 1", "Category 2", "Category 3"],
		)
		self.assertEqual(category_field["value"][0]["image"], "sample-category.png")
		self.assertEqual(
			category_field["value"][0]["destinations"][0]["value"],
			"CATEGORY-1",
		)
		self.assertEqual(len(brand_field["value"]), 1)
		self.assertEqual(brand_field["value"][0]["title"], "Brand One")
		self.assertEqual(brand_field["value"][0]["image"], "brand.png")
		self.assertEqual(field_value["header"][0]["block_details"]["model"]["fields"][0]["value"], [])

	def test_apply_template_replaces_root_layout(self):
		page = frappe._dict(
			name="HOME-1",
			parent1=None,
			template="Old Template",
			field_value=json.dumps(
				{
					"seo_title": "Keep this title",
					"header": [{"name": "Old Header"}],
					"main": [{"name": "Old Main"}],
					"footer": [{"name": "Old Footer"}],
				}
			),
		)
		page.save = Mock()
		template = frappe._dict(
			name="New Template",
			page_name="New Template",
			data_json=json.dumps(
				{
					"starter_content": {
						"header": [{"name": "New Header"}],
						"main": [{"name": "New Main"}],
						"footer": [{"name": "New Footer"}],
					}
				}
			),
		)

		with (
			patch(
				"ecommerce.api._builder_effective_field_value",
				side_effect=lambda _page, value: value,
			),
			patch(
				"ecommerce.api._builder_page_tree_names",
				return_value=[page.name],
			),
		):
			result = _apply_builder_page_template(page, template)

		self.assertEqual(page.template, template.name)
		self.assertEqual(page.field_value["header"], [{"name": "New Header"}])
		self.assertEqual(page.field_value["main"], [{"name": "New Main"}])
		self.assertEqual(page.field_value["footer"], [{"name": "New Footer"}])
		self.assertEqual(page.field_value["seo_title"], "Keep this title")
		self.assertEqual(result["previous_template"], "Old Template")
		page.save.assert_called_once_with(ignore_permissions=True)

	def test_empty_builder_block_has_no_user_content(self):
		block = {
			"block_details": {
				"model": {
					"fields": [
						{"name": "title", "type": "text"},
						{"name": "items", "type": "repeater", "value": None},
					]
				}
			}
		}

		self.assertFalse(_builder_block_has_user_content(block))

	def test_default_values_are_not_user_content(self):
		block = {
			"block_details": {
				"model": {
					"fields": [
						{"name": "grid", "default": 3, "value": 3},
					]
				}
			}
		}

		self.assertFalse(_builder_block_has_user_content(block))

	def test_entered_value_is_user_content(self):
		block = {
			"block_details": {
				"model": {
					"fields": [
						{"name": "title", "type": "text", "value": "Featured"},
					]
				}
			}
		}

		self.assertTrue(_builder_block_has_user_content(block))

	def test_template_defaults_survive_page_merge(self):
		template_fields = [
			{"name": "heading", "type": "text", "default": "Latest stories"},
			{
				"name": "items",
				"type": "repeater",
				"default": [{"title": "A practical buying guide"}],
			},
		]

		merged = _merge_builder_template_fields(template_fields)

		self.assertEqual(merged[0]["value"], "Latest stories")
		self.assertEqual(
			merged[1]["value"],
			[{"title": "A practical buying guide"}],
		)

		# Defaults must be cloned so editing one page cannot mutate the template.
		merged[1]["value"][0]["title"] = "Changed"
		self.assertEqual(
			template_fields[1]["default"][0]["title"],
			"A practical buying guide",
		)

	def test_saved_empty_value_is_preserved(self):
		merged = _merge_builder_template_fields(
			[{"name": "heading", "default": "Latest stories"}],
			[{"name": "heading", "value": ""}],
		)

		self.assertEqual(merged[0]["value"], "")

	def test_field_defaults_are_valid_preview_content(self):
		article_defaults = [
			{"title": "How to choose the right headphones"},
			{"title": "Create a workspace that inspires"},
			{"title": "The best compact cameras for travel"},
		]

		self.assertTrue(_builder_value_has_content(article_defaults))

	def test_storefront_shell_ignores_article_header_and_footer(self):
		rendered_html = """
		<header><nav>Store navigation</nav></header>
		<div class="main">
			<article><header>Article heading</header><footer>Article date</footer></article>
		</div>
		<footer><footer class="site-footer">Store footer</footer></footer>
		"""

		self.assertEqual(
			_extract_storefront_section(rendered_html, "header"),
			"<nav>Store navigation</nav>",
		)
		self.assertEqual(
			_extract_storefront_section(rendered_html, "footer"),
			'<footer class="site-footer">Store footer</footer>',
		)

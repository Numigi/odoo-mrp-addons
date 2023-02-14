# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import collections
from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _action_compute_bom_cost(self):
        # Find all the product with BOM and not in material of other product
        finished_products = self.search(
            [
                ("bom_ids", "!=", False),
                ("bom_ids.active", "=", True),
                ("bom_line_ids", "=", False)
            ]
        )
        # Ex: material_product_level_dict = {
        #     0: Finished product (not in material of other product),
        #     1: Component of Level 0 with BOM
        #     2: Component of Level 1 with BOM
        #     ............
        # }
        material_product_level_dict = {}
        for finished_product in finished_products:
            next_level = 0
            if next_level in material_product_level_dict:
                material_product_level_dict[next_level] |= finished_product
            else:
                material_product_level_dict = {
                    0: finished_product,
                }
            next_level += 1
            finish_bom = self.env['mrp.bom']._bom_find(product=finished_product)
            finish_bom_lines = finish_bom.bom_line_ids
            finish_semi_bom_lines = finish_bom_lines.filtered(lambda r: r.child_bom_id)
            current_semi_bom_lines = finish_semi_bom_lines
            while current_semi_bom_lines:
                if next_level in material_product_level_dict:
                    material_product_level_dict[next_level] |= \
                        current_semi_bom_lines.mapped("product_id")
                else:
                    material_product_level_dict.update({
                        next_level: current_semi_bom_lines.mapped("product_id"),
                    })
                next_semi_bom_lines = \
                    current_semi_bom_lines.mapped(
                        "child_bom_id.bom_line_ids"
                    ).filtered(lambda r: r.child_bom_id)
                if next_semi_bom_lines:
                    next_level += 1
                    current_semi_bom_lines = next_semi_bom_lines
                else:
                    current_semi_bom_lines = False
        order_dict = \
            collections.OrderedDict(
                sorted(material_product_level_dict.items(), reverse=True)
            )
        updated_bom_cost_products = self.browse()
        for products in order_dict.values():
            for product in products.filtered(
                lambda r: r not in updated_bom_cost_products
            ):
                product.button_bom_cost()
                updated_bom_cost_products |= product

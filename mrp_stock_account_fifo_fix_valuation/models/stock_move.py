# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _is_mrp_unbuilt(self):
        return (
            self.location_id.usage == "internal"
            and self.location_dest_id.usage == "production"
        )

    def _run_valuation(self, quantity=None):
        """
        Override to prevent get the product standard price when doing valuation on
        picking return when stock valuation for FIFO and valuation is
        in automated mode on the product category of the product.
        """
        value_to_return = super()._run_valuation(quantity)
        if self._is_mrp_unbuilt():
            product_category = self.product_id.categ_id
            if (
                self.origin_returned_move_id
                and product_category.property_cost_method == "fifo"
                and product_category.property_valuation == "real_time"
            ):
                value = -self.origin_returned_move_id.price_unit * self.product_uom_qty
                value_to_return = (
                    value if quantity is None or not self.value else self.value
                )
                if self.product_id.cost_method in ["fifo"]:
                    self.write(
                        {
                            "value": value_to_return,
                            "price_unit": -self.origin_returned_move_id.price_unit,
                        }
                    )
        return value_to_return

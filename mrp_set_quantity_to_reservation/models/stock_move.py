# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "stock.move"

    def _set_quantities_to_reservation(self):
        for move in self:
            if move.state not in ('partially_available', 'assigned'):
                continue
            for move_line in move.move_line_ids:
                if move.has_tracking == 'none' or (
                        move.picking_type_id.use_existing_lots
                        and move_line.lot_id) or (
                        move.picking_type_id.use_create_lots
                        and move_line.lot_name) or (
                        not move.picking_type_id.use_existing_lots
                        and not move.picking_type_id.use_create_lots):
                    move_line.qty_done = move_line.product_uom_qty

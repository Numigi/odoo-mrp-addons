# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_backorder_move_vals(self):
        self.ensure_one()
        return {
            'state': 'confirmed',
            # 'reservation_date': self.reservation_date,
            'move_orig_ids': [(4, m.id) for m in self.mapped('move_orig_ids')],
            'move_dest_ids': [(4, m.id) for m in self.mapped('move_dest_ids')]
        }

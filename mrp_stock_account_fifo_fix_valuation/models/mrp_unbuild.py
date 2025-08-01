# Copyright 2025 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def _generate_consume_moves(self):
        moves = super()._generate_consume_moves()
        for unbuild in self:
            for move in moves:
                move.write(
                    {
                        "origin_returned_move_id": (
                            unbuild.mo_id.finished_move_line_ids.filtered(
                                lambda move: move.product_id == unbuild.product_id
                            ).move_id.id
                            if unbuild.mo_id
                            else False
                        ),
                    }
                )
                moves += move
        return moves

# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpProduction__mrp_cost(models.Model):

    _inherit = "mrp.production"

    def _cal_price(self, consumed_moves):
        super()._cal_price(consumed_moves)

        if self._should_set_finished_move_cost():
            self._set_finished_move_cost(consumed_moves)

        return True

    def _should_set_finished_move_cost(self):
        move = self._get_main_finished_move()
        return move and move.state not in ("done", "cancel") and move.quantity_done > 0

    def _set_finished_move_cost(self, consumed_moves):
        move = self._get_main_finished_move()
        qty_done = self.__get_qty_done(move)
        value = self._get_finished_move_value(consumed_moves)
        move.price_unit = value / qty_done if qty_done else 0
        move.value = value
        self.__set_time_lines_recorded()

    def _get_main_finished_move(self):
        return self.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_id
        )

    def _get_finished_move_value(self, consumed_moves):
        work_center_cost = self._get_workcenter_cost()
        return sum([-m.value for m in consumed_moves]) + work_center_cost

    def _get_workcenter_cost(self):
        return sum(
            line._get_cost()
            for line in self.__get_unrecorded_time_lines()
        )

    def __get_qty_done(self, move):
        return move.product_uom._compute_quantity(
            move.quantity_done,
            move.product_id.uom_id,
        )

    def __set_time_lines_recorded(self):
        lines = self.__get_unrecorded_time_lines()
        lines.write({"cost_already_recorded": True})

    def __get_unrecorded_time_lines(self):
        return self.mapped("workorder_ids.time_ids").filtered(lambda line: 
            line.date_end and not line.cost_already_recorded)

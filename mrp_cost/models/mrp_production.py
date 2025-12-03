# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero

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

    @api.multi
    def action_view_cost_analysis(self):
        """ Redirects to the Cost Analysis report """
        self.ensure_one()
        # Ensure the report action ID matches the one defined in XML
        action = self.env.ref(
            'mrp_cost.action_report_mrp_cost_analysis').report_action(
            self)
        return action

    def _get_raw_material_costs(self):
        """
        Calculate the total cost of raw materials consumed.
        Relies on stock valuation layers (stock.valuation.layer) or move valuation (value field).
        This simplified version uses the 'value' field from 'stock.move'.
        For FIFO/AVCO, the 'value' on the move reflects the actual cost.
        For Standard Price, it reflects the standard cost.
        """
        self.ensure_one()
        # Find moves that consumed materials for this production order
        consumed_moves = self.move_raw_ids.filtered(
            lambda m: m.state == 'done' and not m.scrapped)
        total_cost = 0.0
        lines_data = []
        # Sum the absolute value as consumed moves have negative values
        for move in consumed_moves:
            # Value should be negative for consumed goods, use abs() or *-1
            move_cost = abs(move.value)
            total_cost += move_cost
            lines_data.append(
                {'product_id': move.product_id, 'qty': move.product_uom_qty,
                    # Quantity in the move's UoM
                    'uom_name': move.product_uom.name, 'cost': move_cost,
                    'unit_cost': abs(move.price_unit) if not float_is_zero(
                        move.product_uom_qty,
                        precision_rounding=move.product_uom.rounding) else 0.0,
                    # Or move_cost / move.product_uom_qty
                    'bom_line_id': move.bom_line_id.id if move.bom_line_id else None
                    # For linking in the report
                })
        return total_cost, lines_data

    def _get_operation_costs(self):
        """
        Calculate the total cost of manufacturing operations based on time lines.
        Now includes Operator detail grouped by Operation + Operator.
        """
        self.ensure_one()
        total_cost = 0.0
        lines_data = []

        for workorder in self.workorder_ids:
            # Case 1: The work order has detailed time lines (tracking)
            if workorder.time_ids:
                # Dictionary to group by operator on this work order
                # Key: User ID (or 'Unknown' if empty)
                ops_by_user = {}

                for time_line in workorder.time_ids:
                    # time_line is a mrp.workcenter.productivity record
                    user = time_line.user_id
                    user_id = user.id if user else False
                    operator_name = user.name if user else "Unknown"

                    # Duration in hours
                    duration_hours = time_line.duration / 60.0
                    cost_hour = time_line.workcenter_id.costs_hour
                    cost = duration_hours * cost_hour

                    if user_id not in ops_by_user:
                        ops_by_user[user_id] = {
                            'operation_id': workorder.operation_id.id if workorder.operation_id else None,
                            'operation_name': workorder.operation_id.name if workorder.operation_id else workorder.name,
                            'workcenter_name': workorder.workcenter_id.name,
                            'operator': operator_name, 'duration': 0.0,
                            'cost_hour': cost_hour, 'cost': 0.0, }

                    # Sum of durations and costs for this operator
                    ops_by_user[user_id]['duration'] += duration_hours
                    ops_by_user[user_id]['cost'] += cost

                # Add consolidated lines to the main list
                for user_id, data in ops_by_user.items():
                    lines_data.append(data)
                    total_cost += data['cost']

            # Case 2: No time lines, but a manual duration on the work order
            elif workorder.duration > 0:
                duration_hours = workorder.duration / 60.0
                cost_hour = workorder.workcenter_id.costs_hour
                operation_cost = duration_hours * cost_hour

                lines_data.append({
                    'operation_id': workorder.operation_id.id if workorder.operation_id else None,
                    'operation_name': workorder.operation_id.name if workorder.operation_id else workorder.name,
                    'workcenter_name': workorder.workcenter_id.name,
                    'operator': 'Unspecified',  # No time_ids = no tracked operator
                    'duration': duration_hours, 'cost_hour': cost_hour,
                    'cost': operation_cost, })
                total_cost += operation_cost

        return total_cost, lines_data

    def _get_scrap_costs(self):
        """
        Calculate the total cost of scrapped materials.
        This relies on the 'value' of the scrap moves.
        """
        self.ensure_one()
        total_cost = 0.0
        lines_data = []
        scrap_moves = self.env['stock.move'].search(
            [('production_id', '=', self.id), ('scrapped', '=', True),
                ('state', '=', 'done')])
        # Alternative: Search stock.scrap linked to production_id
        # scraps = self.env['stock.scrap'].search([('production_id', '=', self.id)])

        for move in scrap_moves:
            # Value might be positive or negative depending on context, use abs()
            move_cost = abs(move.value)
            total_cost += move_cost
            lines_data.append(
                {'product_id': move.product_id, 'qty': move.product_uom_qty,
                    'uom_name': move.product_uom.name, 'cost': move_cost,
                    'unit_cost': abs(move.price_unit) if not float_is_zero(
                        move.product_uom_qty,
                        precision_rounding=move.product_uom.rounding) else 0.0, })
        return total_cost, lines_data

    def _get_byproduct_costs_and_qty(self):
        """
        Calculate the value and quantity of by-products produced.
        By-products typically reduce the overall cost of the main product.
        Their value might be based on their own standard price or cost.
        """
        self.ensure_one()
        total_value = 0.0  # By-products usually have a value, reducing net cost
        lines_data = []
        # Find finished moves that are NOT the main product
        byproduct_moves = self.move_finished_ids.filtered(
            lambda m: m.state == 'done' and m.product_id != self.product_id)
        for move in byproduct_moves:
            # Value is usually positive for produced goods
            move_value = move.value
            total_value += move_value
            lines_data.append(
                {'product_id': move.product_id, 'qty': move.product_uom_qty,
                    'uom_name': move.product_uom.name, 'value': move_value,
                    # This is the value credited
                    'unit_value': move.price_unit if not float_is_zero(
                        move.product_uom_qty,
                        precision_rounding=move.product_uom.rounding) else 0.0, })
        return total_value, lines_data

    def _get_finished_product_data(self):
        """ Get quantity and UoM for the main finished product. """
        self.ensure_one()
        finished_moves = self.move_finished_ids.filtered(
            lambda m: m.state == 'done' and m.product_id == self.product_id)
        total_qty = sum(finished_moves.mapped('product_uom_qty'))
        uom = self.product_uom_id  # Assume all finished moves use the MO's UoM for simplicity
        return total_qty, uom

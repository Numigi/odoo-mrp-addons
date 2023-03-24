# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    manufacturing_order_id = fields.Many2one(
        "mrp.production",
        string="Related Manufacturing Order",
    )
    workorder_id = fields.Many2one(
        "mrp.workorder",
        string="Work Order",
    )

    @api.multi
    def _timesheet_postprocess_values(self, values):
        """
        In the case where an account analytic
        line is created from a manufacturing order,
        we consider the cost per hour of the work center
        instead of the cost per hour per employee.

        """
        result = super(AccountAnalyticLine, self)._timesheet_postprocess_values(values)
        sudo_self = self.sudo()
        for timesheet in sudo_self:
            if timesheet.manufacturing_order_id:
                result[timesheet.id] = {}

        return result

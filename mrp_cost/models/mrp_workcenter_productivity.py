# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):

    _inherit = "mrp.workcenter.productivity"

    cost_already_recorded = fields.Boolean()

    def _get_cost(self):
        return self.duration / 60 * self.workcenter_id.costs_hour

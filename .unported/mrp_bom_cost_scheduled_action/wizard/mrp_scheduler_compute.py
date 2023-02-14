# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class MrpSchedulerCompute(models.TransientModel):
    _name = 'mrp.scheduler.compute'
    _description = 'Run Scheduler Manually'

    @api.multi
    def bom_cost_calculation(self):
        self.ensure_one()
        self.env['product.product']._action_compute_bom_cost()
        return {'type': 'ir.actions.act_window_close'}

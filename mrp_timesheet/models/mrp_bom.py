# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    project_id = fields.Many2one('project.project', string='Project',
                                 domain=[('allow_timesheets', '=', True)],
                                 default=lambda
                                     self: self._default_project_id())

    @api.model
    def _default_project_id(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'mrp_timesheet.project_id')) or False

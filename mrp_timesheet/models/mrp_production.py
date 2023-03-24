# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    project_id = fields.Many2one(
        "project.project", domain=[("allow_timesheets", "=", True)], string="Project"
    )
    analytic_account_id = fields.Many2one(
        related="project_id.analytic_account_id", store=True, readonly=True
    )

    @api.onchange("bom_id", "bom_id.project_id")
    def _onchange_project_id(self):
        if self.bom_id and self.bom_id.project_id:
            self.project_id = self.bom_id.project_id.id

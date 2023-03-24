# -*- coding: utf-8 -*-
# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_id = fields.Many2one(
        "project.project", string="Project", domain=[("allow_timesheets", "=", True)]
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res["project_id"] = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp_timesheet.project_id", default=False)
        )

        return res

    @api.model
    def set_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "mrp_timesheet.project_id", self.project_id.id
        )

        super(ResConfigSettings, self).set_values()

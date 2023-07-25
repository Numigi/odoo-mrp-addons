# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RevisionBom(models.Model):
    _name = 'revision.bom'
    _inherit = ['revision.bom', 'mail.thread', 'mail.activity.mixin']

    component_line_ids = fields.One2many(tracking=True)
    operation_line_ids = fields.One2many(tracking=True)
    approval_line_ids = fields.One2many(tracking=True)
    name = fields.Char(tracking=True)
    type_id = fields.Many2one(tracking=True)
    apply_on = fields.Selection(tracking=True)
    product_id = fields.Many2one(tracking=True)
    new_rev_product_id = fields.Many2one(tracking=True)
    bom_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    user_id = fields.Many2one(tracking=True)
    effectivity = fields.Selection(tracking=True)
    effective_date = fields.Date(tracking=True)
    note = fields.Text(tracking=True)
    revision_count = fields.Integer(tracking=True)
    allow_apply_change = fields.Boolean(tracking=True)
    user_can_approve = fields.Boolean(tracking=True)
    user_can_reject = fields.Boolean(tracking=True)
    is_active = fields.Boolean(tracking=True)
    is_approve = fields.Boolean(tracking=True)
    is_reject = fields.Boolean(tracking=True)
    approval_check = fields.Boolean(tracking=True)
    new_bom_id = fields.Many2one(tracking=True)
    main_bom_id = fields.Many2one(tracking=True)
    state = fields.Selection(tracking=True)
    is_approval = fields.Boolean(tracking=True)
    button_boolean = fields.Boolean(tracking=True)
    is_check = fields.Boolean(tracking=True)

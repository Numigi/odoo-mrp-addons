# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, fields

class ProductTemplate(models.Model):
    """ Inherit product.template to add the cost analysis button. """
    _inherit = 'product.template'

    # Field to control button visibility (alternative to mrp_product_qty)
    # This checks if there's *any* BoM for variants of this template
    bom_count = fields.Integer(compute='_compute_bom_count', string='BoM Count')

    @api.multi
    @api.depends('product_variant_ids.bom_ids') # Recalculate if variants or their BoMs change
    def _compute_bom_count(self):
        """ Compute if any variant has a BoM. """
        for template in self:
            # Check if any variant of this template has at least one BoM
            template.bom_count = self.env['mrp.bom'].search_count([
                ('product_tmpl_id', '=', template.id)
            ])


    @api.multi
    def action_view_cost_analysis_template(self):
        """ Redirects to the Cost Analysis report for product variants """
        self.ensure_one()
        # Get all product variants linked to this template
        product_ids = self.mapped('product_variant_ids').ids
        # Ensure the report action ID matches the one defined in XML
        action = self.env.ref(
            'mrp_cost.action_report_product_cost_analysis').report_action(product_ids)
        return action

class ProductProduct(models.Model):
    """ Inherit product.product for specific actions if needed, or if BoMs are only on variant. """
    _inherit = 'product.product'

    # Field to make button visibility easier on the product.product form
    bom_count = fields.Integer(compute='_compute_bom_count', string='BoM Count')

    @api.multi
    @api.depends('bom_ids')
    def _compute_bom_count(self):
        """ Compute if this specific product variant has a BoM. """
        for product in self:
            # Count BoMs where this product is the main output
            product.bom_count = self.env['mrp.bom'].search_count([
                '|',
                ('product_id', '=', product.id),
                '&',
                ('product_id', '=', False),
                ('product_tmpl_id', '=', product.product_tmpl_id.id)
            ])


    @api.multi
    def action_view_cost_analysis_product(self):
        """ Redirects to the Cost Analysis report for this product variant """
        self.ensure_one()
        # Ensure the report action ID matches the one defined in XML
        action = self.env.ref(
            'mrp_cost.action_report_product_cost_analysis').report_action(self)
        return action
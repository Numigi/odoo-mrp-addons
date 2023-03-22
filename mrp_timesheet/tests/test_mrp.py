# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import SavepointCase


class TestMRP(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_id = cls.env.ref('project.project_project_2').sudo()
        product_id = cls.env['product.product'].create({
            'name': 'Test',
            'type': 'product',
        })
        cls.project_mrp_id = cls.env.ref('project.project_project_1').sudo()
        res_config_id = cls.env['res.config.settings'].create(
            {'project_id':

                 cls.project_mrp_id.id})
        res_config_id.execute()
        cls.bom_1 = cls.env['mrp.bom'].create({
            'product_id': product_id.id,
            'product_tmpl_id': product_id.product_tmpl_id.id,
            'product_uom_id': product_id.uom_id.id,
            'product_qty': 1.0,
            'routing_id': cls.env.ref('mrp.mrp_routing_3').id,
        })
        cls.mo = cls.env['mrp.production'].new({
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'product_qty': 2.0,
            'bom_id': cls.bom_1.id,
        })

        cls.mo._onchange_project_id()
        mo_vals = cls.env['mrp.production']._convert_to_write(cls.mo._cache)
        cls.mo = cls.env['mrp.production'].create(mo_vals)

    def test_bom_project_id(self):
        assert self.bom_1.project_id == self.project_mrp_id

    def test_mo_project_id(self):
        assert self.mo.project_id == self.project_mrp_id
        assert self.mo.analytic_account_id == self.project_mrp_id.analytic_account_id
        assert self.mo.analytic_account_id

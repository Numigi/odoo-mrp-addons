# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import TransactionCase


class TestMRP(TransactionCase):
    def setUp(self):
        super(TestMRP, self).setUp()
        self.project_id = self.env.ref("project.project_project_2").sudo()
        product_id = self.env["product.product"].create(
            {
                "name": "Test",
                "type": "product",
            }
        )
        self.project_mrp_id = self.env.ref("project.project_project_1").sudo()
        res_config_id = self.env["res.config.settings"].create(
            {"project_id": self.project_mrp_id.id}
        )
        res_config_id.execute()
        self.bom_1 = self.env["mrp.bom"].create(
            {
                "product_id": product_id.id,
                "product_tmpl_id": product_id.product_tmpl_id.id,
                "product_uom_id": product_id.uom_id.id,
                "product_qty": 1.0,
                "routing_id": self.env.ref("mrp.mrp_routing_3").id,
            }
        )
        self.mo = self.env["mrp.production"].new(
            {
                "product_id": product_id.id,
                "product_uom_id": product_id.uom_id.id,
                "product_qty": 2.0,
                "bom_id": self.bom_1.id,
            }
        )

        self.mo._onchange_project_id()
        mo_vals = self.env["mrp.production"]._convert_to_write(self.mo._cache)
        self.mo = self.env["mrp.production"].create(mo_vals)

    def test_bom_project_id(self):
        assert self.bom_1.project_id == self.project_mrp_id

    def test_mo_project_id(self):
        assert self.mo.project_id == self.project_mrp_id
        assert self.mo.analytic_account_id == self.project_mrp_id.analytic_account_id
        assert self.mo.analytic_account_id

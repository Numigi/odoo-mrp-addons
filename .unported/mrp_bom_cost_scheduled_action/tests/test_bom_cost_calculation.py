# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import SavepointCase


class TestBomCostCalculation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.finished_1 = cls.env["product.product"].create({
            "name": "Finished 1",
            "type": "product",
            "standard_price": 99,
        })
        cls.semi_component_1 = cls.env["product.product"].create({
            "name": "Semi Component 1",
            "type": "product",
            "standard_price": 99,
        })
        cls.semi_component_2 = cls.env["product.product"].create({
            "name": "Semi Component 2",
            "type": "product",
            "standard_price": 99,
        })
        cls.component_1 = cls.env["product.product"].create({
            "name": "Component 1",
            "type": "product",
            "standard_price": 100,
        })
        cls.component_2 = cls.env["product.product"].create({
            "name": "Component 2",
            "type": "product",
            "standard_price": 100,
        })
        cls.component_3 = cls.env["product.product"].create({
            "name": "Component 3",
            "type": "product",
            "standard_price": 100,
        })
        cls.semi_component_1_bom = cls.env["mrp.bom"].create({
            "product_tmpl_id": cls.semi_component_1.product_tmpl_id.id,
            "product_qty": 1,
            "bom_line_ids": [
                (0, 0, {
                    "product_id": cls.component_1.id,
                    "product_qty": 1,
                }),
                (0, 0, {
                    "product_id": cls.component_2.id,
                    "product_qty": 1,
                }),
                (0, 0, {
                    "product_id": cls.semi_component_2.id,
                    "product_qty": 1,
                }),
            ]
        })
        cls.semi_component_2_bom = cls.env["mrp.bom"].create({
            "product_tmpl_id": cls.semi_component_2.product_tmpl_id.id,
            "product_qty": 1,
            "bom_line_ids": [
                (0, 0, {
                    "product_id": cls.component_3.id,
                    "product_qty": 2,
                }),
            ]
        })
        cls.finsihed_1_bom = cls.env["mrp.bom"].create({
            "product_tmpl_id": cls.finished_1.product_tmpl_id.id,
            "product_qty": 1,
            "bom_line_ids": [
                (0, 0, {
                    "product_id": cls.semi_component_1.id,
                    "product_qty": 1,
                }),
                (0, 0, {
                    "product_id": cls.component_3.id,
                    "product_qty": 2,
                }),
            ]
        })

    def test_mrp_bom_cost_scheduled_action_by_cron(self):
        cron = self.env.ref("mrp_bom_cost_scheduled_action.ir_cron_update_bom_cost")
        cron.method_direct_trigger()
        self.assertNotEqual(self.semi_component_1.standard_price, 99)
        self.assertNotEqual(self.finished_1.standard_price, 999)

    def test_mrp_bom_cost_scheduled_action_by_wizard(self):
        wizard = self.env["mrp.scheduler.compute"].create({})
        wizard.bom_cost_calculation()
        self.assertNotEqual(self.semi_component_1.standard_price, 99)
        self.assertNotEqual(self.finished_1.standard_price, 999)

    def test_mrp_bom_cost_multi_bom_level_calculation(self):
        cron = self.env.ref("mrp_bom_cost_scheduled_action.ir_cron_update_bom_cost")
        cron.method_direct_trigger()
        self.assertEqual(self.semi_component_2.standard_price, 200)
        self.assertEqual(self.semi_component_1.standard_price, 400)
        self.assertEqual(self.finished_1.standard_price, 600)

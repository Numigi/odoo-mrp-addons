# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase


class TestMRP(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "cost_method": "fifo",
            }
        )

        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
            }
        )

        cls.product_c = cls.env["product.product"].create(
            {
                "name": "Product C",
                "type": "product",
            }
        )

        cls.workcenter_cost = 100
        cls.workcenter = cls.env["mrp.workcenter"].create(
            {
            "name": "My Work Center",
            "costs_hour": cls.workcenter_cost,
        })

        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_a.id,
                "product_tmpl_id": cls.product_a.product_tmpl_id.id,
                "bom_line_ids": [
                    (0, 0, cls._get_bom_line_vals(cls.product_b, 1)),
                    (0, 0, cls._get_bom_line_vals(cls.product_c, 2)),
                ]
            })

        cls.order = cls.env["mrp.production"].create(
            {
                "product_id": cls.product_a.id,
                "product_uom_id": cls.product_a.uom_id.id,
                "bom_id": cls.bom.id,
            }
        )
        cls.workorder = cls.env["mrp.workorder"].create(
            {
                "name": "/",
                "production_id": cls.order.id,
                "workcenter_id": cls.workcenter.id,
            }
        )

    @classmethod
    def _get_bom_line_vals(cls, product, quantity):
        return {
            "product_id": product.id,
            "product_qty": quantity,
            "product_uom_id": product.uom_id.id,
        }

    @classmethod
    def _get_time_vals(cls, hours):
        now = datetime.now()
        return {
            "workcenter_id": cls.workcenter.id,
            "date_start": now - timedelta(hours=hours),
            "date_end": now,
            "loss_id": cls.env.ref("mrp.category_productive").id,
        }

    def test_component_cost(self):
        self.product_b.standard_price = 200
        self.product_c.standard_price = 300
        self._run_production()
        move = self.order.move_finished_ids
        assert move.value == 800  # 1 * 200 + 2 * 300

    def test_workcenter_cost(self):
        self.workorder.write({"time_ids": [(0, 0, self._get_time_vals(2))]})
        self._run_production()
        move = self.order.move_finished_ids
        assert move.value == 200  # 2 hours * 100

    def _run_production(self):
        wizard = self.env['mrp.product.produce'].with_context({
            'active_id': self.order.id,
            'active_ids': [self.order.id],
        }).create({
            'product_qty': 1.0,
        })
        wizard._onchange_product_qty()
        wizard.do_produce()
        self.order.post_inventory()

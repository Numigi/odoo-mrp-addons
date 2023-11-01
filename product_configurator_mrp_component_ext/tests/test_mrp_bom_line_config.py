# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class MrpBomLineConfig(TransactionCase):
    def setUp(self):
        super(MrpBomLineConfig, self).setUp()

        self.product_id = self.env.ref("product.product_product_3")

        # create bom
        self.bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_id.product_tmpl_id.id,
                "product_qty": 1.00,
                "type": "normal",
                "ready_to_produce": "all_available",
            }
        )

        # create MRP Bom Line Conf
        self.bom_line_conf_id = self.env["mrp.bom.line.config"].create(
            {
                "bom_id": self.bom_id.id,
                "product_tmpl_id": self.product_id.product_tmpl_id.id,
                "product_qty": 1.00,
            }
        )

    def test_00_user_access_MrpBomLineConfig(self):
        user_id = self.env.ref("base.user_demo")
        self.bom_line_conf_id.with_user(user_id)

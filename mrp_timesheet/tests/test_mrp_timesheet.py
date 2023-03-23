# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import datetime, timedelta, time

from odoo import fields
from pytz import timezone, utc

from .test_mrp import TestMRP


class TestMRPWorkOrder(TestMRP):
    def setUp(self):
        super(TestMRPWorkOrder, self).setUp()
        day = datetime.date(datetime.today())

        self.workcenter_id = self.env["mrp.workcenter"].create(
            {
                "name": "Assembly Line",
                "costs_hour": 40,
            }
        )
        if day.weekday() in (5, 6):
            day -= timedelta(days=2)
        tz = timezone(self.workcenter_id.resource_calendar_id.tz)

        def time_to_string_utc_datetime(time):
            return fields.Datetime.to_string(
                tz.localize(datetime.combine(day, time)).astimezone(utc)
            )

        self.mo.button_plan()
        self.workorder_id = self.mo.workorder_ids[0]

        date_start = time_to_string_utc_datetime(time(10, 43, 22))
        date_end = time_to_string_utc_datetime(time(11, 43, 22))

        self.env["mrp.workcenter.productivity"].create(
            {
                "workcenter_id": self.workcenter_id.id,
                "date_start": date_start,
                "date_end": date_end,
                "loss_id": self.env.ref("mrp.block_reason7").id,
                "description": self.env.ref("mrp.block_reason7").name,
                "user_id": self.env.ref("base.user_demo").id,
                "workorder_id": self.workorder_id.id,
            }
        )
        # duration => 60min
        self.analytic_line_id = self.env["account.analytic.line"].search(
            [
                ("manufacturing_order_id", "=", self.mo.id),
                ("workorder_id", "=", self.workorder_id.id),
            ]
        )
        assert self.analytic_line_id

    def test_analytic_line_employee(self):
        assert self.analytic_line_id.employee_id == self.env.ref("hr.employee_qdp")

    def test_analytic_line_project(self):
        assert self.analytic_line_id.project_id == self.project_mrp_id

    def test_analytic_line_account_id(self):
        assert (
            self.analytic_line_id.account_id == self.project_mrp_id.analytic_account_id
        )

    def test_analytic_line_unit_amount(self):
        # Expected (60 / 60) => 1
        assert self.analytic_line_id.unit_amount == 1

    def test_analytic_line_amount(self):
        # Expected (-60 / 60) * 40 => - 40
        assert self.analytic_line_id.amount == -40

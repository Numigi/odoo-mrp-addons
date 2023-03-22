# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import datetime, timedelta, time

from odoo import fields
from pytz import timezone, utc

from .test_mrp import TestMRP


class TestMRPWorkOrder(TestMRP):

    @classmethod
    def setUpClass(cls):
        super(TestMRPWorkOrder, cls).setUpClass()
        day = datetime.date(datetime.today())

        cls.workcenter_id = cls.env.ref('mrp.mrp_workcenter_0')
        if day.weekday() in (5, 6):
            day -= timedelta(days=2)
        tz = timezone(cls.workcenter_id.resource_calendar_id.tz)

        def time_to_string_utc_datetime(time):
            return fields.Datetime.to_string(
                tz.localize(datetime.combine(day, time)).astimezone(utc)
            )

        cls.mo.button_plan()
        print('===========================', cls.mo.analytic_account_id)
        cls.workorder_id = cls.mo.workorder_ids[0]

        date_start = time_to_string_utc_datetime(time(10, 43, 22))
        date_end = time_to_string_utc_datetime(time(10, 56, 22))

        cls.env['mrp.workcenter.productivity'].create({
            'workcenter_id': cls.workcenter_id.id,
            'date_start': date_start,
            'date_end': date_end,
            'loss_id': cls.env.ref('mrp.block_reason7').id,
            'description': cls.env.ref('mrp.block_reason7').name,
            'user_id': cls.env.ref('base.user_demo').id,
            'workorder_id':cls.workorder_id.id
        })

    def test_create_analytic_line(self):
        analytic_line_id = self.env['account.analytic.line'].search(
            [('manufacturing_order_id', '=', self.mo.id),
             (
                 'workorder_id',
                 '=',
                 self.workorder_id.id)
             ])
        assert analytic_line_id
        assert analytic_line_id.employee_id == self.env.ref(
            'hr.employee_qdp')

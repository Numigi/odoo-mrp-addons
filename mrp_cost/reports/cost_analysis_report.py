# -*- coding: utf-8 -*-
# Part of the new public module for MRP cost analysis.

from odoo import api, models
from odoo.tools import float_is_zero


class ReportCostAnalysis(models.AbstractModel):
    """ Abstract Model for Cost Analysis report QWeb """
    _name = 'report.mrp_cost.report_cost_analysis_template'
    _description = 'MRP Cost Analysis Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        productions = self.env['mrp.production'].browse(docids).filtered(
            lambda p: p.state == 'done')

        if not productions:
            return {'doc_ids': docids, 'doc_model': 'mrp.production', 'docs': [],
                'message': 'No completed Manufacturing Orders found.'}

        products_data = {}
        # Odoo 12: Use mapped to iterate over unique products
        products = productions.mapped('product_id')

        for product in products:
            # Filter MOs related to this specific product
            mos = productions.filtered(lambda p: p.product_id == product)

            total_raw_cost = 0.0
            total_ops_cost = 0.0
            total_scrap_cost = 0.0
            total_byproduct_value = 0.0
            total_finished_qty = 0.0

            all_raw_lines = []
            all_ops_lines = []
            all_scrap_lines = []
            all_byproduct_lines = []

            for mo in mos:
                # Retrieve costs using methods defined in mrp_production.py
                raw_cost, raw_lines = mo._get_raw_material_costs()
                ops_cost, ops_lines = mo._get_operation_costs()
                scrap_cost, scrap_lines = mo._get_scrap_costs()
                byproduct_value, byproduct_lines = mo._get_byproduct_costs_and_qty()
                finished_qty, _ = mo._get_finished_product_data()

                total_raw_cost += raw_cost
                total_ops_cost += ops_cost
                total_scrap_cost += scrap_cost
                total_byproduct_value += byproduct_value
                total_finished_qty += finished_qty

                all_raw_lines.extend(raw_lines)
                all_ops_lines.extend(ops_lines)
                all_scrap_lines.extend(scrap_lines)
                all_byproduct_lines.extend(byproduct_lines)

            # Consolidate lines data
            # Group raw materials by product
            final_raw_lines = self._consolidate_lines(all_raw_lines, ['product_id'])

            # UPDATE: Group operations by Operation, Workcenter, AND Operator
            final_ops_lines = self._consolidate_lines(all_ops_lines,
                ['operation_id', 'workcenter_name', 'operator'])

            # Group scraps and byproducts by product
            final_scrap_lines = self._consolidate_lines(all_scrap_lines, ['product_id'])
            final_byproduct_lines = self._consolidate_lines(all_byproduct_lines,
                ['product_id'])

            # Calculate Net Cost and Unit Cost
            net_total_cost = (
                        total_raw_cost + total_ops_cost + total_scrap_cost - total_byproduct_value)
            unit_cost = 0.0
            if not float_is_zero(total_finished_qty, precision_digits=5):
                unit_cost = net_total_cost / total_finished_qty

            # Get UoM from the first MO (assuming consistency across MOs)
            main_uom = mos[0].product_uom_id if mos else self.env['uom.uom']

            products_data[product.id] = {'product': product,
                'total_finished_qty': total_finished_qty, 'main_uom': main_uom,
                'mo_count': len(mos), 'raw_material_lines': final_raw_lines,
                'operation_lines': final_ops_lines, 'scrap_lines': final_scrap_lines,
                'byproduct_lines': final_byproduct_lines,
                'total_raw_cost': total_raw_cost, 'total_ops_cost': total_ops_cost,
                'total_scrap_cost': total_scrap_cost,
                'total_byproduct_value': total_byproduct_value,
                'net_total_cost': net_total_cost, 'unit_cost': unit_cost,
                'currency': self.env.user.company_id.currency_id, }

        docs = list(products_data.values())

        return {'doc_ids': docids, 'doc_model': 'mrp.production', 'docs': docs,
            'message': False}

    def _consolidate_lines(self, lines, group_keys):
        """
        Helper to group and sum lines based on a list of keys.
        Updated to handle composite keys (e.g. Operation + Operator).
        """
        if not lines or not group_keys:
            return lines

        consolidated = {}

        for line in lines:
            # Create a unique composite key tuple based on all keys in group_keys
            # Handle Odoo recordsets by using their ID, otherwise use the value
            current_key = tuple(
                line.get(k).id if hasattr(line.get(k), 'id') else line.get(k) for k in
                group_keys)

            if current_key not in consolidated:
                # Initialize the group with data from the first line found
                consolidated[current_key] = line.copy()
                # Ensure numeric fields are initialized for summation
                consolidated[current_key]['qty'] = consolidated[current_key].get('qty',
                    0.0)
                consolidated[current_key]['cost'] = consolidated[current_key].get(
                    'cost', 0.0)
                # Initialize duration if present (specific to operations)
                if 'duration' in line:
                    consolidated[current_key]['duration'] = consolidated[
                        current_key].get('duration', 0.0)
            else:
                # Aggregate quantities and costs
                consolidated[current_key]['qty'] += line.get('qty', 0.0)
                consolidated[current_key]['cost'] += line.get('cost', 0.0)
                if 'duration' in line:
                    consolidated[current_key]['duration'] += line.get('duration', 0.0)

            # Recalculate unit costs/values after aggregation
            qty = consolidated[current_key]['qty']
            cost = consolidated[current_key]['cost']

            # Calculate unit cost or unit value, avoiding division by zero
            if not float_is_zero(qty, precision_digits=5):
                if 'unit_cost' in consolidated[current_key]:
                    consolidated[current_key]['unit_cost'] = cost / qty
                if 'unit_value' in consolidated[current_key]:
                    consolidated[current_key]['unit_value'] = cost / qty
            else:
                if 'unit_cost' in consolidated[current_key]:
                    consolidated[current_key]['unit_cost'] = 0.0
                if 'unit_value' in consolidated[current_key]:
                    consolidated[current_key]['unit_value'] = 0.0

        return list(consolidated.values())


class ReportProductCostAnalysis(models.AbstractModel):
    """ Abstract Model for Product Cost Analysis report QWeb """
    _name = 'report.mrp_cost.report_product_cost_analysis_tmpl'
    _description = 'Product Cost Analysis Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Fetch data for the report based on product variants """
        # Find all *done* production orders for the given product variant IDs
        productions = self.env['mrp.production'].search(
            [('product_id', 'in', docids), ('state', '=', 'done')])

        # Reuse the logic from the MO-based report
        report_model = self.env['report.mrp_cost.report_cost_analysis_template']
        report_data = report_model._get_report_values(productions.ids, data=data)

        # Adjust context if needed (e.g., indicate it's product-based)
        report_data['report_origin'] = 'product'
        return report_data
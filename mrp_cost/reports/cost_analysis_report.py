# -*- coding: utf-8 -*-
# Part of the new public module for MRP cost analysis.

from odoo import api, models

class ReportCostAnalysis(models.AbstractModel):
    """ Abstract Model for Cost Analysis report QWeb """
    _name = 'report.mrp_cost.report_cost_analysis_template'
    _description = 'MRP Cost Analysis Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Fetch data for the report """
        docs = []
        productions = self.env['mrp.production'].browse(docids).filtered(lambda p: p.state == 'done')

        if not productions:
             # Handle cases where no production orders are done or found
             # Maybe raise an error or return an empty structure
             # For now, return structure indicating no MOs processed
             return {
                 'doc_ids': docids,
                 'doc_model': 'mrp.production',
                 'docs': [],
                 'message': 'No completed Manufacturing Orders found for the selection.'
             }


        # Group productions by finished product for the report structure
        # Similar to the original get_lines logic
        products_data = {}
        product_productions = productions.grouped('product_id')

        for product, mos in product_productions.items():
            # Get costs for this group of MOs producing the same product
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

            # Consolidate lines data if needed (e.g., group raw materials by product)
            # For simplicity, we pass all lines for now. Template can group/sum.
            final_raw_lines = self._consolidate_lines(all_raw_lines, ['product_id'])
            final_ops_lines = self._consolidate_lines(all_ops_lines, ['operation_id', 'workcenter_name']) # Or just operation_id
            final_scrap_lines = self._consolidate_lines(all_scrap_lines, ['product_id'])
            final_byproduct_lines = self._consolidate_lines(all_byproduct_lines, ['product_id'])


            # Calculate net cost and unit cost
            net_total_cost = total_raw_cost + total_ops_cost + total_scrap_cost - total_byproduct_value
            unit_cost = net_total_cost / total_finished_qty if total_finished_qty else 0.0

            # Get the UoM from the first MO (assuming consistency)
            main_uom = mos[0].product_uom_id if mos else self.env['uom.uom']

            products_data[product.id] = {
                'product': product,
                'total_finished_qty': total_finished_qty,
                'main_uom': main_uom,
                'mo_count': len(mos),
                'raw_material_lines': final_raw_lines,
                'operation_lines': final_ops_lines,
                'scrap_lines': final_scrap_lines,
                'byproduct_lines': final_byproduct_lines, # Use byproduct value later
                'total_raw_cost': total_raw_cost,
                'total_ops_cost': total_ops_cost,
                'total_scrap_cost': total_scrap_cost,
                'total_byproduct_value': total_byproduct_value,
                'net_total_cost': net_total_cost,
                'unit_cost': unit_cost,
                'currency': self.env.user.company_id.currency_id, # Currency from company
            }

        # Convert dict to list for the template
        docs = list(products_data.values())

        return {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': docs, # This list contains the aggregated data per product
            'message': False # No error message
        }

    def _consolidate_lines(self, lines, group_keys):
        """ Helper to group and sum lines based on keys """
        # Example: group raw materials by product_id
        # This requires careful handling of UoMs if they differ
        # For simplicity in this example, we'll assume UoM is consistent or we use the base UoM
        # A more robust version might convert quantities before summing.

        # Basic consolidation for quantity and cost/value based on the first key for now
        if not lines or not group_keys:
            return lines

        key_field = group_keys[0] # Simplistic grouping by the first key
        consolidated = {}

        for line in lines:
            key_value = line.get(key_field)
            # Handle recordsets vs IDs if necessary
            key_id = key_value.id if hasattr(key_value, 'id') else key_value

            if key_id not in consolidated:
                consolidated[key_id] = line.copy() # Start with the first line's data
                # Ensure 'qty' and 'cost'/'value' are initialized if missing, although they should exist
                consolidated[key_id]['qty'] = consolidated[key_id].get('qty', 0.0)
                consolidated[key_id]['cost'] = consolidated[key_id].get('cost', consolidated[key_id].get('value', 0.0))
            else:
                # Sum quantities and costs/values
                # WARNING: This assumes UoMs are compatible. A real implementation
                # should check UoMs and potentially convert before summing.
                consolidated[key_id]['qty'] += line.get('qty', 0.0)
                consolidated[key_id]['cost'] += line.get('cost', line.get('value', 0.0))
                # Recalculate unit cost/value after summing
                qty = consolidated[key_id]['qty']
                cost = consolidated[key_id]['cost']
                if 'unit_cost' in consolidated[key_id]:
                     consolidated[key_id]['unit_cost'] = cost / qty if not float_is_zero(qty, precision_digits=5) else 0.0
                if 'unit_value' in consolidated[key_id]:
                    consolidated[key_id]['unit_value'] = cost / qty if not float_is_zero(qty, precision_digits=5) else 0.0

        return list(consolidated.values())

class ReportProductCostAnalysis(models.AbstractModel):
    """ Abstract Model for Product Cost Analysis report QWeb """
    # This report is triggered from the product/template form
    _name = 'report.mrp_cost.report_product_cost_analysis_tmpl'
    _description = 'Product Cost Analysis Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Fetch data for the report based on product variants """
        # Find all *done* production orders for the given product variant IDs
        productions = self.env['mrp.production'].search([
            ('product_id', 'in', docids),
            ('state', '=', 'done')
        ])

        # Reuse the logic from the MO-based report
        report_model = self.env['report.mrp_cost.report_cost_analysis_template']
        report_data = report_model._get_report_values(productions.ids, data=data)

        # Adjust context if needed (e.g., indicate it's product-based)
        report_data['report_origin'] = 'product'
        return report_data
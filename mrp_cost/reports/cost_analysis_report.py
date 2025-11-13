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
                'message': 'Aucun ordre de fabrication terminé trouvé.'}

        products_data = {}

        # --- CORRECTION ODOO 12 ---
        # 1. Récupérer les produits uniques
        products = productions.mapped('product_id')

        # 2. Itérer directement sur le RecordSet des produits (pas de .items())
        for product in products:
            # 3. Filtrer manuellement les OFs pour ce produit
            mos = productions.filtered(lambda p: p.product_id == product)

            # --- Le reste du code reste identique ---
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

            # Consolidate lines data
            final_raw_lines = self._consolidate_lines(all_raw_lines, ['product_id'])
            final_ops_lines = self._consolidate_lines(all_ops_lines,
                ['operation_id', 'workcenter_name'])
            final_scrap_lines = self._consolidate_lines(all_scrap_lines, ['product_id'])
            final_byproduct_lines = self._consolidate_lines(all_byproduct_lines,
                ['product_id'])

            net_total_cost = total_raw_cost + total_ops_cost + total_scrap_cost - total_byproduct_value
            unit_cost = net_total_cost / total_finished_qty if total_finished_qty else 0.0

            main_uom = mos[0].product_uom_id if mos else self.env['uom.uom']

            # On utilise product.id comme clé pour le dictionnaire final
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
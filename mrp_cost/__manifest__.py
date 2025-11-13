# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "MRP Cost",
    "version": "2.1.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Recognize the accounting cost of manufacturing orders",
    "depends": [
        "mrp",
        "stock_account",
    ],
    'data': [
        'views/mrp_production_view.xml',
        'views/product_view.xml',
        'views/report_cost_analysis.xml',

    ],
    "installable": True,
}

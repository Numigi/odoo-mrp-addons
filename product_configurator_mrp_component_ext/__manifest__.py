# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Configurator Manufacturing Components ext",
    "version": "1.0.0",
    "category": "Manufacturing",
    "summary": """Extended fonctionnalities of BOM
    Support for configurable products""",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "AGPL-3",
    "website": "https://numigi.com/r/home",
    "depends": ["product_configurator_mrp_component"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}

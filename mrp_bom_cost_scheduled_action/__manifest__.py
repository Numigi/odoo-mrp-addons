# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "MRP BoM Cost Scheduled Action",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    "category": "Mrp",
    "summary": "MRP BoM Cost Scheduled Action",
    "depends": [
        "mrp_bom_cost",
    ],
    "data": [
        # Data
        "data/cron_data.xml",
        # Wizard
        "wizard/mrp_scheduler_compute.xml",
    ],
    "installable": True,
}

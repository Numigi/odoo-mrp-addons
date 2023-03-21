# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "MRP Timesheet",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Mrp",
    "summary": "Visualize the manufacturing orders times in the timesheets",
    "depends": [
        "account",
        "hr_timesheet",
        "mrp_analytic",
        "project",
    ],
    "data": [
        'views/res_config_settings_views.xml',
        'views/mrp_bom_views.xml',
        'views/mrp_production_views.xml',
    ],
    "installable": True,
}

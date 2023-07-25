# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sync PLM Chatter",
    "version": "1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "mrp",
    "depends": ["sync_plm", "document_url"],
    "summary": """
        Adds the possiblity to attach external documents to an ECO (product revision),
        and to trace field modifications on form view.
        """,
    "data": [
        "views/revision_bom_views.xml",
    ],
    "installable": True,
}

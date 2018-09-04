# -*- coding: utf-8 -*-
{
    'name': "OLAP Reporting Base",

    'summary': """Generic Reporting Base""",

    'description': """
OLAP Reporting Base
===================

Manage the creation of reports on Odoo objects.
    """,
    'version': '0.1',

    'author': "Unipart Digital",
    'website': "http://www.unipart.digital",

    'category': "Extra Tools",
    'depends': ['base',
                'project',
                'edi'],  # FIXME: Should not depend on EDI, but needs the patching of BaseModel.

    'data': [
        "security/ir.model.access.csv",
        "data/project_data.xml",
        "views/report_menu_views.xml",
        "views/report_views.xml",
    ],
}

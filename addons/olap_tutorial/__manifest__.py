# -*- coding: utf-8 -*-
{
    'name': "UDES Reporting Tutorial",
    'version': '0.1',

    'author': "Unipart Digital",
    'website': "http://www.unipart.digital",

    'category': "Extra Tools",
    'depends': ['olap',
                'stock'],

    'data': [
        'data/olap_report_data.xml',
        "data/ir_cron.xml",
        'views/report_tutorial_views.xml',
        'views/report_tutorial_viewer_views.xml',
    ],
}

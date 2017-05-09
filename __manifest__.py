# -*- coding: utf-8 -*-
{
    'name' : 'ENJOY TRAVEL',
    'version' : '1.0',
    'summary': 'Sistema el control de autos y casas de renta',
    'description': """
ENJOY
====================
Sistema el control de autos y casas de renta
    """,
    'category': 'enjoy',
    'website': 'https://www.enjoycuba.es',
    'images' : ['images/accounts.jpeg','images/bank_statement.jpeg','images/cash_register.jpeg','images/chart_of_accounts.jpeg','images/customer_invoice.jpeg','images/journal_entries.jpeg'],
    'depends' : ['base_setup', 'report'],
    'data': [
        'security/enjoy_groups.xml',
        'security/ir.model.access.csv',
        'vistas/_menu.xml',
        'vistas/auto.xml',
        'vistas/modelo.xml',
        'vistas/lugar.xml',
        'vistas/viajes.xml',
        'vistas/transfer.xml',
        'vistas/tablilla.xml',
        'vistas/casa.xml',
        'vistas/servicio.xml',
        'vistas/zona.xml',
        'vistas/provincia.xml',
        'vistas/reporte.xml',
        'vistas/comision.xml',
        'vistas/catalogo.xml',
        'workflows/workflow_reporte.xml',
        'report/report_enjoy_casa.xml',
        'report/report_enjoy_catalogo.xml',
        'report/report_casa.xml',
        'wizard/enjoy_reporte_mail.xml',
        'security/enjoy_rules.xml',
    ],
    'demo': [
        # 'demo/presupueto_demo.xml',
    ],
    'qweb': [
        'static/src/xml/widget_radi.xml'
    ],
    'js': ['static/src/js/widget_radio.js'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

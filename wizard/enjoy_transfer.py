# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import tools, _
from odoo.modules.module import get_module_resource

from datetime import date, datetime
import smtplib

class enjoy_Reporte_Base(models.Model):
    _name = "enjoy.report.mail"
    _description = "enjoy Reporte Base"

    company_id = fields.Many2one('res.company', string='Empresa', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    catalogo_id = fields.Many2one('enjoy.catalogo', 'Catálogo', required=True)
    destino_ids = fields.One2many('enjoy.destino','report_id','Remitentes')

    @api.multi
    def imprimir_reporte(self):
        result = self.env['report'].get_action(self, 'enjoy.report_enjoy_catalogo')
        for d in self.destino_ids:
            sender = d.name
            receivers = d.name
            message = "%s" % self.catalogo_id.name
            smtpObj = smtplib.SMTP(host='smtp.uci.cu', port=25)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.ehlo()
            smtpObj.login(user="roche", password="Camilita0712*")
            smtpObj.sendmail(sender, receivers, message)
            print "Successfully sent email"

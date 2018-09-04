# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _


class RTBRecord(models.Model):
    _name = "olap_tutorial.record.receipt_to_bin"
    _inherit = "olap.report.record"
    _description = """Record the number of items received"""

    picking_id = fields.Many2one(
        'stock.picking', 'Picking', required=True, index=True)
    po_number = fields.Char('PO Number')
    scheduled_date = fields.Datetime('Scheduled Date')
    num_lines = fields.Integer('Line Count')


class RTBModel(models.AbstractModel):
    _name = "olap_tutorial.model.receipt_to_bin"
    _inherit = "olap.report.model"

    _record_model = RTBRecord._name
    _reported_model = 'stock.picking'

    @api.model
    def get_candidate_records(self):
        """Get all pickings updated in the last 24 hours"""
        goods_in_type = self.env.ref('stock.picking_type_in')
        max_age = datetime.now() - timedelta(hours=24)
        res = self.env[self._reported_model].search(
            [('picking_type_id', '=', goods_in_type.id),
             ('create_date', '>', fields.Datetime.to_string(max_age))])
        return res

    @api.model
    def update_records(self, candidates):
        ReceiptToBin = self.env[RTBRecord._name]

        existing_reports = ReceiptToBin.search(
            [('picking_id', 'in', candidates.ids)])

        existing_reports_by_picking = dict(existing_reports.groupby(
            lambda r: r.picking_id.id))

        for picking in candidates:
            vals = {
                'name': picking.name,
                'po_number': picking.origin,
                'scheduled_date': picking.scheduled_date,
                'num_lines': len(picking.move_lines),
            }

            if picking.id in existing_reports_by_picking.keys():
                existing_reports_by_picking[picking.id].write(vals)
            else:
                vals.update({'picking_id': picking.id})
                ReceiptToBin.create(vals)


class RTBViewer(models.TransientModel):
    _name = "olap_tutorial.report.viewer.receipt_to_bin"
    _inherit = "olap.report.viewer"
    _description = """Custom viewer for RTB report, summarises the report"""

    _record_model = RTBRecord._name

    mean_lines = fields.Integer('Mean Lines')
    total_lines = fields.Integer('Total Lines')

    rtb_record_ids = fields.One2many(RTBRecord._name, string="Report",
                                     compute='_compute_report')

    @api.multi
    def _compute_report(self):
        ReceiptToBin = self.env[RTBRecord._name]

        recs = ReceiptToBin.search(self.get_report_domain())
        self.mean_lines = self.mean(recs.mapped('num_lines'))
        self.total_lines = sum(recs.mapped('num_lines'))
        self.rtb_record_ids = recs

    @api.multi
    def action_compute_report(self):
        res = super(RTBViewer, self).action_compute_report()
        res.update({'name': _('RTB Report')})
        return res

    @api.model
    def mean(self, items):
        if items:
            return sum(items) / len(items)
        return 0

    @api.multi
    def get_report_domain(self):
        """Return a domain that represents the current state set on this record
        """
        self.ensure_one()
        return [('scheduled_date', '>', self.from_date),
                ('scheduled_date', '<', self.to_date)]

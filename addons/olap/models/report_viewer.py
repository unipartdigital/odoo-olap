# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, _


class ReportViewer(models.TransientModel):
    _name = "olap.report.viewer"
    _description = """Transient model, custom report can specify a few fields
    and then use this form to show a pre-filtered list of report records, and 
    optionally add some extra stuff, like a graph summarising the report 
    records, or totals.
    """

    def _default_from_date(self):
        max_age = datetime.now() - timedelta(days=30)
        return fields.Datetime.to_string(max_age)

    from_date = fields.Datetime('From:', default=_default_from_date)
    to_date = fields.Datetime('To:', default=fields.Datetime.now)

    @api.multi
    def _compute_report(self):
        raise NotImplementedError()

    @api.multi
    def action_compute_report(self):
        self.ensure_one()
        self._compute_report()
        return self.reload_view(_('Report'))

    @api.multi
    def reload_view(self, report_name):
        """Generate a dictionary to send to the UI to get it to leave edit-mode
        on the current record.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _(report_name),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'main'
        }

    @api.multi
    def get_report_domain(self):
        """Return a domain that represents the current state set on this record
        """
        return []

    @api.multi
    def action_goto_export_view(self):
        # TODO: goto actual export view, rather than pre-filtered list view.
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Report Export'),
            'res_model': self._record_model,
            'view_mode': 'tree',
            'target': 'main',
            'domain': self.get_report_domain(),
        }

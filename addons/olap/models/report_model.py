# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ReportModel(models.AbstractModel):
    _name = "olap.report.model"
    _description = """Abstract model that implements the custom code for
    finding report candidates, and creating/updating report records for them.
    """

    # The model that is used when creating report records.
    _record_model = None
    # The model that is the one primarily being reported on
    _reported_model = None

    @api.model
    def get_candidate_records(self):
        """Get records of the tracked model that are candidates for
        creating/updating reports."""
        raise NotImplementedError()

    @api.model
    def update_records(self, candidates):
        """update reports for all candidates.
        """
        raise NotImplementedError()

    @api.multi
    def action_view_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Report'),
            'res_model': self._record_model,
            'view_mode': 'tree',
            'target': 'main',
        }

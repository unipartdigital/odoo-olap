# -*- coding: utf-8 -*-
import logging
import traceback

from odoo.exceptions import UserError

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    """Extend ``project.task`` to include Report information"""
    _inherit = 'project.task'

    report_id = fields.Many2one('olap.report',
                                string="EDI Document",
                                index=True, ondelete='cascade')


class Report(models.Model):
    _name = "olap.report"
    _description = """Holds references to the abstract model that is in charge
    of creating/maintaining the individual report records, and providing 
    available report views.
    Also provides the entry point for custom code.
    """
    _inherit = ['mail.thread']

    # TODO: add relation to ir.action.window to record defaule report viewer?
    # TODO: generic views for record and report.viewer for inheritance.

    def _default_project_id(self):
        return self.env.ref('olap.project_default')

    name = fields.Char(string='Name')
    model_id = fields.Many2one('ir.model', string="Report Model",
                               required=True, index=True)
    last_updated = fields.Datetime('Last Update', required=True,
                                   default=fields.Datetime.now,
                                   readonly=True)
    sequence = fields.Integer(string="Sequence")

    # Issue tracking
    project_id = fields.Many2one('project.project', string="Issue Tracker",
                                 required=True, default=_default_project_id)
    issue_ids = fields.One2many('project.task', string="Issues",
                                domain=['|', ('stage_id.fold', '=', False),
                                        ('stage_id', '=', False)],
                                inverse_name='report_id')
    issue_count = fields.Integer(string="Issue Count",
                                 compute='_compute_issue_counts', store=True)
    open_issue_count = fields.Integer(string="Open Issue Count",
                                      compute='_compute_issue_counts',
                                      store=True)

    @api.multi
    @api.depends('issue_ids', 'issue_ids.stage_id', 'issue_ids.report_id')
    def _compute_issue_counts(self):
        """Compute number of open issues (for UI display)"""
        for rec in self:
            rec.issue_count = len(rec.issue_ids)
            rec.open_issue_count = (len(rec.issue_ids.filtered(
                lambda i: i.stage_id == self.env.ref('olap.task_type_closed'))))

    @api.multi
    def _issue_vals(self):
        """Construct values for corresponding issues"""
        self.ensure_one()
        vals = {'project_id': self.project_id.id,
                'report_id': self.id}
        return vals

    @api.multi
    def raise_issue(self, fmt, err):
        """Raise issue via issue tracker"""
        self.ensure_one()

        # Parse exception
        title = err.name if isinstance(err, UserError) else str(err)
        tbe = traceback.TracebackException.from_exception(err)

        # Construct issue
        vals = self._issue_vals()
        vals['name'] = ("[%s] %s" % (self.name, title))
        issue = self.env['project.task'].create(vals)

        # Add traceback if applicable
        trace = ''.join(tbe.format())
        _logger.error(trace)
        if not isinstance(err, UserError):
            issue.message_post(body=trace, content_subtype='plaintext')
            self.sudo().message_post(body=trace,
                                     content_subtype='plaintext')

        # Add summary
        self.sudo().message_post(body=(fmt % title),
                                 content_subtype='plaintext')
        return issue

    @api.model
    def get_candidate_records(self):
        """Get all the records of the tracked model that need reports updating
        """
        return self.env[self.model_id.model].get_candidate_records()

    @api.model
    def update_report(self, candidates=None):
        """Optionally find candidates, then update reports for candidates.
        """
        if self.open_issue_count > 0:
            raise UserError(_('Cannot update report with open issues.'))
        try:
            with self.env.cr.savepoint():
                if candidates is None:
                    candidates = self.get_candidate_records()
                for r, batch in candidates.batched():
                    self.env[self.model_id.model].update_records(batch)
                self.last_updated = fields.Datetime.now()
                return True
        except Exception as err:
            self.raise_issue(_("Error generating report: %s"), err)
            return False

    @api.multi
    def action_update_report(self):
        self.close_issues()
        return self.update_report()

    @api.multi
    def close_issues(self):
        """Close all open issues"""
        for issue in self.mapped('issue_ids'):
            closed = issue.stage_find(issue.project_id.id,
                                      [('fold', '=', True)])
            issue.stage_id = closed

    @api.multi
    def action_view_issues(self):
        """View open issues"""
        self.ensure_one()
        action = self.env.ref('project.action_view_task').read()[0]
        action['domain'] = [(self._fields['issue_ids'].inverse_name,
                             '=', self.id)]
        action['context'] = {'default_%s' % k: v
                             for k, v in self._issue_vals().items()}
        action['context'].update({'create': True})
        return action

    @api.multi
    def action_close_issues(self):
        """Close all open issues"""
        self.close_issues()
        return True

    @api.multi
    def action_view_report(self):
        self.env[self.model_id.model].action_view_report()

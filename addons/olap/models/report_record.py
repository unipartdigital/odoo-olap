# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReportRecord(models.AbstractModel):
    _name = "olap.report.record"
    _description = """Holds the actual data."""

    name = fields.Char(string="Name", required=True, readonly=True,
                       index=True)

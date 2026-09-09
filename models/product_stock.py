from datetime import date
from odoo import api, models, fields


class SubComponent(models.Model):
    _name = 'sub.component'
    _description = 'Sub Component Model'
    _rec_name = 'component_name'
from odoo import models, fields


class ProductionMachine(models.Model):
    _name = 'production.machine'
    _description = 'Máy sản xuất'
    _order = 'name'

    name = fields.Char(
        string='Tên máy',
        required=True
    )

    code = fields.Char(
        string='Mã máy'
    )

    team_id = fields.Many2one(
        'production.team',
        string='Nhóm sản xuất'
    )

    operator_id = fields.Many2one(
        'res.users',
        string='Người vận hành'
    )

    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )

    note = fields.Text(
        string='Ghi chú'
    )
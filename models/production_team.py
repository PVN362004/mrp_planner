from odoo import models, fields


class ProductionTeam(models.Model):
    _name = 'production.team'
    _description = 'Nhóm sản xuất'
    _order = 'name'

    name = fields.Char(
        string='Tên nhóm',
        required=True
    )

    leader_id = fields.Many2one(
        'res.users',
        string='Trưởng nhóm'
    )

    member_ids = fields.Many2many(
        'res.users',
        string='Thành viên'
    )

    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )

    note = fields.Text(
        string='Ghi chú'
    )
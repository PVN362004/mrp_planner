from odoo import models, fields


class ProductionTeam(models.Model):
    _name = 'production.team'
    _description = 'Nhóm sản xuất'
    _rec_name = 'name'

    name = fields.Char(
        string='Tên nhóm sản xuất',
        required=True
    )

    team_code = fields.Char(
        string='Mã nhóm'
    )

    team_leader_id = fields.Many2one(
        'res.users',
        string='Nhóm trưởng'
    )

    member_ids = fields.Many2many(
        'res.users',
        'production_team_user_rel',
        'team_id',
        'user_id',
        string='Thành viên'
    )

    member_count = fields.Integer(
        string='Số thành viên',
        compute='_compute_member_count'
    )

    active = fields.Boolean(
        string='Đang hoạt động',
        default=True
    )

    assignment_ids = fields.One2many(
        'work.assignment',
        'team_id',
        string='Công việc'
    )

    def _compute_member_count(self):
        for record in self:
            record.member_count = len(record.member_ids)
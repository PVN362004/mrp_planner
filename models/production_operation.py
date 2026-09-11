from odoo import models, fields, api

class ProductionOperation(models.Model):
    _name = 'production.operation'
    _description = 'Công đoạn sản xuất'
    _order = 'sequence, id'

    name = fields.Char(string='Tên công đoạn', required=True)
    sequence = fields.Integer(string='Thứ tự', default=1)
    order_id = fields.Many2one('manufacturing.order', string='Lệnh sản xuất', required=True, ondelete='cascade')
    component_id = fields.Many2one('sub.component', string='Linh kiện')
    quantity = fields.Integer(string='Số lượng', default=1)
    team_id = fields.Many2one('production.team', string='Nhóm sản xuất')
    machine_id = fields.Many2one('production.machine', string='Máy sản xuất')
    expect_duration = fields.Float(string='Thời gian dự kiến (phút)', default = 0.0)
    real_duration = fields.Float(string='Thời gian thực tế (phút)', compute='_compute_real_duration', store=True, default = 1)

    state = fields.Selection([
        ('pending', 'Chờ'),
        ('ready', 'Sẵn sàng'),
        ('progress', 'Đang sản xuất'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', default='pending')

    date_start = fields.Datetime(string='Bắt đầu')
    date_end = fields.Datetime(string='Hoàn thành')
    note = fields.Text(string='Ghi chú')

    @api.depends('date_start', 'date_end')
    def _compute_real_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.end - record.date_start
                record.real_duration = round(delta.total_seconds() / 60.0, 1)
            else:
                record.real_duration = 0.0

    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        if self.machine_id and self.machine_id.team_id:
            self.team_id = self.machine_id.team_id

    def action_ready(self):
        for record in self:
            record.state = 'ready'

    def action_start(self):
        for record in self:
            record.state = 'progress'
            record.date_start = fields.Datetime.now()

    def action_done(self):
        for record in self:
            record.state = 'done'
            record.date_end = fields.Datetime.now()

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_reset(self):
        for record in self:
            record.state = 'pending'
            record.date_start = False
            record.date_end = False


class ProductionTeam(models.Model):
    _name = 'production.team'
    _description = 'Nhóm sản xuất'
    _order = 'name'

    name = fields.Char(string='Tên nhóm', required=True)
    leader_id = fields.Many2one('res.users', string='Trưởng nhóm')
    member_ids = fields.Many2many('res.users', string='Thành viên')
    active = fields.Boolean(string='Hoạt động', default=True)
    note = fields.Text(string='Ghi chú')


class ProductionMachine(models.Model):
    _name = 'production.machine'
    _description = 'Máy sản xuất'
    _order = 'name'

    name = fields.Char(string='Tên máy', required=True)
    code = fields.Char(string='Mã máy')
    team_id = fields.Many2one('production.team', string='Nhóm sản xuất')
    operator_id = fields.Many2one('res.users', string='Người vận hành')
    active = fields.Boolean(string='Hoạt động', default=True)
    note = fields.Text(string='Ghi chú')
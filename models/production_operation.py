from odoo import models, fields


class ProductionOperation(models.Model):
    _name = 'production.operation'
    _description = 'Công đoạn sản xuất'
    _order = 'sequence, id'

    name = fields.Char(
        string='Tên công đoạn',
        required=True
    )

    sequence = fields.Integer(
        string='Thứ tự',
        default=1
    )

    order_id = fields.Many2one(
        'manufacturing.order',
        string='Lệnh sản xuất',
        required=True,
        ondelete='cascade'
    )

    component_id = fields.Many2one(
        'sub.component',
        string='Linh kiện'
    )

    quantity = fields.Integer(
        string='Số lượng',
        default=1
    )

    team_id = fields.Many2one(
        'production.team',
        string='Nhóm sản xuất'
    )

    machine_id = fields.Many2one(
        'production.machine',
        string='Máy sản xuất'
    )

    state = fields.Selection(
        [
            ('pending', 'Chờ'),
            ('ready', 'Sẵn sàng'),
            ('progress', 'Đang sản xuất'),
            ('done', 'Hoàn thành'),
            ('cancel', 'Đã hủy'),
        ],
        string='Trạng thái',
        default='pending'
    )

    date_start = fields.Datetime(
        string='Bắt đầu'
    )

    date_end = fields.Datetime(
        string='Hoàn thành'
    )

    note = fields.Text(
        string='Ghi chú'
    )

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
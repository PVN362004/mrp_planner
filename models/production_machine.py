from odoo import models, fields, api


class WorkAssignment(models.Model):
    _name = 'work.assignment'
    _description = 'Phân bổ công việc sản xuất'
    _rec_name = 'name'
    _order = 'start_datetime desc'

    name = fields.Char(
        string='Tên công việc',
        required=True
    )

    # =========================
    # ĐƠN SẢN XUẤT
    # =========================

    production_order_id = fields.Many2one(
        'manufacturing.order',
        string='Đơn sản xuất',
        ondelete='set null'
    )

    # =========================
    # SẢN PHẨM
    # =========================

    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        ondelete='set null'
    )

    # =========================
    # LINH KIỆN
    # =========================

    component_id = fields.Many2one(
        'product.product',
        string='Linh kiện',
        ondelete='set null'
    )

    quantity = fields.Float(
        string='Số lượng',
        default=1
    )

    # =========================
    # PHÂN BỔ
    # =========================

    team_id = fields.Many2one(
        'production.team',
        string='Nhóm sản xuất',
        ondelete='set null'
    )

    machine_id = fields.Many2one(
        'production.machine',
        string='Máy sản xuất',
        ondelete='set null'
    )

    operator_id = fields.Many2one(
        'res.users',
        string='Người thực hiện',
        ondelete='set null'
    )

    # =========================
    # TRẠNG THÁI
    # =========================

    state = fields.Selection(
        [
            ('waiting', 'Chờ thực hiện'),
            ('in_progress', 'Đang thực hiện'),
            ('done', 'Hoàn thành'),
            ('paused', 'Tạm dừng'),
            ('cancelled', 'Đã hủy'),
        ],
        string='Trạng thái',
        default='waiting',
        required=True
    )

    # =========================
    # THỜI GIAN
    # =========================

    start_datetime = fields.Datetime(
        string='Bắt đầu',
        required=True
    )

    expected_end_datetime = fields.Datetime(
        string='Dự kiến hoàn thành'
    )

    actual_end_datetime = fields.Datetime(
        string='Hoàn thành thực tế'
    )

    duration = fields.Float(
        string='Thời gian dự kiến (giờ)',
        compute='_compute_duration'
    )

    note = fields.Text(
        string='Ghi chú'
    )

    active = fields.Boolean(
        default=True
    )

    @api.depends(
        'start_datetime',
        'expected_end_datetime'
    )
    def _compute_duration(self):
        for record in self:
            if record.start_datetime and record.expected_end_datetime:
                delta = (
                    record.expected_end_datetime
                    - record.start_datetime
                )

                record.duration = delta.total_seconds() / 3600
            else:
                record.duration = 0

    def action_start(self):
        for record in self:
            record.state = 'in_progress'

            if record.machine_id:
                record.machine_id.status = 'working'
                record.machine_id.operator_id = record.operator_id

    def action_done(self):
        for record in self:
            record.state = 'done'
            record.actual_end_datetime = fields.Datetime.now()

            if record.machine_id:
                record.machine_id.status = 'available'
                record.machine_id.operator_id = False

    def action_pause(self):
        for record in self:
            record.state = 'paused'

            if record.machine_id:
                record.machine_id.status = 'stop'
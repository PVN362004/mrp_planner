from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductionOperation(models.Model):
    _name = 'production.operation'
    _description = 'Công đoạn sản xuất'
    _order = 'sequence, id'

    name = fields.Char(string='Tên công đoạn', required=True)
    sequence = fields.Integer(string='Thứ tự', default=1)
    order_id = fields.Many2one('manufacturing.order', string='Lệnh sản xuất', required=True, ondelete='cascade')
    component_id = fields.Many2many('sub.component', string='Linh kiện')
    quantity = fields.Integer(string='Số lượng', default=1)
    team_id = fields.Many2one('production.team', string='Nhóm sản xuất')
    machine_id = fields.Many2one('production.machine', string='Máy sản xuất')
    expect_duration = fields.Float(string='Thời gian dự kiến (phút)', default = 0.0)
    real_duration = fields.Float(string='Thời gian thực tế (phút)', compute='_compute_real_duration', store=True, default = 0.0)

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
    available_qty_info = fields.Char(string='Tồn kho', compute='_compute_available_qty')

    @api.depends('component_id')
    def _compute_available_qty(self):
        for record in self:
            if record.component_id:
                # Trích xuất số lượng của từng linh kiện thành chuỗi (VD: "50" hoặc "50, 100")
                record.available_qty_info = ', '.join([str(c.quantity) for c in record.component_id])
            else:
                record.available_qty_info = '0'

    @api.depends('date_start', 'date_end')
    def _compute_real_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
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
            # Tạo điều kiện tìm kiếm các công đoạn khác đang chạy (trạng thái progress)
            domain = [('state', '=', 'progress'), ('id', '!=', record.id)]
            
            # Kiểm tra xem có bị trùng Máy hoặc Trùng Nhóm sản xuất không
            if record.machine_id and record.team_id:
                domain += ['|', ('machine_id', '=', record.machine_id.id), ('team_id', '=', record.team_id.id)]
            elif record.machine_id:
                domain += [('machine_id', '=', record.machine_id.id)]
            elif record.team_id:
                domain += [('team_id', '=', record.team_id.id)]
            
            # Nếu công đoạn này có gán máy hoặc nhóm, tiến hành kiểm tra
            if record.machine_id or record.team_id:
                conflict_op = self.env['production.operation'].search(domain, limit=1)
                
                # Nếu tìm thấy máy hoặc nhóm đang làm công đoạn khác, bật màn hình báo lỗi
                if conflict_op:
                    # Xác định cụ thể là Máy hay Nhóm đang bận để thông báo chi tiết
                    if conflict_op.machine_id and conflict_op.machine_id == record.machine_id:
                        busy_name = f"Máy '{conflict_op.machine_id.name}'"
                    else:
                        busy_name = f"Nhóm '{conflict_op.team_id.name}'"
                        
                    raise UserError(
                        f"Không thể bắt đầu! {busy_name} hiện đang bận và đã được phân công:\n"
                        f"- Công đoạn: {conflict_op.name}\n"
                        f"- Thuộc Lệnh SX: {conflict_op.order_id.mo_id}\n\n"
                        f"Vui lòng đợi công đoạn trên hoàn tất, hoặc chọn Máy/Nhóm khác!"
                    )

            # Nếu không có xung đột, cho phép bắt đầu bình thường
            record.state = 'progress'
            record.date_start = fields.Datetime.now()

    def action_done(self):
        for record in self:
            record.state = 'done'
            record.date_end = fields.Datetime.now()
            
            # KIỂM TRA ĐỂ TỰ ĐỘNG HOÀN THÀNH LỆNH SẢN XUẤT
            if record.order_id:
                # Tìm các công đoạn thuộc Lệnh SX hiện tại mà chưa ở trạng thái 'done' hoặc 'cancel'
                unfinished_ops = record.order_id.operation_ids.filtered(
                    lambda op: op.state not in ('done', 'cancel')
                )
                
                # Nếu không còn công đoạn nào dang dở và Lệnh SX chưa hoàn thành
                if not unfinished_ops and record.order_id.state != 'done':
                    # Tự động gọi hàm action_done() của Lệnh SX (sẽ cập nhật trạng thái Lệnh thành done và tự động trừ/cộng kho)
                    record.order_id.action_done()

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
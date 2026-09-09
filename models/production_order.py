from odoo import models, fields

class ProductionOrder(models.Model):
    _name = 'production.order'
    _description = 'Lệnh sản xuất tùy chỉnh'
    _rec_name = 'name'

    name = fields.Char(string='Mã Lệnh Sản Xuất', required=True, default='LSX/2026/001')
    product_name = fields.Char(string='Tên sản phẩm', required=True)
    product_qty = fields.Integer(string='Số lượng', default=1, required=True)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string='Trạng thái', default='draft')

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
            for rec in self:
                rec.state = 'done'

    def action_cancel(self):
            for rec in self:
                rec.state = 'cancel'

    def action_draft(self):
            for rec in self:
                rec.state = 'draft'


    line_ids = fields.One2many('production.order.line', 'order_id', string='Thành phần linh kiện')

class ProductionOrderLine(models.Model):
    _name = 'production.order.line'
    _description = 'Chi tiết linh kiện lệnh sản xuất'

    order_id = fields.Many2one('production.order', string='Lệnh sản xuất', ondelete='cascade')
    sub_component_id = fields.Many2one('sub.component', string='Linh kiện', required=True)
    quantity = fields.Integer(string='Số lượng', default=1, required=True)
    note = fields.Char(string='Ghi chú')
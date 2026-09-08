# -*- coding: utf-8 -*-
from odoo import api, models, fields

class ProductOrder(models.Model):
    _name = 'product.order'
    _description = 'Lệnh làm việc'
    _rec_name = 'name'

    name = fields.Char(string='Mã', required=True)
    planner_id = fields.Many2one(
        'product.planner', 
        string='Thuộc sản phẩm', 
        required=True, 
        ondelete='cascade'
    )
    
    product_code = fields.Char(related='planner_id.product_code', string='Mã hàng', readonly=True)
    product_name = fields.Char(related='planner_id.product_name', string='Tên hàng', readonly=True)

    bom_id = fields.Many2one(
        'product.bom', 
        string='Định mức BoM liên quan',
        domain="[('product_id', '=', planner_id)]" 
    )

    stage = fields.Selection([
        ('stamping', 'Dập & Uốn vỏ inox'),
        ('welding', 'Hàn phôi / Mâm nhiệt'),
        ('assembly', 'Lắp ráp chi tiết'),
        ('testing', 'Kiểm tra an toàn điện & Đun thử'),
        ('packing', 'Đóng gói & Dán nhãn')
    ], string='Bước thực hiện', default='assembly', required=True)

    quantity = fields.Integer(string='SL cần xử lý', default=1)
    duration_expected = fields.Float(string='Thời gian dự kiến (phút)', default=15.0)

    status = fields.Selection([
        ('Chờ thực hiện'),
        ('Đang xử lý'),
        ('Đã hoàn thành'),
        ('Hủy bỏ')
    ], string='Trạng thái', default='Chờ thực hiện')

    note = fields.Char(string='Ghi chú kỹ thuật')
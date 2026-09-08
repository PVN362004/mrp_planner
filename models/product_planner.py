# -*- coding: utf-8 -*-
from odoo import api, models, fields

class ProductPlanner(models.Model):
    _name = 'product.planner'
    _description = 'Kế hoạch Sản phẩm'
    _rec_name = 'product_name'

    # Thông tin cơ bản của sản phẩm / chi tiết
    product_name = fields.Char(string='Tên sản phẩm', required=True)
    product_code = fields.Char(string='Mã hàng', required=True)
    product_type = fields.Selection([
        ('in_house', 'Tự sản xuất'),
        ('subcontract', 'Gia công ngoài'),
        ('buy', 'Mua ngoài'),
        ('finished', 'Thành phẩm hoàn chỉnh')
    ], string='Loại sản phẩm', default='in_house', required=True)
    
    company = fields.Char(string='Tên công ty / Xưởng', required=True)
    product_quantity = fields.Integer(string='Số lượng cần làm', default=1)
    product_description = fields.Text(string='Mô tả kỹ thuật')

    # Liên kết sang BoM (Nếu đây là thành phẩm hoặc cụm lắp ráp)
    bom_ids = fields.One2many(
        'product.bom', 
        'product_id', 
        string='Định mức BoM'
    )

    # Liên kết sang danh sách công đoạn Work Order
    workorder_ids = fields.One2many(
        'product.order', 
        'planner_id', 
        string='Danh sách Work Order'
    )
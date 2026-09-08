# -*- coding: utf-8 -*-
from odoo import api, models, fields

class ProductBom(models.Model):
    _name = 'product.bom'
    _description = 'Định mức nguyên vật liệu (BoM)'
    _rec_name = 'code'

    code = fields.Char(string='Mã định mức', required=True, default='BOM-001')
    product_id = fields.Many2one(
        'product.planner', 
        string='Sản phẩm hoàn thiện', 
        required=True, 
        ondelete='cascade'
    )
    product_qty = fields.Float(string='Số lượng thành phẩm', default=1.0)
    line_ids = fields.One2many(
        'product.bom.line', 
        'bom_id', 
        string='Danh sách linh kiện/vật tư'
    )


class ProductBomLine(models.Model):
    _name = 'product.bom.line'
    _description = 'Chi tiết linh kiện trong BoM'

    bom_id = fields.Many2one('product.bom', string='Thuộc BoM', ondelete='cascade')
    component_id = fields.Many2one(
        'product.planner', 
        string='Linh kiện / Bán thành phẩm', 
        required=True
    )
    product_qty = fields.Float(string='Số lượng tiêu hao', default=1.0)
    uom_name = fields.Char(string='Đơn vị tính', default='Cái')
    production_method = fields.Selection([
        ('in_house', 'Tự sản xuất'),
        ('subcontract', 'Gia công ngoài'),
        ('buy', 'Mua ngoài')
    ], string='Cách cung ứng', default='in_house')
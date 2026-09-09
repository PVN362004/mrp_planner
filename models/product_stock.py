from odoo import api, models, fields
from datetime import datetime

class ProductionStock(models.Model):
    _name = 'production.stock'
    _description = 'Kho'
    _rec_name = 'stock_name'

    stock_name = fields.Char(string='Tên kho', required=True)
    location_code = fields.Char(string='Mã kho')

    line_ids = fields.One2many('production.stock.line', 'stock_id', string='Thông tin tồn kho')

class ProductionStockLine(models.Model):
    _name = 'production.stock.line'
    _description = 'Thông tin tồn kho'

    stock_id = fields.Many2one('production.stock', string='Kho', ondelete='cascade')
    product_name = fields.Char(string='Sản phẩm', required=True)
    quantity = fields.Float(string='Số lượng tồn', default=0.0, required=True) 
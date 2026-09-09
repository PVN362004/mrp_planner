from datetime import date
from odoo import api, models, fields


class SubComponent(models.Model):
    _name = 'sub.component'
    _description = 'Sub Component Model'
    _rec_name = 'component_name'

    component_name = fields.Char(string='Tên sản phẩm', required=True)
    component_id = fields.Char(string='Mã sản phẩm')
    component_method = fields.Selection([
        ('in_house', 'Tự sản xuất'),
        ('outsource', 'Thuê ngoài'),
        ('assembly', 'Chỉ lắp ráp')
    ], string='Phương thức sản xuất', required=True, default='in_house')
    company_name = fields.Char(string='Tên công ty')
    quantity = fields.Integer(string='Số lượng', required=True, default='1')
    buying_cost = fields.Integer(string='Giá mua', required=True, default='0')
    sale_cost = fields.Integer(string='Giá bán', required=True, default='0')
    note = fields.Char(string='Ghi chú', required=False)
    
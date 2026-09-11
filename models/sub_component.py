from datetime import datetime
from odoo import api, models, fields


class SubComponent(models.Model):
    _name = 'sub.component'
    _description = 'Sub Component Model'
    _rec_name = 'component_name'

    component_name = fields.Char(string='Tên sản phẩm', required=True)
    _sql_constraints = [
        ('component_name_unique', 'UNIQUE(component_name)', 'Tên sản phẩm/linh kiện này đã tồn tại trong kho!')
    ]

    def _default_component_id(self):
                today_str = datetime.now().strftime('%d%m%y')
                prefix = f"SP{today_str}"
                last_record = self.env['sub.component'].search([('component_id', 'like', f"{prefix}%")], order='id desc', limit=1)
                
                if last_record and last_record.component_id and last_record.component_id.startswith(prefix):
                    try:
                        last_seq = int(last_record.component_id[len(prefix):])
                        new_seq = last_seq + 1
                    except ValueError:
                        new_seq = 1
                else:
                    new_seq = 1
                    
                return f"{prefix}{new_seq:03d}"
    
    component_id = fields.Char(string='Mã sản phẩm', required=True, copy=False, readonly=True, default=_default_component_id)

    component_method = fields.Selection([
        ('in_house', 'Tự sản xuất'),
        ('outsource', 'Thuê ngoài'),
        ('buying', 'Mua ngoài'),
        ('assembly', 'Chỉ lắp ráp')
    ], string='Phương thức sản xuất', required=True, default='in_house')

    company_id = fields.Many2one('company.name', string='Tên công ty', ondelete='set null')
    quantity = fields.Integer(string='Số lượng', required=True, default=1)
    buying_cost = fields.Integer(string='Giá mua', required=True, default=0)
    sale_cost = fields.Integer(string='Giá bán', required=True, default=0)
    note = fields.Char(string='Ghi chú', required=False)

    product_type = fields.Selection([
        ('material', 'Nguyên liệu'),
        ('product', 'Sản phẩm hoàn chỉnh'),
        ('component', 'Linh kiện'),
    ], string='Loại sản phẩm', required=True, default='material')


class CompanyName(models.Model):
    _name = 'company.name'
    _description = 'Company Model'
    _rec_name = "company_id"

    company_id = fields.Char(string='Tên công ty', required=True)
    company_email = fields.Char(string='Email công ty')
    company_address = fields.Char(string='Địa chỉ của công ty')


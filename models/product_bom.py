from odoo import api, models, fields

class ProductBom(models.Model):
    _name = 'production.bom'
    _description = 'Bom cho lệnh sản xuất'
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'sub.component', 
        string='Sản phẩm', 
        required=True
    )

    quantity = fields.Integer(string='Số lượng', required=True, default=1)
    reference = fields.Char(string='Tham chiếu') 
    
    bom_type = fields.Selection([
        ('manufacture', 'Tự sản xuất'),
        ('assembly', 'Chỉ lắp ráp'),
        ('subcontracting', 'Thuê ngoài'),
    ], string='Loại BOM', default='manufacture')
    
    company_id = fields.Many2one('company.name', string='Tên công ty', ondelete='set null')
    
    bom_line_ids = fields.One2many('production.bom.line', 'bom_id', string='Danh sách linh kiện')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id and rec.product_id.company_id:
                rec.company_id = rec.product_id.company_id


class ProductBomLine(models.Model):
    _name = 'production.bom.line'
    _description = 'Chi tiết linh kiện BOM'

    bom_id = fields.Many2one('production.bom', string='BOM', ondelete='cascade')

    sub_component_id = fields.Many2one('sub.component', string='Linh kiện', required=True)
    quantity = fields.Integer(string='Số lượng', default=1, required=True)
    note = fields.Char(string='Ghi chú')


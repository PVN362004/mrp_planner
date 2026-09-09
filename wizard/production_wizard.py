from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductionMethodWizard(models.TransientModel):
    _name = 'production.method.wizard'
    _description = 'Wizard chọn phương thức sản xuất'

    order_id = fields.Many2one('sale.order', string='Đơn hàng')
    line_ids = fields.One2many('production.method.wizard.line', 'wizard_id', string='Chi tiết linh kiện')

    def action_confirm_production(self):
        po_dict = {} 

        for line in self.line_ids:
            qty_to_produce = line.required_qty 
            if qty_to_produce <= 0:
                continue

            if line.production_method in ['in_house', 'assembly']:
                bom = self.env['mrp.bom']._bom_find(product=line.product_id, company_id=self.env.company.id)

                mo_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': qty_to_produce,
                    'product_uom_id': line.product_id.uom_id.id,
                    'origin': self.order_id.name, 
                    'company_id': self.env.company.id,
                }
                
                if bom:
                    mo_vals['bom_id'] = bom.id
                    
                mo = self.env['mrp.production'].create(mo_vals)
                mo._onchange_bom_id() 


            elif line.production_method == 'outsource':
                vendor = line.product_id.seller_ids and line.product_id.seller_ids[0].partner_id
                
                if not vendor:
                    raise UserError(f"Sản phẩm {line.product_id.name} chưa được cấu hình Nhà Cung Cấp. Vui lòng vào sản phẩm thiết lập Vendor trước khi tạo lệnh.")

                if vendor.id not in po_dict:
                    po_dict[vendor.id] = []

                po_dict[vendor.id].append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_qty': qty_to_produce,
                    'price_unit': line.product_id.standard_price,
                    'product_uom': line.product_id.uom_po_id.id or line.product_id.uom_id.id,
                    'date_planned': fields.Datetime.now(),
                }))
                
        if po_dict:
            for vendor_id, po_lines in po_dict.items():
                po_vals = {
                    'partner_id': vendor_id,
                    'origin': self.order_id.name, 
                    'order_line': po_lines
                }
                self.env['purchase.order'].create(po_vals)

        return {'type': 'ir.actions.act_window_close'}

class ProductionMethodWizardLine(models.TransientModel):
    _name = 'production.method.wizard.line'
    _description = 'Chi tiết linh kiện'

    wizard_id = fields.Many2one('production.method.wizard')
    
    sub_component_id = fields.Many2one('sub.component', string='Linh kiện (Tự nhập)', required=True)
    
    qty_to_produce = fields.Float(string='SL Chốt làm/mua', required=True, default=1.0)
    
    production_method = fields.Selection([
        ('in_house', 'Tự sản xuất'),
        ('outsource', 'Thuê ngoài'),
        ('assembly', 'Chỉ lắp ráp')
    ], string='Phương thức Sản Xuất', required=True)

    @api.onchange('sub_component_id')
    def _onchange_sub_component(self):
        for rec in self:
            if rec.sub_component_id:
                rec.qty_to_produce = rec.sub_component_id.quantity
                rec.production_method = rec.sub_component_id.component_method
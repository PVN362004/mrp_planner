from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductionMethodWizard(models.TransientModel):
    _name = 'production.method.wizard'
    _description = 'Wizard chọn phương thức sản xuất'

    order_id = fields.Many2one('sale.order', string='Đơn hàng')
    line_ids = fields.One2many('production.method.wizard.line', 'wizard_id', string='Chi tiết linh kiện')

    def action_confirm_production(self):
        self.ensure_one()
        
        if not self.line_ids:
            raise UserError("Vui lòng thêm ít nhất một linh kiện vào phương án sản xuất!")
        
        order_lines_vals = []
        for line in self.line_ids:
            if line.qty_to_produce <= 0:
                continue
                
            order_lines_vals.append((0, 0, {
                'sub_component_id': line.sub_component_id.id,
                'quantity': line.qty_to_produce,
                'note': f"Phương thức: {line.production_method}"
            }))

        custom_po_vals = {
            'name': f"LSX/{self.order_id.name or 'Manual'}",

            'product_name': (
                f"Theo đơn hàng {self.order_id.name}"
                if self.order_id.name
                else "Sản xuất thủ công"
            ),

            'product_qty': 1,

            'state': 'confirmed',

            'line_ids': order_lines_vals,
        }
        new_custom_order = self.env['production.order'].create(custom_po_vals)

        return {
            'name': 'Lệnh Sản Xuất Đã Tạo',
            'type': 'ir.actions.act_window',
            'res_model': 'custom.production.order',
            'view_mode': 'form',
            'res_id': new_custom_order.id,
            'target': 'current',
        }

class ProductionMethodWizardLine(models.TransientModel):
    _name = 'production.method.wizard.line'
    _description = 'Chi tiết linh kiện trong Wizard'

    wizard_id = fields.Many2one('production.method.wizard')
    
    sub_component_id = fields.Many2one('sub.component', string='Linh kiện', required=True)
    
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
from odoo import api, models, fields
from datetime import datetime

class ManufacturingOrder(models.Model):
    _name = 'manufacturing.order'
    _description = 'Lệnh sản xuất'
    _rec_name = 'mo_id'

    def _default_mo_id(self):
        today_str = datetime.now().strftime('%d%m%y')
        prefix = f"SP{today_str}"
        last_record = self.env['manufacturing.order'].search([('mo_id', 'like', f"{prefix}%")], order='id desc', limit=1)
        
        if last_record and last_record.mo_id.startswith(prefix):
            try:
                last_seq = int(last_record.mo_id[len(prefix):])
                new_seq = last_seq + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1
            
        return f"{prefix}{new_seq:03d}"

    mo_id = fields.Char(string='Mã Lệnh Sản Xuất', required=True, copy=False, readonly=True, default=_default_mo_id)

    product_id = fields.Many2one(
            'sub.component', 
            string='Sản phẩm', 
            required=True
        )
    
    product_qty = fields.Integer(string='Số lượng', default=1, required=True)
    customer_name = fields.Many2one('customer.partner', string='Tên khách hàng', ondelete='set null')
    sale_cost = fields.Integer(string='Giá bán', required=True, default=1)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string='Trạng thái', default='draft')

    
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'


    def action_cancel(self):
            for rec in self:
                rec.state = 'cancel'

    def action_draft(self):
            for rec in self:
                rec.state = 'draft'


    def action_progress(self):
            for rec in self:
                rec.state = 'progress'


    def action_done(self):
        for rec in self:
            rec.state = 'done'
            
            # 1. Cập nhật trực tiếp vào bản ghi sản phẩm đã chọn
            if rec.product_id:
                rec.product_id.quantity += rec.product_qty
                rec.product_id.product_type = 'product'
                rec.product_id.sale_cost = rec.sale_cost

            # 2. Trừ linh kiện đã sử dụng
            for line in rec.line_ids:
                if line.sub_component_id:
                    line.sub_component_id.quantity -= line.quantity

        self.unlink()
        return {
                'type': 'ir.actions.act_window',
                'name': 'Lệnh sản xuất',
                'res_model': 'manufacturing.order',
                'view_mode': 'list,form',
                'target': 'current',
            }

    bom_id = fields.Many2one('production.bom', string='Định mức (BOM)')
    line_ids = fields.One2many('manufacturing.order.line', 'order_id', string='Thành phần linh kiện')

    @api.onchange('bom_id', 'product_qty')
    def _onchange_bom_id(self):
        for rec in self:
            lines = [(5, 0, 0)]

            if rec.bom_id:
                bom_qty = max(rec.bom_id.quantity, 1)
                ratio = rec.product_qty / bom_qty

                for bom_line in rec.bom_id.bom_line_ids:

                    lines.append((0, 0, {
                        'sub_component_id': bom_line.sub_component_id.id,
                        'quantity': int(bom_line.quantity * ratio), 
                        'note': bom_line.note
                    }))

            rec.line_ids = lines
         



class ManufacturingOrderLine(models.Model):
    _name = 'manufacturing.order.line'
    _description = 'Chi tiết linh kiện lệnh sản xuất'

    order_id = fields.Many2one('manufacturing.order', string='Lệnh sản xuất', ondelete='cascade')
    sub_component_id = fields.Many2one('sub.component', string='Linh kiện', required=True)
    quantity = fields.Integer(string='Số lượng', default=1, required=True)
    note = fields.Char(string='Ghi chú')


class CustomerPartner(models.Model):
    _name = 'customer.partner'
    _description = 'Customer Partner Model'
    _rec_name = "customer_name"

    customer_name = fields.Char(string='Tên khách hàng', required=True)
    customer_email = fields.Char(string='Email khách hàng')
    customer_address = fields.Char(string='Địa chỉ của khách hàng')
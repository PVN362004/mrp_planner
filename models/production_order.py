from odoo import api, models, fields
from datetime import datetime

class ProductionOrder(models.Model):
    _name = 'production.order'
    _description = 'Lệnh sản xuất tùy chỉnh'
    _rec_name = 'mo_id'

    def _default_mo_id(self):
        today_str = datetime.now().strftime('%d%m%y')
        prefix = f"SP{today_str}"
        last_record = self.env['production.order'].search([('mo_id', 'like', f"{prefix}%")], order='id desc', limit=1)
        
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
    product_name = fields.Char(string='Tên sản phẩm', required=True)
    product_qty = fields.Integer(string='Số lượng', default=1, required=True)
    customer_name = fields.Many2one('customer.partner', string='Tên khách hàng', ondelete='restrict')
    sale_cost = fields.Integer(string='Giá bán', required=True, default=1)
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
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


    line_ids = fields.One2many('production.order.line', 'order_id', string='Thành phần linh kiện')


    def action_done(self):
        for rec in self:
            rec.state = 'done'
            finished_product = self.env['sub.component'].search([
                ('component_name', '=', rec.product_name)
            ], limit=1)
            
            if finished_product:
                finished_product.quantity += rec.product_qty
            else:
                self.env['sub.component'].create({
                    'component_name': rec.product_name,
                    'component_method': 'in_house', 
                    'quantity': rec.product_qty,
                    'sale_cost': rec.sale_cost,
                })

            for line in rec.line_ids:
                if line.sub_component_id:
                    line.sub_component_id.quantity -= line.quantity


class ProductionOrderLine(models.Model):
    _name = 'production.order.line'
    _description = 'Chi tiết linh kiện lệnh sản xuất'

    order_id = fields.Many2one('production.order', string='Lệnh sản xuất', ondelete='cascade')
    sub_component_id = fields.Many2one('sub.component', string='Linh kiện', required=True)
    quantity = fields.Integer(string='Số lượng', default=1, required=True)
    note = fields.Char(string='Ghi chú')


class CustomerPartner(models.Model):
    _name = 'customer.partner'
    _description = 'Customer Partner Model'
    _rec_name = "customer_name"

    customer_name = fields.Char(string='Ten khach hang', required=True)
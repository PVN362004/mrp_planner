from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_production_wizard(self):
        self.ensure_one()
        return {
            'name': 'Lên Phương Án Sản Xuất (Thủ công)',
            'type': 'ir.actions.act_window',
            'res_model': 'production.method.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            }
        }

from odoo import api, models, fields
from datetime import datetime

class ProductBom(models.Model):
    _name = 'production.bom'
    _description = 'Bom cho lệnh sản xuất'
    _rec_name = 'bom_id'

    bom_id = fields.Char(string='Bom Sản Xuất', required=True, copy=False, readonly=True, default=_default_bom_id)
    def _default_bom_id(self):
            today_str = datetime.now().strftime('%d%m%y')
            prefix = f"BOM{today_str}"
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
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    first_approver = fields.Many2one('res.users',string="First Approver")
    second_approver = fields.Many2one('res.users',string="Second Approver")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['first_approver'] = int(self.env['ir.config_parameter'].sudo().get_param("custom_purchase_double_approval.first_approver", default=False)) or False
        res['second_approver'] = int(self.env['ir.config_parameter'].sudo().get_param("custom_purchase_double_approval.second_approver", default=False)) or False
        return res

    def set_values(self):
        self.ensure_one()
        self.env['ir.config_parameter'].set_param("custom_purchase_double_approval.first_approver",self.first_approver.id)
        self.env['ir.config_parameter'].set_param("custom_purchase_double_approval.second_approver",self.second_approver.id)
        super(ResConfigSettings, self).set_values()



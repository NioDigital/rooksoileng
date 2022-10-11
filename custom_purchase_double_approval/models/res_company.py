from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    first_approver = fields.Many2one('res.users',string="First Approver")
    second_approver = fields.Many2one('res.users',string="Second Approver")

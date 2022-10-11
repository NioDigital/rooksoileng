# from odoo import fields, models, _


# class PurchaseOrder(models.Model):
#     _inherit = ['purchase.order']

#     state = fields.Selection(selection_add=[('first_approval','First Approval')])
#     date_approve1 = fields.Datetime('Confirmation Date1', readonly=1, index=True, copy=False)

#     def button_first_approve(self, force=False):
#         self.write({'state': 'first_approval', 'date_approve1': fields.Datetime.now()})
#         user = self.env['res.users'].search([])
#         for loop in user:
#             if loop.has_group('custom_purchase_double_approval.group_managing_director'):
#                 activity_user_id = loop.id
#         activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','Confirm Purchase Order')])
#         if not activity_type:
#             activity_type = self.env['mail.activity.type'].create({'name':'Confirm Purchase Order',
#                 'res_model':'purchase.order',
#                 'delay_unit':'days',
#                 'default_user_id': self.env.user.id,
#                 'summary': 'Purchase Order Final Confirmation Notification',
#                 'default_note': 'Please click on Confirm button for the Final confirmation',
#                 'delay_count':0})
#         if activity_user_group and activity_type:
#             date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
#             self.activity_schedule(
#                     activity_type_id=activity_type.id,
#                     summary=activity_type.summary,
#                     note=activity_type.default_note,
#                     user_id=activity_user_id,
#                     date_deadline=date_deadline
#                 )
#         return {}

#     def send_to_approval(self):
#         if self.company_id.po_double_validation == 'two_step' and self.state == 'sent':
#             self.state = 'to approve'
#             user = self.env['res.users'].search([])
#             for loop in user:
#                 if loop.has_group('purchase.group_purchase_manager'):
#                     activity_user_id = loop.id
#             activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','Purchase Order Notification')])
#             if not activity_type:
#                 activity_type = self.env['mail.activity.type'].create({'name':'Purchase Order Notification',
#                     'res_model':'purchase.order',
#                     'delay_unit':'days',
#                     'default_user_id': self.env.user.id,
#                     'summary': 'Purchase Order First Level Approval Notification',
#                     'default_note': 'Please click on Approve button for the First Level of confirmation',
#                     'delay_count':0})
#             if activity_user_group and activity_type:
#                 date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
#                 self.activity_schedule(
#                         activity_type_id=activity_type.id,
#                         summary=activity_type.summary,
#                         note=activity_type.default_note,
#                         user_id=activity_user_id,
#                         date_deadline=date_deadline
#                     )


#     def action_rfq_send(self):
#         '''
#         This function opens a window to compose an email, with the edi purchase template message loaded by default
#         '''
#         self.ensure_one()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             if self.env.context.get('send_rfq', False):
#                 template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase')[2]
#             else:
#                 template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase_done')[2]
#         except ValueError:
#             template_id = False
#         try:
#             compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
#         except ValueError:
#             compose_form_id = False
#         ctx = dict(self.env.context or {})
#         ctx.update({
#             'default_model': 'purchase.order',
#             'active_model': 'purchase.order',
#             'active_id': self.ids[0],
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'custom_layout': "mail.mail_notification_paynow",
#             'force_email': True,
#             'mark_rfq_as_sent': True,
#         })

#         # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
#         # object. Therefore, we pass the model description in the context, in the language in which
#         # the template is rendered.
#         lang = self.env.context.get('lang')
#         if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
#             template = self.env['mail.template'].browse(ctx['default_template_id'])
#             if template and template.lang:
#                 lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

#         self = self.with_context(lang=lang)
#         if self.state in ['draft', 'sent']:
#             ctx['model_description'] = _('Request for Quotation')
#         else:
#             ctx['model_description'] = _('Purchase Order')

#         activity_user_group = self.user_has_groups('custom_purchase_double_approval.group_service_engineer')
#         activity_user_id = False
#         user = self.env['res.users'].search([])
#         for loop in user:
#             if loop.has_group('custom_purchase_double_approval.group_service_engineer'):
#                 activity_user_id = loop.id
#         activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','RFQ Allocation Notification')])
#         if not activity_type:
#             activity_type = self.env['mail.activity.type'].create({'name':'RFQ Allocation Notification',
#                 'res_model':'purchase.order',
#                 'delay_unit':'days',
#                 'default_user_id': self.env.user.id,
#                 'summary': 'Allocate RFQ to the Service Engineer',
#                 'default_note': 'Please click on Send to Approval button after completed the Process form Service Engineer',
#                 'delay_count':0})
#         if activity_user_group and activity_type:
#             date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
#             self.activity_schedule(
#                     activity_type_id=activity_type.id,
#                     summary=activity_type.summary,
#                     note=activity_type.default_note,
#                     user_id=activity_user_id,
#                     date_deadline=date_deadline
#                 )

#         return {
#             'name': _('Compose Email'),
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
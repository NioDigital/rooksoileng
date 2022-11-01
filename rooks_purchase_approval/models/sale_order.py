from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
	_inherit = "sale.order"

	def action_create_rfq(self):
		for order in self.order_line:
			if order.product_id and order.product_type == 'product':
				order._purchase_service_create()
		purchase_order_ids = self._get_purchase_orders()
		attachment = []
		for attachments in self.env['ir.attachment'].search([('res_id', '=', self.id)]):
			attachment.append(attachments.id)
		if attachment:
			for purchase in purchase_order_ids:
				purchase.message_post(attachment_ids=attachment)
		# for line in purchase_order_ids:	
		user = self.env['res.users'].search([])
		activity_user_id = False
		for loop in user:
			if loop.has_group('rooks_purchase_approval.group_engineer_manager'):
				activity_user_id = loop.id
		activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','RFQ Allocation Notification')])
		if not activity_type:
			activity_type = self.env['mail.activity.type'].create({'name':'RFQ Allocation Notification',
				'res_model':'purchase.order',
				'delay_unit':'days',
				# 'res_id': 
				'default_user_id': self.env.user.id,
				'summary': 'RFQ Engineer Manager Notification',
				'default_note': 'Please click on Approve button for Engineer Manager Confirmation',
				'delay_count':0})
		if activity_type:
			date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
			purchase_order_ids.activity_schedule(
			    activity_type_id=activity_type.id,
			    summary=activity_type.summary,
			    note=activity_type.default_note,
			    user_id=activity_user_id,
			    date_deadline=date_deadline
			)
		# return activity_type
		# return True

	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		purchase_order = self.env['purchase.order'].search([('origin', '=', self.name)])
		for order in purchase_order:
			if order.state != 'purchase':
				raise UserError(_("Create RFQ and Confirm it to confirm the SaleOrder"))
			else:
				return res

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	def _purchase_service_create(self, quantity=False):
		""" On Sales Order confirmation, some lines (services ones) can create a purchase order line and maybe a purchase order.
			If a line should create a RFQ, it will check for existing PO. If no one is find, the SO line will create one, then adds
			a new PO line. The created purchase order line will be linked to the SO line.
			:param quantity: the quantity to force on the PO line, expressed in SO line UoM
		"""
		PurchaseOrder = self.env['purchase.order']
		supplier_po_map = {}
		sale_line_purchase_map = {}
		for line in self:
			line = line.with_company(line.company_id)
			# determine vendor of the order (take the first matching company and product)
			suppliers = line.product_id._select_seller(quantity=line.product_uom_qty, uom_id=line.product_uom)
			if not suppliers:
				raise UserError(_("There is no vendor associated to the product %s. Please define a vendor for this product.") % (line.product_id.display_name,))
			supplierinfo = suppliers[0]
			partner_supplier = supplierinfo.name  # yes, this field is not explicit .... it is a res.partner !

			# determine (or create) PO
			purchase_order = supplier_po_map.get(partner_supplier.id)
			if not purchase_order:
				purchase_order = PurchaseOrder.search([
					('partner_id', '=', partner_supplier.id),
					('state', '=', 'draft'),
					('company_id', '=', line.company_id.id),
				], limit=1)
			if not purchase_order:
				values = line._purchase_service_prepare_order_values(supplierinfo)
				purchase_order = PurchaseOrder.create(values)
			else:  # update origin of existing PO
				so_name = line.order_id.name
				# origins = []
				if purchase_order.origin:
					values = line._purchase_service_prepare_order_values(supplierinfo)
					purchase_order = PurchaseOrder.create(values)
			supplier_po_map[partner_supplier.id] = purchase_order

			# add a PO line to the PO
			values = line._purchase_service_prepare_line_values(purchase_order, quantity=quantity)
			purchase_line = line.env['purchase.order.line'].create(values)

			# link the generated purchase to the SO line
			sale_line_purchase_map.setdefault(line, line.env['purchase.order.line'])
			sale_line_purchase_map[line] |= purchase_line
		return sale_line_purchase_map

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	state = fields.Selection(selection_add=[('first_approval','Engineer Manager Approved'),
											('second_approver','PO Manager Approved'),
											('third_approve', 'Managing Director Approved')])

	signature = fields.Binary(string="Signature")

	def send_approve(self):
		# if self.state == 'first_approval':
		self.write({'state': 'first_approval'})
		user = self.env['res.users'].search([])
		activity_user_id = False
		for loop in user:
			if loop.has_group('rooks_purchase_approval.group_purchase_coordinator'):
				activity_user_id = loop.id
		activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','Purchase Order Notification')])
		if not activity_type:
			activity_type = self.env['mail.activity.type'].create({'name':'Purchase Order Notification',
                'res_model':'purchase.order',
                'delay_unit':'days',
                'default_user_id': self.env.user.id,
                'summary': 'RFQ Second Level Approval Notification',
                'default_note': 'Please click on Approve button for Purchase Manager Confirmation',
                'delay_count':0})
		if activity_type:
			date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
			self.activity_schedule(
				    activity_type_id=activity_type.id,
				    summary=activity_type.summary,
				    note=activity_type.default_note,
				    user_id=activity_user_id,
				    date_deadline=date_deadline
				)
		return activity_type

	def send_approve2(self):
		self.write({'state': 'second_approver'})
		user = self.env['res.users'].search([])
		activity_user_id = False
		for loop in user:
			if loop.has_group('rooks_purchase_approval.group_managing_directors'):
				activity_user_id = loop.id
		activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','Purchase Order Confirm Notification')])
		if not activity_type:
			activity_type = self.env['mail.activity.type'].create({'name':'Purchase Order Confirm Notification',
                'res_model':'purchase.order',
                'delay_unit':'days',
                'default_user_id': self.env.user.id,
                'summary': 'RFQ Third Level Approval Notification',
                'default_note': 'Please click on Approve button for Final Confirmation',
                'delay_count':0})
		if activity_type:
			date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
			self.activity_schedule(
				    activity_type_id=activity_type.id,
				    summary=activity_type.summary,
				    note=activity_type.default_note,
				    user_id=activity_user_id,
				    date_deadline=date_deadline
				)
		return activity_type

	def send_approve3(self):
		self.write({'state': 'third_approve'})
		user = self.env['res.users'].search([])
		activity_user_id = False
		for loop in user:
			if loop.has_group('rooks_purchase_approval.group_purchase_coordinator'):
				activity_user_id = loop.id
		activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','Managing Director Approved')])
		if not activity_type:
			activity_type = self.env['mail.activity.type'].create({'name':'Managing Director Approved',
                'res_model':'purchase.order',
                'delay_unit':'days',
                'default_user_id': self.env.user.id,
                'summary': 'RFQ Approved by Managing Director',
                'default_note': 'RFQ Approved by Managing Director',
                'delay_count':0})
		if activity_type:
			date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
			self.activity_schedule(
				    activity_type_id=activity_type.id,
				    summary=activity_type.summary,
				    note=activity_type.default_note,
				    user_id=activity_user_id,
				    date_deadline=date_deadline
				)
		return activity_type

	def button_cancel(self):
		res = super(PurchaseOrder, self).button_cancel()
		user = self.env['res.users'].search([])
		activity_user_id = False
		for loop in user:
			if loop.has_group('rooks_purchase_approval.group_purchase_coordinator'):
				activity_user_id = loop.has_group('rooks_purchase_approval.group_engineer_manager')
			activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','RFQ Cancellation Notification')])
			if not activity_type:
				activity_type = self.env['mail.activity.type'].create({'name':'RFQ Cancellation Notification',
	                'res_model':'purchase.order',
	                'delay_unit':'days',
	                'default_user_id': self.env.user.id,
	                'summary': 'RFQ Cancellation Notification',
	                'default_note': 'RFQ Cancellation Notification',
	                'delay_count':0})
			if activity_type:
				date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
				self.activity_schedule(
					    activity_type_id=activity_type.id,
					    summary=activity_type.summary,
					    note=activity_type.default_note,
					    user_id=activity_user_id,
					    date_deadline=date_deadline
					)
			return activity_type

			if loop.has_group('rooks_purchase_approval.group_managing_directors'):
				activity_user_id = loop.has_group('rooks_purchase_approval.group_purchase_coordinator')
			activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','RFQ Cancellation Notification')])
			if not activity_type:
				activity_type = self.env['mail.activity.type'].create({'name':'RFQ Cancellation Notification',
	                'res_model':'purchase.order',
	                'delay_unit':'days',
	                'default_user_id': self.env.user.id,
	                'summary': 'RFQ Cancellation Notification',
	                'default_note': 'RFQ Cancellation Notification',
	                'delay_count':0})
			if activity_type:
				date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
				self.activity_schedule(
					    activity_type_id=activity_type.id,
					    summary=activity_type.summary,
					    note=activity_type.default_note,
					    user_id=activity_user_id,
					    date_deadline=date_deadline
					)
			return activity_type
		return res

	def action_rfq_send(self):
		''' 
		This function opens a window to compose an email, with the edi purchase template message loaded by default
		'''
		self.ensure_one()
		if self.state == 'third_approve':
			self.write({'state' : 'sent'})
			ir_model_data = self.env['ir.model.data']
			try:
				if self.env.context.get('send_rfq', False):
				    template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase')[2]
				else:
				    template_id = ir_model_data._xmlid_lookup('purchase.email_template_edi_purchase_done')[2]
			except ValueError:
				template_id = False
			try:
				compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
			except ValueError:
				compose_form_id = False
			ctx = dict(self.env.context or {})
			ctx.update({
				'default_model': 'purchase.order',
				'active_model': 'purchase.order',
				'active_id': self.ids[0],
				'default_res_id': self.ids[0],
				'default_use_template': bool(template_id),
				'default_template_id': template_id,
				'default_composition_mode': 'comment',
				'custom_layout': "mail.mail_notification_paynow",
				'force_email': True,
				'mark_rfq_as_sent': True,
			})

			# In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
			# object. Therefore, we pass the model description in the context, in the language in which
			# the template is rendered.
			lang = self.env.context.get('lang')
			if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
				template = self.env['mail.template'].browse(ctx['default_template_id'])
			if template and template.lang:
			    lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

			self = self.with_context(lang=lang)
			if self.state in ['draft', 'sent']:
				ctx['model_description'] = _('Request for Quotation')
			else:
				ctx['model_description'] = _('Purchase Order')

			return {
				'name': _('Compose Email'),
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'res_model': 'mail.compose.message',
				'views': [(compose_form_id, 'form')],
				'view_id': compose_form_id,
				'target': 'new',
				'context': ctx,
			}

	def button_confirm(self):
		res = super(PurchaseOrder, self).button_confirm()
		if not self.env.user.has_group('rooks_purchase_approval.group_purchase_coordinator') or self.state == 'third_approve':
			raise UserError(_("Only Purchase Coordinator can confirm the PO once approved by Managing Director."))
		else:
			return res












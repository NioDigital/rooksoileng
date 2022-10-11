from odoo import api, fields, models, _
from datetime import datetime, date

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	def button_confirm(self):
		for order in self:
			if order.state not in ['draft', 'sent']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if order._approval_allowed():
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
				activity_user_id = False
				user = self.env['res.users'].search([])
				for loop in user:
					if loop.has_group('custom_purchase_double_approval.group_managing_director'):
						activity_user_id = loop.id
				print(activity_user_id,"Activity user id")
				activity_type = self.env['mail.activity.type'].sudo().search([('name','ilike','Confirm Purchase Order')])
				print(activity_type,"Activity TYPE")
				# if not activity_type:
				# 	activity_type = self.env['mail.activity.type'].create({'name':'Confirm Purchase Order',
				# 		'res_model':'purchase.order',
				# 		'delay_unit':'days',
				# 		'default_user_id': self.env.user.id,
				# 		'summary': 'Purchase Order Final Confirmation Notification',
				# 		'default_note': 'Please click on Confirm button for the Final confirmation',
				# 		'delay_count':0})
				if activity_type:
					date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type)
					# date_deadline = datetime.date.now()
					self.activity_schedule(
					    activity_type_id=activity_type.id,
					    summary=activity_type.summary,
					    note=activity_type.default_note,
					    user_id=activity_user_id,
					    date_deadline=date_deadline
					)
				return activity_type
			if order.partner_id not in order.message_partner_ids:
				order.message_subscribe([order.partner_id.id])
		return True

	def _approval_allowed(self):
		"""Returns whether the order qualifies to be approved by the current user"""
		self.ensure_one()
		return (
			self.company_id.po_double_validation == 'one_step'
			or (self.company_id.po_double_validation == 'two_step'
				and self.amount_total < self.env.company.currency_id._convert(
					self.company_id.po_double_validation_amount, self.currency_id, self.company_id,
					self.date_order or fields.Date.today()))
			or self.user_has_groups('custom_purchase_double_approval.group_managing_director'))
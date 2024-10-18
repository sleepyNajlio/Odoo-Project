from odoo import models, api, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class ProjectTask(models.Model):
	_inherit = 'project.task'

	client_description = fields.Html(string='Client Description', sanitize_attributes=False)
	dev_description = fields.Html(string='Developer Description', sanitize_attributes=False)
	is_accepted = fields.Boolean(string='Is Accepted', default=False, tracking=True)
	current_user_id = fields.Many2one('res.users', string='Current User', compute='_compute_current_user_id')
	stage_sequence = fields.Integer(related='stage_id.sequence')

	@api.depends('user_ids')
	def _compute_current_user_id(self):
		for task in self:
			task.current_user_id = self.env.user.id

	def accept_task(self):
		if self.allocated_hours <= 0:
			raise UserError('You must set the allocated hours for this task before accepting it')
		self.is_accepted = True
	
	@api.model
	def create(self, vals):
		if 'stage_id' in vals.keys():
			task_type = self.env['project.task.type'].browse(vals['stage_id'])
			if task_type.allow_create:
				return super().create(vals)
			else:
				raise UserError('You are not allowed to create a task in ' + str(task_type.name))
		else:
			return super().create(vals)
	def write(self, vals):
		print('write method for task: ' + str(self.name) + '-----------' + str(vals))
		# Estimation time validation
		if 'stage_id' in vals.keys():
			task_type = self.env['project.task.type'].browse(vals['stage_id'])
			if task_type.required_estimation:
				if 'is_accepted' in vals.keys() and vals['is_accepted'] == False:
					raise UserError('You must accept this task before moving it to ' + str(task_type.name))
				elif self.is_accepted == False and 'is_accepted' not in vals.keys():
					raise UserError('You must accept this task before moving it to ' + str(task_type.name))
				elif self.allocated_hours <= 0 and 'allocated_hours' not in vals.keys():
					raise UserError('You must set the allocated hours for this task before moving it to ' + str(task_type.name))
				elif 'allocated_hours' in vals.keys() and vals['allocated_hours'] <= 0:
					raise UserError('You must set the allocated hours for this task before moving it to ' + str(task_type.name))
		elif self.stage_id.required_estimation:
			if 'allocated_hours' in vals.keys() and vals['allocated_hours'] <= 0:
				raise UserError("only Strictly positive numbers")
		return super().write(vals)

	def timesheet_tracking_check(self):
		print("timesheet tracking check")

		# Getting current week start and end dates
		today = datetime.now().date()
		start_of_week = today - timedelta(days=today.weekday())
		end_of_week = start_of_week + timedelta(days=4)
		timesheets = self.env['account.analytic.line'].search([('date', '>=', start_of_week), ('date', '>=', end_of_week)])
		users = self.env['res.users'].search([])

		# Grouping timesheets by user
		group_timesheets = {}
		for timesheet in timesheets:
			if timesheet.user_id in group_timesheets.keys():
				group_timesheets[timesheet.user_id] = group_timesheets[timesheet.user_id] + timesheet.unit_amount
			else:
				group_timesheets[timesheet.user_id] = timesheet.unit_amount




		# Getting all accepted tasks and their assigned users
		# tasks = self.env['project.task'].search([('is_accepted', '==', True)])
		# users = []
		# for task in tasks:
		# 	for user in task.user_ids:
		# 		if user not in users:
		# 			users.append(user)
		#
		# # Grouping timesheets by user
		# group_timesheets = {}
		# for timesheet in timesheets:
		# 	if timesheet.user_id in group_timesheets.keys():
		# 		group_timesheets[timesheet.user_id] = group_timesheets[timesheet.user_id] + timesheet.unit_amount
		# 	else:
		# 		group_timesheets[timesheet.user_id] = timesheet.unit_amount
		#
		# # Adding users with no timesheet
		# for user in users:
		# 	if user not in group_timesheets.keys():
		# 		group_timesheets[user] = 0
		#
		# # Sending reminder to users with less than 6.5 hours of timesheet
		# for user in group_timesheets.keys():
		# 	if group_timesheets[user] < 6.5:
		# 		print('send reminder to ' + str(user.name))
		# 		self._send_timesheet_reminder(user)

	def _send_timesheet_reminder(self, user):
		message_body = f"Dear {user.name},\n\nYou have logged less than 7 hours of timesheet entries for yesterday. Please ensure your timesheet is up to date."

		user.partner_id.message_post(
				body=message_body,
				subject="Timesheet Reminder",
				# message_type='notification',  # This ensures it's a discussion comment
				subtype_id=self.env.ref('mail.mt_comment').id,  # Standard discussion subtype
				# partner_ids=[user.partner_id.id]  # Notify the user
		)
		# Optionally, print to the console (for debug purposes)
		print(f"Reminder sent to {user.name} to fill timesheet.")



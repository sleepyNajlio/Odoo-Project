from odoo import models, api, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class ProjectTask(models.Model):
	_inherit = 'project.task'

	client_description = fields.Html(string='Client Description', sanitize_attributes=False)
	dev_description = fields.Html(string='Developer Description', sanitize_attributes=False)
	start_time = fields.Datetime(string='Start Time')
	is_accepted = fields.Boolean(string='Is Accepted', default=False)
	current_user_id = fields.Many2one('res.users', string='Current User', compute='_compute_current_user_id')
	stage_sequence = fields.Integer(related='stage_id.sequence')


	# open wizard to set the allocated hours
	def open_estimation_time_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Estimation Time Wizard',
			'view_mode': 'form',
			'res_model': 'project.task.estimation.time.wizard',
			'target': 'new',
			'context': {
				'default_task_id': self.id,
			}
		}

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
		task_type = self.env['project.task.type'].browse(vals['stage_id'])
		if task_type.allow_create:
			return super().create(vals)
		else:
			raise UserError('You are not allowed to create a task in ' + str(task_type.name))
		
	def write(self, vals):
		print('write method -----------' + str(vals))
		# Estimation time validation
		if 'stage_id' in vals.keys():
			task_type = self.env['project.task.type'].browse(vals['stage_id'])
			if task_type.required_estimation:
				if 'is_accepted' in vals.keys() and vals['is_accepted'] == False:
					raise UserError('You must accept this task before moving it to ' + str(task_type.name))
				elif self.is_accepted == False and not 'is_accepted' in vals.keys():
					raise UserError('You must accept this task before moving it to ' + str(task_type.name))
				elif self.allocated_hours <= 0 and not 'allocated_hours' in vals.keys():
					raise UserError('You must set the allocated hours for this task before moving it to ' + str(task_type.name))
				elif 'allocated_hours' in vals.keys() and vals['allocated_hours'] <= 0:
					raise UserError('You must set the allocated hours for this task before moving it to ' + str(task_type.name))
				elif not self.start_time:
					self.start_time = datetime.now()
					# print("start time: " + str(self.start_time))
		elif self.stage_id.required_estimation:
			if 'allocated_hours' in vals.keys() and vals['allocated_hours'] <= 0:
				raise UserError(" You can't change the allocated hours of this task")
		return super().write(vals)

	def timesheet_tracking_check(self):
		print("timesheet tracking check")
		timesheets = self.env['account.analytic.line'].search([('date', '=', datetime.now().date() - timedelta(days=1))])
		# get all timesheets
		# timesheets = self.env['account.analytic.line'].search([])
		# get all users with assigned tasks
		tasks = self.env['project.task'].search([])
		users = []
		for task in tasks:
			for user in task.user_ids:
				if user not in users:
					users.append(user)

		print("users : " + str(users))
		## Grouping timesheets by user
		# print group timesheets users
		# for user in users:
		# 	print("user : " + str(user.name))
		# groupe_timesheets = {}
		# for timesheet in timesheets:
		# 	if timesheet.user_id in groupe_timesheets.keys():
		# 		groupe_timesheets[timesheet.user_id] = groupe_timesheets[timesheet.user_id] + timesheet.unit_amount
		# 	else:
		# 		groupe_timesheets[timesheet.user_id] = timesheet.unit_amount
		# for user in users:
		# 	if user.user_id not in groupe_timesheets.keys():
		# 		groupe_timesheets[user.user_id] = 0
		#
		# for user in groupe_timesheets.keys():
		# 	print(str(user.name) + " : " + str(groupe_timesheets[user]))
		#
		# for user in groupe_timesheets.keys():
		# 	if groupe_timesheets[user] < 6.5:
		# 		print('send reminder to ' + str(user.name))
		# 		self._send_timesheet_reminder(user)

	def _send_timesheet_reminder(self, user):
		print(user.partner_id)
		# user.notify_success(message='My success message')
		# Create the message body
		message_body = f"Dear {user.name},\n\nYou have logged less than 7 hours of timesheet entries for yesterday. Please ensure your timesheet is up to date."
		
		# Send the discussion message to the user
		user.partner_id.message_post(
				body=message_body,
				subject="Timesheet Reminder",
				# message_type='notification',  # This ensures it's a discussion comment
				subtype_id=self.env.ref('mail.mt_comment').id,  # Standard discussion subtype
				# partner_ids=[user.partner_id.id]  # Notify the user
		)
		# Optionally, print to the console (for debug purposes)
		print(f"Reminder sent to {user.name} to fill timesheet.")



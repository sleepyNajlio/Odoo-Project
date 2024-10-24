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
	dev_hours = fields.Float(string='Developer Hours', tracking=True)
	analyse_hours = fields.Float(string='Analyse Hours', compute='_compute_analyse_hours')
	review_hours = fields.Float(string='Review Hours', compute='_compute_review_hours')
	allocated_hours = fields.Float("Total Allocated Time", compute="_compute_allocated_hours", tracking=True)
	hide_accept_button = fields.Boolean(compute='_compute_hide_accept_button')

	@api.depends('write_date', 'stage_id', 'current_user_id', 'user_ids')
	def _compute_hide_accept_button(self):
		for task in self:
			required_estimation = task.stage_id.required_estimation
			task.hide_accept_button = task.is_accepted  or required_estimation or (task.current_user_id not in task.user_ids)


	@api.depends('dev_hours')
	def _compute_analyse_hours(self):
		for rec in self:
			project = self.env['project.project'].browse(rec.project_id.id)
			for task in rec:
				task.analyse_hours = task.dev_hours * project.analyse_hours_pc / 100

	@api.depends('dev_hours')
	def _compute_review_hours(self):
		for rec in self:
			project = self.env['project.project'].browse(rec.project_id.id)
			for task in rec:
				task.review_hours = task.dev_hours * project.review_hours_pc / 100

	@api.depends('dev_hours', 'analyse_hours', 'review_hours')
	def _compute_allocated_hours(self):
		for task in self:
			task.allocated_hours = task.dev_hours + task.analyse_hours + task.review_hours

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
		if 'stage_id' in vals.keys():
			task_type = self.env['project.task.type'].browse(vals['stage_id'])
			if task_type.required_estimation:
				if 'is_accepted' in vals.keys() and vals['is_accepted'] == False:
					raise UserError('You must accept this task before moving it to ' + str(task_type.name))
				elif self.is_accepted == False and 'is_accepted' not in vals.keys():
					raise UserError('You must accept this task before moving it to ' + str(task_type.name))
			if task_type.required_timesheet:
				if 'timesheet_ids' in vals.keys() and len(vals['timesheet_ids']) == 0:
					raise UserError('You must log timesheet entries before moving this task to ' + str(task_type.name))
				elif len(self.timesheet_ids) == 0 and 'timesheet_ids' not in vals.keys():
					raise UserError('You must log timesheet entries before moving this task to ' + str(task_type.name))
		elif self.stage_id.required_estimation:
			if 'allocated_hours' in vals.keys() and vals['allocated_hours'] <= 0:
				raise UserError("only Strictly positive numbers")

		return super().write(vals)



from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectTaskType(models.Model):
	_inherit = 'project.task.type'

	allow_create = fields.Boolean(default=False)
	required_estimation = fields.Boolean(default=False)
	required_timesheet = fields.Boolean(default=False)
	




	# def write(self, vals):
	# 	# print('write method -----------' + str(vals))
	# 	# if 'sequence' in vals.keys():
		# 	raise UserError('You are not allowed to change the sequence of a task type')
		# return super().write(vals)

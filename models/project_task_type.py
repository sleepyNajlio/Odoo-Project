from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectTaskType(models.Model):
	_inherit = 'project.task.type'

	allow_create = fields.Boolean(default=False)
	required_estimation = fields.Boolean(default=False)
	required_timesheet = fields.Boolean(default=False)

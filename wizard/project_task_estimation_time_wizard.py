from odoo import models, fields
from odoo.exceptions import UserError

class ProjectTaskEstimationTimeWizard(models.TransientModel):
	_name = "project.task.estimation.time.wizard"
	_description = "Estimation time wizard"

	task_id = fields.Many2one('project.task')
	estimation_time = fields.Float(required=True, default=0)

	def action_confirm(self):
		print(self)
		# if self.estimation_time < 0:
		# 	raise UserError("estimation time should not be less than 0")
		# else:
		# 	print(str(self.task_id))

		return {
            'type': 'ir.actions.act_window_close'
        	}
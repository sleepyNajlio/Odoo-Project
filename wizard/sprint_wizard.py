from odoo import models, fields

class SprintWizard(models.TransientModel):
	_name = 'sprint.wizard'
	_description = 'Sprint Wizard'

	project_id = fields.Many2one('project.project', string='Project', required=True)
	start_date = fields.Date(string='Start Date', required=True)
	end_date = fields.Date(string='End Date', required=True)

	def create_sprint(self):
		self.env['lean_project.sprint'].create({
			'project_id': self.project_id.id,
			'start_date': self.start_date,
			'end_date': self.end_date
		})
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}
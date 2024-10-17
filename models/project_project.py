from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_template_id = fields.Many2one('project.template', string='Project Template')

    @api.model
    def create(self, vals):
        project = super().create(vals)
        print('project: ' + str(vals))
        if 'project_template_id' in vals.keys() and vals['project_template_id']:
            project_template = self.env['project.template'].browse(vals['project_template_id'])
            stage_ids = project_template.task_type_ids
            print('stages: ' + str(stage_ids.mapped('id')))
            project.type_ids = stage_ids
            print("type_ids: " + str(project.type_ids))
        return project




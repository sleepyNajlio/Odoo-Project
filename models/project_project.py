
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_template_id = fields.Many2one('project.template', string='Project Template')
    business_analyst_id = fields.Many2one('res.users', string="Business Analyst")
    code_review_id = fields.Many2one('res.users', string="Code Review")
    analyse_hours_pc = fields.Integer(string="Business Analyse Allocated Time (%)", required=True)
    review_hours_pc =fields.Integer(string="Code Review Allocated Time (%)", required=True)

    @api.model
    def create(self, vals):
        project = super().create(vals)
        # print('project: ' + str(vals))
        if 'project_template_id' in vals.keys() and vals['project_template_id']:
            project_template = self.env['project.template'].browse(vals['project_template_id'])
            stage_ids = project_template.task_type_ids
            # print('stages: ' + str(stage_ids.mapped('id')))
            project.type_ids = stage_ids
            # print("type_ids: " + str(project.type_ids))
        return project


    @api.constrains('analyse_hours_pc', 'review_hours_pc')
    def check_percentage(self):
        if self.analyse_hours_pc < 0 or self.analyse_hours_pc > 100:
            raise ValidationError("The business analyse allocated time must be between 0 and 100")
        if self.review_hours_pc < 0 or self.review_hours_pc > 100:
            raise ValidationError("The code review allocated time must be between 0 and 100")


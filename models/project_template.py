from odoo import models, fields, api

class ProjectTemplate(models.Model):
    _name = 'project.template'
    _description = 'Project Template'

    name = fields.Char(string='Name')
    task_type_ids = fields.Many2many('project.task.type', string='Tasks Types')






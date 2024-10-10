from datetime import timedelta, datetime
from odoo import models, fields, api

class ProjectSprint(models.Model):
    _name = 'project.sprint'
    _description = 'Sprint'
    _order = 'start_date desc , end_date asc'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    project_id = fields.Many2one('project.project', string='Project', required=True)
    start_date = fields.Date(string='Start Date', required=True, default=lambda self:self._get_start_date())
    end_date = fields.Date(string='End Date', required=True, default=lambda self:self._get_start_date() + timedelta(days=4))
    user_ids = fields.Many2many('res.users', string='Users')
    task_ids = fields.Many2many('project.task', string='Tasks')
    progress = fields.Float("Progress", compute='_compute_sprint_progress', store=True, group_operator="avg")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='State', default='draft')


    @api.depends('task_ids')
    def _compute_sprint_progress(self):
        for sprint in self:
            if sprint.task_ids:
                total_hours = sum(task.allocated_hours for task in sprint.task_ids)
                spent_hours = sum(task.effective_hours for task in sprint.task_ids)
                sprint.progress = (spent_hours / total_hours) * 100
            else:
                sprint.progress = 0

    @staticmethod
    def _get_start_date():
        today = datetime.now().date()
        if today.weekday() > 3:
            return today + timedelta(days=7 - today.weekday())
        else:
            return today - timedelta(days=today.weekday())

    # Button Actions
    def action_start_sprint(self):
        for record in self:
            sprint_stage = record.env['project.task.type'].search([('name', '=', 'Sprint')])
            record.state = 'in_progress'
            for task in record.task_ids:
                task.write({'stage_id': sprint_stage.id})

    def action_cancel_sprint(self):
        for record in self:
            backlog_stage = record.env['project.task.type'].search([('name', '=', 'Backlog')])
            record.state = 'canceled'
            for task in record.task_ids:
                if task.stage_id.name == 'Sprint':
                    task.write({'stage_id': backlog_stage.id})

    def action_done_sprint(self):
        for record in self:
            record.state = 'done'







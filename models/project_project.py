from lib2to3.fixes.fix_input import context

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

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

    _logger = logging.getLogger(__name__)

    def timesheet_tracking_check(self):
        print("timesheet tracking check")
        # self._logger.info("timesheet tracking check")
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        timesheets = self.env['account.analytic.line'].search([('date', '>=', start_of_week), ('date', '<=', end_of_week)])
        users = self.env['res.users'].search([('share', '=', False), ('state', '=', 'active')])
        group_timesheets = {}
        for timesheet in timesheets:
            if timesheet.user_id in group_timesheets.keys():
                group_timesheets[timesheet.user_id] = group_timesheets[timesheet.user_id] + timesheet.unit_amount
            else:
                group_timesheets[timesheet.user_id] = timesheet.unit_amount
        for user in users:
            if user not in group_timesheets.keys():
                group_timesheets[user] = 0

        for user in group_timesheets.keys():
            if group_timesheets[user] < 32:
                print('send reminder to ' + str(user.name))
                self._send_timesheet_reminder(user, start_of_week, end_of_week)

    def _send_timesheet_reminder(self, user, start_of_week, end_of_week):
        user_timesheet = self.env['account.analytic.line'].search([('user_id', '=', user.id), ('date', '>=', start_of_week), ('date', '<=', end_of_week)])
        date_range = {start_of_week + timedelta(days=i): 0 for i in range((end_of_week - start_of_week).days + 1)}
        for timesheet in user_timesheet:
            date_range[timesheet.date] += timesheet.unit_amount

        template_context = {
            'date_range': date_range,
            'date_start': start_of_week,
            'date_stop': end_of_week,

        }



        template = self.env.ref('leansoft_project.mail_template_timesheet_weekly_reminder_user')

        template.with_context(template_context).send_mail(user.id, force_send=True)

        # Optionally, print to the console (for debug purposes)
        print(f"Reminder sent to {user.name} to fill timesheet.")



{
    'name' : 'leansoft project',
    'version' : '1.0',
    'summary': 'Project management',
    'sequence': 10,
    'description': """
			""",
    'depends': ['base','project','timesheet_grid'],
    'data': [
        'security/ir.model.access.csv',
		'views/project_task_type_views.xml',
        'views/project_task_views.xml',
        'views/project_sprint_views.xml',
        'views/project_template_views.xml',
        'views/project_project_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}



{
    'name' : 'leansoft project',
    'version' : '1.0',
    'summary': 'Project management',
    'sequence': 10,
    'description': """
			""",
    'depends': ['base','project'],
    'data': [
        'security/ir.model.access.csv',
		'data/project_data.xml',
        'data/task_type_data.xml',
		'views/project_task_type_views.xml',
		'wizard/project_task_estimation_time_wizard_views.xml',
        'views/project_task_views.xml',
		'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

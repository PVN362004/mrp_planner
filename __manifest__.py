{
    'name': 'Product Inventory',
    'version': '19.0.1.0.0',
    'category': 'Management',
    'summary': 'Product Inventory',
    'author': 'Nhan',
    'license': 'AGPL-3',
    'depends': ['base', 'product', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/readonly_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': -1,
}
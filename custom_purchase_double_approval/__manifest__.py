# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Purchase Order Double Approval',
    'summary': """ Custom Purchase Order Double Approval """,
    'description': """ Purchase Order Double Approval """,
    'version': '15.0.1.0.0',
    'author': 'Nio Digital',
    'company': 'Nio Digital',
    'maintainer': 'Nio Digital',
    'website': 'https://www.nio.odoo.com/',
    'category': 'Purchase',
    'depends': ['base', 'purchase'],
    'license': 'AGPL-3',
    'data': [
        'security/hr_security.xml',
        # 'views/res_company_inherited.xml',
        # 'views/res_config_settings_inherited.xml',
        # 'views/sale_order_inherited.xml',
        'views/purchase_order.xml',
        'views/purchase_report.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

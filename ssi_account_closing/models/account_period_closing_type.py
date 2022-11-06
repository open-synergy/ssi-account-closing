# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class AccountPeriodClosingType(models.Model):
    _name = "account.period_closing_type"
    _inherit = ["mixin.master_data"]
    _description = "Period Closing Type"

    name = fields.Char(
        string="Period Closing Type",
    )
    journal_id = fields.Many2one(
        string="Default Journal",
        comodel_name="account.journal",
    )
    period_type_ids = fields.Many2many(
        string="Period Type(s)",
        comodel_name="date.range.type",
        relation="rel_period_closing_type_2_date_range_type",
        column1="period_closing_type_id",
        column2="date_range_type_id",
    )
    mapping_ids = fields.One2many(
        string="Mapping",
        comodel_name="account.period_closing_type_mapping",
        inverse_name="type_id",
    )

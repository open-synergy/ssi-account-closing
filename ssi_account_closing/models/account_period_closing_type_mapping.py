# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class AccountPeriodClosingTypeMapping(models.Model):
    _name = "account.period_closing_type_mapping"
    _description = "Period Closing Type Mapping"
    _order = "sequence, id"

    type_id = fields.Many2one(
        string="Closing Type",
        comodel_name="account.period_closing_type",
    )
    name = fields.Char(
        string="Description",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
        required=True,
    )
    python_computation = fields.Text(
        string="Computation",
        required=True,
        default="AccountingNone",
    )
    destination_account_domain = fields.Text(
        string="Destination Account Domain",
        required=True,
        default="[]",
    )

    def _compute_destination_account_ids(self):
        Account = self.env["account.account"]
        for record in self:
            domain = safe_eval(record.destination_account_domain, {})
            result = Account.search(domain).ids
            record.destination_account_ids = result

    destination_account_ids = fields.Many2many(
        string="Destination Account(s)",
        comodel_name="account.account",
        compute="_compute_destination_account_ids",
    )

# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models

from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor as AEP
from odoo.addons.mis_builder.models.mis_safe_eval import mis_safe_eval


class AccountPeriodClosingMapping(models.Model):
    _name = "account.period_closing_mapping"
    _description = "Period Closing Mapping"
    _order = "closing_id, sequence, id"

    closing_id = fields.Many2one(
        string="Period Closing",
        comodel_name="account.period_closing",
        required=True,
        ondelete="cascade",
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
    account_ids = fields.Many2many(
        string="Account(s)",
        comodel_name="account.account",
        relation="rel_period_closing_mapping_2_account",
        column1="mapping_id",
        column2="account_id",
    )

    def _prepare_create_move_line(self, account, amount):
        self.ensure_one()
        return {
            "name": self.name,
            "account_id": account.id,
            "debit": amount > 0 and abs(amount) or 0.0,
            "credit": amount < 0 and abs(amount) or 0.0,
        }

    def _prepare_move_line(self):
        self.ensure_one()
        result = []
        for account in self.account_ids:
            amount = self._compute_amount(account)
            if isinstance(amount, float):
                result.append((0, 0, self._prepare_create_move_line(account, amount)))
        return result

    def _compute_amount(self, account):
        self.ensure_one()
        aep = AEP(self.closing_id.company_id, False, "account.account")
        computation = self.python_computation.replace("account", account.code)
        aep.parse_expr(computation)
        aep.done_parsing()
        aep.do_queries(self.closing_id.date_start, self.closing_id.date_end)
        computation = aep.replace_expr(computation)
        return mis_safe_eval(computation, {})

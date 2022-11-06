# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountClosing(models.Model):
    _name = "account.period_closing"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.date_duration",
    ]
    _description = "Account Period Closing"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_open",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    # Mixin duration attribute
    _date_start_readonly = True
    _date_end_readonly = True
    _date_start_states_list = ["draft"]
    _date_start_states_readonly = ["draft"]
    _date_end_states_list = ["draft"]
    _date_end_states_readonly = ["draft"]

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="account.period_closing_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.depends(
        "type_id",
    )
    def _compute_allowed_period_ids(self):
        DateRange = self.env["date.range"]
        for record in self:
            result = []
            if record.type_id:
                domain = [
                    ("type_id", "in", record.type_id.period_type_ids.ids),
                ]
                result = DateRange.search(domain).ids
            record.allowed_period_ids = result

    allowed_period_ids = fields.Many2many(
        string="Allowed Period(s)",
        comodel_name="date.range",
        compute="_compute_allowed_period_ids",
        store=False,
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="date.range",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    move_id = fields.Many2one(
        string="# Accounting Entry",
        comodel_name="account.move",
        readonly=True,
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        domain=[
            ("type", "=", "general"),
        ],
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    mapping_ids = fields.One2many(
        string="Mapping(s)",
        comodel_name="account.period_closing_mapping",
        inverse_name="closing_id",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )

    @api.model
    def _get_policy_field(self):
        res = super(AccountClosing, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    def action_done(self):
        _super = super(AccountClosing, self)
        _super.action_done()
        for record in self.sudo():
            record._create_accounting_entry()

    def action_cancel(self, cancel_reason=False):
        _super = super(AccountClosing, self)
        _super.action_cancel(cancel_reason)
        for record in self.sudo():
            record._unlink_accounting_entry()

    def _unlink_accounting_entry(self):
        self.ensure_one()
        if self.move_id:
            self.move_id.with_context(force_delete=True).unlink()

    def _create_accounting_entry(self):
        self.ensure_one()
        AccountMove = self.env["account.move"]
        move = AccountMove.with_context(check_move_validity=False).create(
            self._prepare_account_move()
        )

        for mapping in self.mapping_ids:
            mapping._create_move_line(move)

        move.action_post()

        self.write(
            {
                "move_id": move.id,
            }
        )

    def _prepare_account_move(self):
        self.ensure_one()
        return {
            "name": self.name,
            "journal_id": self.journal_id.id,
            "date": self.date,
        }

    @api.onchange(
        "period_id",
    )
    def onchange_date_start(self):
        self.date_start = False
        if self.period_id:
            self.date_start = self.period_id.date_start

    @api.onchange(
        "period_id",
    )
    def onchange_date_end(self):
        self.date_end = False
        if self.period_id:
            self.date_end = self.period_id.date_end

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange(
        "type_id",
    )
    def onchange_mapping_ids(self):
        self.mapping_ids = False
        result = []
        if self.type_id:
            for mapping in self.type_id.mapping_ids:
                result.append(
                    (
                        0,
                        0,
                        {
                            "sequence": mapping.sequence,
                            "name": mapping.name,
                            "python_computation": mapping.python_computation,
                            "account_ids": mapping.destination_account_ids.ids,
                        },
                    )
                )
        self.mapping_ids = result

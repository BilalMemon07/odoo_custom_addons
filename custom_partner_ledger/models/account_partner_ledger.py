from odoo import models, api, fields, _
from odoo.tools import date_utils
from odoo.tools import SQL
from odoo.exceptions import UserError

class PartnerLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    def _get_custom_display_config(self):
        res = super()._get_custom_display_config()
        res['templates']['AccountReportFilters'] = 'custom_partner_ledger.AccountFilterAccount'
        return res

    def _get_query_sums(self, report, options) -> SQL:
        """ Override to filter partners based on payment dates """
        queries = []
        print("======================>" + str(options))
        
        payment_date_from = options.get('payment_date')['date_from']
        payment_date_to = options.get('payment_date')['date_to']
        if payment_date_from or payment_date_to:
            # raise UserError(str(options.get('payment_date')['date_from']))
            # Create the currency table.
            for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
                query = report._get_report_query(column_group_options, 'from_beginning')
                
                date_from = options['date']['date_from']
                
                # Main query for partner sums
                queries.append(SQL(
                    """
                    (WITH partner_sums AS (
                        SELECT
                            account_move_line.partner_id            AS groupby,
                            %(column_group_key)s                    AS column_group_key,
                            SUM(%(debit_select)s)                   AS debit,
                            SUM(%(credit_select)s)                  AS credit,
                            SUM(%(balance_select)s)                 AS amount,
                            SUM(%(balance_select)s)                 AS balance,
                            BOOL_AND(account_move_line.reconciled)  AS all_reconciled,
                            MAX(account_move_line.date)             AS latest_date
                        FROM %(table_references)s
                        %(currency_table_join)s
                        WHERE %(search_condition)s
                        GROUP BY account_move_line.partner_id
                    )
                    SELECT *
                    FROM partner_sums ps
                    WHERE ps.balance != 0
                    OR ps.all_reconciled = FALSE
                    OR ps.latest_date >= %(date_from)s
                    %(payment_date_filter)s
                    )""",
                    column_group_key=column_group_key,
                    debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
                    credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
                    balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
                    table_references=query.from_clause,
                    currency_table_join=report._currency_table_aml_join(column_group_options),
                    search_condition=query.where_clause,
                    date_from=date_from,
                    payment_date_filter=SQL(
                        "AND NOT EXISTS ("
                        "SELECT 1 FROM account_move_line aml "
                        "JOIN account_move am ON am.id = aml.move_id "
                        "JOIN account_payment ap ON ap.move_id = am.id "
                        "WHERE aml.partner_id = ps.groupby "
                        "AND am.state = 'posted' "
                        "AND ap.date >= %s AND ap.date <= %s"
                        ")", 
                        payment_date_from or '1900-01-01', 
                        payment_date_to or '9999-12-31'
                    ) if payment_date_from or payment_date_to else SQL("")
                ))

            return SQL(' UNION ALL ').join(queries)
        else:
            # Create the currency table.
            for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
                query = report._get_report_query(column_group_options, 'from_beginning')
                date_from = options['date']['date_from']
                queries.append(SQL(
                    """
                    (WITH partner_sums AS (
                        SELECT
                            account_move_line.partner_id            AS groupby,
                            %(column_group_key)s                    AS column_group_key,
                            SUM(%(debit_select)s)                   AS debit,
                            SUM(%(credit_select)s)                  AS credit,
                            SUM(%(balance_select)s)                 AS amount,
                            SUM(%(balance_select)s)                 AS balance,
                            BOOL_AND(account_move_line.reconciled)  AS all_reconciled,
                            MAX(account_move_line.date)             AS latest_date
                        FROM %(table_references)s
                        %(currency_table_join)s
                        WHERE %(search_condition)s
                        GROUP BY account_move_line.partner_id
                    )
                    SELECT *
                    FROM partner_sums
                    WHERE partner_sums.balance != 0
                    OR partner_sums.all_reconciled = FALSE
                    OR partner_sums.latest_date >= %(date_from)s
                    )""",
                    column_group_key=column_group_key,
                    debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
                    credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
                    balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
                    table_references=query.from_clause,
                    currency_table_join=report._currency_table_aml_join(column_group_options),
                    search_condition=query.where_clause,
                    date_from=date_from,
                ))

            return SQL(' UNION ALL ').join(queries)


    def _get_sums_without_partner(self, options):
        """ Override to filter reconciled lines based on payment dates """
        queries = []

        payment_date_from = options.get('payment_date')['date_from']
        payment_date_to = options.get('payment_date')['date_to']
        if payment_date_from or payment_date_to:

            report = self.env.ref('account_reports.partner_ledger_report')
            for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
                query = report._get_report_query(column_group_options, 'from_beginning')
                
                queries.append(SQL(
                    """
                    SELECT
                        %(column_group_key)s        AS column_group_key,
                        aml_with_partner.partner_id AS groupby,
                        SUM(%(debit_select)s)       AS debit,
                        SUM(%(credit_select)s)      AS credit,
                        SUM(%(balance_select)s)     AS amount,
                        SUM(%(balance_select)s)     AS balance
                    FROM %(table_references)s
                    JOIN account_partial_reconcile partial
                        ON account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id
                    JOIN account_move_line aml_with_partner ON
                        (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                        AND aml_with_partner.partner_id IS NOT NULL
                    %(currency_table_join)s
                    LEFT JOIN account_move am ON am.id = aml_with_partner.move_id
                    LEFT JOIN account_payment ap ON ap.move_id = am.id
                    WHERE partial.max_date <= %(date_to)s AND %(search_condition)s
                        AND account_move_line.partner_id IS NULL
                        %(payment_date_filter)s
                    GROUP BY aml_with_partner.partner_id
                    """,
                    column_group_key=column_group_key,
                    debit_select=report._currency_table_apply_rate(SQL("CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE partial.amount END")),
                    credit_select=report._currency_table_apply_rate(SQL("CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE partial.amount END")),
                    balance_select=report._currency_table_apply_rate(SQL("-SIGN(aml_with_partner.balance) * partial.amount")),
                    table_references=query.from_clause,
                    currency_table_join=report._currency_table_aml_join(column_group_options, aml_alias=SQL("aml_with_partner")),
                    date_to=column_group_options['date']['date_to'],
                    search_condition=query.where_clause,
                    payment_date_filter=SQL(
                        "AND (ap.id IS NULL OR ap.date < %s OR ap.date > %s)", 
                        payment_date_from or '1900-01-01', 
                        payment_date_to or '9999-12-31'
                    ) if payment_date_from or payment_date_to else SQL("")
                ))

            return SQL(" UNION ALL ").join(queries)
        else:
            report = self.env.ref('account_reports.partner_ledger_report')
            for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
                query = report._get_report_query(column_group_options, 'from_beginning')
                queries.append(SQL(
                    """
                    SELECT
                        %(column_group_key)s        AS column_group_key,
                        aml_with_partner.partner_id AS groupby,
                        SUM(%(debit_select)s)       AS debit,
                        SUM(%(credit_select)s)      AS credit,
                        SUM(%(balance_select)s)     AS amount,
                        SUM(%(balance_select)s)     AS balance
                    FROM %(table_references)s
                    JOIN account_partial_reconcile partial
                        ON account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id
                    JOIN account_move_line aml_with_partner ON
                        (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                        AND aml_with_partner.partner_id IS NOT NULL
                    %(currency_table_join)s
                    WHERE partial.max_date <= %(date_to)s AND %(search_condition)s
                        AND account_move_line.partner_id IS NULL
                    GROUP BY aml_with_partner.partner_id
                    """,
                    column_group_key=column_group_key,
                    debit_select=report._currency_table_apply_rate(SQL("CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE partial.amount END")),
                    credit_select=report._currency_table_apply_rate(SQL("CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE partial.amount END")),
                    balance_select=report._currency_table_apply_rate(SQL("-SIGN(aml_with_partner.balance) * partial.amount")),
                    table_references=query.from_clause,
                    currency_table_join=report._currency_table_aml_join(column_group_options, aml_alias=SQL("aml_with_partner")),
                    date_to=column_group_options['date']['date_to'],
                    search_condition=query.where_clause,
                ))

            return SQL(" UNION ALL ").join(queries)
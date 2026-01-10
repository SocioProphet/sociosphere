-- Income Statement skeleton.
-- Expects a canonical ledger table: finance_journal_lines(period, account_id, amount, side, currency, statement_line_id)

select
  period,
  statement_line_id,
  sum(
    case
      when side = 'credit' then amount
      when side = 'debit' then -amount
      else 0
    end
  ) as value
from finance_journal_lines
where statement_line_id in ('Revenue','COGS','OperatingExpenses')
group by 1,2
order by 1,2;

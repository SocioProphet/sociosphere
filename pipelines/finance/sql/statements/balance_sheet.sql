-- Balance Sheet skeleton.
-- Expects finance_journal_lines(period, account_id, amount, side, currency, statement_line_id)

select
  period,
  statement_line_id,
  sum(
    case
      when side = 'debit' then amount
      when side = 'credit' then -amount
      else 0
    end
  ) as value
from finance_journal_lines
where statement_line_id in ('Cash','AccountsReceivable','DeferredRevenue','Equity')
group by 1,2
order by 1,2;

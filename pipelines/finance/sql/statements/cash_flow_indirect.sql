-- Cash Flow (Indirect) skeleton (placeholder).
-- Expects finance_journal_lines(period, account_id, amount, side, currency, statement_line_id)

select
  period,
  'OperatingCashFlow' as statement_line_id,
  sum(
    case
      when statement_line_id = 'OperatingCashFlow' then
        case when side = 'debit' then amount when side='credit' then -amount else 0 end
      else 0
    end
  ) as value
from finance_journal_lines
group by 1;

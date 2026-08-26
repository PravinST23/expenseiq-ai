import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { analyticsApi } from '../api/resources'
import { Card, ErrorBanner, Spinner, StatCard } from '../components/ui'
import { CATEGORICAL, STATUS } from '../theme'

function ChartCard({ title, subtitle, children }) {
  return (
    <Card className="p-5">
      <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
      {subtitle ? (
        <p className="text-xs text-slate-500">{subtitle}</p>
      ) : null}
      <div className="mt-4 h-72">{children}</div>
    </Card>
  )
}

const STATUS_COLOR_MAP = {
  Approved: STATUS.good,
  Rejected: STATUS.critical,
}

function statusColor(status, index) {
  return STATUS_COLOR_MAP[status] || CATEGORICAL[index % CATEGORICAL.length]
}

export default function Analytics() {
  const [overview, setOverview] = useState(null)
  const [byCategory, setByCategory] = useState(null)
  const [byEmployee, setByEmployee] = useState(null)
  const [approvalSummary, setApprovalSummary] = useState(null)
  const [liability, setLiability] = useState(null)
  const [aiAccuracy, setAiAccuracy] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      analyticsApi.overview(),
      analyticsApi.spendByCategory(),
      analyticsApi.spendByEmployee(),
      analyticsApi.approvalStatusSummary(),
      analyticsApi.reimbursementLiability(),
      analyticsApi.aiAccuracy(),
    ])
      .then(
        ([
          overviewData,
          category,
          employee,
          summary,
          liabilityData,
          accuracy,
        ]) => {
          setOverview(overviewData)
          setByCategory(category)
          setByEmployee(employee)
          setApprovalSummary(summary)
          setLiability(liabilityData)
          setAiAccuracy(accuracy)
        },
      )
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <ErrorBanner message={error} />
  if (!overview) return <Spinner />

  return (
    <div>
      <h1 className="text-xl font-semibold text-slate-900">
        Expense Analytics
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Live feeds - the same endpoints Power BI connects to via Get Data
        → Web.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Employees" value={overview.total_employees} />
        <StatCard label="Total Claims" value={overview.total_expenses} />
        <StatCard
          label="Total Spend"
          value={`₹${overview.total_amount.toLocaleString('en-IN')}`}
        />
        <StatCard
          label="Approved Value"
          value={`₹${overview.approved_amount.toLocaleString('en-IN')}`}
          tone="good"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartCard
          title="Spend by Category"
          subtitle="Total amount claimed per expense category"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={byCategory} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="category"
                tick={{ fontSize: 11 }}
                width={110}
              />
              <Tooltip
                formatter={(value) => `₹${Number(value).toLocaleString('en-IN')}`}
              />
              <Bar dataKey="total_amount" radius={[0, 4, 4, 0]}>
                {byCategory.map((entry, index) => (
                  <Cell
                    key={entry.category}
                    fill={CATEGORICAL[index % CATEGORICAL.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Spend by Employee"
          subtitle="Top claimants by total amount"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={byEmployee.slice(0, 8)}
              margin={{ bottom: 40 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis
                dataKey="employee_name"
                tick={{ fontSize: 10 }}
                angle={-30}
                textAnchor="end"
                interval={0}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(value) => `₹${Number(value).toLocaleString('en-IN')}`}
              />
              <Bar
                dataKey="total_amount"
                radius={[4, 4, 0, 0]}
                fill={CATEGORICAL[0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Approval Status Summary"
          subtitle="Where every claim currently sits in the workflow"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={approvalSummary}
                dataKey="count"
                nameKey="status"
                innerRadius={60}
                outerRadius={95}
                paddingAngle={2}
              >
                {approvalSummary.map((entry, index) => (
                  <Cell
                    key={entry.status}
                    fill={statusColor(entry.status, index)}
                  />
                ))}
              </Pie>
              <Legend
                verticalAlign="bottom"
                wrapperStyle={{ fontSize: 11 }}
              />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Reimbursement Liability Tracker"
          subtitle={`Outstanding liability: ₹${liability.outstanding_liability.toLocaleString('en-IN')}`}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={liability.by_state}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="state" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(value) => `₹${Number(value).toLocaleString('en-IN')}`}
              />
              <Bar dataKey="total_amount" radius={[4, 4, 0, 0]}>
                {liability.by_state.map((entry) => (
                  <Cell
                    key={entry.state}
                    fill={
                      entry.state === 'PAID'
                        ? STATUS.good
                        : entry.state === 'APPROVED'
                          ? STATUS.warning
                          : CATEGORICAL[0]
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <Card className="mt-6 p-5">
        <h2 className="text-sm font-semibold text-slate-900">
          AI Pipeline Accuracy Feed
        </h2>
        <p className="text-xs text-slate-500">
          QA evidence: risk score distribution and duplicate detection
          rate across all processed receipts.
        </p>
        <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-5">
          <StatCard
            label="Total Processed"
            value={aiAccuracy.total_expenses}
          />
          <StatCard
            label="Duplicate Rate"
            value={`${aiAccuracy.duplicate_rate}%`}
            tone={aiAccuracy.duplicate_rate > 0 ? 'critical' : 'good'}
          />
          <StatCard
            label="Avg Fraud Risk"
            value={aiAccuracy.average_fraud_risk?.toFixed(0) ?? 'n/a'}
          />
          <StatCard
            label="Avg Compliance Risk"
            value={aiAccuracy.average_compliance_risk?.toFixed(0) ?? 'n/a'}
          />
          <StatCard
            label="Avg AI Confidence"
            value={aiAccuracy.average_confidence?.toFixed(0) ?? 'n/a'}
            tone="good"
          />
        </div>
      </Card>
    </div>
  )
}

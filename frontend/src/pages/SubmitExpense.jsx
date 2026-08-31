import { useEffect, useState } from 'react'
import { useSession } from '../context/session'
import { expensesApi, projectsApi, receiptsApi } from '../api/resources'
import {
  Button,
  Card,
  ErrorBanner,
  Field,
  inputClass,
  Spinner,
} from '../components/ui'
import {
  DuplicateBadge,
  EngineBadge,
  RecommendationBadge,
  RiskBadge,
  StatusBadge,
} from '../components/badges'

const CATEGORIES = [
  'Travel',
  'Meals',
  'Hotel',
  'Office Supplies',
  'Entertainment',
  'Software Subscription',
  'Client Entertainment',
]

const EMPTY_FORM = {
  project_id: '',
  expense_category: 'Travel',
  merchant_name: '',
  amount: '',
  currency: 'INR',
  expense_date: new Date().toISOString().slice(0, 10),
  payment_method: 'Card',
  description: '',
  is_sensitive: false,
}

export default function SubmitExpense() {
  const { session } = useSession()

  const [projects, setProjects] = useState([])
  const [form, setForm] = useState(EMPTY_FORM)
  const [file, setFile] = useState(null)

  const [step, setStep] = useState('form') // form | uploading | done
  const [expense, setExpense] = useState(null)
  const [receipt, setReceipt] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    projectsApi
      .list()
      .then((data) => {
        setProjects(data)
        if (data.length) {
          setForm((f) => ({ ...f, project_id: data[0].id }))
        }
      })
      .catch((err) => setError(err.message))
  }, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleCreateExpense(event) {
    event.preventDefault()
    setError(null)

    try {
      const created = await expensesApi.create({
        expense_number: `EXP${Date.now().toString(36).toUpperCase()}`,
        employee_id: session.employeeId,
        project_id: form.project_id,
        expense_category: form.expense_category,
        merchant_name: form.merchant_name,
        amount: Number(form.amount),
        currency: form.currency,
        expense_date: form.expense_date,
        payment_method: form.payment_method,
        description: form.description || null,
        is_sensitive: form.is_sensitive,
      })

      setExpense(created)
      setStep('receipt')
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleUploadReceipt(event) {
    event.preventDefault()
    if (!file) {
      setError('Choose a receipt image first.')
      return
    }

    setStep('uploading')
    setError(null)

    try {
      const formData = new FormData()
      formData.append('receipt_number', `RCT${Date.now().toString(36).toUpperCase()}`)
      formData.append('expense_id', expense.id)
      formData.append('file', file)

      const uploaded = await receiptsApi.upload(formData)
      setReceipt(uploaded)

      const refreshed = await expensesApi.get(expense.id)
      setExpense(refreshed)

      setStep('done')
    } catch (err) {
      setError(err.message)
      setStep('receipt')
    }
  }

  function reset() {
    setForm(EMPTY_FORM)
    setFile(null)
    setExpense(null)
    setReceipt(null)
    setStep('form')
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-xl font-semibold text-slate-900">
        Submit an Expense
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Fill in the claim, then photograph the receipt - ExpenseIQ's AI
        pipeline (OCR, Gemini/Ollama, duplicate detection, Groq risk
        scoring, auto-approval) runs automatically on upload.
      </p>

      <ErrorBanner message={error} />

      {step === 'form' ? (
        <Card className="mt-6 p-6">
          <form onSubmit={handleCreateExpense} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Field label="Project">
                <select
                  className={inputClass}
                  value={form.project_id}
                  onChange={(e) => update('project_id', e.target.value)}
                  required
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.project_name}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Category">
                <select
                  className={inputClass}
                  value={form.expense_category}
                  onChange={(e) =>
                    update('expense_category', e.target.value)
                  }
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Field label="Merchant">
                <input
                  className={inputClass}
                  value={form.merchant_name}
                  onChange={(e) => update('merchant_name', e.target.value)}
                  required
                />
              </Field>

              <Field label="Amount">
                <input
                  type="number"
                  step="0.01"
                  className={inputClass}
                  value={form.amount}
                  onChange={(e) => update('amount', e.target.value)}
                  required
                />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Field label="Expense Date">
                <input
                  type="date"
                  className={inputClass}
                  value={form.expense_date}
                  onChange={(e) => update('expense_date', e.target.value)}
                  required
                />
              </Field>

              <Field label="Payment Method">
                <select
                  className={inputClass}
                  value={form.payment_method}
                  onChange={(e) =>
                    update('payment_method', e.target.value)
                  }
                >
                  <option>Card</option>
                  <option>Cash</option>
                  <option>UPI</option>
                  <option>Bank Transfer</option>
                </select>
              </Field>
            </div>

            <Field label="Description (optional)">
              <textarea
                className={inputClass}
                rows={2}
                value={form.description}
                onChange={(e) => update('description', e.target.value)}
              />
            </Field>

            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={form.is_sensitive}
                onChange={(e) =>
                  update('is_sensitive', e.target.checked)
                }
              />
              This receipt contains sensitive financial data - process
              it fully offline via Ollama (never sent to the cloud).
            </label>

            <Button type="submit" className="w-full">
              Save Expense &amp; Continue to Receipt Upload
            </Button>
          </form>
        </Card>
      ) : null}

      {step === 'receipt' || step === 'uploading' ? (
        <Card className="mt-6 p-6">
          <p className="text-sm font-medium text-slate-700">
            Expense {expense.expense_number} saved. Now attach the
            receipt image.
          </p>

          <form onSubmit={handleUploadReceipt} className="mt-4 space-y-4">
            <Field label="Receipt Image (JPG / PNG / PDF)">
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                className={inputClass}
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </Field>

            <Button
              type="submit"
              className="w-full"
              disabled={step === 'uploading'}
            >
              {step === 'uploading'
                ? 'Processing through AI pipeline...'
                : 'Upload & Run AI Pipeline'}
            </Button>

            {step === 'uploading' ? (
              <Spinner label="OCR -> Hybrid Router -> Duplicate Check -> Groq Risk Scoring -> Auto-Approval..." />
            ) : null}
          </form>
        </Card>
      ) : null}

      {step === 'done' ? (
        <Card className="mt-6 p-6">
          <p className="text-sm font-semibold text-emerald-700">
            Receipt processed successfully.
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <StatusBadge status={expense.status} />
            <RecommendationBadge
              recommendation={expense.ai_recommendation}
            />
            <DuplicateBadge isDuplicate={expense.is_duplicate} />
            <EngineBadge engine={expense.processing_engine} />
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <RiskBadge label="Fraud Risk" score={expense.fraud_risk_score} />
            <RiskBadge
              label="Compliance Risk"
              score={expense.compliance_risk_score}
            />
            <RiskBadge
              label="AI Confidence"
              score={expense.ai_confidence_score}
            />
          </div>

          <p className="mt-4 text-xs text-slate-500">
            Receipt #{receipt?.receipt_number} - OCR status{' '}
            {receipt?.ocr_status}, AI status {receipt?.ai_status}.
          </p>

          <Button variant="ghost" className="mt-4" onClick={reset}>
            Submit Another Expense
          </Button>
        </Card>
      ) : null}
    </div>
  )
}

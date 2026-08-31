import apiClient from './client'

// ---------------------------------------------------------
// Auth
// ---------------------------------------------------------

export const authApi = {
  login: (email, password) =>
    apiClient
      .post('/auth/login', { email, password })
      .then((r) => r.data),
  signup: (payload) =>
    apiClient.post('/auth/signup', payload).then((r) => r.data),
  me: () => apiClient.get('/auth/me').then((r) => r.data),
}

// ---------------------------------------------------------
// Teams (MAC)
// ---------------------------------------------------------

export const teamsApi = {
  list: () => apiClient.get('/teams/').then((r) => r.data),
  create: (payload) =>
    apiClient.post('/teams/', payload).then((r) => r.data),
  update: (id, payload) =>
    apiClient.put(`/teams/${id}`, payload).then((r) => r.data),
  remove: (id) => apiClient.delete(`/teams/${id}`).then((r) => r.data),
}

// ---------------------------------------------------------
// Employees
// ---------------------------------------------------------

export const employeesApi = {
  list: () => apiClient.get('/employees/').then((r) => r.data),
  get: (id) => apiClient.get(`/employees/${id}`).then((r) => r.data),
  create: (payload) =>
    apiClient.post('/employees/', payload).then((r) => r.data),
}

// ---------------------------------------------------------
// Projects
// ---------------------------------------------------------

export const projectsApi = {
  list: () => apiClient.get('/projects/').then((r) => r.data),
  create: (payload) =>
    apiClient.post('/projects/', payload).then((r) => r.data),
  remove: (id) => apiClient.delete(`/projects/${id}`).then((r) => r.data),
}

// ---------------------------------------------------------
// Expenses
// ---------------------------------------------------------

export const expensesApi = {
  list: () => apiClient.get('/expenses/').then((r) => r.data),
  get: (id) => apiClient.get(`/expenses/${id}`).then((r) => r.data),
  create: (payload) =>
    apiClient.post('/expenses/', payload).then((r) => r.data),
  pendingForMe: () =>
    apiClient.get('/expenses/pending-for-me').then((r) => r.data),
  updateReimbursement: (id, payload) =>
    apiClient
      .patch(`/expenses/${id}/reimbursement`, payload)
      .then((r) => r.data),
}

// ---------------------------------------------------------
// Receipts
// ---------------------------------------------------------

export const receiptsApi = {
  list: () => apiClient.get('/receipts/').then((r) => r.data),
  upload: (formData) =>
    apiClient
      .post('/receipts/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data),
}

// ---------------------------------------------------------
// Approvals
// ---------------------------------------------------------

export const approvalsApi = {
  list: () => apiClient.get('/approvals/').then((r) => r.data),
  byExpense: (expenseId) =>
    apiClient
      .get(`/approvals/expense/${expenseId}`)
      .then((r) => r.data),
  create: (payload) =>
    apiClient.post('/approvals/', payload).then((r) => r.data),
}

// ---------------------------------------------------------
// AI Analysis
// ---------------------------------------------------------

export const aiAnalysisApi = {
  byExpense: (expenseId) =>
    apiClient
      .get(`/ai-analysis/expense/${expenseId}`)
      .then((r) => r.data),
  byReceipt: (receiptId) =>
    apiClient
      .get(`/ai-analysis/receipt/${receiptId}`)
      .then((r) => r.data),
}

// ---------------------------------------------------------
// Duplicate Checks
// ---------------------------------------------------------

export const duplicateChecksApi = {
  byExpense: (expenseId) =>
    apiClient
      .get(`/duplicate-checks/expense/${expenseId}`)
      .then((r) => r.data)
      .catch(() => null),
}

// ---------------------------------------------------------
// Analytics
// ---------------------------------------------------------

export const analyticsApi = {
  overview: () => apiClient.get('/analytics/overview').then((r) => r.data),
  spendByCategory: () =>
    apiClient.get('/analytics/spend-by-category').then((r) => r.data),
  spendByEmployee: () =>
    apiClient.get('/analytics/spend-by-employee').then((r) => r.data),
  spendByProject: () =>
    apiClient.get('/analytics/spend-by-project').then((r) => r.data),
  approvalStatusSummary: () =>
    apiClient
      .get('/analytics/approval-status-summary')
      .then((r) => r.data),
  reimbursementLiability: () =>
    apiClient
      .get('/analytics/reimbursement-liability')
      .then((r) => r.data),
  aiAccuracy: () =>
    apiClient.get('/analytics/ai-accuracy').then((r) => r.data),
}

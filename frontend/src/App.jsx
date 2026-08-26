import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { useSession } from './context/session'
import Login from './pages/Login'
import SubmitExpense from './pages/SubmitExpense'
import MyExpenses from './pages/MyExpenses'
import ExpenseDetail from './pages/ExpenseDetail'
import ApprovalQueue from './pages/ApprovalQueue'
import Reimbursements from './pages/Reimbursements'
import Analytics from './pages/Analytics'

function RequireAuth({ children }) {
  const { isAuthenticated } = useSession()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function HomeRedirect() {
  const { session } = useSession()
  if (!session) return <Navigate to="/login" replace />
  if (session.role === 'EMPLOYEE') return <Navigate to="/submit" replace />
  return <Navigate to="/approvals" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/submit" element={<SubmitExpense />} />
        <Route path="/my-expenses" element={<MyExpenses />} />
        <Route path="/expenses/:id" element={<ExpenseDetail />} />
        <Route path="/approvals" element={<ApprovalQueue />} />
        <Route path="/reimbursements" element={<Reimbursements />} />
        <Route path="/analytics" element={<Analytics />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

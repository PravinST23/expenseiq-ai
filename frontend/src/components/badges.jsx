import { Badge } from './ui'
import {
  approvalStatusTone,
  recommendationStatus,
  riskStatus,
} from '../theme'

export function StatusBadge({ status }) {
  return <Badge tone={approvalStatusTone(status)}>{status}</Badge>
}

const RECOMMENDATION_LABELS = {
  AUTO_APPROVE_RECOMMENDED: 'Auto-Approve',
  ESCALATE_FOR_REVIEW: 'Escalate for Review',
  REJECT_RECOMMENDED: 'Reject Recommended',
}

export function RecommendationBadge({ recommendation }) {
  if (!recommendation) return <Badge tone="neutral">Pending AI Review</Badge>
  return (
    <Badge tone={recommendationStatus(recommendation)} icon="✦">
      {RECOMMENDATION_LABELS[recommendation] || recommendation}
    </Badge>
  )
}

export function RiskBadge({ label, score }) {
  if (score === null || score === undefined) {
    return <Badge tone="neutral">{label}: n/a</Badge>
  }
  return (
    <Badge tone={riskStatus(score)}>
      {label}: {Number(score).toFixed(0)}
    </Badge>
  )
}

export function DuplicateBadge({ isDuplicate }) {
  if (!isDuplicate) return null
  return (
    <Badge tone="critical" icon="⚠">
      Duplicate Detected
    </Badge>
  )
}

export function EngineBadge({ engine }) {
  if (!engine) return null
  const label = engine === 'ollama' ? 'Ollama (offline)' : 'Gemini (cloud)'
  return <Badge tone="neutral">{label}</Badge>
}

export function ReimbursementBadge({ state }) {
  const tone =
    state === 'PAID' ? 'good' : state === 'APPROVED' ? 'warning' : 'neutral'
  return <Badge tone={tone}>{state}</Badge>
}

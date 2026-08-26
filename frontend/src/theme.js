// Validated categorical + status palette (see dataviz skill /
// references/palette.md). Categorical hues are used in FIXED
// order - never reassigned per filter - and status colors are
// reserved for state, never reused as a series color.

export const CATEGORICAL = [
  '#2a78d6', // 1 blue
  '#eb6834', // 2 orange
  '#1baf7a', // 3 aqua
  '#eda100', // 4 yellow
  '#e87ba4', // 5 magenta
  '#008300', // 6 green
  '#4a3aa7', // 7 violet
  '#e34948', // 8 red
]

export const STATUS = {
  good: '#0ca30c',
  warning: '#fab219',
  serious: '#ec835a',
  critical: '#d03b3b',
}

export function riskStatus(score) {
  const value = Number(score ?? 0)
  if (value >= 70) return 'critical'
  if (value >= 40) return 'warning'
  return 'good'
}

export function recommendationStatus(recommendation) {
  switch (recommendation) {
    case 'AUTO_APPROVE_RECOMMENDED':
      return 'good'
    case 'ESCALATE_FOR_REVIEW':
      return 'warning'
    case 'REJECT_RECOMMENDED':
      return 'critical'
    default:
      return 'warning'
  }
}

export function approvalStatusTone(status) {
  if (!status) return 'warning'
  if (status === 'Approved') return 'good'
  if (status === 'Rejected') return 'critical'
  return 'warning'
}

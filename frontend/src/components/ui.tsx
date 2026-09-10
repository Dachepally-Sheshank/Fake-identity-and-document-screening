import type { PropsWithChildren } from 'react'
import type { AlertLevel, Decision } from '../types/domain'

const toneClass = (tone: AlertLevel) => `tone-${tone}`
export function StatusBadge({ decision }: { decision: Decision }) { const tone: AlertLevel = decision === 'VERIFIED' ? 'success' : decision === 'HIGH_RISK' ? 'error' : 'warning'; return <span className={`badge ${toneClass(tone)}`}>{decision.replace('_', ' ')}</span> }
export function Notice({ tone, children }: PropsWithChildren<{ tone: AlertLevel }>) { return <div role="status" className={`notice ${toneClass(tone)}`}>{children}</div> }
export function Card({ title, children, action }: PropsWithChildren<{ title?: string; action?: React.ReactNode }>) { return <section className="card">{title && <div className="card-head"><h2>{title}</h2>{action}</div>}{children}</section> }
export function PageHeader({ eyebrow, title, children }: PropsWithChildren<{ eyebrow: string; title: string }>) { return <header className="page-header"><p className="eyebrow">{eyebrow}</p><div className="header-row"><h1>{title}</h1>{children}</div></header> }

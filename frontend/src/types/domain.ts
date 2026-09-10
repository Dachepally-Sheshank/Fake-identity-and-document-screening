export type Decision = 'VERIFIED' | 'MANUAL_REVIEW' | 'HIGH_RISK'
export type AlertLevel = 'success' | 'warning' | 'error' | 'info'
export type Signal = { id: string; label: string; score: number; status: AlertLevel; detail: string }
export type Verification = { id: string; subject: string; documentType: string; createdAt: string; riskScore: number; decision: Decision; signals: Signal[]; hash: string }
export type UploadDraft = { documentName: string; documentType: string; faceReference?: string; scenario: 'genuine' | 'blurred' | 'tampered' | 'face-mismatch' }
export type Metric = { label: string; value: string; change: string; tone: AlertLevel }

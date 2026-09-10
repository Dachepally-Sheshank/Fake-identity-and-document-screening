import type { AuditApi, ScreeningApi } from './contracts'
import type { Decision, Signal, UploadDraft, Verification } from '../types/domain'

const delay = (ms = 450) => new Promise((resolve) => setTimeout(resolve, ms))
const signalSets: Record<UploadDraft['scenario'], Signal[]> = {
  genuine: [{ id: 'quality', label: 'Document quality', score: 4, status: 'success', detail: 'Sharp image and complete document boundaries.' }, { id: 'ocr', label: 'OCR confidence', score: 3, status: 'success', detail: 'Synthetic fields extracted with high confidence.' }, { id: 'forensics', label: 'Tamper analysis', score: 2, status: 'success', detail: 'No simulated edit artifacts detected.' }, { id: 'face', label: 'Face comparison', score: 5, status: 'success', detail: 'Synthetic portrait and selfie reference align.' }],
  blurred: [{ id: 'quality', label: 'Document quality', score: 28, status: 'warning', detail: 'Low sharpness may obscure fields.' }, { id: 'ocr', label: 'OCR confidence', score: 18, status: 'warning', detail: 'Some characters require human confirmation.' }, { id: 'forensics', label: 'Tamper analysis', score: 5, status: 'success', detail: 'No simulated edit artifacts detected.' }, { id: 'face', label: 'Face comparison', score: 5, status: 'success', detail: 'Synthetic portrait and selfie reference align.' }],
  tampered: [{ id: 'quality', label: 'Document quality', score: 7, status: 'success', detail: 'Image is readable.' }, { id: 'ocr', label: 'OCR confidence', score: 8, status: 'success', detail: 'Fields extracted with high confidence.' }, { id: 'forensics', label: 'Tamper analysis', score: 64, status: 'error', detail: 'Demo edit boundary and font inconsistency detected.' }, { id: 'face', label: 'Face comparison', score: 9, status: 'warning', detail: 'Face reference is inconclusive.' }],
  'face-mismatch': [{ id: 'quality', label: 'Document quality', score: 3, status: 'success', detail: 'Sharp image and complete document boundaries.' }, { id: 'ocr', label: 'OCR confidence', score: 3, status: 'success', detail: 'Synthetic fields extracted with high confidence.' }, { id: 'forensics', label: 'Tamper analysis', score: 3, status: 'success', detail: 'No simulated edit artifacts detected.' }, { id: 'face', label: 'Face comparison', score: 72, status: 'error', detail: 'Synthetic face embedding distance exceeds the demo threshold.' }],
}
export const inferDemoScenario = (fileName: string): UploadDraft['scenario'] => {
  const normalized = fileName.toLowerCase()
  if (/(fake|tamper|manipulat|forger|edit)/.test(normalized)) return 'tampered'
  if (/(mismatch|different-face|face-fail)/.test(normalized)) return 'face-mismatch'
  if (/(blur|low-quality|unclear)/.test(normalized)) return 'blurred'
  return 'genuine'
}
const decide = (score: number): Decision => score >= 60 ? 'HIGH_RISK' : score >= 25 ? 'MANUAL_REVIEW' : 'VERIFIED'
const calculateRisk = (signals: Signal[]): { riskScore: number; escalation?: Signal } => {
  const average = Math.round(signals.reduce((sum, signal) => sum + signal.score, 0) / signals.length)
  const criticalForgery = signals.find((signal) => signal.id === 'forensics' && signal.score >= 50)
  const criticalFaceMismatch = signals.find((signal) => signal.id === 'face' && signal.score >= 60)
  const critical = criticalForgery ?? criticalFaceMismatch
  if (!critical) return { riskScore: average }
  const riskScore = Math.max(70, Math.min(95, critical.score + 15))
  return { riskScore, escalation: { id: 'escalation', label: 'Critical-evidence escalation', score: riskScore, status: 'error', detail: `${critical.label} crossed the critical threshold (${critical.score}/100), so the risk engine raised the final score above the high-risk floor.` } }
}
const build = (draft: UploadDraft): Verification => { const baseSignals = signalSets[draft.scenario]; const { riskScore, escalation } = calculateRisk(baseSignals); const signals = escalation ? [...baseSignals, escalation] : baseSignals; const id = `VR-${crypto.randomUUID().slice(0, 8).toUpperCase()}`; return { id, subject: 'Synthetic Test Identity', documentType: draft.documentType, createdAt: new Date().toISOString(), riskScore, decision: decide(riskScore), signals, hash: `sha256:${crypto.randomUUID().replaceAll('-', '').slice(0, 32)}` } }
let records: Verification[] = [build({ documentName: 'demo-genuine-id.png', documentType: 'Synthetic ID Card', scenario: 'genuine' }), build({ documentName: 'demo-tampered-id.png', documentType: 'Synthetic ID Card', scenario: 'tampered' }), build({ documentName: 'demo-blurred-id.png', documentType: 'Synthetic ID Card', scenario: 'blurred' })]
export const demoScreeningApi: ScreeningApi = { async uploadDocument(file) { await delay(); return { document_id: crypto.randomUUID(), filename: file.name, sha256: 'demo', byte_size: file.size } }, async analyzeDocument(_, scenario) { return this.submitVerification({ documentName: 'demo.png', documentType: 'Synthetic Test ID', scenario }) }, async submitVerification(draft) { await delay(900); const record = build(draft); records = [record, ...records]; return record }, async listVerifications() { await delay(); return records }, async getVerification(id) { await delay(200); return records.find((record) => record.id === id) } }
export const demoAuditApi: AuditApi = { async getAuditRecords() { await delay(); return records.map((record, index) => ({ verificationId: record.id, documentHash: record.hash, resultHash: `sha256:result${index}${record.riskScore}`, timestamp: record.createdAt, status: index === 1 ? 'PENDING' : 'ANCHORED' })) } }

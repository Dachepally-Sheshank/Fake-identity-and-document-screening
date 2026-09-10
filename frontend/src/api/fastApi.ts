import type { AuditApi, ScreeningApi } from './contracts'
import type { Verification } from '../types/domain'

// The local Vite proxy makes development requests same-origin. Set VITE_API_BASE_URL for a deployed API.
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init)
  if (!response.ok) {
    const payload = await response.json().catch(() => undefined) as { error?: { message?: string } } | undefined
    throw new Error(payload?.error?.message ?? `API request failed (${response.status}).`)
  }
  return response.json() as Promise<T>
}
type ApiVerification = Omit<Verification, 'riskScore' | 'createdAt'> & { risk_score: number; created_at: string }
const mapVerification = (item: ApiVerification): Verification => ({ ...item, riskScore: item.risk_score, createdAt: item.created_at, documentType: 'Synthetic Test ID', subject: 'Synthetic Test Identity', hash: '' })

export const fastApi: ScreeningApi = {
  async uploadDocument(file) {
    const form = new FormData(); form.append('file', file)
    return request('/documents/upload', { method: 'POST', body: form })
  },
  async analyzeDocument(documentId, scenario) {
    const mappedScenario = scenario === 'face-mismatch' ? 'genuine' : scenario
    return request<ApiVerification>(`/documents/${documentId}/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ demo_scenario: mappedScenario }) }).then(mapVerification)
  },
  async submitVerification() { throw new Error('Use uploadDocument and analyzeDocument with the FastAPI backend.') },
  listVerifications() { return request<ApiVerification[]>('/verifications').then((items) => items.map(mapVerification)) },
  getVerification(id) { return request<ApiVerification>(`/verification/${id}`).then(mapVerification) },
}

export const fastAuditApi: AuditApi = {
  async getAuditRecords() {
    const verifications = await fastApi.listVerifications()
    return Promise.all(verifications.map(async (item) => {
      const audit = await request<{ verification_id: string; document_hash: string; result_hash: string; timestamp?: string; created_at: string }>(`/audit/${item.id}`)
      return { verificationId: audit.verification_id, documentHash: `sha256:${audit.document_hash}`, resultHash: `sha256:${audit.result_hash}`, timestamp: audit.created_at, status: 'ANCHORED' as const }
    }))
  },
}

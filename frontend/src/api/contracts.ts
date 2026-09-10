import type { UploadDraft, Verification } from '../types/domain'

export interface ScreeningApi {
  uploadDocument(file: File): Promise<{ document_id: string; filename: string; sha256: string; byte_size: number }>
  analyzeDocument(documentId: string, scenario: UploadDraft['scenario']): Promise<Verification>
  submitVerification(draft: UploadDraft): Promise<Verification>
  listVerifications(): Promise<Verification[]>
  getVerification(id: string): Promise<Verification | undefined>
}

export interface AuditApi { getAuditRecords(): Promise<Array<{ verificationId: string; documentHash: string; resultHash: string; timestamp: string; status: 'ANCHORED' | 'PENDING' }>> }

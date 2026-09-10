import { describe, expect, it } from 'vitest'
import { demoScreeningApi, inferDemoScenario } from './demoApi'

describe('inferDemoScenario', () => {
  it('routes a clearly labelled fake test document to tamper analysis', () => {
    expect(inferDemoScenario('synthetic_fake_aadhaar_test.png')).toBe('tampered')
  })
  it('escalates critical forgery evidence to high risk instead of diluting it in an average', async () => {
    const result = await demoScreeningApi.submitVerification({ documentName: 'synthetic_fake_aadhaar_test.png', documentType: 'Synthetic Test ID', scenario: 'tampered' })
    expect(result.decision).toBe('HIGH_RISK')
    expect(result.riskScore).toBeGreaterThanOrEqual(70)
  })
})

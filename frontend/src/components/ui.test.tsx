import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatusBadge } from './ui'

describe('StatusBadge', () => { it('renders a readable screening decision', () => { render(<StatusBadge decision="MANUAL_REVIEW" />); expect(screen.getByText('MANUAL REVIEW')).toBeTruthy() }) })

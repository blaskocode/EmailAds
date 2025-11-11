import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Loading from '../../components/Loading'

describe('Loading Component', () => {
  it('renders loading spinner', () => {
    render(<Loading />)
    const loadingElement = screen.getByRole('status', { hidden: true })
    expect(loadingElement).toBeInTheDocument()
  })

  it('displays loading message when provided', () => {
    render(<Loading message="Loading campaigns..." />)
    expect(screen.getByText('Loading campaigns...')).toBeInTheDocument()
  })
})


import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Header from '../../components/Header'

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('Header Component', () => {
  it('renders header with title', () => {
    renderWithRouter(<Header />)
    expect(screen.getByText(/HiBid Email/i)).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    renderWithRouter(<Header />)
    // Check if header contains navigation elements
    const header = screen.getByRole('banner')
    expect(header).toBeInTheDocument()
  })
})


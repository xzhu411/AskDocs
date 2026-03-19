import { FC, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

export const Container: FC<Props> = ({ children }) => (
  <div className="max-w-4xl mx-auto px-4 py-8">
    {children}
  </div>
)

export const Button: FC<{
  onClick?: () => void
  children: ReactNode
  disabled?: boolean
  variant?: 'primary' | 'secondary'
  className?: string
  type?: 'button' | 'submit'
}> = ({
  onClick,
  children,
  disabled = false,
  variant = 'primary',
  className = '',
  type = 'button',
}) => {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors'
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 disabled:bg-gray-100',
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  )
}

export const Card: FC<{ children: ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
)

export const Badge: FC<{ children: ReactNode; variant?: 'default' | 'success' | 'warning' }> = ({
  children,
  variant = 'default',
}) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${variants[variant]}`}>
      {children}
    </span>
  )
}

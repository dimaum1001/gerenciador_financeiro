import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

const LoadingSpinner = ({ size = 'md', className, ...props }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  }

  return (
    <Loader2 
      className={cn(
        'animate-spin text-muted-foreground',
        sizeClasses[size],
        className
      )}
      {...props}
    />
  )
}

export default LoadingSpinner

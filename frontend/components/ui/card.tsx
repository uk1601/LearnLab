import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const cardVariants = cva(
  "rounded-lg transition-colors",
  {
    variants: {
      variant: {
        default: "bg-card border border-border text-card-foreground",
        primary: "bg-primary/10 border border-primary/30 text-foreground",
        secondary: "bg-secondary/10 border border-secondary/30 text-foreground",
        accent: "bg-accent/10 border border-accent/30 text-foreground",
        destructive: "bg-destructive/10 border border-destructive/30 text-foreground",
        warning: "bg-warning/10 border border-warning/30 text-foreground",
        success: "bg-success/10 border border-success/30 text-foreground",
        ghost: "bg-transparent text-foreground",
        outline: "border border-border text-foreground",
      },
      size: {
        default: "p-6",
        sm: "p-4",
        lg: "p-8",
      },
      shadow: {
        default: "shadow-sm",
        md: "shadow-md",
        lg: "shadow-lg",
        none: "",
      },
      hover: {
        default: "",
        lift: "hover:-translate-y-0.5 transition-transform",
        glow: "hover:shadow-lg hover:shadow-primary/20 transition-shadow",
        none: "",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      shadow: "default",
      hover: "none",
    },
  }
)

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, shadow, hover, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, size, shadow, hover, className }))}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center pt-4", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
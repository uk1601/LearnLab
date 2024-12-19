import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="container mx-auto min-h-screen py-10 px-4">
      {/* Theme Toggle */}
      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      {/* Header */}
      <section className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Welcome to LearnLab
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          This is a demonstration of our design system with light and dark mode support.
        </p>
      </section>

      {/* Card Variants */}
      <section className="mb-12">
        <h2 className="text-3xl font-bold tracking-tight mb-6">Card Variants</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Default Card with Lift Effect */}
          <Card variant="default" shadow="md" hover="lift">
            <CardHeader>
              <CardTitle>Default Card</CardTitle>
              <CardDescription>With lift hover effect</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Content goes here</p>
            </CardContent>
            <CardFooter>
              <Button variant="default">Action</Button>
            </CardFooter>
          </Card>

          {/* Secondary Card with Glow Effect */}
          <Card variant="secondary" shadow="md" hover="glow">
            <CardHeader>
              <CardTitle>Secondary Card</CardTitle>
              <CardDescription>With glow hover effect</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Content goes here</p>
            </CardContent>
            <CardFooter>
              <Button variant="secondary" size="sm">Action</Button>
            </CardFooter>
          </Card>

          {/* Accent Card */}
          <Card variant="accent" shadow="lg">
            <CardHeader>
              <CardTitle>Accent Card</CardTitle>
              <CardDescription>With large shadow</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Content goes here</p>
            </CardContent>
            <CardFooter>
              <Button variant="accent" size="lg">Action</Button>
            </CardFooter>
          </Card>

          {/* Warning Card */}
          <Card variant="warning" shadow="md">
            <CardHeader>
              <CardTitle>Warning Card</CardTitle>
              <CardDescription>For important notifications</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Warning content goes here</p>
            </CardContent>
            <CardFooter>
              <Button variant="warning">Acknowledge</Button>
            </CardFooter>
          </Card>

          {/* Destructive Card */}
          <Card variant="destructive" shadow="md">
            <CardHeader>
              <CardTitle>Destructive Card</CardTitle>
              <CardDescription>For critical actions</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Destructive content goes here</p>
            </CardContent>
            <CardFooter>
              <Button variant="destructive">Delete</Button>
            </CardFooter>
          </Card>

          {/* Success Card */}
          <Card variant="success" shadow="md" hover="lift">
            <CardHeader>
              <CardTitle>Success Card</CardTitle>
              <CardDescription>For positive feedback</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Success content goes here</p>
            </CardContent>
            <CardFooter>
              <Button variant="outline">Continue</Button>
            </CardFooter>
          </Card>
        </div>
      </section>

      {/* Interactive Elements */}
      <section className="mb-12">
        <h2 className="text-3xl font-bold tracking-tight mb-6">Interactive Elements</h2>
        
        {/* Button Variants */}
        <div className="space-y-6">
          <h3 className="text-2xl font-semibold">Button Variants</h3>
          <div className="flex flex-wrap gap-4">
            <Button variant="default">Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="accent">Accent</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="warning">Warning</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
        </div>

        {/* Button Sizes */}
        <div className="space-y-6 mt-8">
          <h3 className="text-2xl font-semibold">Button Sizes</h3>
          <div className="flex flex-wrap items-center gap-4">
            <Button size="sm" variant="default">Small</Button>
            <Button size="default" variant="secondary">Default</Button>
            <Button size="lg" variant="accent">Large</Button>
            <Button size="icon" variant="outline">👋</Button>
          </div>
        </div>

        {/* Card Hover Effects */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <Card variant="outline" hover="lift" className="text-center p-6">
            <p className="font-semibold">Lift Effect</p>
          </Card>
          <Card variant="outline" hover="glow" className="text-center p-6">
            <p className="font-semibold">Glow Effect</p>
          </Card>
          <Card variant="outline" shadow="lg" className="text-center p-6">
            <p className="font-semibold">Large Shadow</p>
          </Card>
        </div>
      </section>

      {/* Typography */}
      <section className="mt-12 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">Typography</h2>
        <div className="space-y-4">
          <Card variant="default" className="p-6">
            <h1 className="text-4xl font-bold tracking-tight">Heading 1</h1>
            <h2 className="text-3xl font-bold tracking-tight">Heading 2</h2>
            <h3 className="text-2xl font-bold tracking-tight">Heading 3</h3>
            <p className="text-lg leading-7">
              Regular paragraph text with good line length. The quick brown fox jumps over the lazy dog.
            </p>
            <p className="text-lg text-muted-foreground">
              Secondary text color example.
            </p>
            <small className="text-sm text-muted-foreground block">
              Small text example
            </small>
          </Card>
        </div>
      </section>

      {/* Color Gradients */}
      <section className="mt-12 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight mb-6">Gradients</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card variant="ghost" className="overflow-hidden">
            <div className="bg-gradient-primary text-primary-foreground p-6">
              <h3 className="font-semibold">Primary Gradient</h3>
              <p>Background gradient example</p>
            </div>
          </Card>
          <Card variant="ghost" className="overflow-hidden">
            <div className="bg-gradient-secondary text-secondary-foreground p-6">
              <h3 className="font-semibold">Secondary Gradient</h3>
              <p>Background gradient example</p>
            </div>
          </Card>
        </div>
      </section>
    </div>
  )
}
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

      {/* Components Demo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Default Card */}
        <Card variant="default" shadow="md">
          <CardHeader>
            <CardTitle>Default Card</CardTitle>
            <CardDescription>This is a default card variant</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Content goes here</p>
          </CardContent>
          <CardFooter>
            <Button variant="default">Action</Button>
          </CardFooter>
        </Card>

        {/* Secondary Card */}
        <Card variant="secondary" shadow="md">
          <CardHeader>
            <CardTitle>Secondary Card</CardTitle>
            <CardDescription>This is a secondary card variant</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Content goes here</p>
          </CardContent>
          <CardFooter>
            <Button variant="secondary">Action</Button>
          </CardFooter>
        </Card>

        {/* Accent Card */}
        <Card variant="accent" shadow="md">
          <CardHeader>
            <CardTitle>Accent Card</CardTitle>
            <CardDescription>This is an accent card variant</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Content goes here</p>
          </CardContent>
          <CardFooter>
            <Button variant="accent">Action</Button>
          </CardFooter>
        </Card>
      </div>

      {/* Button Variants */}
      <section className="mt-12 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">Button Variants</h2>
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

        {/* Button Sizes */}
        <div className="flex flex-wrap items-center gap-4">
          <Button size="sm">Small</Button>
          <Button size="default">Default</Button>
          <Button size="lg">Large</Button>
          <Button size="icon">👋</Button>
        </div>
      </section>

      {/* Typography */}
      <section className="mt-12 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">Typography</h2>
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">Heading 1</h1>
          <h2 className="text-3xl font-bold tracking-tight">Heading 2</h2>
          <h3 className="text-2xl font-bold tracking-tight">Heading 3</h3>
          <p className="text-lg leading-7">
            Regular paragraph text with good line length. The quick brown fox jumps over the lazy dog.
          </p>
          <p className="text-lg text-muted-foreground">
            Secondary text color example.
          </p>
          <small className="text-sm text-muted-foreground">
            Small text example
          </small>
        </div>
      </section>
    </div>
  )
}
'use client';

import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation';
import { 
  Book, 
  Headphones, 
  BrainCircuit, 
  ChevronRight, 
  Sparkles,
  GraduationCap,
  LightbulbIcon,
  Share2
} from 'lucide-react';

const Home = (): JSX.Element => {
  const router = useRouter();

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  const features = [
    {
      icon: Headphones,
      title: "Audio Learning",
      description: "Transform documents into engaging podcasts",
      color: "bg-primary/10 border-primary"
    },
    {
      icon: BrainCircuit,
      title: "Interactive Quizzes",
      description: "Test your knowledge with AI-powered questions",
      color: "bg-secondary/10 border-secondary"
    },
    {
      icon: Sparkles,
      title: "Smart Flashcards",
      description: "Master concepts through spaced repetition",
      color: "bg-accent/10 border-accent"
    },
    {
      icon: Share2,
      title: "Share & Learn",
      description: "Generate and share your learning journey",
      color: "bg-success/10 border-success"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-background pt-16 md:pt-24">
        <div className="container-base relative z-10">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            <motion.div
              variants={fadeIn}
              initial="hidden"
              animate="show"
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="inline-block"
                >
                  <span className="inline-flex items-center gap-2 rounded-lg bg-accent/10 px-3 py-1 text-sm text-accent">
                    <Sparkles className="h-4 w-4" />
                    Revolutionizing PDF Learning
                  </span>
                </motion.div>
                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight">
                  Transform PDFs into
                  <br />
                  Learning Adventures
                </h1>
                <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl">
                  Enhance your understanding with interactive learning experiences, from audio podcasts to smart flashcards
                </p>
              </div>
              
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="flex flex-col sm:flex-row gap-4"
              >
                <Button 
                  size="lg"
                  variant="accent"
                  onClick={() => router.push('/auth')}
                >
                  Get Started <ChevronRight className="ml-2 h-5 w-5" />
                </Button>              
              </motion.div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="relative lg:pl-8"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-background to-transparent z-10" />
                <div className="grid grid-cols-2 gap-4">
                  {features.map((feature, index) => (
                    <motion.div
                      key={feature.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 * index }}
                      className={`feature-card ${feature.color} border-2`}
                    >
                      <feature.icon className="h-8 w-8 mb-2" />
                      <h3 className="font-semibold">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">
                        {feature.description}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Background decorative elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-[80%] top-0 -z-10 transform-gpu blur-3xl" aria-hidden="true">
            <div className="aspect-[1155/678] w-[72.1875rem] bg-gradient-to-tr from-accent to-primary opacity-20" />
          </div>
          <div className="absolute left-[50%] top-0 -z-10 transform-gpu blur-3xl" aria-hidden="true">
            <div className="aspect-[1155/678] w-[72.1875rem] bg-gradient-to-tr from-primary to-secondary opacity-30" />
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 md:py-32">
        <div className="container-base">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-16"
          >
            <h2 className="text-gradient text-3xl sm:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Four simple steps to transform your learning experience
            </p>
          </motion.div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { icon: Book, title: "Upload PDF", description: "Start by uploading your study material" },
              { icon: Headphones, title: "Generate Content", description: "Create podcasts, flashcards, and quizzes" },
              { icon: BrainCircuit, title: "Learn & Practice", description: "Engage with interactive content" },
              { icon: Share2, title: "Share Progress", description: "Share your learning journey" }
            ].map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="mb-4 relative">
                  <div className="w-16 h-16 mx-auto rounded-full bg-accent/10 flex items-center justify-center">
                    <step.icon className="h-8 w-8 text-accent" />
                  </div>
                  {index < 3 && (
                    <div className="hidden md:block absolute top-8 left-[60%] w-full border-t-2 border-dashed border-accent/30" />
                  )}
                </div>
                <h3 className="font-semibold mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
'use client';

import { DashboardLayout } from "./dashboard-layout";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { 
  FileText, 
  MessageSquare, 
  Headphones, 
  BrainCircuit,
  Share2,
  ChevronLeft,
  Diamond
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface FileLayoutProps {
  children: React.ReactNode;
  fileId: string;
}

interface SidebarItem {
  icon: React.ElementType;
  label: string;
  href: string;
  tooltip: string;
  bgColor: string;
}

export function FileLayout({ children, fileId }: FileLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();

  const sidebarItems: SidebarItem[] = [
    {
      icon: FileText,
      label: "View PDF",
      href: `/dashboard/${fileId}/view-pdf`,
      tooltip: "View and read your PDF",
      bgColor: "bg-blue-50 dark:bg-blue-950"
    },
    {
      icon: MessageSquare,
      label: "Chat",
      href: `/dashboard/${fileId}/chat`,
      tooltip: "Chat with your document",
      bgColor: "bg-green-50 dark:bg-green-950"
    },
    {
      icon: Headphones,
      label: "Podcasts",
      href: `/dashboard/${fileId}/podcast`,
      tooltip: "Listen to generated podcasts",
      bgColor: "bg-purple-50 dark:bg-purple-950"
    },
    {
      icon: BrainCircuit,
      label: "Quizzes",
      href: `/dashboard/${fileId}/quiz`,
      tooltip: "Test your knowledge",
      bgColor: "bg-orange-50 dark:bg-orange-950"
    },
    {
      icon: Diamond,
      label: "Flashcards",
      href: `/dashboard/${fileId}/flashcard`,
      tooltip: "Study with flashcards",
      bgColor: "bg-pink-50 dark:bg-pink-950"
    },
    {
      icon: Share2,
      label: "Share",
      href: `/dashboard/${fileId}/social`,
      tooltip: "Share your learnings",
      bgColor: "bg-indigo-50 dark:bg-indigo-950"
    }
  ];

  return (
    <DashboardLayout>
      <div className="flex gap-6">
        {/* Sidebar */}
        <aside className="w-[76px] shrink-0">
          <div className="flex flex-col gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-xl p-3 hover:scale-105 transition-all duration-200 border border-black"
              onClick={() => router.push('/dashboard')}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            
            <Separator />
            
            <TooltipProvider>
              <div className="space-y-3">
                {sidebarItems.map((item) => (
                  <Tooltip key={item.href} delayDuration={100}>
                    <TooltipTrigger asChild>
                      <Link href={item.href} className="block">
                        <Button
                          variant={pathname === item.href ? "default" : "ghost"}
                          size="icon"
                          className={cn(
                            "w-full h-12 rounded-xl p-3 border border-black",
                            "transition-all duration-200",
                            "hover:scale-120 hover:shadow-lg",
                            "hover:bg-primary hover:text-primary-foreground",
                            pathname === item.href 
                              ? "bg-primary text-primary-foreground shadow-md" 
                              : cn(item.bgColor, "hover:brightness-110"),
                          )}
                        >
                          <item.icon className="h-5 w-5" />
                          <span className="sr-only">{item.label}</span>
                        </Button>
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent 
                      side="right"
                      className="animate-in zoom-in-50 duration-200"
                    >
                      <p>{item.tooltip}</p>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>
            </TooltipProvider>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>
    </DashboardLayout>
  );
}
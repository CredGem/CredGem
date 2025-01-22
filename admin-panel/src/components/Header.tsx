import { useTheme } from "next-themes";
import { MoonIcon, SunIcon } from "./Icons";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
export function Header() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <header className="w-full flex justify-end p-4 bg-background/80 backdrop-blur-sm border-b border-default-200/50">
      <ThemeSwitch />
    </header>
  );
}

function ThemeSwitch() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="outline"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="text-foreground"
    >
      {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
    </Button>
  );
} 
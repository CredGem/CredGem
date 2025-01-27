import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUp } from "lucide-react";
import { useNavigate } from "react-router-dom";

export interface DashboardCardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
    changeValue: number;
    redirectTo: string;
  }
  
  export function DashboardCardSkeleton() {
    return (
      <Card className="flex-1">
        <Skeleton className="h-24" />
      </Card>
    )
  }

  export function DashboardCard({ title, value, icon, changeValue, redirectTo }: DashboardCardProps) {
    const navigate = useNavigate();
    return (
      <Card className="flex-1">
        <div className="flex p-4 gap-4">
          <div className="flex items-start">
            <div className="flex items-center bg-ring/30 rounded-md p-2">
              {icon}
            </div>
          </div>
          <div className="flex flex-col flex-1">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">{title}</span>
              <Badge variant="secondary" className="flex font-normal text-blue-500 items-center gap-0.5 text-xs h-5 py-3 px-2 bg-ring/20">
                <ArrowUp className="w-3 h-3" />
                <span>{changeValue}%</span>
              </Badge>
            </div>
            <p className="text-2xl font-semibold">{value}</p>
          </div>
        </div>
        <CardFooter className="px-4 py-1 border-t bg-ring/20 rounded-b-md">
          <Button variant="ghost" className="h-8 px-0 font-medium" onClick={() => navigate(redirectTo)}>
            View All
          </Button>
        </CardFooter>
      </Card>
    )
  }
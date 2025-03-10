import { ArrowDown, ArrowLeftRight, ArrowUp, EllipsisVertical, Wallet } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useInsightsStore } from "@/store/useInsightsStore";
import React, { useEffect, useState } from "react";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { BackgroundVariantsDark, BackgroundVariantsLight } from "@/components/background-varients";
import { useTheme } from "@/components/theme-provider";




function BarChartCard() {
  const { creditUsageTimeSeries, isLoadingFetchCreditUsageTimeSeries, error, fetchCreditUsageTimeSeries } = useInsightsStore();
  const [timeRange, setTimeRange] = useState("7");

  // Replace the NextUI color function with explicit hex colors
  const getColorForIndex = (index: number) => {
    const colors = [
      "#FF6B6B", // red
      "#4ECDC4", // teal
      "#FFD166", // yellow
      "#6A0572", // purple
      "#1A936F", // green
      "#3D5A80", // blue
      "#F18F01", // orange
      "#7B4B94"  // violet
    ];
    return colors[index % colors.length];
  };

  useEffect(() => {
    const now = new Date();
    const startDate = new Date(now);
    startDate.setDate(startDate.getDate() - parseInt(timeRange));

    fetchCreditUsageTimeSeries(startDate.toISOString(), now.toISOString(), "day");
  }, [timeRange, fetchCreditUsageTimeSeries]);

  const chartData = React.useMemo(() => {
    if (!creditUsageTimeSeries?.points) return [];

    // Group by timestamp first
    const groupedByDay = creditUsageTimeSeries.points.reduce((acc, point) => {
      const date = new Date(point.timestamp);
      const dateKey = date.toISOString().split('T')[0];

      if (!acc[dateKey]) {
        acc[dateKey] = {
          weekday: date.toLocaleDateString('en-US', { weekday: 'short' }),
          timestamp: date,
        };
      }

      // Add data for this credit type - use debits_amount instead of transaction_count
      acc[dateKey][point.credit_type_name] = point.debits_amount;
      
      return acc;
    }, {} as Record<string, any>);

    // Convert to array and sort by timestamp
    return Object.values(groupedByDay)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }, [creditUsageTimeSeries?.points]);

  // Get unique credit types
  const creditTypes = React.useMemo(() => {
    if (!creditUsageTimeSeries?.points) return [];
    
    // Extract all keys from the chartData that aren't 'weekday' or 'timestamp'
    if (chartData.length > 0) {
      return Object.keys(chartData[0]).filter(key => 
        key !== 'weekday' && key !== 'timestamp'
      );
    }
    
    return Array.from(new Set(creditUsageTimeSeries.points.map(p => p.credit_type_name)));
  }, [creditUsageTimeSeries?.points, chartData]);

  return (

    <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              <h3 className="text-small font-medium text-default-500">Credit Usage by Day</h3>
            </CardTitle>

            <div className="flex items-center gap-2">
              <Select
                aria-label="Time Range"
                value={timeRange}
                onValueChange={(value) => setTimeRange(value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">7 Days</SelectItem>
                  <SelectItem value="14">14 Days</SelectItem>
                  <SelectItem value="30">30 Days</SelectItem>
                </SelectContent>
              </Select>

              <DropdownMenu>
                <DropdownMenuTrigger>
                  <Button variant="ghost" className="w-8 h-8">
                    <EllipsisVertical />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem key="view-details">View Details</DropdownMenuItem>
                  <DropdownMenuItem key="export-data">Export Data</DropdownMenuItem>
                  <DropdownMenuItem key="set-alert">Set Alert</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardHeader>
        <CardContent>
        <div className="flex-1 w-full h-[350px]">
          {isLoadingFetchCreditUsageTimeSeries ? (
            <div className="h-full w-full flex items-center justify-center">
              <Skeleton className="h-[200px] w-full" />
            </div>
          ) : error ? (
            <div className="h-full w-full flex items-center justify-center text-danger">
              {error}
            </div>
          ) : (
            <>
              <dd className="flex w-full justify-end gap-4 text-tiny text-default-500">
                {creditTypes.map((category, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{
                        backgroundColor: getColorForIndex(index),
                      }}
                    />
                    <span className="capitalize">{category}</span>
                  </div>
                ))}
              </dd>

              <ResponsiveContainer
                className="[&_.recharts-surface]:outline-none"
                width="100%"
                height={300}
              >
                <BarChart
                  data={chartData}
                  margin={{
                    top: 20,
                    right: 14,
                    left: -8,
                    bottom: 5,
                  }}
                >
                  <XAxis
                    dataKey="weekday"
                    strokeOpacity={0.25}
                    style={{ fontSize: "var(--nextui-font-size-tiny)" }}
                    tickLine={false}
                  />
                  <YAxis
                    axisLine={false}
                    style={{ fontSize: "var(--nextui-font-size-tiny)" }}
                    tickLine={false}
                  />
                  <Tooltip
                    content={({ label, payload }) => (
                      <div className="flex h-auto min-w-[120px] items-center gap-x-2 rounded-medium bg-background p-2 text-tiny shadow-small">
                        <div className="flex w-full flex-col gap-y-1">
                          <span className="font-medium text-foreground">{label}</span>
                          {payload?.map((p, index) => {
                            const name = p.name;
                            const value = p.value;

                            return (
                              <div key={`${index}-${name}`} className="flex w-full items-center gap-x-2">
                                <div
                                  className="h-2 w-2 flex-none rounded-full"
                                  style={{
                                    backgroundColor: getColorForIndex(index),
                                  }}
                                />
                                <div className="flex w-full items-center justify-between gap-x-2 pr-1 text-xs text-default-700">
                                  <span className="text-default-500">{name}</span>
                                  <span className="font-mono font-medium text-default-700">{value}</span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    cursor={false}
                  />
                  {creditTypes.map((category, index) => (
                    <Bar
                      key={`${category}-${index}`}
                      dataKey={category}
                      name={category}
                      fill={getColorForIndex(index)}
                      radius={[4, 4, 0, 0]}
                      stackId="bars"
                      barSize={24}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </>
          )}
        </div>
      
        </CardContent>

    </Card>
  );
}

function CircleChartCard() {
  const { creditUsage, isLoadingFetchCreditUsage, error, fetchCreditUsage } = useInsightsStore();
  const [timeRange, setTimeRange] = useState("per-day");

  // Replace the NextUI color function with explicit hex colors
  const getColorForIndex = (index: number) => {
    const colors = [
      "#FF6B6B", // red
      "#4ECDC4", // teal
      "#FFD166", // yellow
      "#6A0572", // purple
      "#1A936F", // green
      "#3D5A80", // blue
      "#F18F01", // orange
      "#7B4B94"  // violet
    ];
    return colors[index % colors.length];
  };

  useEffect(() => {
    const now = new Date();
    const startDate = new Date(now);
    startDate.setDate(startDate.getDate() - (timeRange === "per-day" ? 1 : timeRange === "per-week" ? 7 : 30));

    fetchCreditUsage(startDate.toISOString(), now.toISOString());
  }, [timeRange, fetchCreditUsage]);

  const chartData = creditUsage?.map(item => ({
    name: item.credit_type_name,
    value: item.transaction_count
  })) || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-x-2">
          <dt>
            <h3 className="text-small font-medium text-default-500">Credit Distribution</h3>
          </dt>
          <div className="flex items-center justify-end gap-x-2">
            <Select
              aria-label="Time Range"
              value={timeRange}
              onValueChange={(value) => setTimeRange(value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="per-day">Per Day</SelectItem>
                <SelectItem value="per-week">Per Week</SelectItem>
                <SelectItem value="per-month">Per Month</SelectItem>
              </SelectContent>
            </Select>
            <DropdownMenu>
              <DropdownMenuTrigger>
                <Button variant="ghost" className="w-8 h-8">
                  <EllipsisVertical />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem key="view-details">View Details</DropdownMenuItem>
                <DropdownMenuItem key="export-data">Export Data</DropdownMenuItem>
                <DropdownMenuItem key="set-alert">Set Alert</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      <CardContent>
      <div className="flex h-full flex-wrap items-center justify-center gap-x-2 lg:flex-nowrap">
        {isLoadingFetchCreditUsage ? (
          <p>Loading...</p>
        ) : error ? (
          <div className="text-danger">{error}</div>
        ) : (
          <ResponsiveContainer
            className="[&_.recharts-surface]:outline-none"
            height={200}
            width="100%"
          >
            <PieChart accessibilityLayer margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <Tooltip
                content={({ payload }) => (
                  <div className="flex h-8 min-w-[120px] items-center gap-x-2 rounded-medium bg-background px-1 text-tiny shadow-small">
                    {payload?.map((p: any, index: any) => {
                      const name = p.name;
                      const value = p.value;

                      return (
                        <div key={`${index}-${name}`} className="flex w-full items-center gap-x-2">
                          <div
                            className="h-2 w-2 flex-none rounded-full"
                            style={{
                              backgroundColor: getColorForIndex(payload.findIndex((item: any) => item.name === name))
                            }}
                          />
                          <div className="flex w-full items-center justify-between gap-x-2 pr-1 text-xs text-default-700">
                            <span className="text-default-500">{name}</span>
                            <span className="font-mono font-medium text-default-700">
                              {value}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                cursor={false}
              />
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                innerRadius="68%"
                paddingAngle={-20}
                strokeWidth={0}
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getColorForIndex(index)}
                  />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        )}

        <div className="flex w-full flex-col justify-center gap-4 p-4 text-tiny text-default-500 lg:p-0">
          {chartData.map((item, index) => (
            <div key={index} className="flex items-center gap-2">
              <span
                className="h-2 w-2 rounded-full"
                style={{
                  backgroundColor: getColorForIndex(index)
                }}
              />
              <span className="capitalize">{item.name}</span>
            </div>
          ))}
        </div>
      </div>
      </CardContent>
    </Card>
  );
}


interface DashboardCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

export function DashboardCard({ title, value, description, icon }: DashboardCardProps) {
  return (
    <Card className="flex-1">
      <CardHeader className="p-2">
        <CardTitle className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium truncate">{title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="py-1 px-2">
        <p className="text-xl font-bold truncate">{value}</p>
        <p className="text-xs text-muted-foreground truncate py-1">{description}</p>
      </CardContent>
    </Card>
  )
}




export default function Dashboard() {
  const {fetchWalletActivity, fetchTrendingWallets, generalInsights, fetchGeneralInsights } = useInsightsStore();
  const { theme } = useTheme()
  const isDarkMode = theme === "dark"

  useEffect(() => {
    const now = new Date();
    const startDate = new Date(now);
    startDate.setDate(startDate.getDate() - 30);

    fetchWalletActivity(startDate.toISOString(), now.toISOString());
    fetchTrendingWallets(startDate.toISOString(), now.toISOString());
    fetchGeneralInsights();
  }, [fetchWalletActivity, fetchTrendingWallets]);

  const totalTransactions = generalInsights?.total_transactions || 0;
  const totalDeposits = generalInsights?.total_deposits || 0;
  const totalDebits = generalInsights?.total_debits || 0;
  const totalWallets = generalInsights?.total_wallets || 0;

  const cardBackgroundVariant = isDarkMode ? BackgroundVariantsDark["blue"] : BackgroundVariantsLight["blue"];

  return (
    <div className={`h-[100vh] flex flex-col gap-4 p-10`}>
      <div className={`flex flex-col relative gap-4 p-4 rounded-lg ${cardBackgroundVariant}`}>
        <h1 className="text-2xl font-bold">CredGem Insights</h1>
        <p className="text-sm text-muted-foreground">Welcome to your dashboard</p>
      </div>
      <div className="flex flex-row gap-4 w-full rounded-lg">
        <DashboardCard title="Total Wallets" value={totalWallets.toString()} description="Total number of wallets" icon={<Wallet className="w-4 h-4 text-ring" />} />
        <DashboardCard title="Total Transactions" value={totalTransactions.toString()} description="Total number of transactions" icon={<ArrowLeftRight className="w-4 h-4 text-ring" />} />
        <DashboardCard title="Total Deposits" value={totalDeposits.toString()} description="Total number of deposits" icon={<ArrowDown className="w-4 h-4 text-ring" />} />
        <DashboardCard title="Total Debits" value={totalDebits.toString()} description="Total number of debits" icon={<ArrowUp className="w-4 h-4 text-ring" />} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <CircleChartCard />
        <BarChartCard />
      </div>
    </div>
  )
}

import React, { useEffect, useState } from "react";
import { Card, Button, Select, SelectItem, Dropdown, DropdownItem, DropdownMenu, DropdownTrigger, Chip, cn, Divider, RadioGroup, VisuallyHidden, useRadio, Spinner } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { ResponsiveContainer, PieChart, Pie, Tooltip, Cell, Area, AreaChart, YAxis, BarChart, Bar, XAxis } from "recharts";
import { useInsightsStore } from "../store/useInsightsStore";

interface DashboardCardProps {
  title: string;
  value: string;
  description: string;
}

function DashboardCard({ title, value, description }: DashboardCardProps) {
  return (
    <Card className="p-6">
      <h3 className="text-foreground-500 text-sm">{title}</h3>
      <p className="text-3xl font-bold mt-2 text-foreground">{value}</p>
      <p className="text-foreground-500 text-sm mt-2">{description}</p>
    </Card>
  );
}

function CircleChartCard() {
  const { creditUsage, isLoading, error, fetchCreditUsage } = useInsightsStore();
  const [timeRange, setTimeRange] = useState("per-day");

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
    <Card className="min-h-[240px] border border-transparent dark:border-default-100">
      <div className="flex flex-col gap-y-2 p-4 pb-0">
        <div className="flex items-center justify-between gap-x-2">
          <dt>
            <h3 className="text-small font-medium text-default-500">Credit Distribution</h3>
          </dt>
          <div className="flex items-center justify-end gap-x-2">
            <Select
              aria-label="Time Range"
              classNames={{
                trigger: "min-w-[100px] min-h-7 h-7",
                value: "text-tiny !text-default-500",
                selectorIcon: "text-default-500",
                popoverContent: "min-w-[120px]",
              }}
              selectedKeys={[timeRange]}
              onChange={(e) => setTimeRange(e.target.value)}
              listboxProps={{
                itemClasses: {
                  title: "text-tiny",
                },
              }}
              placeholder="Per Day"
              size="sm"
            >
              <SelectItem key="per-day">Per Day</SelectItem>
              <SelectItem key="per-week">Per Week</SelectItem>
              <SelectItem key="per-month">Per Month</SelectItem>
            </Select>
            <Dropdown
              classNames={{
                content: "min-w-[120px]",
              }}
              placement="bottom-end"
            >
              <DropdownTrigger>
                <Button isIconOnly radius="full" size="sm" variant="light">
                  <Icon icon="solar:menu-dots-bold" width={16} height={16} />
                </Button>
              </DropdownTrigger>
              <DropdownMenu
                itemClasses={{
                  title: "text-tiny",
                }}
                variant="flat"
              >
                <DropdownItem key="view-details">View Details</DropdownItem>
                <DropdownItem key="export-data">Export Data</DropdownItem>
                <DropdownItem key="set-alert">Set Alert</DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </div>
        </div>
      </div>
      <div className="flex h-full flex-wrap items-center justify-center gap-x-2 lg:flex-nowrap">
        {isLoading ? (
          <Spinner />
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
                    {payload?.map((p, index) => {
                      const name = p.name;
                      const value = p.value;

                      return (
                        <div key={`${index}-${name}`} className="flex w-full items-center gap-x-2">
                          <div
                            className="h-2 w-2 flex-none rounded-full"
                            style={{
                              backgroundColor: `hsl(var(--nextui-primary-${(index + 1) * 200}))`,
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
                    fill={`hsl(var(--nextui-primary-${(index + 1) * 200}))`}
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
                  backgroundColor: `hsl(var(--nextui-primary-${(index + 1) * 200}))`,
                }}
              />
              <span className="capitalize">{item.name}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function BarChartCard() {
  const { creditUsageTimeSeries, isLoading, error, fetchCreditUsageTimeSeries } = useInsightsStore();
  const [timeRange, setTimeRange] = useState("7");

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
      
      // Initialize with 0 if not exists
      if (!acc[dateKey][point.credit_type_name]) {
        acc[dateKey][point.credit_type_name] = 0;
      }
      acc[dateKey][point.credit_type_name] = point.transaction_count;
      return acc;
    }, {} as Record<string, any>);

    // Convert to array and sort by timestamp
    return Object.values(groupedByDay)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }, [creditUsageTimeSeries?.points]);

  // Get unique credit types
  const creditTypes = React.useMemo(() => {
    if (!creditUsageTimeSeries?.points) return [];
    return Array.from(new Set(creditUsageTimeSeries.points.map(p => p.credit_type_name)));
  }, [creditUsageTimeSeries?.points]);

  return (
    <Card className="min-h-[240px] border border-transparent dark:border-default-100">
      <div className="flex flex-col gap-y-4 p-4">
        <dt>
          <h3 className="text-small font-medium text-default-500">Credit Usage by Day</h3>
        </dt>
        {isLoading ? (
          <Spinner />
        ) : error ? (
          <div className="text-danger">{error}</div>
        ) : (
          <>
            <dd className="flex w-full justify-end gap-4 text-tiny text-default-500">
              {Array.from(new Set(chartData.map(d => d.credit_type_name))).map((category, index) => (
                <div key={index} className="flex items-center gap-2">
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{
                      backgroundColor: `hsl(var(--nextui-secondary-${(index + 1) * 200}))`,
                    }}
                  />
                  <span className="capitalize">{category}</span>
                </div>
              ))}
            </dd>

            <ResponsiveContainer
              className="[&_.recharts-surface]:outline-none"
              height={200}
              width="100%"
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
                                  backgroundColor: `hsl(var(--nextui-secondary-${(index + 1) * 200}))`,
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
                    fill={`hsl(var(--nextui-secondary-${(index + 1) * 200}))`}
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

      <Divider className="mx-auto w-full max-w-[calc(100%-2rem)] bg-default-100" />

      <div className="flex justify-between items-center p-4">
        <RadioGroup
          aria-label="Time Range"
          className="flex gap-x-2"
          value={timeRange}
          onValueChange={setTimeRange}
          orientation="horizontal"
        >
          <ButtonRadioItem value="7">7 days</ButtonRadioItem>
          <ButtonRadioItem value="14">14 days</ButtonRadioItem>
          <ButtonRadioItem value="30">30 days</ButtonRadioItem>
        </RadioGroup>

        <Dropdown placement="bottom-end">
          <DropdownTrigger>
            <Button isIconOnly size="sm" variant="light">
              <Icon height={16} icon="solar:menu-dots-bold" width={16} />
            </Button>
          </DropdownTrigger>
          <DropdownMenu>
            <DropdownItem key="view-details">View Details</DropdownItem>
            <DropdownItem key="export-data">Export Data</DropdownItem>
            <DropdownItem key="set-alert">Set Alert</DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </div>
    </Card>
  );
}

// Add ButtonRadioItem component
const ButtonRadioItem = React.forwardRef<HTMLInputElement, any>((props, ref) => {
  const { Component, isSelected, getBaseProps, getInputProps } = useRadio(props);

  return (
    <Component {...getBaseProps()} ref={ref}>
      <VisuallyHidden>
        <input {...getInputProps()} />
      </VisuallyHidden>
      <Button
        disableRipple
        className={cn("pointer-events-none text-default-500", {
          "text-foreground": isSelected,
        })}
        size="sm"
        variant={isSelected ? "solid" : "flat"}
      >
        {props.children}
      </Button>
    </Component>
  );
});

ButtonRadioItem.displayName = "ButtonRadioItem";

export function Home() {
  const { walletActivity, trendingWallets, isLoading, error, fetchWalletActivity, fetchTrendingWallets } = useInsightsStore();

  useEffect(() => {
    const now = new Date();
    const startDate = new Date(now);
    startDate.setDate(startDate.getDate() - 30);
    
    fetchWalletActivity(startDate.toISOString(), now.toISOString());
    fetchTrendingWallets(startDate.toISOString(), now.toISOString());
  }, [fetchWalletActivity, fetchTrendingWallets]);

  const totalTransactions = walletActivity?.points.reduce((sum, point) => sum + point.total_transactions, 0) || 0;
  const totalDeposits = walletActivity?.points.reduce((sum, point) => sum + point.total_deposits, 0) || 0;
  const totalDebits = walletActivity?.points.reduce((sum, point) => sum + point.total_debits, 0) || 0;

  return (
    <div className="flex flex-col gap-4 p-8">
      <h1 className="text-4xl font-bold text-foreground">Welcome to CredGem</h1>
      <p className="text-lg text-foreground-500">
        Your comprehensive credit management platform
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
        <DashboardCard 
          title="Total Transactions" 
          value={totalTransactions.toString()} 
          description="Last 30 days"
        />
        <DashboardCard 
          title="Total Deposits" 
          value={`${totalDeposits.toLocaleString()}`} 
          description="Last 30 days"
        />
        <DashboardCard 
          title="Total Debits"
          value={`${totalDebits.toLocaleString()}`}
          description="Last 30 days"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <CircleChartCard />
        <BarChartCard />
      </div>
    </div>
  );
} 
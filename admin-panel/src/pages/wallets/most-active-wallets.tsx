"use client"

import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, LabelList, XAxis, YAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
const chartData = [
  { wallet: "January", transactions: 186 },
  { wallet: "February", transactions: 305 },
  { wallet: "March", transactions: 237 },
  { wallet: "April", transactions: 73 },
  { wallet: "May", transactions: 209 },
  { wallet: "June", transactions: 214 },
]

const chartConfig = {

  transactions: {
    label: "Transactions",
    color: "hsl(var(--chart-1))",
  },
  label: {
    color: "hsl(var(--foreground))",
  },
} satisfies ChartConfig

export function MostActiveWallets({ title, description, data }: { title: string, description: string, data: any }) {
  return (
    <Card className="flex flex-col">
    <CardHeader className="items-center pb-0">
      <CardTitle>{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
    </CardHeader>
    <CardContent className="flex-1 pb-0">
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={data}
            layout="vertical"
            margin={{
              right: 16,
            }}
          >
            <CartesianGrid horizontal={false} />
            <YAxis
              dataKey="wallet"
              type="category"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              // tickFormatter={(value) => value.slice(0, 3)}
              hide
            />
            <XAxis dataKey="transactions" type="number" hide />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Bar
              dataKey="transactions"
              layout="vertical"
              fill="var(--color-transactions)"
              radius={4}
            >
              <LabelList
                dataKey="wallet"
                position="insideLeft"
                offset={8}
                className="fill-[--color-label]"
                fontSize={12}
              />
              {/* <LabelList
                dataKey="desktop"
                position="right"
                offset={8}
                className="fill-foreground"
                fontSize={12}
              /> */}
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 font-medium leading-none">
          Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
        </div>
        <div className="leading-none text-muted-foreground">
          Showing total visitors for the last 6 months
        </div>
      </CardFooter>
    </Card>
  )
}

"use client";

import type {ComponentProps} from "react";
import type {ButtonProps} from "@/components/ui/button";

import React from "react";
import {useControlledState} from "@react-stately/utils";
import {m, LazyMotion, domAnimation} from "framer-motion";
import {cn} from "@/lib/utils";

export type VerticalStepProps = {
  className?: string;
  description?: React.ReactNode;
  title?: React.ReactNode;
};

export interface VerticalStepsProps extends React.HTMLAttributes<HTMLButtonElement> {
  /**
   * An array of steps.
   *
   * @default []
   */
  steps?: VerticalStepProps[];
  /**
   * The color of the steps.
   *
   * @default "primary"
   */
  color?: ButtonProps["color"];
  /**
   * The current step index.
   */
  currentStep?: number;
  /**
   * The default step index.
   *
   * @default 0
   */
  defaultStep?: number;
  /**
   * Whether to hide the progress bars.
   *
   * @default false
   */
  hideProgressBars?: boolean;
  /**
   * The custom class for the steps wrapper.
   */
  className?: string;
  /**
   * The custom class for the step.
   */
  stepClassName?: string;
  /**
   * Callback function when the step index changes.
   */
  onStepChange?: (stepIndex: number) => void;
}

function CheckIcon(props: ComponentProps<"svg">) {
  return (
    <svg {...props} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <m.path
        animate={{pathLength: 1}}
        d="M5 13l4 4L19 7"
        initial={{pathLength: 0}}
        strokeLinecap="round"
        strokeLinejoin="round"
        transition={{
          delay: 0.2,
          type: "tween",
          ease: "easeOut",
          duration: 0.3,
        }}
      />
    </svg>
  );
}

const VerticalSteps = React.forwardRef<HTMLButtonElement, VerticalStepsProps>(
  (
    {
      color = "primary",
      steps = [],
      defaultStep = 0,
      onStepChange,
      currentStep: currentStepProp,
      hideProgressBars = false,
      stepClassName,
      className,
      ...props
    },
    ref,
  ) => {
    const [currentStep, setCurrentStep] = useControlledState(
      currentStepProp,
      defaultStep,
      onStepChange,
    );

    const colors = React.useMemo(() => {
      let userColor;
      let fgColor;

      const colorsVars = [
        "[--active-fg-color:hsl(var(--foreground))]",
        "[--active-border-color:hsl(var(--primary))]",
        "[--active-color:hsl(var(--primary))]",
        "[--complete-background-color:hsl(var(--primary))]",
        "[--complete-border-color:hsl(var(--primary))]",
        "[--inactive-border-color:hsl(var(--muted))]",
        "[--inactive-color:hsl(var(--muted-foreground))]",
      ];

      switch (color) {
        case "primary":
          userColor = "[--step-color:hsl(var(--primary))]";
          fgColor = "[--step-fg-color:hsl(var(--primary-foreground))]";
          break;
        case "secondary":
          userColor = "[--step-color:hsl(var(--secondary))]";
          fgColor = "[--step-fg-color:hsl(var(--secondary-foreground))]";
          break;
        case "destructive":
          userColor = "[--step-color:hsl(var(--destructive))]";
          fgColor = "[--step-fg-color:hsl(var(--destructive-foreground))]";
          break;
        default:
          userColor = "[--step-color:hsl(var(--primary))]";
          fgColor = "[--step-fg-color:hsl(var(--primary-foreground))]";
          break;
      }

      if (!className?.includes("--step-fg-color")) colorsVars.unshift(fgColor);
      if (!className?.includes("--step-color")) colorsVars.unshift(userColor);
      if (!className?.includes("--inactive-bar-color"))
        colorsVars.push("[--inactive-bar-color:hsl(var(--bg-primary))]");

      return colorsVars;
    }, [color, className]);

    return (
      <nav aria-label="Progress" className="max-w-fit">
        <ol className={cn("flex flex-col gap-y-3", colors, className)}>
          {steps?.map((step, stepIdx) => {
            let status =
              currentStep === stepIdx ? "active" : currentStep < stepIdx ? "inactive" : "complete";

            return (
              <li key={stepIdx} className="relative">
                <div className="flex w-full max-w-full items-center">
                  <button
                    key={stepIdx}
                    ref={ref}
                    aria-current={status === "active" ? "step" : undefined}
                    className={cn(
                      "group flex w-full cursor-pointer items-center justify-center gap-4 rounded-large px-3 py-2.5",
                      stepClassName,
                    )}
                    onClick={() => setCurrentStep(stepIdx)}
                    {...props}
                  >
                    <div className="flex h-full items-center">
                      <LazyMotion features={domAnimation}>
                        <div className="relative">
                          <m.div
                            animate={status}
                            className={cn(
                              "relative flex h-[34px] w-[34px] items-center justify-center rounded-full border-medium text-large font-semibold text-default-foreground",
                              {
                                "shadow-lg": status === "complete",
                              },
                            )}
                            data-status={status}
                            initial={false}
                            transition={{duration: 0.25}}
                            variants={{
                              inactive: {
                                backgroundColor: "transparent",
                                borderColor: "hsl(var(--muted))",
                                color: "hsl(var(--muted-foreground))",
                              },
                              active: {
                                backgroundColor: "transparent",
                                borderColor: "hsl(var(--primary))",
                                color: "hsl(var(--primary))",
                              },
                              complete: {
                                backgroundColor: "hsl(var(--primary))",
                                borderColor: "hsl(var(--primary))",
                              },
                            }}
                          >
                            <div className="flex items-center justify-center">
                              {status === "complete" ? (
                                <CheckIcon className="h-6 w-6 text-primary-foreground" />
                              ) : (
                                <span>{stepIdx + 1}</span>
                              )}
                            </div>
                          </m.div>
                        </div>
                      </LazyMotion>
                    </div>
                    <div className="flex-1 text-left">
                      <div>
                        <div
                          className={cn(
                            "text-medium font-medium text-default-foreground transition-[color,opacity] duration-300 group-active:opacity-70",
                            {
                              "text-default-500": status === "inactive",
                            },
                          )}
                        >
                          {step.title}
                        </div>
                        <div
                          className={cn(
                            "text-tiny text-default-600 transition-[color,opacity] duration-300 group-active:opacity-70 lg:text-small",
                            {
                              "text-default-500": status === "inactive",
                            },
                          )}
                        >
                          {step.description}
                        </div>
                      </div>
                    </div>
                  </button>
                </div>
                {stepIdx < steps.length - 1 && !hideProgressBars && (
                  <div
                    aria-hidden="true"
                    className={cn(
                      "pointer-events-none absolute left-3 top-[calc(64px_*_var(--idx)_+_1)] flex h-1/2 -translate-y-1/3 items-center px-4",
                    )}
                    style={{
                      // @ts-ignore
                      "--idx": stepIdx,
                    }}
                  >
                    <div
                      className={cn(
                        "relative h-full w-0.5 bg-[var(--inactive-bar-color)] transition-colors duration-300",
                        "after:absolute after:block after:h-0 after:w-full after:bg-[var(--active-border-color)] after:transition-[height] after:duration-300 after:content-['']",
                        {
                          "after:h-full": stepIdx < currentStep,
                        },
                      )}
                    />
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    );
  },
);

VerticalSteps.displayName = "VerticalSteps";

export default VerticalSteps;

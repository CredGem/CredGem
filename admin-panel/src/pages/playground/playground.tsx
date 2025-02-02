"use client";

import React, { useEffect } from "react";
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css';
import VerticalSteps from "../../components/playground/vertical-step";
import { CreateCreditType } from "@/components/playground/create-credit-type";
import { CreateWallet } from "@/components/playground/create-wallet";
import { DepositCredits } from "@/components/playground/deposit-credits";
import { DebitCredits } from "@/components/playground/debit-credits";
import { CheckWalletBalance } from "@/components/playground/check-wallet-balance";
import { Progress } from "@/components/ui/progress";
import confetti from "canvas-confetti";


const steps = [
  {
    title: "Create a Credit Type",
    description:
      "Create a credit type to define the type of credit you want to create.",
    status: "active"
  },
  {
    title: "Create a Wallet",
    description: "Create a wallet to hold the credit.",
    status: "inactive"
  },
  {
    title: "Deposit Funds",
    description:
      "Deposit funds into the wallet.",
    status: "inactive"
  },
  {
    title: "Debit Funds",
    description: "Debit funds from the wallet.",
    status: "inactive"
  },
  {
    title: "Check Wallet Balance",
    description: "Check the balance of the wallet.",
    status: "inactive"
  },
];

function StepsComponent({currentStep, setCurrentStep}: {currentStep: number, setCurrentStep: (step: number) => void}) {

  return (
    <section className="max-w-sm">
      <h1 className="mb-2 text-xl font-medium" id="getting-started">
        Getting started
      </h1>
      <p className="mb-5 text-small text-default-500">
        Follow the steps to configure your account. This allows you to set up your business address.
      </p>
      <Progress
        className="mb-5"
        value={currentStep * 20}
      />
      <VerticalSteps
        hideProgressBars
        currentStep={currentStep}
        stepClassName="border border-default-200 rounded-md dark:border-default-50 aria-[current]:bg-default-100 dark:aria-[current]:bg-default-50"
        steps={steps}
        onStepChange={setCurrentStep}
      />
    </section>
  );
}

function ActionArea({stepIndex, onSuccess, walletId, setWalletId, creditTypeId, setCreditTypeId}: { stepIndex: number, onSuccess: () => void, walletId: string, setWalletId: (walletId: string) => void, creditTypeId: string, setCreditTypeId: (creditTypeId: string) => void}) {
    useEffect(() => {
        hljs.highlightAll();
      }, []);

      
  return (
    <>
      <h2 className="text-xl font-medium mb-4">{steps[stepIndex].title}</h2>
      {stepIndex === 0 && <CreateCreditType onSuccess={onSuccess} setCreditTypeId={setCreditTypeId}/>}
      {stepIndex === 1 && <CreateWallet onSuccess={onSuccess} setWalletId={setWalletId}/>}
      {stepIndex === 2 && <DepositCredits onSuccess={onSuccess} setCreditTypeId={setCreditTypeId} creditTypeId={creditTypeId} setWalletId={setWalletId} walletId={walletId}/>}
      {stepIndex === 3 && <DebitCredits onSuccess={onSuccess} setWalletId={setWalletId} walletId={walletId} setCreditTypeId={setCreditTypeId} creditTypeId={creditTypeId}/>}
      {stepIndex === 4 && <CheckWalletBalance onSuccess={onSuccess} setWalletId={setWalletId} walletId={walletId}/>}

    </>
  );
}


export default function Playground() {
  const [currentStep, setCurrentStep] = React.useState(0);
  const [done, setDone] = React.useState(false);
  const [creditTypeId, setCreditTypeId] = React.useState<string>("");
  const [walletId, setWalletId] = React.useState<string>("");
  const onSuccess = () => {
    steps[currentStep].status = "complete";
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }else{
        setDone(true);
    }
  }

  useEffect(() => {
    steps[currentStep].status = "active";
  }, [currentStep]);

  useEffect(() => {
    if (done) {
      const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };
        confetti({
          ...defaults,
        });
    }
  }, [done]);

  return (
    <div className="flex gap-8 p-20">
      <div className="w-1/3">
        <StepsComponent currentStep={currentStep} setCurrentStep={setCurrentStep}/>
      </div>
      <div className="w-2/3 border rounded-lg p-6 bg-default-50">
        <ActionArea stepIndex={currentStep} onSuccess={onSuccess} setCreditTypeId={setCreditTypeId} creditTypeId={creditTypeId} setWalletId={setWalletId} walletId={walletId}/>
      </div>
    </div>
  );
}
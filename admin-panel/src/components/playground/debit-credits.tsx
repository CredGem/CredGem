import { useState } from "react";
import { useWalletStore } from "../../store/useWalletStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ScriptCopyBtn from "../ui/script-copy-btn";
import { Label } from "@radix-ui/react-label";

const stepCode = (creditTypeId: string, description: string, amount: number, purpose: string, serviceId: string) => `curl -X POST http://localhost:8000/api/v1/wallets/wallet_123/debit \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "debit",
    "credit_type_id": "${creditTypeId}",
    "description": "${description}",
    "issuer": "system",
    "payload": {
      "type": "debit",
      "amount": ${amount}
    },
    "context": {
      "purpose": "${purpose}",
      "service_id": "${serviceId}"
    }
  }'`


export function DebitCredits({onSuccess, setWalletId, walletId, setCreditTypeId, creditTypeId}: {onSuccess: () => void, setWalletId: (walletId: string) => void, walletId: string, setCreditTypeId: (creditTypeId: string) => void, creditTypeId: string}) {
    const [description, setDescription] = useState('Initial deposit');
    const [amount, setAmount] = useState(100);
    const [purpose, setPurpose] = useState('service_payment');
    const [serviceId, setServiceId] = useState('srv_456');

    const { 
        processCredits,
        isLoading,
      } = useWalletStore();

      const handleCreate = async () => {
        await processCredits('debit', walletId, creditTypeId, amount, description, 'system', {purpose, serviceId});
        onSuccess();
      };

    return (
        <div className="flex flex-col gap-4 h-full relative">
            <div className="flex flex-col gap-4 pb-16">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="creditTypeId">Credit Type ID</Label>
                        <Input id="creditTypeId" value={creditTypeId} onChange={(e) => setCreditTypeId(e.target.value)} />
                    </div>
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="description">Description</Label>
                        <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
                    </div>
                </div>
                
                <div className="flex flex-col gap-2">
                    <Label htmlFor="amount">Amount</Label>
                    <Input id="amount" value={amount.toString()} onChange={(e) => setAmount(Number(e.target.value))} />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="purpose">Purpose</Label>
                        <Input id="purpose" value={purpose} onChange={(e) => setPurpose(e.target.value)} />
                    </div>
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="serviceId">Service ID</Label>
                        <Input id="serviceId" value={serviceId} onChange={(e) => setServiceId(e.target.value)} />
                    </div>
                </div>

                <div className="w-full flex">
                    <ScriptCopyBtn 
                        className="w-full flex-1"
                        codeLanguage="bash" 
                        lightTheme="min-light" 
                        darkTheme="github-dark" 
                        commandMap={{"bash": stepCode(creditTypeId, description, amount, purpose, serviceId)}}
                    >
                    </ScriptCopyBtn>
                </div>
            </div>
            <div className="flex flex-col gap-4 bg-background">
                <Button variant="outline" onClick={handleCreate} disabled={isLoading}>
                    Send Request
                </Button>
            </div>
        </div>
    )
}
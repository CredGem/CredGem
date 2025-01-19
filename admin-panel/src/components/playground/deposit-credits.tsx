import { useState } from "react";
import { useWalletStore } from "../../store/useWalletStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ScriptCopyBtn from "@/components/ui/script-copy-btn";
import { Label } from "@radix-ui/react-label";

const stepCode = (creditTypeId: string, description: string, amount: number, source: string, reference: string) => `curl -X POST http://localhost:8000/api/v1/wallets/wallet_123/deposit \\
    -H "Authorization: Bearer YOUR_TOKEN" \\
    -H "Content-Type: application/json" \\
    -d '{
      "type": "deposit",
      "credit_type_id": "${creditTypeId}",
      "description": "${description}",
      "issuer": "system",
      "payload": {
        "type": "deposit",
        "amount": "${amount}"
      },
      "context": {
        "source": "${source}",
        "reference": "${reference}"
      }
    }'`


export function DepositCredits({onSuccess, setCreditTypeId, creditTypeId, setWalletId, walletId}: {onSuccess: () => void, setCreditTypeId: (creditTypeId: string) => void, creditTypeId: string, setWalletId: (walletId: string) => void, walletId: string}) {
    const [description, setDescription] = useState('Initial deposit');
    const [amount, setAmount] = useState(100);
    const [source, setSource] = useState('bank_transfer');
    const [reference, setReference] = useState('tx_789');

    const { 
        processCredits,
        isLoading,
      } = useWalletStore();

      const handleCreate = async () => {
        await processCredits('deposit', walletId, creditTypeId, amount, description, 'system', {source, reference});
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

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="amount">Amount</Label>
                        <Input id="amount" value={amount.toString()} onChange={(e) => setAmount(Number(e.target.value))} />
                    </div>
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="walletId">Wallet ID</Label>
                        <Input id="walletId" value={walletId} onChange={(e) => setWalletId(e.target.value)} />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="source">Source</Label>
                        <Input id="source" value={source} onChange={(e) => setSource(e.target.value)} />
                    </div>
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="reference">Reference</Label>
                        <Input id="reference" value={reference} onChange={(e) => setReference(e.target.value)} />
                    </div>
                </div>

                <div className="w-full flex">
                    <ScriptCopyBtn 
                        className="w-full flex-1"
                        codeLanguage="bash" 
                        lightTheme="min-light" 
                        darkTheme="github-dark" 
                        commandMap={{"bash": stepCode(creditTypeId, description, amount, source, reference)}}
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
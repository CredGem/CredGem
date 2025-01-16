import { useState } from "react";
import { useWalletStore } from "../../store/useWalletStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ScriptCopyBtn from "@/components/ui/script-copy-btn";
import { Label } from "@/components/ui/label";

const stepCode = (name: string, userId: string, organization: string) => `curl -X POST http://localhost:8000/api/v1/wallets \\
    -H "Authorization: Bearer YOUR_TOKEN" \\
    -H "Content-Type: application/json" \\
    -d '{
      "name": "${name}",
      "context": {
        "user_id": "${userId}",
        "organization": "${organization}"
      }
    }'`


export function CreateWallet({onSuccess, setWalletId}: {onSuccess: () => void, setWalletId: (walletId: string) => void}) {
    const [name, setName] = useState('regular');
    const [userId, setUserId] = useState('user_123');
    const [organization, setOrganization] = useState('acme_corp');

    const { 
        createWallet,
        isLoading,
      } = useWalletStore();

      const handleCreate = async () => {
        const wallet = await createWallet({name, context: {userId, organization}});
        setWalletId(wallet.id);
        onSuccess();
      };

    return (
        <div className="flex flex-col gap-4 h-full relative">
            <div className="flex flex-col gap-4 pb-16">
                <div className="flex flex-col gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
                </div>
                <div className="flex flex-col gap-2">
                    <Label htmlFor="userId">User ID</Label>
                    <Input id="userId" value={userId} onChange={(e) => setUserId(e.target.value)} />
                </div>
                <div className="flex flex-col gap-2">
                    <Label htmlFor="organization">Organization</Label>
                    <Input id="organization" value={organization} onChange={(e) => setOrganization(e.target.value)} />
                </div>
                <div className="w-full flex">
                    <ScriptCopyBtn 
                        className="w-full flex-1"
                        codeLanguage="bash" 
                        lightTheme="min-light" 
                        darkTheme="github-dark" 
                        commandMap={{"bash": stepCode(name, userId, organization)}}
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
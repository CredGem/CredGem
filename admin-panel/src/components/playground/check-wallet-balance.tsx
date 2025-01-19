import { useWalletStore } from "../../store/useWalletStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ScriptCopyBtn from "@/components/ui/script-copy-btn";
import { Label } from "@radix-ui/react-label";
import { useState } from "react";

const stepCode = (walletId: string) => {
    return {
        "bash": `curl -X GET http://localhost:8000/api/v1/wallets/${walletId} \\
    -H "Authorization: Bearer YOUR_TOKEN"`,
    "python": `async with CredGemClient(
        api_key="your-api-key",
        base_url="http://localhost:8000"  # Explicitly set the API URL
    ) as client:
        wallet = await client.wallets.get(${walletId})
        print(wallet)
    `
    }
}



export function CheckWalletBalance({onSuccess, setWalletId, walletId}: {onSuccess: () => void, setWalletId: (walletId: string) => void, walletId: string}) {
    const [response, setResponse] = useState<any>(null);
    const { 
        fetchWallet,
        isLoading,
      } = useWalletStore();

      const handleCreate = async () => {
        const response = await fetchWallet(walletId);
        setResponse(response);
        onSuccess();
      };

    return (
        <div className="flex flex-col gap-4 h-full relative">
            <div className="flex flex-col gap-4 pb-16">
                <div className="flex flex-col gap-2">
                    <Label htmlFor="walletId">Wallet ID</Label>
                    <Input id="walletId" value={walletId} onChange={(e) => setWalletId(e.target.value)} />
                </div>

                <div className="w-full flex">
                    <ScriptCopyBtn 
                        className="w-full flex-1"
                        codeLanguage="bash" 
                        lightTheme="min-light" 
                        darkTheme="github-dark" 
                        commandMap={stepCode(walletId)}
                    >
                    </ScriptCopyBtn>
                </div>
                {response && <div className="w-full flex flex-col gap-2">
                    <Label>Response</Label>
                    <ScriptCopyBtn 
                        className="w-full flex-1"
                        codeLanguage="bash" 
                        lightTheme="min-light" 
                        darkTheme="github-dark" 
                        commandMap={{"bash": JSON.stringify(response, null, 4)}}
                    >
                    </ScriptCopyBtn>
                </div>}
            </div>
            <div className="flex flex-col gap-4 bg-background">
                <Button variant="outline" onClick={handleCreate} disabled={isLoading}>
                    Send Request
                </Button>
            </div>
        </div>
    )
}
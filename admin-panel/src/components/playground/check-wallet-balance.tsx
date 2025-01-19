import { useWalletStore } from "../../store/useWalletStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ScriptCopyBtn from "@/components/ui/script-copy-btn";
import { Label } from "@radix-ui/react-label";

const stepCode = (walletId: string) => `curl -X GET http://localhost:8000/api/v1/wallets/${walletId} \\
    -H "Authorization: Bearer YOUR_TOKEN"'`


export function CheckWalletBalance({onSuccess, setWalletId, walletId}: {onSuccess: () => void, setWalletId: (walletId: string) => void, walletId: string}) {

    const { 
        fetchWallet,
        isLoading,
      } = useWalletStore();

      const handleCreate = async () => {
        await fetchWallet(walletId);
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
                        commandMap={{"bash": stepCode(walletId)}}
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
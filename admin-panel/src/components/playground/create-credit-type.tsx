import { useState } from "react";
import { useWalletStore } from "../../store/useWalletStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ScriptCopyBtn from "@/components/ui/script-copy-btn";
import { Label } from "@radix-ui/react-label";

const stepCode = (name: string, description: string) => `curl -X POST http://localhost:8000/api/v1/credit-types \\
-H "Authorization: Bearer YOUR_TOKEN" \\
-H "Content-Type: application/json" \\
-d '{
  "name": "${name}",
  "description": "${description}"
}'`


export function CreateCreditType({onSuccess, setCreditTypeId}: {onSuccess: () => void, setCreditTypeId: (creditTypeId: string) => void}) {
    const [name, setName] = useState('regular');
    const [description, setDescription] = useState('Standard currency credits');

    const { 
        createCreditType,
        isLoading,
      } = useWalletStore();

      const handleCreate = async () => {
        const creditType = await createCreditType({name, description});
        setCreditTypeId(creditType.id);
        console.log(creditType);
        onSuccess();
      };

    return (
        <div className="flex flex-col gap-4 relative">
            <div className="flex flex-col gap-4 pb-16">
                <div className="flex flex-col gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
                </div>
                <div className="flex flex-col gap-2">
                    <Label htmlFor="description">Description</Label>
                    <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
                </div>
                <div className="w-full flex">
                    <ScriptCopyBtn 
                        className="w-full flex-1"
                        codeLanguage="bash" 
                        lightTheme="min-light" 
                        darkTheme="github-dark" 
                        commandMap={{"bash": stepCode(name, description)}}
                    >
                    </ScriptCopyBtn>
                </div>
            </div>
            <div className="flex flex-col gap-4 absolute bottom-0 left-0 right-0 bg-background">
                <Button variant="outline" onClick={handleCreate} disabled={isLoading}>
                    Send Request
                </Button>
            </div>
        </div>
    )
}
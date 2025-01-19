import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Icon } from "@iconify/react";
import { WalletContextPair } from "../types/wallet";

interface KeyValuePairsInputProps {
  pairs: WalletContextPair[];
  onChange: (pairs: WalletContextPair[]) => void;
  label?: string;
}

export function KeyValuePairsInput({ pairs, onChange, label = "Context" }: KeyValuePairsInputProps) {
  const handleAddPair = () => {
    onChange([...pairs, { key: '', value: '' }]);
  };

  const handleRemovePair = (index: number) => {
    onChange(pairs.filter((_, i) => i !== index));
  };

  const handlePairChange = (index: number, field: 'key' | 'value', value: string) => {
    const newPairs = [...pairs];
    newPairs[index][field] = value;
    onChange(newPairs);
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <p className="text-small font-medium">{label}</p>
        <Button
          variant="outline"
          onClick={handleAddPair}
        >
          <Icon icon="solar:add-circle-bold" width={16} height={16} />
          Add Field
        </Button>
      </div>
      {pairs.map((pair, index) => (
        <div key={index} className="flex gap-2 items-start">
          <Input
            size={16}
            placeholder="Enter key"
            value={pair.key}
            onChange={(e) => handlePairChange(index, 'key', e.target.value)}
          />
          <Input
            size={16}
            placeholder="Enter value"
            value={pair.value}
            onChange={(e) => handlePairChange(index, 'value', e.target.value)}
          />
          {pairs.length > 1 && (
            <Button
              variant="outline"
              color="destructive"
              className="mt-7"
              onClick={() => handleRemovePair(index)}
            >
              <Icon icon="solar:trash-bin-trash-bold" width={16} height={16} />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
} 
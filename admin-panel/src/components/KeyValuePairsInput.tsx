import React from "react";
import { Button, Input } from "@nextui-org/react";
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
          size="sm"
          variant="flat"
          color="primary"
          onPress={handleAddPair}
          startContent={<Icon icon="solar:add-circle-bold" width={16} height={16} />}
        >
          Add Field
        </Button>
      </div>
      {pairs.map((pair, index) => (
        <div key={index} className="flex gap-2 items-start">
          <Input
            size="sm"
            label="Key"
            placeholder="Enter key"
            value={pair.key}
            onChange={(e) => handlePairChange(index, 'key', e.target.value)}
          />
          <Input
            size="sm"
            label="Value"
            placeholder="Enter value"
            value={pair.value}
            onChange={(e) => handlePairChange(index, 'value', e.target.value)}
          />
          {pairs.length > 1 && (
            <Button
              isIconOnly
              size="sm"
              variant="light"
              color="danger"
              className="mt-7"
              onPress={() => handleRemovePair(index)}
            >
              <Icon icon="solar:trash-bin-trash-bold" width={16} height={16} />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
} 
import { useState } from "react";
import { Calculator } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface AreaCalculatorProps {
  onAreaChange: (area: number) => void;
  onCoverageTypeChange: (type: string) => void;
}

export const AreaCalculator = ({ onAreaChange, onCoverageTypeChange }: AreaCalculatorProps) => {
  const [width, setWidth] = useState(30);
  const [length, setLength] = useState(20);
  const [coverageType, setCoverageType] = useState("policarbonato-alveolar");

  const area = width * length;

  const handleWidthChange = (value: string) => {
    const newWidth = parseFloat(value) || 0;
    setWidth(newWidth);
    onAreaChange(newWidth * length);
  };

  const handleLengthChange = (value: string) => {
    const newLength = parseFloat(value) || 0;
    setLength(newLength);
    onAreaChange(width * newLength);
  };

  const handleCoverageTypeChange = (value: string) => {
    setCoverageType(value);
    onCoverageTypeChange(value);
  };

  return (
    <Card className="h-fit">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Calculator className="w-5 h-5" />
          Calculadora de Área
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="width" className="text-sm font-medium">
              Largura (metros)
            </Label>
            <Input
              id="width"
              type="number"
              value={width}
              onChange={(e) => handleWidthChange(e.target.value)}
              className="text-center"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="length" className="text-sm font-medium">
              Comprimento (metros)
            </Label>
            <Input
              id="length"
              type="number"
              value={length}
              onChange={(e) => handleLengthChange(e.target.value)}
              className="text-center"
            />
          </div>
        </div>

        <div className="bg-muted rounded-lg p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
            <Calculator className="w-4 h-4" />
            Área Total:
          </div>
          <div className="text-2xl font-bold text-primary">
            {area.toFixed(2)} m²
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="font-semibold">Tipo de Cobertura</h3>
          <Select value={coverageType} onValueChange={handleCoverageTypeChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="policarbonato-alveolar">
                Policarbonato Alveolar - R$ 120,00/m²
              </SelectItem>
              <SelectItem value="lona-pvc">
                Lona PVC - R$ 85,00/m²
              </SelectItem>
              <SelectItem value="telha-translucida">
                Telha Translúcida - R$ 35,00/m²
              </SelectItem>
              <SelectItem value="lona-premium">
                Lona Premium Blackout - R$ 150,00/m²
              </SelectItem>
            </SelectContent>
          </Select>

          <div className="bg-success rounded-lg p-4">
            <div className="text-sm text-success-foreground mb-1">💰 Valor Total:</div>
            <div className="text-2xl font-bold text-success-foreground">
              R$ {(area * getCoveragePrice(coverageType)).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-success-foreground/80 mt-1">
              {getCoverageName(coverageType)} - R$ {getCoveragePrice(coverageType).toFixed(2)}/m²
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const getCoveragePrice = (type: string): number => {
  const prices: Record<string, number> = {
    "policarbonato-alveolar": 120,
    "lona-pvc": 85,
    "telha-translucida": 35,
    "lona-premium": 150,
  };
  return prices[type] || 120;
};

const getCoverageName = (type: string): string => {
  const names: Record<string, string> = {
    "policarbonato-alveolar": "Policarbonato Alveolar",
    "lona-pvc": "Lona PVC",
    "telha-translucida": "Telha Translúcida",
    "lona-premium": "Lona Premium Blackout",
  };
  return names[type] || "Policarbonato Alveolar";
};
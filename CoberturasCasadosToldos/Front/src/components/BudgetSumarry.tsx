import { FileText, Share2, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface BudgetSummaryProps {
  area: number;
  coverageType: string;
}

export const BudgetSummary = ({ area, coverageType }: BudgetSummaryProps) => {
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

  const generateBudgetId = () => {
    const prefixes: Record<string, string> = {
      "policarbonato-alveolar": "COT-",
      "lona-pvc": "COT-",
      "telha-translucida": "COT-",
      "lona-premium": "COT-",
    };
    return (prefixes[coverageType] || "COT-") + Math.floor(Math.random() * 900000 + 100000);
  };

  const materialPrice = getCoveragePrice(coverageType);
  const materialTotal = area * materialPrice;
  const installationTotal = area * 35; // R$ 35/m² installation
  const total = materialTotal + installationTotal;
  const totalWithInstallment = total * 1.12; // 12% for installments

  return (
    <Card className="h-fit">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <FileText className="w-5 h-5" />
          Resumo do Orçamento
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Orçamento:</div>
            <div className="font-semibold">{generateBudgetId()}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Data:</div>
            <div className="font-semibold">{new Date().toLocaleDateString('pt-BR')}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Cliente:</div>
            <div className="font-semibold">Cliente Exemplo</div>
          </div>
          <div>
            <div className="text-muted-foreground">Válido até:</div>
            <div className="font-semibold">
              {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString('pt-BR')}
            </div>
          </div>
        </div>

        <Separator />

        <div>
          <h4 className="font-semibold mb-3">Detalhes do Projeto</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Dimensões:</span>
              <span className="font-medium">30m × 20m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Área total:</span>
              <span className="font-bold">{area.toFixed(2)} m²</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Material:</span>
              <span className="font-medium">{getCoverageName(coverageType)}</span>
            </div>
          </div>
        </div>

        <Separator />

        <div>
          <h4 className="font-semibold mb-3">Discriminação de Custos</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Material ({area.toFixed(2)} m² × R$ {materialPrice.toFixed(2)})</span>
              <span className="font-medium">R$ {materialTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="flex justify-between">
              <span>Instalação ({area.toFixed(2)} m² × R$ 35,00)</span>
              <span className="font-medium">R$ {installationTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
        </div>

        <div className="bg-success rounded-lg p-4">
          <div className="flex justify-between items-center">
            <span className="text-success-foreground font-semibold">Valor Total:</span>
            <span className="text-2xl font-bold text-success-foreground">
              R$ {totalWithInstallment.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="text-xs text-success-foreground/80 mt-1">
            Parcelas em até 12x sem juros no cartão
          </div>
        </div>

        <div className="bg-muted rounded-lg p-3 text-xs text-muted-foreground">
          ✅ Incluso: Material, instalação, estrutura de suporte e garantia de 2 anos. Prazo de entrega: 5-7 dias após confirmação do pedido.
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="flex-1">
            <Share2 className="w-4 h-4 mr-1" />
            Compartilhar
          </Button>
          <Button size="sm" className="flex-1">
            <Download className="w-4 h-4 mr-1" />
            Gerar PDF
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
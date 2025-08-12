import { Building2, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Header = () => {
  return (
    <header className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-primary rounded-lg p-2">
            <Building2 className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">CoberturasPro</h1>
            <p className="text-sm text-muted-foreground">Calculadora de Orçamentos</p>
          </div>
        </div>
        <Button variant="outline" size="sm">
          <Monitor className="w-4 h-4 mr-2" />
          Versão Tablet
        </Button>
      </div>
    </header>
  );
};
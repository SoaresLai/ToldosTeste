import { Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CoverageVisualizationProps {
  area: number;
  coverageType: string;
  width: number;
  length: number;
}

export const CoverageVisualization = ({ area, coverageType, width, length }: CoverageVisualizationProps) => {
  const getCoverageColor = (type: string): string => {
    const colors: Record<string, string> = {
      "policarbonato-alveolar": "bg-cyan-400",
      "lona-pvc": "bg-blue-500",
      "telha-translucida": "bg-amber-400",
      "lona-premium": "bg-gray-700",
    };
    return colors[type] || "bg-cyan-400";
  };

  return (
    <Card className="h-fit">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Eye className="w-5 h-5" />
          Visualização da Cobertura
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="bg-gradient-to-b from-blue-50 to-blue-100 rounded-lg p-8 flex items-center justify-center min-h-[300px]">
          <div className="relative">
            {/* 3D Effect Shadow */}
            <div 
              className="absolute top-2 left-2 bg-gray-300 rounded-lg opacity-50"
              style={{
                width: `${Math.min(width * 8, 200)}px`,
                height: `${Math.min(length * 6, 150)}px`,
              }}
            />
            
            {/* Main Coverage Rectangle */}
            <div 
              className={`${getCoverageColor(coverageType)} rounded-lg border-2 border-gray-400 shadow-lg relative`}
              style={{
                width: `${Math.min(width * 8, 200)}px`,
                height: `${Math.min(length * 6, 150)}px`,
              }}
            >
              {/* Grid pattern to simulate coverage texture */}
              <div className="absolute inset-0 opacity-20">
                <div className="grid grid-cols-4 grid-rows-3 h-full">
                  {Array.from({ length: 12 }).map((_, i) => (
                    <div key={i} className="border border-white/50" />
                  ))}
                </div>
              </div>
              
              {/* Highlight effect */}
              <div className="absolute top-0 left-0 w-full h-1/3 bg-white/20 rounded-t-lg" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-primary">Largura</div>
            <div className="text-muted-foreground">{width.toFixed(1)}m</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-primary">Comprimento</div>
            <div className="text-muted-foreground">{length.toFixed(1)}m</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-primary">Área</div>
            <div className="text-success font-bold">{area.toFixed(1)} m²</div>
          </div>
        </div>

        <div className="text-xs text-muted-foreground text-center bg-muted rounded p-2">
          📏 Escala 1:20 (cada quadrado = 1m²)
        </div>
      </CardContent>
    </Card>
  );
}; 
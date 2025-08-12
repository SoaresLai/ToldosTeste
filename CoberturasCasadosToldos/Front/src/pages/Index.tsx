import { useState } from "react";
import { Header } from "@/components/Header";
import { AreaCalculator } from "@/components/AreaCalculator";
import { CoverageVisualization } from "@/components/CoverageVisualization";
import { BudgetSummary } from "@/components/BudgetSummary";

const Index = () => {
  const [area, setArea] = useState(600); // 30 * 20
  const [coverageType, setCoverageType] = useState("policarbonato-alveolar");

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-6">
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <AreaCalculator 
              onAreaChange={setArea}
              onCoverageTypeChange={setCoverageType}
            />
          </div>
          <div className="lg:col-span-1">
            <CoverageVisualization 
              area={area}
              coverageType={coverageType}
              width={30}
              length={20}
            />
          </div>
          <div className="lg:col-span-1">
            <BudgetSummary 
              area={area}
              coverageType={coverageType}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;

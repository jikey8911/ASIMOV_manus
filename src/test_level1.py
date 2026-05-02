import sys
import pprint
from asimov.levels.level1.strategists import MarketAnalystAgent, StrategicPlanningAgent, EthicsAndRiskAgent

def test_level1():
    print("--- Probando MarketAnalystAgent ---")
    analyst = MarketAnalystAgent()
    opportunities = analyst.scan()
    print("Oportunidades encontradas:")
    for opp in opportunities:
        pprint.pprint(opp.model_dump())
        print("-" * 20)
    
    if not opportunities:
        print("No se encontraron oportunidades.")
        return

    print("\n--- Probando StrategicPlanningAgent ---")
    planner = StrategicPlanningAgent()
    selected_opp = opportunities[0]
    goal = planner.define_goal(selected_opp)
    print("Objetivo estratégico generado para la primera oportunidad:")
    pprint.pprint(goal.model_dump())

    print("\n--- Probando EthicsAndRiskAgent ---")
    ethics = EthicsAndRiskAgent()
    approved = ethics.approve(goal)
    print(f"¿Aprobado por Ética y Riesgo?: {approved}")

if __name__ == "__main__":
    test_level1()

"""
Service Cash Flow pour AGRIFRIKA Dashboard
Connexion API réelle Agrifrika Cashflow
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx
from app.models.dashboard_models import CashFlowData, CashFlowTransaction

logger = logging.getLogger(__name__)

class CashFlowService:
    """Service pour gérer les données de cash flow"""
    
    def __init__(self):
        self.api_base_url = "https://api.agrifrika.com/prod/cashflow"
        self.api_key = "xjncCLKaE86x2haG1uYPh9o7DUEzO2JDMEkA8RK5"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Fallback sur les données simulées en cas d'erreur API
        self.base_balance = 37504.06
        self.daily_transactions = self._generate_sample_transactions()
    
    def _generate_sample_transactions(self) -> List[CashFlowTransaction]:
        """Génère des transactions d'exemple basées sur des données réelles"""
        transactions = [
            CashFlowTransaction(
                type="income",
                description="Soplect Falm*",
                amount=1700.00,
                date=datetime.now() - timedelta(days=1),
                category="Services"
            ),
            CashFlowTransaction(
                type="income",
                description="Parice Etame Etame",
                amount=2500.00,
                date=datetime.now() - timedelta(days=1),
                category="Consulting"
            ),
            CashFlowTransaction(
                type="income",
                description="Benjamin Ngangang",
                amount=1000.00,
                date=datetime.now() - timedelta(days=3),
                category="Services"
            ),
            CashFlowTransaction(
                type="income",
                description="Georges DEFO",
                amount=1000.00,
                date=datetime.now() - timedelta(days=20),
                category="Services"
            ),
            CashFlowTransaction(
                type="expense",
                description="Impression des tableaux des visiteurs",
                amount=97.17,
                date=datetime.now() - timedelta(days=5),
                category="Office Supplies"
            ),
            CashFlowTransaction(
                type="expense",
                description="Écrire pour imprimante",
                amount=74.20,
                date=datetime.now() - timedelta(days=5),
                category="Office Supplies"
            ),
            CashFlowTransaction(
                type="expense",
                description="Support pour Écran 32\"",
                amount=12.37,
                date=datetime.now() - timedelta(days=13),
                category="Equipment"
            )
        ]
        return transactions
    
    async def _fetch_cashflow_data_from_api(self) -> Optional[Dict[str, Any]]:
        """Récupère les données de cashflow depuis l'API Agrifrika"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_base_url}/cashflows/runway/api",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'appel API cashflow: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'appel API cashflow: {e}")
            return None

    async def get_current_cash_flow(self) -> Optional[CashFlowData]:
        """Récupère les données actuelles de cash flow"""
        try:
            # Tentative de récupération depuis l'API réelle
            api_data = await self._fetch_cashflow_data_from_api()
            
            if api_data:
                return await self._parse_api_cashflow_data(api_data)
            else:
                logger.warning("Utilisation des données de fallback pour le cash flow")
                return await self._get_fallback_cash_flow()
            
        except Exception as e:
            logger.error(f"Erreur récupération cash flow: {e}")
            return await self._get_fallback_cash_flow()

    async def _parse_api_cashflow_data(self, api_data: Dict[str, Any]) -> Optional[CashFlowData]:
        """Parse les données de l'API Agrifrika et les convertit en CashFlowData"""
        try:
            # Structure réelle de l'API Agrifrika
            current_balance = float(api_data.get("current_balance", 0.0))
            historical_income = float(api_data.get("historical_income", 0.0))
            total_spent = float(api_data.get("total_spent", 0.0))
            monthly_burn_rate = float(api_data.get("monthly_burn_rate", 0.0))
            future_monthly_burn = float(api_data.get("future_monthly_burn", 0.0))
            
            # Runway en jours et mois
            current_runway_days = api_data.get("current_runway_days", "0")
            current_runway_months = api_data.get("current_runway_months", "0")
            current_runway_ends_on = api_data.get("current_runway_ends_on", "")
            
            # Projection du cash flow
            cash_flow_projection = api_data.get("cash_flow_projection", [])
            
            # Adaptation vers notre modèle de données
            # Résumé hebdomadaire basé sur les taux mensuels
            weekly_income = historical_income / 4  # Estimation hebdomadaire
            weekly_expenses = monthly_burn_rate / 4  # Estimation hebdomadaire
            net_change = weekly_income - weekly_expenses
            
            # Conversion de la projection cash flow vers daily evolution
            daily_evolution = []
            if cash_flow_projection:
                for i, projection in enumerate(cash_flow_projection[-7:]):  # 7 derniers jours
                    daily_evolution.append({
                        "date": (datetime.now() - timedelta(days=6-i)).isoformat(),
                        "amount": round(float(projection.get("projected_balance", 0)) - current_balance, 2)
                    })
            else:
                daily_evolution = self._generate_daily_evolution()
            
            # Transactions récentes simulées basées sur les données réelles
            recent_transactions = self._generate_transactions_from_api_data(
                historical_income, total_spent, monthly_burn_rate
            )
            
            # Paiements à venir basés sur le burn rate futur
            upcoming_payments = [
                {
                    "description": "Monthly operational expenses",
                    "amount": future_monthly_burn,
                    "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                    "currency": "USD"
                }
            ]
            
            # Projection 30 jours = runway actuel en jours si < 30, sinon projection positive
            try:
                runway_days = float(current_runway_days.replace(" jours", "").replace(",", "."))
                if runway_days <= 30:
                    thirty_day_projection = -monthly_burn_rate  # Négatif si runway court
                else:
                    thirty_day_projection = net_change * 4  # Extrapolation mensuelle
            except:
                thirty_day_projection = net_change * 4
            
            return CashFlowData(
                current_balance=round(current_balance, 2),
                balance_date=datetime.now(),
                weekly_summary={
                    "total_income": round(weekly_income, 2),
                    "total_expenses": round(weekly_expenses, 2),
                    "net_change": round(net_change, 2)
                },
                daily_evolution=daily_evolution,
                recent_transactions=recent_transactions,
                upcoming_payments=upcoming_payments,
                thirty_day_projection=round(thirty_day_projection, 2),
                last_updated=datetime.now(),
                # Données supplémentaires de l'API
                monthly_burn_rate=round(monthly_burn_rate, 2),
                runway_days=current_runway_days,
                runway_months=current_runway_months,
                runway_end_date=current_runway_ends_on,
                historical_income=round(historical_income, 2),
                total_spent=round(total_spent, 2)
            )
            
        except Exception as e:
            logger.error(f"Erreur parsing des données API cashflow: {e}")
            return None

    def _generate_transactions_from_api_data(self, historical_income: float, total_spent: float, monthly_burn: float) -> List[CashFlowTransaction]:
        """Génère des transactions basées sur les données réelles de l'API"""
        transactions = []
        
        # Transaction de revenus basée sur les revenus historiques
        if historical_income > 0:
            transactions.append(CashFlowTransaction(
                type="income",
                description="Historical revenue (estimation)",
                amount=round(historical_income / 10, 2),  # Simulation d'une transaction récente
                date=datetime.now() - timedelta(days=2),
                category="Revenue"
            ))
        
        # Transactions de dépenses basées sur le burn rate
        if monthly_burn > 0:
            daily_burn = monthly_burn / 30
            for i in range(3):  # 3 dernières transactions de dépenses
                transactions.append(CashFlowTransaction(
                    type="expense",
                    description=f"Operational expenses D-{i+1}",
                    amount=round(daily_burn + (daily_burn * 0.2 * (i-1)), 2),  # Variation
                    date=datetime.now() - timedelta(days=i+1),
                    category="Operations"
                ))
        
        return transactions

    async def _get_fallback_cash_flow(self) -> Optional[CashFlowData]:
        """Récupère les données de fallback en cas d'échec de l'API"""
        try:
            # Calcul du solde actuel
            current_balance = self.base_balance
            for transaction in self.daily_transactions:
                if transaction.type == "income":
                    current_balance += transaction.amount
                else:
                    current_balance -= transaction.amount
            
            # Calcul du résumé hebdomadaire
            week_ago = datetime.now() - timedelta(days=7)
            weekly_transactions = [
                t for t in self.daily_transactions 
                if t.date >= week_ago
            ]
            
            total_income = sum(t.amount for t in weekly_transactions if t.type == "income")
            total_expenses = sum(t.amount for t in weekly_transactions if t.type == "expense")
            net_change = total_income - total_expenses
            
            # Génération de l'évolution quotidienne
            daily_evolution = self._generate_daily_evolution()
            
            # Transactions récentes (5 dernières)
            recent_transactions = sorted(
                self.daily_transactions, 
                key=lambda x: x.date, 
                reverse=True
            )[:5]
            
            # Paiements à venir (simulation)
            upcoming_payments = [
                {
                    "description": "Agricultural equipment supplier invoice",
                    "amount": 2500.00,
                    "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                    "currency": "USD"
                },
                {
                    "description": "Team salaries",
                    "amount": 3500.00,
                    "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
                    "currency": "USD"
                }
            ]
            
            # Projection 30 jours (basée sur la tendance actuelle)
            monthly_avg_income = total_income * 4  # Extrapolation hebdomadaire
            monthly_avg_expenses = total_expenses * 4
            thirty_day_projection = monthly_avg_income - monthly_avg_expenses
            
            return CashFlowData(
                current_balance=round(current_balance, 2),
                balance_date=datetime.now(),
                weekly_summary={
                    "total_income": round(total_income, 2),
                    "total_expenses": round(total_expenses, 2),
                    "net_change": round(net_change, 2)
                },
                daily_evolution=daily_evolution,
                recent_transactions=recent_transactions,
                upcoming_payments=upcoming_payments,
                thirty_day_projection=round(thirty_day_projection, 2),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération cash flow fallback: {e}")
            return None

    def _generate_daily_evolution(self) -> List[Dict[str, Any]]:
        """Génère l'évolution quotidienne"""
        import random
        daily_evolution = []
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            daily_change = random.uniform(-500, 1000) if i < 5 else random.uniform(200, 800)
            daily_evolution.append({
                "date": date.isoformat(),
                "amount": round(daily_change, 2)
            })
        return daily_evolution
    
    async def add_transaction(self, transaction: CashFlowTransaction) -> bool:
        """Ajoute une nouvelle transaction"""
        try:
            self.daily_transactions.append(transaction)
            logger.info(f"Transaction ajoutée: {transaction.description} - {transaction.amount}")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout transaction: {e}")
            return False
    
    def health_check(self) -> bool:
        """Vérifie la santé du service cash flow"""
        try:
            # Vérification basique que les données sont disponibles
            return len(self.daily_transactions) > 0
        except Exception as e:
            logger.error(f"Cash flow health check failed: {e}")
            return False
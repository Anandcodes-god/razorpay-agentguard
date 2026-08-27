import json
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models import Agent, IntentContract, Transaction


async def seed_agents(session: AsyncSession) -> Dict[str, str]:
    """Create 3 demo agents. Returns dict mapping names to IDs."""
    now = datetime.now(timezone.utc)
    
    agents_data = [
        {
            'id': 'agent_shopbot_001',
            'name': 'ShopBot',
            'principal_id': 'user_anand_123',
            'is_verified': True,
            'scope': json.dumps({'categories': ['groceries', 'food', 'footwear', 'sports'], 'merchants': []}),
            'max_budget': 5000000,  # ₹50,000 in paise
            'expires_at': now + timedelta(days=30),
        },
        {
            'id': 'agent_unknown_002',
            'name': 'UnknownBot',
            'principal_id': '',
            'is_verified': False,
            'scope': None,
            'max_budget': None,
            'expires_at': None,
        },
        {
            'id': 'agent_expired_003',
            'name': 'ExpiredBot',
            'principal_id': 'user_old_456',
            'is_verified': True,
            'scope': json.dumps({'categories': ['electronics']}),
            'max_budget': 1000000,  # ₹10,000
            'expires_at': now - timedelta(days=7),
        }
    ]
    
    agent_map = {}
    for data in agents_data:
        # Check if exists
        result = await session.execute(select(Agent).where(Agent.id == data['id']))
        agent = result.scalars().first()
        
        if not agent:
            agent = Agent(**data)
            session.add(agent)
            
        agent_map[data['name']] = data['id']
        
    return agent_map


async def seed_intent_contracts(session: AsyncSession) -> Dict[str, str]:
    """Create 2 demo intent contracts. Returns dict mapping names to IDs."""
    now = datetime.now(timezone.utc)
    
    contracts_data = [
        {
            'id': 'ic_grocery_001',
            'agent_id': 'agent_shopbot_001',
            'raw_instruction': 'Buy groceries under ₹2,000',
            'purpose': 'purchase_groceries',
            'categories': json.dumps(['groceries', 'food']),
            'max_amount': 200000,  # ₹2,000 in paise
            'currency': 'INR',
            'merchant_constraints': json.dumps({}),
            'requires_confirmation_above': 200000,
            'expires_at': now + timedelta(hours=24),
        },
        {
            'id': 'ic_shoes_002',
            'agent_id': 'agent_shopbot_001',
            'raw_instruction': 'Buy running shoes under ₹5,000',
            'purpose': 'purchase_running_shoes',
            'categories': json.dumps(['footwear', 'sports']),
            'max_amount': 500000,  # ₹5,000 in paise
            'currency': 'INR',
            'merchant_constraints': json.dumps({}),
            'requires_confirmation_above': 500000,
            'expires_at': now + timedelta(hours=24),
        }
    ]
    
    contract_map = {}
    for data in contracts_data:
        # Check if exists
        result = await session.execute(select(IntentContract).where(IntentContract.id == data['id']))
        contract = result.scalars().first()
        
        if not contract:
            contract = IntentContract(**data)
            session.add(contract)
            
        # Using purpose as the name key for the map
        contract_map[data['purpose']] = data['id']
        
    return contract_map


async def seed_transaction_history(session: AsyncSession) -> None:
    """Create synthetic transaction history for ShopBot."""
    now = datetime.now(timezone.utc)
    
    # Check if we already have transactions for this agent
    result = await session.execute(
        select(Transaction).where(Transaction.agent_id == 'agent_shopbot_001')
    )
    existing = result.scalars().all()
    if len(existing) >= 8:
        return
        
    groceries = [
        ('BigBasket', 145000), ('QuickMart', 85000), ('FreshDirect', 178000), 
        ('BigBasket', 52000), ('QuickMart', 115000), ('LocalGrocer', 94000)
    ]
    
    footwear = [
        ('Nike', 410000), ('Puma', 275000)
    ]
    
    transactions = []
    
    # Generate 6 grocery transactions
    for i, (merchant, amount) in enumerate(groceries):
        tx_time = now - timedelta(hours=random.randint(2, 22), minutes=random.randint(0, 59))
        tx = Transaction(
            id=f"tx_hist_groc_{i}",
            agent_id='agent_shopbot_001',
            intent_contract_id='ic_grocery_001',
            merchant_name=merchant,
            merchant_category='groceries',
            amount=amount,
            currency='INR',
            description=f'Grocery purchase at {merchant}',
            status='allowed',
            created_at=tx_time
        )
        transactions.append(tx)
        
    # Generate 2 footwear transactions
    for i, (merchant, amount) in enumerate(footwear):
        tx_time = now - timedelta(hours=random.randint(24, 48), minutes=random.randint(0, 59))
        tx = Transaction(
            id=f"tx_hist_shoe_{i}",
            agent_id='agent_shopbot_001',
            intent_contract_id='ic_shoes_002',
            merchant_name=merchant,
            merchant_category='footwear',
            amount=amount,
            currency='INR',
            description=f'Shoe purchase at {merchant}',
            status='allowed',
            created_at=tx_time
        )
        transactions.append(tx)
        
    session.add_all(transactions)


async def seed_all(session: AsyncSession) -> Dict[str, Any]:
    """Run all seed functions. Returns summary."""
    agents = await seed_agents(session)
    contracts = await seed_intent_contracts(session)
    await seed_transaction_history(session)
    await session.commit()
    
    return {
        'agents_created': len(agents),
        'contracts_created': len(contracts),
        'history_transactions': 8
    }

# /// script
# requires-python = ">=X.XX" TODO: Update this to the minimum Python version you want to support
# dependencies = [
#   TODO: Add any dependencies your script requires
# ]
# ///

# TODO: Update the main function to your needs or remove it.


def main() -> None:
    print("Start coding in Python today!")


if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_MEMBERS = 1000

# ---------------------------------------------------------
# 1. GENERAR TABLA: MEMBERS
# ---------------------------------------------------------
plans = ['Basic', 'Gold', 'Platinum']
plan_prices = {'Basic': 30, 'Gold': 50, 'Platinum': 80}
status_options = ['Active', 'Churned']

members_data = []

start_date_range = datetime(2025, 1, 1)
end_date_range = datetime(2026, 6, 1)

for i in range(1, NUM_MEMBERS + 1):
    join_date = fake.date_between(start_date_range, end_date_range)
    plan = random.choices(plans, weights=[0.5, 0.3, 0.2])[0]
    
    # Mayor probabilidad de churn en plan Basic
    status_weight = [0.6, 0.4] if plan == 'Basic' else [0.8, 0.2]
    status = random.choices(status_options, weights=status_weight)[0]
    
    churn_date = None
    if status == 'Churned':
        # La fecha de churn ocurre entre 30 y 180 días después del ingreso
        days_active = random.randint(30, 180)
        churn_date = join_date + timedelta(days=days_active)
        if churn_date > datetime(2026, 8, 1).date():
            churn_date = datetime(2026, 8, 1).date()

    members_data.append({
        'member_id': i,
        'full_name': fake.name(),
        'age': random.randint(18, 65),
        'gender': random.choice(['M', 'F']),
        'join_date': join_date,
        'plan_type': plan,
        'monthly_fee': plan_prices[plan],
        'status': status,
        'churn_date': churn_date
    })

df_members = pd.DataFrame(members_data)

# ---------------------------------------------------------
# 2. GENERAR TABLA: CHECKINS
# ---------------------------------------------------------
checkins_data = []
checkin_id = 1
activity_types = ['Gym Floor', 'Group Class', 'Personal Trainer']

for index, row in df_members.iterrows():
    m_id = row['member_id']
    j_date = row['join_date']
    c_date = row['churn_date'] if row['status'] == 'Churned' else datetime(2026, 8, 20).date()
    
    # Definir frecuencia de visitas por semana según el estado
    # Los activos van entre 2 y 5 veces por semana, los que cancelaron iban entre 0 y 2
    if row['status'] == 'Active':
        weekly_visits = random.randint(2, 5)
    else:
        weekly_visits = random.randint(0, 2)
        
    current_date = j_date
    while current_date <= c_date:
        if random.random() < (weekly_visits / 7.0):
            activity = random.choices(activity_types, weights=[0.6, 0.3, 0.1])[0]
            checkins_data.append({
                'checkin_id': checkin_id,
                'member_id': m_id,
                'checkin_date': current_date,
                'activity_type': activity
            })
            checkin_id += 1
        current_date += timedelta(days=1)

df_checkins = pd.DataFrame(checkins_data)

# ---------------------------------------------------------
# 3. GENERAR TABLA: SUPPORT INTERACTIONS
# ---------------------------------------------------------
interactions_data = []
interaction_id = 1
issue_categories = ['Billing', 'Facility Maintenance', 'App Support', 'Trainer Dispute']

for index, row in df_members.iterrows():
    # Los usuarios con Churned o tarifa alta tienden a registrar más tickets
    num_tickets = random.choices([0, 1, 2, 3], weights=[0.6, 0.25, 0.1, 0.05])[0]
    if row['status'] == 'Churned':
        num_tickets += random.choice([1, 2])
        
    for _ in range(num_tickets):
        ticket_date = fake.date_between(row['join_date'], row['churn_date'] if row['churn_date'] else datetime(2026, 8, 20).date())
        category = random.choice(issue_categories)
        resolution_days = random.randint(1, 10) if row['status'] == 'Churned' else random.randint(1, 3)
        
        interactions_data.append({
            'interaction_id': interaction_id,
            'member_id': row['member_id'],
            'ticket_date': ticket_date,
            'category': category,
            'resolution_days': resolution_days
        })
        interaction_id += 1

df_interactions = pd.DataFrame(interactions_data)

# Exportar a CSV
df_members.to_csv('members.csv', index=False)
df_checkins.to_csv('checkins.csv', index=False)
df_interactions.to_csv('interactions.csv', index=False)

print("¡Datasets generados con éxito! Se crearon: members.csv, checkins.csv e interactions.csv")
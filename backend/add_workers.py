#!/usr/bin/env python3
import os
import json
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8002/api")

# Worker data with daily salaries (need to divide by 8 for hourly)
workers = [
    ("SODOKIN", "SAMUEL", "CHARPENTIER", 10000.00),
    ("NGOMA", "MAGLOIRE", "GUICHETIER", 8000.00),
    ("BOULENDE", "MARIUS", "CHAUFFEUR-MÉCANICIEN", 12000.00),
    ("MBOUMBA MBOUMBA", "MERLIN", "MAGASINIER", 13000.00),
    ("MOUELLE NDOUMBE", "ROBERT", "CHEF D'EQUIPE-FERRAILLEUR", 14000.00),
    ("BAMBARA", "HALIDOU", "MAÇON", 10000.00),
    ("BANCE", "ISSA", "AIDE+", 7000.00),
    ("HAND", "STANY", "CHEF D'EQUIPE", 15000.00),
    ("OGANDAGA TSAMBA", "STÉPHÈNE DERICK", "AIDE+", 7000.00),
    ("KAPPE GOGOMADO", "ERIC MARCELIN", "CHEF D'EQUIPE-COFFREUR", 12000.00),
    ("BOUSSAMBA", "JEAN EMERY", "CHARPENTIER", 11000.00),
    ("KOUMBA MBADINGA", "GAËL", "BETONNIER", 10000.00),
    ("MILAM AUDANG", "BRICE", "FERRAILLEUR", 10000.00),
    ("DITOMBI ABDOULAYE", "JABBI", "CONDUCTEUR", 12000.00),
    ("OBIANG ONDO", "CARL", "CHEF D'EQUIPE", 14000.00),
    ("MEDEDJI", "DJOHOUNGBA SÉBASTIEN", "PEINTRE", 10000.00),
    ("KOUTON", "GBENAKPON PROSPER", "CHAUFFEUR-BOB CAT", 10000.00),
    ("DONGBETO", "GASPARD ELIE", "CHEF D'EQUIPE-MAÇON", 13000.00),
    ("MBA ATAGANA", "CHARLIE", "AIDE-MAÇON", 8000.00),
    ("MBA ATAGANA", "CHARLIE", "FERRAILLER", 10000.00),
    ("BOUSSENGUI", "BRICE", "AIDE", 7000.00),
    ("ZANNE", "YACOUBA", "BETONNIER", 10000.00),
    ("OLLENDE", "JEAN PAUL", "FERRAILLEUR", 10000.00),
    ("BARA", "HAROUNA", "MAÇON", 10000.00),
    ("AMADOU", "COUMARE", "FERRAILLEUR", 10000.00),
    ("NGANTSIE KOUERE", "ROMÉO ALDRICH", "AIDE+", 7000.00),
    ("MAWELE", "ERIC", "AIDE-MAÇON", 7000.00),
    ("BANCE", "AMADOU", "PLOMBIER", 10000.00),
    ("MOULOUNGUI", "DAN HURLICH", "AIDE-MAÇON", 6000.00),
    ("EKOME ESSONO KODJO", "LOÏC", "GUICHETIER", 7000.00),
    ("EKOME ESSONO KODJO", "LOÏC", "MAÇON-COFFREUR", 10000.00),
    ("NDJOUTIT", "LIONEL", "AIDE+", 7000.00),
    ("BAGOUENDI OULOUBA", "YVANNE", "AIDE-MAÇON", 6000.00),
    ("ZOUMBOUBADI", "ODILON WAREN", "AIDE-MAÇON", 7000.00),
    ("KOUMBA MBADINGA", "GAËL", "AIDE-MAÇON", 7000.00),
    ("KOUMBA MBADINGA", "GAËL", "BETONNIER", 10000.00),
    ("DOSSEKPLI", "KOKORUI FRANCK", "SOUDEUR", 10000.00),
    ("MOUBAMBA", "PIERRE BRICE", "CHEF DE CHANTIER-ADJOINT", 14000.00),
    ("WOUGNESSI MBA", "ALAIN RICHARD", "AIDE-MAÇON", 7000.00),
    ("N'GOUAKA", "PAUL", "MAÇON", 10000.00),
    ("DIBOUCKA", "GISCARD", "MAÇON", 10000.00),
    ("DIBOUCKA", "GISCARD", "MAÇON", 10000.00),
    ("TCHEWEK", "MICHEL", "CHARPENTIER", 10000.00),
    ("MANDJOUA", "AYMARD", "AIDE+", 8000.00),
    ("NGAMBA MVOULOU", "ROMEO", "AIDE", 5000.00),
    ("NKOUA ALAGA", "BLAISE DEL", "AIDE", 6000.00),
    ("MAYOMBO BECKA", "LEWISH CHELSEA", "AIDE-MAÇON", 6000.00),
    ("OGOULA RAPENDY", "CHRIS TERENCE", "AIDE-MAÇON", 7000.00),
    ("MOUNGUENGUI", "HABIB RENAUD", "AIDE-MAÇON", 7000.00),
    ("SANAWAGOU PAMBOU", "JEFF RODRIGUEZ", "AIDE-MAÇON", 7000.00),
    ("GUIDJI", "ANATOLE", "MAÇON-COFFREUR", 10000.00),
    ("NZOHOU", "PAUL", "CHEF D'EQUIPE-MAÇON", 12000.00),
    ("GAMBONE", "DAOUDA", "MAÇON-COFFREUR", 10000.00),
    ("GUIDJI", "ANATOLE", "MAÇON", 10000.00),
    ("AGAYA NKOMA", "BLANDINE", "TECHNICIENE DE SURFACE", 6000.00),
    ("AGBOTON", "JESUGO ALEXIS", "COFFREUR-CHARPENTIER", 10000.00),
    ("BARA", "HADARO", "MAÇON", 10000.00),
    ("AMPASSA", "ROCHELI FOLKNER", "AIDE-MAÇON", 6000.00),
    ("KOUMBA NDINGA", "JOËLLE", "ÉLECTRICIENNE", 11000.00),
    ("NYAMA DITONGA", "GASTON", "AIDE-MAÇON", 6000.00),
    ("BETCHIKI BOUYONGO", "JUDICAEL LYLAS", "AIDE-MAÇON", 7000.00),
    ("BITEGHE BI NKOULOU", "JEAN PREVERT", "AIDE", 5000.00),
    ("DEMBELE", "OUSMANE", "FERRAILLEUR", 10000.00),
    ("MBOUMBA", "GÉRALD URLICH", "AIDE-MAÇON", 7000.00),
    ("BASSONO BAPIO", "APPOLINAIRE", "PEINTRE", 10000.00),
    ("SAWADOGO SIBLI", "LAZARE", "PEINTRE", 10000.00),
    ("BOUSSAMBA", "EDDY JOËL", "MAÇON", 10000.00),
    ("SOSSA", "EPIPHANE", "MAÇON", 10000.00),
    ("SODOKIN", "AGBEGNIGAN FLORENT", "MAÇON", 10000.00),
    ("KINGA", "JUSLIN", "MAÇON", 10000.00),
    ("KAMBITSI", "LÉA CARMELLE", "TECHNICIENE DE SURFACE", 6000.00)
]

def get_roles():
    response = requests.get(f"{API_BASE}/roles")
    return {role['name'].upper(): role['id'] for role in response.json()}

def create_role(name):
    response = requests.post(f"{API_BASE}/roles", json={"name": name})
    return response.json()['role_id']

def get_role_id(role_name, existing_roles):
    normalized = role_name.upper()
    
    # Direct matches
    if normalized in existing_roles:
        return existing_roles[normalized]
    
    # Role mappings for similar names
    mappings = {
        'CHAUFFEUR-MÉCANICIEN': 'CHAUFFEUR',
        'CHEF D\'EQUIPE-FERRAILLEUR': 'CHEF D\'ÉQUIPE-FERRAILLEUR', 
        'AIDE+': 'AIDE',
        'CHEF D\'EQUIPE': 'CHEF DE CHANTIER',
        'CHEF D\'EQUIPE-COFFREUR': 'CHEF D\'ÉQUIPE-CHARPENTIER',
        'BETONNIER': 'BETONIER',
        'CONDUCTEUR': 'CHAUFFEUR',
        'PEINTRE': 'CHARPENTIER',
        'CHAUFFEUR-BOB CAT': 'CHAUFFEUR', 
        'CHEF D\'EQUIPE-MAÇON': 'CHEF D\'ÉQUIPE-MAÇON',
        'AIDE-MAÇON': 'AIDE MAÇON',
        'FERRAILLER': 'FERRAILLEUR',
        'PLOMBIER': 'CHARPENTIER',
        'MAÇON-COFFREUR': 'MAÇON',
        'SOUDEUR': 'CHARPENTIER',
        'CHEF DE CHANTIER-ADJOINT': 'CHEF DE CHANTIER',
        'TECHNICIENE DE SURFACE': 'AIDE',
        'COFFREUR-CHARPENTIER': 'CHARPENTIER',
        'ÉLECTRICIENNE': 'CHARPENTIER'
    }
    
    if normalized in mappings:
        mapped = mappings[normalized]
        if mapped.upper() in existing_roles:
            return existing_roles[mapped.upper()]
    
    # Create new role if no mapping found
    return create_role(role_name)

def get_construction_sites():
    response = requests.get(f"{API_BASE}/construction-sites")
    return {site['name']: site['id'] for site in response.json()}

def add_worker(last_name, first_name, role_name, daily_salary):
    existing_roles = get_roles()
    role_id = get_role_id(role_name, existing_roles)
    hourly_rate = daily_salary / 8
    
    sites = get_construction_sites()
    construction_site_id = sites.get("DGDI-Libreville", 1)
    
    data = {
        "name": first_name,
        "last_name": last_name, 
        "role_id": role_id,
        "hourly_rate": hourly_rate,
        "construction_site_id": construction_site_id
    }
    
    response = requests.post(f"{API_BASE}/employees", json=data)
    if response.status_code == 200:
        print(f"Added: {first_name} {last_name} - {role_name} ({hourly_rate}/hr)")
    else:
        print(f"Failed: {first_name} {last_name} - {response.text}")

if __name__ == "__main__":
    for last_name, first_name, role_name, daily_salary in workers:
        add_worker(last_name, first_name, role_name, daily_salary)
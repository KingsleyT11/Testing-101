from __future__ import annotations
from typing import List, Dict, Any
import httpx

GOOGLE_CONTACTS_API = "https://people.googleapis.com/v1/people:searchContacts"


async def fetch_google_contacts(access_token: str, query: str = "", page_size: int = 50) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "query": query,
        "pageSize": page_size,
        "readMask": "names,emailAddresses,phoneNumbers",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(GOOGLE_CONTACTS_API, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for person in data.get("results", []):
            p = person.get("person", {})
            name = (p.get("names", [{}])[0].get("displayName")) if p.get("names") else None
            email = (p.get("emailAddresses", [{}])[0].get("value")) if p.get("emailAddresses") else None
            phone = (p.get("phoneNumbers", [{}])[0].get("value")) if p.get("phoneNumbers") else None
            if name or email or phone:
                results.append({"name": name, "email": email, "phone": phone})
        return results

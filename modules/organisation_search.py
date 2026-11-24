import logging
import requests
from typing import List, Dict, Any, Optional
from integrations.sec_connector import SECConnector
from integrations.tavily_search import TavilySearchClient
from database.connection import SessionLocal
from database.models import Organisation, SearchHistory
from datetime import datetime

logger = logging.getLogger(__name__)

class OrganisationSearchEngine:
    """
    General-purpose organisation discovery across countries and industries.
    Discovers listed, unlisted, private, and non-profit organisations from public web and registry sources.
    """
    def __init__(self):
        self.sec_connector = SECConnector()
        self.tavily_client = TavilySearchClient()

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_clean = query.strip()
        if not query_clean:
            return []

        candidates = []
        seen_names = set()

        # 1. Search SEC EDGAR public registry (covers US and global ADRs/foreign private issuers)
        try:
            sec_matches = self.sec_connector.find_company(query_clean)
            for m in sec_matches:
                name = m.get("name", "").strip()
                if name.lower() not in seen_names:
                    seen_names.add(name.lower())
                    candidates.append({
                        "name": name,
                        "ticker": m.get("ticker"),
                        "cik": m.get("cik"),
                        "stock_exchange": m.get("stock_exchange", "US SEC"),
                        "country": m.get("country", "Global / US"),
                        "industry": "Public Corporation",
                        "description": f"Publicly registered entity under U.S. SEC EDGAR (CIK: {m.get('cik')}, Ticker: {m.get('ticker')}).",
                        "website": f"https://www.sec.gov/edgar/browse/?CIK={m.get('cik')}",
                        "is_listed": True,
                        "source": "U.S. SEC EDGAR"
                    })
        except Exception as e:
            logger.warning(f"SEC search error: {e}")

        # 2. Search Web via Tavily (if configured)
        if self.tavily_client.is_configured():
            try:
                tavily_results = self.tavily_client.search_organisation(query_clean)
                for item in tavily_results:
                    title = item.get("title", "")
                    url = item.get("url", "")
                    content = item.get("content", "")

                    # Extract probable company name
                    clean_title = title.split("-")[0].split("|")[0].split(":")[0].strip()
                    if clean_title.lower() not in seen_names and len(clean_title) > 2:
                        seen_names.add(clean_title.lower())
                        candidates.append({
                            "name": clean_title,
                            "ticker": None,
                            "cik": None,
                            "stock_exchange": "Unspecified / Global Registry",
                            "country": "International / Disclosed Region",
                            "industry": "Commercial / Enterprise",
                            "description": content[:250] + "..." if len(content) > 250 else content,
                            "website": url,
                            "is_listed": False,
                            "source": "Public Web Search"
                        })
            except Exception as e:
                logger.warning(f"Tavily search error: {e}")

        # 3. Direct Wikipedia / Wikidata API fallback for broad corporate discovery
        if len(candidates) < 3:
            try:
                wiki_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": f"{query_clean} company OR corporation OR enterprise",
                    "format": "json",
                    "srlimit": 3
                }
                headers = {"User-Agent": "FinancialButterflyEffect/1.0 (academic.project@university.edu)"}
                resp = requests.get(wiki_url, params=params, headers=headers, timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    search_items = data.get("query", {}).get("search", [])
                    for item in search_items:
                        title = item.get("title", "").strip()
                        snippet = item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
                        if title.lower() not in seen_names:
                            seen_names.add(title.lower())
                            candidates.append({
                                "name": title,
                                "ticker": None,
                                "cik": None,
                                "stock_exchange": "Global / Multi-market",
                                "country": "International",
                                "industry": "Diversified / Enterprise",
                                "description": snippet[:200] + "...",
                                "website": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                                "is_listed": False,
                                "source": "Public Knowledge Base"
                            })
            except Exception as e:
                logger.warning(f"Wikipedia search fallback error: {e}")

        # If still no candidates found, create a direct entry so the user can search any organisation
        if not candidates:
            candidates.append({
                "name": query_clean,
                "ticker": None,
                "cik": None,
                "stock_exchange": "Unspecified",
                "country": "Global",
                "industry": "General Business / Organization",
                "description": f"Publicly searched organization: {query_clean}",
                "website": "",
                "is_listed": False,
                "source": "Direct Search Request"
            })

        return candidates

    def get_or_create_organisation(self, org_data: Dict[str, Any]) -> Organisation:
        """
        Saves or retrieves organisation from local database.
        """
        session = SessionLocal()
        try:
            name = org_data.get("name", "").strip()
            existing = session.query(Organisation).filter(Organisation.name.ilike(name)).first()
            if existing:
                # Update attributes if newly discovered
                if org_data.get("ticker"):
                    existing.ticker = org_data.get("ticker")
                if org_data.get("website") and not existing.website:
                    existing.website = org_data.get("website")
                session.commit()
                session.refresh(existing)
                return existing

            new_org = Organisation(
                name=name,
                country=org_data.get("country", "Global"),
                industry=org_data.get("industry", "Enterprise"),
                description=org_data.get("description", ""),
                website=org_data.get("website", ""),
                stock_exchange=org_data.get("stock_exchange", ""),
                ticker=org_data.get("ticker", ""),
                is_listed=bool(org_data.get("is_listed", False))
            )
            session.add(new_org)
            session.commit()
            session.refresh(new_org)
            return new_org
        finally:
            session.close()

    def record_user_search(self, user_id: int, org_id: int):
        """
        Records or updates search history timestamp for a user and organisation.
        """
        session = SessionLocal()
        try:
            entry = session.query(SearchHistory).filter(
                SearchHistory.user_id == user_id,
                SearchHistory.org_id == org_id
            ).first()

            if entry:
                entry.searched_at = datetime.utcnow()
            else:
                entry = SearchHistory(
                    user_id=user_id,
                    org_id=org_id,
                    searched_at=datetime.utcnow()
                )
                session.add(entry)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error recording user search history: {e}")
        finally:
            session.close()

    def get_user_search_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves recent organisations searched by this user.
        """
        session = SessionLocal()
        try:
            entries = session.query(SearchHistory, Organisation).join(
                Organisation, SearchHistory.org_id == Organisation.id
            ).filter(
                SearchHistory.user_id == user_id
            ).order_by(
                SearchHistory.searched_at.desc()
            ).limit(limit).all()

            history = []
            for sh, org in entries:
                history.append({
                    "history_id": sh.id,
                    "org_id": org.id,
                    "name": org.name,
                    "country": org.country,
                    "industry": org.industry,
                    "description": org.description,
                    "website": org.website,
                    "ticker": org.ticker,
                    "stock_exchange": org.stock_exchange,
                    "is_listed": org.is_listed,
                    "searched_at": sh.searched_at.strftime("%Y-%m-%d %H:%M") if sh.searched_at else "Recently"
                })
            return history
        finally:
            session.close()

    def delete_user_search_entry(self, user_id: int, history_id: int) -> bool:
        """
        Deletes a specific search history entry for the user.
        """
        session = SessionLocal()
        try:
            entry = session.query(SearchHistory).filter(
                SearchHistory.id == history_id,
                SearchHistory.user_id == user_id
            ).first()
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting search history entry {history_id}: {e}")
            return False
        finally:
            session.close()

    def clear_all_user_search_history(self, user_id: int) -> bool:
        """
        Clears all search history records for the user.
        """
        session = SessionLocal()
        try:
            session.query(SearchHistory).filter(
                SearchHistory.user_id == user_id
            ).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing search history for user {user_id}: {e}")
            return False
        finally:
            session.close()

#!/usr/bin/env python3
"""
DevPost Web Scraping Fallback
=============================

Web scraping fallback implementation for DevPost integration.
Used when browser automation fails.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide web scraping fallback for DevPost data extraction
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random

from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from .browser_automation import DevPostHackathonData, DevPostProjectData

logger = logging.getLogger(__name__)


class DevPostWebScraping(ReflectiveModule):
    """Web scraping fallback for DevPost data extraction."""

    def __init__(self, rate_limit_delay: float = 1.0, max_retries: int = 3):
        super().__init__()
        self.module_id = "devpost_web_scraping"
        self.capabilities = [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
        self.dependencies = []
        
        # Scraping configuration
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Set realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': self.dependencies,
            'capabilities': [cap.value for cap in self.capabilities],
            'rate_limit_delay': self.rate_limit_delay,
            'max_retries': self.max_retries
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=100.0,
            issues=[],
            last_check=datetime.now()
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': [cap.value for cap in self.capabilities]
        }

    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make a request with rate limiting and retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making request to {url} (attempt {attempt + 1}/{self.max_retries})")
                
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = self.rate_limit_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Waiting {delay:.2f} seconds before retry")
                    time.sleep(delay)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Add delay between requests
                time.sleep(self.rate_limit_delay)
                
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All retry attempts failed for {url}")
                    raise
                continue
        
        return None

    def extract_hackathon_data(self, hackathon_url: str) -> DevPostHackathonData:
        """Extract hackathon data using web scraping."""
        try:
            logger.info(f"Extracting hackathon data from: {hackathon_url}")
            
            soup = self._make_request(hackathon_url)
            if not soup:
                raise Exception("Failed to fetch hackathon page")
            
            # Extract hackathon title
            title_element = soup.find("h1")
            title = title_element.get_text(strip=True) if title_element else "Unknown Title"
            
            # Extract description
            description_element = soup.find(attrs={"data-testid": "hackathon-description"}) or \
                                soup.find(class_="hackathon-description") or \
                                soup.find(class_="description")
            description = description_element.get_text(strip=True) if description_element else "No description available"
            
            # Extract deadline
            deadline_element = soup.find(attrs={"data-testid": "deadline"}) or \
                             soup.find(class_="deadline") or \
                             soup.find(class_="submission-deadline")
            deadline = deadline_element.get_text(strip=True) if deadline_element else "No deadline found"
            
            # Extract requirements
            requirements = []
            req_elements = soup.find_all(attrs={"data-testid": "requirement"}) or \
                          soup.find_all(class_="requirement") or \
                          soup.find_all(class_="submission-requirement")
            for element in req_elements:
                req_text = element.get_text(strip=True)
                if req_text:
                    requirements.append(req_text)
            
            # Extract prizes
            prizes = []
            prize_elements = soup.find_all(attrs={"data-testid": "prize"}) or \
                           soup.find_all(class_="prize") or \
                           soup.find_all(class_="award")
            for element in prize_elements:
                prize_text = element.get_text(strip=True)
                if prize_text:
                    prizes.append(prize_text)
            
            # Extract sponsors
            sponsors = []
            sponsor_elements = soup.find_all(attrs={"data-testid": "sponsor"}) or \
                             soup.find_all(class_="sponsor") or \
                             soup.find_all(class_="partner")
            for element in sponsor_elements:
                sponsor_text = element.get_text(strip=True)
                if sponsor_text:
                    sponsors.append(sponsor_text)
            
            # Extract submission guidelines
            guidelines_element = soup.find(attrs={"data-testid": "guidelines"}) or \
                               soup.find(class_="guidelines") or \
                               soup.find(class_="submission-guidelines")
            submission_guidelines = guidelines_element.get_text(strip=True) if guidelines_element else "No guidelines found"
            
            return DevPostHackathonData(
                title=title,
                description=description,
                deadline=deadline,
                url=hackathon_url,
                requirements=requirements,
                prizes=prizes,
                sponsors=sponsors,
                submission_guidelines=submission_guidelines,
                extracted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract hackathon data: {e}")
            raise

    def extract_project_data(self, project_url: str) -> DevPostProjectData:
        """Extract project data using web scraping."""
        try:
            logger.info(f"Extracting project data from: {project_url}")
            
            soup = self._make_request(project_url)
            if not soup:
                raise Exception("Failed to fetch project page")
            
            # Extract project title
            title_element = soup.find("h1")
            title = title_element.get_text(strip=True) if title_element else "Unknown Title"
            
            # Extract description
            description_element = soup.find(attrs={"data-testid": "project-description"}) or \
                                soup.find(class_="project-description") or \
                                soup.find(class_="description")
            description = description_element.get_text(strip=True) if description_element else "No description available"
            
            # Extract tags
            tags = []
            tag_elements = soup.find_all(attrs={"data-testid": "tag"}) or \
                         soup.find_all(class_="tag") or \
                         soup.find_all(class_="tech-stack")
            for element in tag_elements:
                tag_text = element.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
            
            # Extract team members
            team_members = []
            member_elements = soup.find_all(attrs={"data-testid": "team-member"}) or \
                            soup.find_all(class_="team-member") or \
                            soup.find_all(class_="member")
            for element in member_elements:
                member_text = element.get_text(strip=True)
                if member_text:
                    team_members.append(member_text)
            
            # Extract GitHub URL
            github_element = soup.find("a", href=lambda x: x and "github.com" in x)
            github_url = github_element.get("href") if github_element else ""
            
            # Extract demo URL
            demo_element = soup.find("a", href=lambda x: x and any(term in x.lower() for term in ["demo", "video", "youtube.com", "vimeo.com"]))
            demo_url = demo_element.get("href") if demo_element else ""
            
            return DevPostProjectData(
                title=title,
                description=description,
                tags=tags,
                team_members=team_members,
                github_url=github_url,
                demo_url=demo_url,
                submission_url=project_url,
                extracted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract project data: {e}")
            raise

    def search_hackathons(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Search for hackathons using web scraping."""
        try:
            logger.info(f"Searching for hackathons with query: {query}")
            
            # Construct search URL
            search_url = "https://devpost.com/hackathons"
            if query:
                search_url += f"?search={query}"
            
            soup = self._make_request(search_url)
            if not soup:
                raise Exception("Failed to fetch hackathon search page")
            
            hackathons = []
            
            # Find hackathon cards
            hackathon_cards = soup.find_all(attrs={"data-testid": "hackathon-card"}) or \
                            soup.find_all(class_="hackathon-card") or \
                            soup.find_all(class_="challenge-card")
            
            for card in hackathon_cards[:limit]:
                try:
                    # Extract hackathon info from card
                    title_element = card.find("h3") or card.find("h2") or card.find("h1")
                    title = title_element.get_text(strip=True) if title_element else "Unknown Title"
                    
                    # Extract URL
                    link_element = card.find("a")
                    url = urljoin("https://devpost.com", link_element.get("href")) if link_element else ""
                    
                    # Extract description
                    desc_element = card.find(class_="description") or card.find("p")
                    description = desc_element.get_text(strip=True) if desc_element else ""
                    
                    # Extract deadline
                    deadline_element = card.find(class_="deadline") or card.find(class_="submission-deadline")
                    deadline = deadline_element.get_text(strip=True) if deadline_element else ""
                    
                    hackathons.append({
                        "title": title,
                        "url": url,
                        "description": description,
                        "deadline": deadline
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse hackathon card: {e}")
                    continue
            
            return hackathons
            
        except Exception as e:
            logger.error(f"Failed to search hackathons: {e}")
            raise

    def close(self):
        """Close the web scraping session."""
        try:
            self.session.close()
            logger.info("Web scraping session closed")
        except Exception as e:
            logger.error(f"Error closing web scraping session: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

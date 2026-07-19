"""Schemas de validation API"""
from typing import Optional, List

class ProspectCreate:
    def __init__(self, first_name: str, last_name: str = "", email: str = "", 
                 phone: str = "", company: str = "", job_title: str = ""):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.company = company
        self.job_title = job_title

class ProspectUpdate:
    def __init__(self, phone: str = None, job_title: str = None, 
                 qualification_score: int = None, conversion_probability: float = None):
        self.phone = phone
        self.job_title = job_title
        self.qualification_score = qualification_score
        self.conversion_probability = conversion_probability

class MessageCreate:
    def __init__(self, prospect_id: int, subject: str, body: str, channel: str = 'email'):
        self.prospect_id = prospect_id
        self.subject = subject
        self.body = body
        self.channel = channel

class SearchRequest:
    def __init__(self, industries: List[str] = None, countries: List[str] = None, 
                 company_sizes: List[str] = None, limit: int = 50):
        self.industries = industries or []
        self.countries = countries or []
        self.company_sizes = company_sizes or []
        self.limit = min(limit, 500)

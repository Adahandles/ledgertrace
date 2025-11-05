"""
County Office Registry for LedgerTrace
Provides direct links to Property Appraisers, Tax Collectors, and Clerks of Court
"""

COUNTY_OFFICES = {
    "Miami-Dade": {
        "property_appraiser": {
            "name": "Miami-Dade Property Appraiser",
            "url": "https://www.miamidade.gov/pa/",
            "search_url": "https://www.miamidade.gov/Apps/PA/PApublicServiceMain/#!/",
            "description": "Property records, assessments, and appeals"
        },
        "tax_collector": {
            "name": "Miami-Dade Tax Collector", 
            "url": "https://www.miamidade.gov/taxcollector/",
            "search_url": "https://www.miamidade.gov/taxcollector/property_search.asp",
            "description": "Tax bills, payments, and delinquency status"
        },
        "clerk_of_court": {
            "name": "Miami-Dade Clerk of Courts",
            "url": "https://www2.miami-dadeclerk.com/",
            "search_url": "https://www2.miami-dadeclerk.com/PremierServices/",
            "description": "Court records, liens, and legal documents"
        }
    },
    "Broward": {
        "property_appraiser": {
            "name": "Broward Property Appraiser",
            "url": "https://bcpa.net/",
            "search_url": "https://web.bcpa.net/bcpaclient/",
            "description": "Property assessments and ownership records"
        },
        "tax_collector": {
            "name": "Broward Tax Collector",
            "url": "https://www.broward.org/TaxCollector/",
            "search_url": "https://www.broward.org/TaxCollector/Pages/PropertyTaxSearch.aspx",
            "description": "Property tax collection and payment services"
        },
        "clerk_of_court": {
            "name": "Broward Clerk of Courts",
            "url": "https://www.browardclerk.org/",
            "search_url": "https://www.browardclerk.org/Web2/CaseSearch/",
            "description": "Court case records and official documents"
        }
    },
    "Palm Beach": {
        "property_appraiser": {
            "name": "Palm Beach Property Appraiser",
            "url": "https://www.pbcgov.org/papa/",
            "search_url": "https://www.pbcgov.org/papa/Asps/PropertySearch/",
            "description": "Property valuations and assessment data"
        },
        "tax_collector": {
            "name": "Palm Beach Tax Collector",
            "url": "https://www.pbctax.com/",
            "search_url": "https://www.pbctax.com/propertysearch",
            "description": "Tax collection and property tax services"
        },
        "clerk_of_court": {
            "name": "Palm Beach Clerk & Comptroller",
            "url": "https://www.mypalmbeachclerk.com/",
            "search_url": "https://www.mypalmbeachclerk.com/web-services/case-search",
            "description": "Official records and court case management"
        }
    },
    "Orange": {
        "property_appraiser": {
            "name": "Orange County Property Appraiser",
            "url": "https://www.ocpafl.org/",
            "search_url": "https://www.ocpafl.org/searches/ParcelSearch.aspx",
            "description": "Property assessments and homestead exemptions"
        },
        "tax_collector": {
            "name": "Orange County Tax Collector",
            "url": "https://www.octaxcol.com/",
            "search_url": "https://www.octaxcol.com/online-services/property-tax-search",
            "description": "Property tax bills and payment processing"
        },
        "clerk_of_court": {
            "name": "Orange County Clerk of Courts",
            "url": "https://myorangeclerk.com/",
            "search_url": "https://myorangeclerk.com/case-search/",
            "description": "Court records and official document filing"
        }
    },
    "Hillsborough": {
        "property_appraiser": {
            "name": "Hillsborough Property Appraiser",
            "url": "https://www.hcpafl.org/",
            "search_url": "https://www.hcpafl.org/Property-Search",
            "description": "Property records and assessment information"
        },
        "tax_collector": {
            "name": "Hillsborough Tax Collector",
            "url": "https://www.hillstax.org/",
            "search_url": "https://www.hillstax.org/property-search/",
            "description": "Tax collection and online payment services"
        },
        "clerk_of_court": {
            "name": "Hillsborough Clerk of Court",
            "url": "https://www.hillsclerk.com/",
            "search_url": "https://pubrec10.hillsclerk.com/",
            "description": "Public records and court case information"
        }
    },
    "Pinellas": {
        "property_appraiser": {
            "name": "Pinellas Property Appraiser",
            "url": "https://www.pcpao.org/",
            "search_url": "https://www.pcpao.org/propertysearch/",
            "description": "Property appraisals and assessment appeals"
        },
        "tax_collector": {
            "name": "Pinellas Tax Collector",
            "url": "https://www.pinellascounty.org/taxcoll/",
            "search_url": "https://www.pinellascounty.org/taxcoll/propsearch.htm",
            "description": "Property tax information and payment options"
        },
        "clerk_of_court": {
            "name": "Pinellas Clerk of Court",
            "url": "https://www.pinellasclerk.org/",
            "search_url": "https://www.pinellasclerk.org/asp/recordssearch/",
            "description": "Court records and marriage licenses"
        }
    },
    "Polk": {
        "property_appraiser": {
            "name": "Polk County Property Appraiser",
            "url": "https://www.polkpa.org/",
            "search_url": "https://www.polkpa.org/propertysearch/",
            "description": "Property assessments and exemption applications"
        },
        "tax_collector": {
            "name": "Polk County Tax Collector",
            "url": "https://www.polktaxes.com/",
            "search_url": "https://www.polktaxes.com/property-taxes/search",
            "description": "Property tax collection and vehicle registration"
        },
        "clerk_of_court": {
            "name": "Polk County Clerk of Courts",
            "url": "https://www.polkcountyclerk.net/",
            "search_url": "https://www.polkcountyclerk.net/court-records/case-search/",
            "description": "Court case records and official filings"
        }
    },
    "Lee": {
        "property_appraiser": {
            "name": "Lee County Property Appraiser",
            "url": "https://www.leepa.org/",
            "search_url": "https://www.leepa.org/Display/DisplaySearch.aspx",
            "description": "Property valuations and ownership information"
        },
        "tax_collector": {
            "name": "Lee County Tax Collector",
            "url": "https://www.leetaxcollector.com/",
            "search_url": "https://www.leetaxcollector.com/property-taxes/property-search/",
            "description": "Tax bill inquiries and payment processing"
        },
        "clerk_of_court": {
            "name": "Lee County Clerk of Courts",
            "url": "https://www.leeclerk.org/",
            "search_url": "https://www.leeclerk.org/records/",
            "description": "Public records and court document access"
        }
    },
    "Collier": {
        "property_appraiser": {
            "name": "Collier County Property Appraiser",
            "url": "https://www.collierappraiser.com/",
            "search_url": "https://www.collierappraiser.com/property-search/",
            "description": "Property appraisals and assessment data"
        },
        "tax_collector": {
            "name": "Collier County Tax Collector",
            "url": "https://www.colliertax.com/",
            "search_url": "https://www.colliertax.com/property-tax-search/",
            "description": "Property tax services and collections"
        },
        "clerk_of_court": {
            "name": "Collier County Clerk of Courts",
            "url": "https://www.colliercountyclerk.com/",
            "search_url": "https://www.colliercountyclerk.com/records-search/",
            "description": "Court records and official document repository"
        }
    },
    "Sumter": {
        "property_appraiser": {
            "name": "Sumter County Property Appraiser",
            "url": "https://www.sumterpa.com/",
            "search_url": "https://www.sumterpa.com/property-search/",
            "description": "Property assessments and homestead applications"
        },
        "tax_collector": {
            "name": "Sumter County Tax Collector",
            "url": "https://www.sumtertaxcollector.com/",
            "search_url": "https://www.sumtertaxcollector.com/property-search/",
            "description": "Property tax collection and delinquency information"
        },
        "clerk_of_court": {
            "name": "Sumter County Clerk of Court",
            "url": "https://www.sumterclerk.com/",
            "search_url": "https://www.sumterclerk.com/records-search/",
            "description": "Court case records and legal document filing"
        }
    },
    "Marion": {
        "property_appraiser": {
            "name": "Marion County Property Appraiser",
            "url": "https://www.pa.marion.fl.us/",
            "search_url": "https://www.pa.marion.fl.us/PropertySearch/",
            "description": "Property appraisals, homestead exemptions, and assessment review"
        },
        "tax_collector": {
            "name": "Marion County Tax Collector",
            "url": "https://mariontax.com/",
            "search_url": "https://mariontax.com/property-search/",
            "description": "Property tax collection, payment processing, and delinquency status"
        },
        "clerk_of_court": {
            "name": "Marion County Clerk of Courts",
            "url": "https://www.marioncountyclerk.org/",
            "search_url": "https://www.marioncountyclerk.org/court-records/",
            "description": "Court records, official documents, and legal case management"
        }
    },
    "Putnam": {
        "property_appraiser": {
            "name": "Putnam County Property Appraiser", 
            "url": "https://www.putnampa.com/",
            "search_url": "https://www.putnampa.com/property-search/",
            "description": "Property assessments, valuations, and exemption applications"
        },
        "tax_collector": {
            "name": "Putnam County Tax Collector",
            "url": "https://www.putnamtaxcollector.com/",
            "search_url": "https://www.putnamtaxcollector.com/tax-search/",
            "description": "Property tax bills, online payments, and tax certificate sales"
        },
        "clerk_of_court": {
            "name": "Putnam County Clerk of Courts",
            "url": "https://www.putnamclerk.com/",
            "search_url": "https://www.putnamclerk.com/records-search/",
            "description": "Court case records, civil filings, and public document access"
        }
    }
}

def get_county_offices(county_name):
    """
    Get county office information for a given county
    
    Args:
        county_name (str): Name of the county
        
    Returns:
        dict: County office information or None if not found
    """
    return COUNTY_OFFICES.get(county_name)

def get_property_search_url(county_name, address=None, parcel_id=None):
    """
    Generate property-specific search URL for county property appraiser
    
    Args:
        county_name (str): Name of the county
        address (str, optional): Property address
        parcel_id (str, optional): Property parcel ID
        
    Returns:
        str: Property search URL
    """
    offices = get_county_offices(county_name)
    if not offices:
        return None
        
    base_url = offices["property_appraiser"]["search_url"]
    
    # Add search parameters if provided
    if address:
        # Simple implementation - most counties support address search
        return f"{base_url}?search={address.replace(' ', '%20')}"
    elif parcel_id:
        return f"{base_url}?parcel={parcel_id}"
    
    return base_url

def get_tax_search_url(county_name, parcel_id=None):
    """
    Generate tax-specific search URL for county tax collector
    
    Args:
        county_name (str): Name of the county  
        parcel_id (str, optional): Property parcel ID
        
    Returns:
        str: Tax search URL
    """
    offices = get_county_offices(county_name)
    if not offices:
        return None
        
    base_url = offices["tax_collector"]["search_url"]
    
    if parcel_id:
        return f"{base_url}?parcel={parcel_id}"
    
    return base_url

def get_court_search_url(county_name, case_number=None):
    """
    Generate court case search URL for county clerk of courts
    
    Args:
        county_name (str): Name of the county
        case_number (str, optional): Court case number
        
    Returns:
        str: Court search URL
    """
    offices = get_county_offices(county_name)
    if not offices:
        return None
        
    base_url = offices["clerk_of_court"]["search_url"]
    
    if case_number:
        return f"{base_url}?case={case_number}"
    
    return base_url

def get_all_supported_counties():
    """
    Get list of all supported counties
    
    Returns:
        list: List of county names
    """
    return list(COUNTY_OFFICES.keys())
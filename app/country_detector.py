"""
Country Detection - Automatically detect country from location string
"""
from typing import Optional, Dict, List


class CountryDetector:
    """Detect Adzuna country code from location string"""

    # Adzuna supported countries
    SUPPORTED_COUNTRIES = {
        'au': 'Australia',
        'at': 'Austria',
        'be': 'Belgium',
        'br': 'Brazil',
        'ca': 'Canada',
        'ch': 'Switzerland',
        'de': 'Germany',
        'es': 'Spain',
        'fr': 'France',
        'gb': 'United Kingdom',
        'in': 'India',
        'it': 'Italy',
        'mx': 'Mexico',
        'nl': 'Netherlands',
        'nz': 'New Zealand',
        'pl': 'Poland',
        'ru': 'Russia',
        'sg': 'Singapore',
        'us': 'United States',
        'za': 'South Africa'
    }

    # City to country mapping (major cities)
    CITY_MAPPING = {
        # Australia
        'sydney': 'au', 'melbourne': 'au', 'brisbane': 'au', 'perth': 'au',
        'adelaide': 'au', 'canberra': 'au', 'hobart': 'au', 'darwin': 'au',

        # Austria
        'vienna': 'at', 'salzburg': 'at', 'graz': 'at', 'innsbruck': 'at',

        # Belgium
        'brussels': 'be', 'antwerp': 'be', 'ghent': 'be', 'bruges': 'be',
        'liege': 'be', 'leuven': 'be',

        # Brazil
        'sao paulo': 'br', 'rio de janeiro': 'br', 'brasilia': 'br',
        'salvador': 'br', 'fortaleza': 'br', 'belo horizonte': 'br',

        # Canada
        'toronto': 'ca', 'vancouver': 'ca', 'montreal': 'ca', 'calgary': 'ca',
        'ottawa': 'ca', 'edmonton': 'ca', 'quebec': 'ca', 'winnipeg': 'ca',

        # Switzerland
        'zurich': 'ch', 'geneva': 'ch', 'basel': 'ch', 'bern': 'ch',
        'lausanne': 'ch', 'lucerne': 'ch',

        # Germany
        'berlin': 'de', 'munich': 'de', 'hamburg': 'de', 'frankfurt': 'de',
        'cologne': 'de', 'stuttgart': 'de', 'dusseldorf': 'de', 'dortmund': 'de',

        # Spain
        'madrid': 'es', 'barcelona': 'es', 'valencia': 'es', 'seville': 'es',
        'zaragoza': 'es', 'malaga': 'es', 'bilbao': 'es',

        # France
        'paris': 'fr', 'marseille': 'fr', 'lyon': 'fr', 'toulouse': 'fr',
        'nice': 'fr', 'nantes': 'fr', 'strasbourg': 'fr', 'bordeaux': 'fr',

        # United Kingdom
        'london': 'gb', 'manchester': 'gb', 'birmingham': 'gb', 'glasgow': 'gb',
        'liverpool': 'gb', 'edinburgh': 'gb', 'leeds': 'gb', 'bristol': 'gb',
        'newcastle': 'gb', 'cardiff': 'gb', 'belfast': 'gb',

        # India
        'mumbai': 'in', 'delhi': 'in', 'bangalore': 'in', 'hyderabad': 'in',
        'chennai': 'in', 'kolkata': 'in', 'pune': 'in', 'ahmedabad': 'in',

        # Italy
        'rome': 'it', 'milan': 'it', 'naples': 'it', 'turin': 'it',
        'florence': 'it', 'venice': 'it', 'bologna': 'it',

        # Mexico
        'mexico city': 'mx', 'guadalajara': 'mx', 'monterrey': 'mx',
        'puebla': 'mx', 'tijuana': 'mx', 'cancun': 'mx',

        # Netherlands
        'amsterdam': 'nl', 'rotterdam': 'nl', 'the hague': 'nl', 'utrecht': 'nl',
        'eindhoven': 'nl', 'groningen': 'nl',

        # New Zealand
        'auckland': 'nz', 'wellington': 'nz', 'christchurch': 'nz',
        'hamilton': 'nz', 'dunedin': 'nz',

        # Poland
        'warsaw': 'pl', 'krakow': 'pl', 'wroclaw': 'pl', 'poznan': 'pl',
        'gdansk': 'pl', 'lodz': 'pl',

        # Russia
        'moscow': 'ru', 'st petersburg': 'ru', 'novosibirsk': 'ru',
        'yekaterinburg': 'ru', 'kazan': 'ru',

        # Singapore
        'singapore': 'sg',

        # United States
        'new york': 'us', 'los angeles': 'us', 'chicago': 'us', 'houston': 'us',
        'phoenix': 'us', 'philadelphia': 'us', 'san antonio': 'us', 'san diego': 'us',
        'dallas': 'us', 'san jose': 'us', 'austin': 'us', 'jacksonville': 'us',
        'san francisco': 'us', 'seattle': 'us', 'denver': 'us', 'boston': 'us',
        'miami': 'us', 'atlanta': 'us', 'washington': 'us', 'las vegas': 'us',

        # South Africa
        'johannesburg': 'za', 'cape town': 'za', 'durban': 'za', 'pretoria': 'za',
    }

    # Country name keywords for detection
    COUNTRY_KEYWORDS = {
        # Sort by length (longest first) to avoid partial matches
        'united kingdom': 'gb',
        'united states': 'us',
        'south africa': 'za',
        'new zealand': 'nz',
        'australia': 'au',
        'austria': 'at',
        'belgium': 'be',
        'brazil': 'br',
        'canada': 'ca',
        'switzerland': 'ch',
        'germany': 'de',
        'spain': 'es',
        'france': 'fr',
        'britain': 'gb',
        'england': 'gb',
        'india': 'in',
        'italy': 'it',
        'mexico': 'mx',
        'netherlands': 'nl',
        'holland': 'nl',
        'poland': 'pl',
        'russia': 'ru',
        'singapore': 'sg',
        'australia': 'au',
        'austrian': 'at',
        'australian': 'au',
        'belgian': 'be',
        'brazilian': 'br',
        'canadian': 'ca',
        'swiss': 'ch',
        'german': 'de',
        'spanish': 'es',
        'french': 'fr',
        'british': 'gb',
        'indian': 'in',
        'italian': 'it',
        'mexican': 'mx',
        'dutch': 'nl',
        'polish': 'pl',
        'russian': 'ru',
        'american': 'us',
        'america': 'us',
    }

    @classmethod
    def detect_country(cls, location: str, default: str = 'us') -> str:
        """
        Detect country code from location string

        Args:
            location: Location string (e.g., "Sydney", "Paris, France", "New York, USA")
            default: Default country code if detection fails

        Returns:
            Two-letter country code (e.g., 'au', 'fr', 'us')
        """
        if not location:
            return default

        location_lower = location.lower().strip()

        # Check for exact city match
        for city, country in cls.CITY_MAPPING.items():
            if city in location_lower:
                return country

        # Check for country keywords
        for keyword, country in cls.COUNTRY_KEYWORDS.items():
            if keyword in location_lower:
                return country

        return default

    @classmethod
    def get_country_name(cls, country_code: str) -> str:
        """Get full country name from code"""
        return cls.SUPPORTED_COUNTRIES.get(country_code, country_code.upper())

    @classmethod
    def get_all_countries(cls) -> Dict[str, str]:
        """Get all supported countries"""
        return cls.SUPPORTED_COUNTRIES.copy()

    @classmethod
    def validate_country_code(cls, country_code: str) -> bool:
        """Check if country code is supported by Adzuna"""
        return country_code.lower() in cls.SUPPORTED_COUNTRIES

    @classmethod
    def is_city_in_country(cls, location: str, country_code: str) -> bool:
        """
        Check if a city belongs to the specified country

        Args:
            location: Location string (e.g., "Sydney")
            country_code: Two-letter country code (e.g., "au")

        Returns:
            True if city is in country, False if unknown or mismatch
        """
        location_lower = location.lower().strip()

        # Check if location is a known city
        detected_country = None
        for city, city_country in cls.CITY_MAPPING.items():
            if city in location_lower:
                detected_country = city_country
                break

        # If no city found, assume it's okay (might be a region/suburb)
        if detected_country is None:
            return True

        # Check if detected country matches the specified country
        return detected_country == country_code.lower()

    @classmethod
    def is_country_name_in_location(cls, location: str) -> Optional[str]:
        """
        Check if location string contains a country name

        Args:
            location: Location string

        Returns:
            Country code if found, None otherwise
        """
        location_lower = location.lower().strip()

        for keyword, country in cls.COUNTRY_KEYWORDS.items():
            if keyword in location_lower:
                return country

        return None


# Convenience functions
def detect_country(location: str, default: str = 'us') -> str:
    """Detect country from location string"""
    return CountryDetector.detect_country(location, default)


def get_country_name(country_code: str) -> str:
    """Get country name from code"""
    return CountryDetector.get_country_name(country_code)

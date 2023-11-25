import requests

SEARCH_API_URL = 'https://api.yelp.com/v3/businesses/search'


class YelpAPI:
    """
    This class implements the Search Yelp Fusion API. to the following APIs:
    Search API - https://docs.developer.yelp.com/reference/v3_business_search
    """
    class YelpAPIError(Exception):
        """This class is used to handle all API errors."""
        pass

    def __init__(self, api_key, timeout_s=None):
        """
            Create a YelpAPI object. An API key from Yelp is required.
            required parameters:
                * api_key - Yelp API key
            optional parameters:
                * timeout_s - Timeout, in seconds, to set for all API calls.
        """
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._yelp_session = requests.Session()
        self._headers = {'Authorization': 'Bearer {}'.format(self._api_key)}

    def close(self):
        """self.close() should be called to close the Session."""
        self._yelp_session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def search_query(self, **kwargs):
        """
        Query the Yelp Search API.
        documentation: https://www.yelp.com/developers/documentation/v3/business_search
        required parameters:
            * one of either:
                * location - text specifying a location to search for
                * latitude and longitude
        """
        if not kwargs.get('location') and (not kwargs.get('latitude') or not kwargs.get('longitude')):
            raise ValueError('A valid location (parameter "location") or latitude/longitude combination '
                             '(parameters "latitude" and "longitude") must be provided.')

        return self._query(SEARCH_API_URL, **kwargs)

    @staticmethod
    def _get_clean_parameters(kwargs):
        """Clean the parameters by filtering out any parameters that have a None value."""
        return dict((k, v) for k, v in kwargs.items() if v is not None)

    def _query(self, url, **kwargs):
        """Query the URL, parse the response as JSON, and check for errors. If all goes well, return the parsed JSON."""
        parameters = YelpAPI._get_clean_parameters(kwargs)
        response = self._yelp_session.get(
            url,
            headers=self._headers,
            params=parameters,
            timeout=self._timeout_s,
        )
        response.raise_for_status()
        # will raise error if error status code received:
        # https://requests.readthedocs.io/en/latest/api/#requests.Response.raise_for_status
        response_json = response.json()  # this will raise a ValueError if the response isn't JSON

        # Yelp can return one of many different API errors, so check for one of them.
        if 'error' in response_json:
            raise YelpAPI.YelpAPIError('{}: {}'.format(response_json['error']['code'],
                                                       response_json['error']['description']))

        return response_json

import urllib.parse
import requests

# Global Variables
test_token = "D2F2394018F3DE779A340B93DBBE60BBAA0CC5F01269BFB7BC44234CC42443C6E4608E03C0C885D17BDB9A310DB65E5026BCBAC7590AAEAFF7FA821DB287D2898404FC6A926F4E510E2AA8436248177B85C8286CDCD6A683C36D994FA449A5F1E915599CC6E65155B33EBF61DB86A3DFC392FCDBD8159EF8241A4CF7526F0DED49E77651A6036A90EB13D2C060E8FD2D8D3DF7A7735391C4B6662F1FED019FC7C1B9F85435935FD8FE017E2C94749042346AE0DBE2FAFA10D124990C67D2A5C0BBD98D1E91E7C41D1D9E9F126A26F63EE4886CEC7A27CEA43ECDAE1C0FC578AAF626F9370A81D791CA8A04F66D91CE5A"

# Exceptions
class MissingTokenException(Exception): pass

def generate_api_call(call_name, params):
        """
        Generates api call url

        Parameters
        ----------

        call_name : string
            Describes the kind of call being made. E.g. 'Validate'xc

        parmas : dict
            Parameters for the api call
        """
        base_url    = "https://ivle.nus.edu.sg/api/Lapi.svc/"

        url = ''.join([base_url, call_name, "?", urllib.parse.urlencode(params)])
        return url



class UserAPI:
    def __init__(self, auth_token):
        self.api_key    = "UY5RaT4yK3lgWflM47CJo"
        self.auth_token = auth_token
        self.user_id = None
        self.name = None
        self.profile = None

    def __repr__(self):
        if not self.name:
            self.name = self.get_name()
        if not self.user_id:
            self.user_id = self.get_user_id()

        return '<User {id}: {name}>'.format(id=self.user_id, name=self.name)

    ###########
    # Profile #
    ###########

    def logged_in(self):
        """
        Returns true if user is logged in. False otherwise.
        """
        if not self.api_key:
            return False

        params = {'APIKey': self.api_key, 'Token': self.auth_token}

        logged_in_url = generate_api_call("Validate", params)
        r = requests.get(logged_in_url)
        return r.json()['Success']

    def get_profile(self):
        """
        Returns a dictionary of profile elements of the user.

        Returns
        -------
        Dictionary with the following:
        'FirstMajor', 'SecondMajor', 'UserID', 'MatriculationYear', 'Email', 'Faculty', 'Name', 'Gender'
        """
        if not self.api_key:
            raise MissingTokenException("User was not instantiated with a token.")

        params = {'APIKey': self.api_key, 'AuthToken': self.auth_token}

        get_profile_url = generate_api_call("Profile_View", params)
        r = requests.get(get_profile_url)
        return r.json()['Results'][0]

    def get_name(self):
        """
        Returns name of user.
        """
        if self.name:
            return self.name
        else:
            self.profile = self.get_profile()
            return self.profile['Name']

    def get_user_id(self):
        """
        Returns user id of user.
        """
        if self.user_id:
            return self.user_id
        else:
            self.profile = self.get_profile()
            return self.profile['UserID']

    ###########
    # Modules #
    ###########

    def get_modules(self):
        """
        Returns information about all modules taken.
        """
        if not self.api_key:
            raise MissingTokenException("User was not instantiated with a token.")

        params = {'APIKey': self.api_key, 'AuthToken': self.auth_token}

        get_modules_url = generate_api_call("Modules", params)
        r = requests.get(get_modules_url)
        return r.json()['Results']

    def get_modules_code_names(self):
        """
        Returns a list of the names of all modules the student has taken.
        """
        return [(mod['CourseName'], mod['CourseCode']) for mod in self.get_modules()]

    def get_modules_taken(self):
        """
        Returns a list of all modules the student has taken.
        """
        if not self.api_key:
            raise MissingTokenException("User was not instantiated with a token.")

        params = {'APIKey': self.api_key, 'AuthToken': self.auth_token, 'StudentID': self.get_user_id()}

        get_modules_url = generate_api_call("Modules_Taken", params)
        r = requests.get(get_modules_url)
        return r.json()['Results']

    def get_modules_taken_code_names(self):
        """
        Returns a list of the names of all modules the student has taken.
        """
        modules_taken = self.get_modules_taken()
        return [mod['ModuleCode'] for mod in modules_taken]

    if __name__ == '__main__':
        pass
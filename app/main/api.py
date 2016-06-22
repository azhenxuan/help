import urllib.parse
import requests

# Global Variables
test_token = "C82A4F677B275897AA6F3AD6C0E90CEC320DBD262BE5A8A392980162CA847D0FFE007589DC8A6C4A291988FD443912310D8EBE38F362263725E4BA9245DF2AF421E9C5D93A6B742E646314B4BC30115C61D6A3582726AA29D79A9D3E8E08FFC93D2A522A94399D7CE3271FB6487C68440CA7B6001F743826151676CE72312EFB719CEDBB73E4C0BEDCC1508142820EC3C4C5B93DF307689252065999F93C20F8C2B35289D7997F1301E865039925AE2B3FA7C9B2A7A7F81D8393AAD3CF6C8E1F32BFDA675B874390323ED2B1759D5A26E58E3315C6A08F9926830C8A80D140BF1E5607FFBE915375640BFFA95F996E22"

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

        params = {'APIKey': self.api_key, 'AuthToken': self.auth_token}

        get_profile_url = generate_api_call("Profile_View", params)
        r = requests.get(get_profile_url)
        if r.json()['Results']:
            self.profile = r.json()['Results'][0]
            return True
        return r.json()

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
        if not self.profile:
            r = requests.get(get_profile_url)
            self.profile = r.json()['Results'][0]
        return self.profile

    def get_name(self):
        """
        Returns name of user.
        """
        if not self.name:
            self.profile = self.get_profile()
            self.name = self.profile['Name']
        return self.name

    def get_user_id(self):
        """
        Returns user id of user.
        """
        if not self.user_id:
            self.profile = self.get_profile()
            return self.profile['UserID']
        return self.user_id

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
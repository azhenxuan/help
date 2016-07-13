import urllib.parse
import requests

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
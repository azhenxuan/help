API_KEY = "UY5RaT4yK3lgWflM47CJo"

import packages.pyivle as pyivle
import getpass

def login(user_id, password):
    p = pyivle.Pyivle(API_KEY)
    p.user_id = user_id
    p.login(user_id, password)
    return p

class User:
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.p = login(user_id, password)

    def get_name(self):
        me = self.p.profile_view()
        return me.Results[0].Name

    def get_curr_mods(self):
        """Returns a list of details about the modules the student is currently taking."""
        return self.p.modules().Results

    def get_curr_mod_names(self):
        """Returns a list of modules the student is currently taking."""
        modules = self.get_curr_mods()
        return [mod.CourseName for mod in modules]

    def get_all_mods(self):
        """Returns a list of details about all modules the student has taken in NUS."""
        return self.p.modules_taken(self.user_id).Results

    def get_all_mod_names(self):
        """Returns a list of modules the student is currently taking."""
        modules = self.get_all_mods()
        return [mod.ModuleTitle for mod in modules]

if __name__ == "__main__":
    # Authenticate
    p = pyivle.Pyivle(API_KEY)
    USER_ID = raw_input("User ID? ")
    PASSWORD = getpass.getpass()
    p.login(USER_ID, PASSWORD)
    
    # Get your name and user ID
    me = p.profile_view()
    print(me.Results[0].Name, me.Results[0].UserID)

    def get_lecturers(mod_id):
        lecturers = p.module_lecturers(mod_id) 
        for lecturer in lecturers.Results:
            print(lecturer.User.Name)
    
            
    # List enrolled modules by course code
    modules = p.modules()
    for mod in modules.Results:
        CourseCode = mod.CourseCode.split("/")[0]
        CourseName = mod.CourseName
        CourseID   = mod.ID
        print(CourseCode + " : " + CourseName)
        
        if CourseID != "00000000-0000-0000-0000-000000000000":
            get_lecturers(CourseID)
        else:
            print("Module not active")

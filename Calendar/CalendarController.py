import Calendar.CalendarFunctions
import Calendar.AccessToken

def startCalendar():
    acc = print(Calendar.AccessToken.generate_access_token())
    #Calendar.CalendarFunctions.create_event()
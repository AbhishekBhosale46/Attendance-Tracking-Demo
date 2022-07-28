import collections
import numpy as np
import pyrebase
import streamlit as st
import pandas as pd
import streamlit_authenticator as sauth
from datetime import date
import database as db
import os
from dotenv import load_dotenv

load_dotenv(".env")
configStr = os.getenv("CONFIG_STR")
firebaseConfiglist = configStr.split(' ')


def todict(lst):
    it = iter(lst)
    dct = dict(zip(it, it))
    return dct


firebaseConfig = todict(firebaseConfiglist)


# ---INITIALIZE APP WITH GIVEN FB CONFIG---
firebase = pyrebase.initialize_app(firebaseConfig)

# ---CREATE A DATABASE---
fbdb = firebase.database()

# ---USERNAME & PASS FOR PROFESSORS USER AUTHENTICATION---
users = db.fetch_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]
authenticator = sauth.Authenticate(names, usernames, hashed_passwords,
                                   "attendancetracking", "abcdxyz", cookie_expiry_days=30)

# ---Removes the top padding---
st.markdown('''<style>
                div.block-container{padding-top:0rem;}
                .css-1jkb0cp {
                background: none;
                backdrop-filter: none;
                }
                </style>''', unsafe_allow_html=True)

# ---Display the pict logo---
st.markdown('''
            <p style="text-align:center; margin-bottom:-25px; margin-top:-10px;"> 
            <img src="https://www.freepnglogos.com/uploads/hogwarts-logo-png/welcome-hogwarts-school-witchcraft-wizardry-16.png" class="img-fluid hover-shadow" height="144dp" width="144dp" alt="Cinque Terre">
            </p>
            ''', unsafe_allow_html=True)

# ---Centers the title---
st.title("📒 Attendance Tracking")
st.markdown('''
            <style>
            .css-10trblm {
            text-align: center;
            }
            h1 {
            margin-bottom: -60px;
            }
            </style>
            ''', unsafe_allow_html=True)

# ---Css for the login form---
st.markdown('''
            <style>
            .css-12ttj6m {
            margin-top: -45px;
            margin-bottom: 4px;
            border: 1.5px solid #16679ab8;
            border-radius: 1rem;
            }
            </style>
            ''', unsafe_allow_html=True)

# ---Button Css---
st.markdown('''
            <style>
            .css-1cpxqw2 {
            font-weight: 510;
            padding: 0.25rem 1.25rem;
            border-radius: 0.75rem;
            margin: 5px;
            background-color: #4472cae8;
            border: 1px solid #31333f00;
            border-width: 1.5px;
            color: white;
            font-size: 14.2px;
            text-transform: uppercase;
            }   
            </style>
            ''', unsafe_allow_html=True)
st.markdown('''
            <style>
            body {
            font-weight: 500;
            text-align: center;
            }  
            </style>
            ''', unsafe_allow_html=True)

# ---Hover Button---
st.markdown('''
            <style>
            .css-1cpxqw2:focus:not(:active) {
            border-color: #caf0f8;
            color: #caf0f8;
            }
            .css-1cpxqw2:hover {
            border-color: #caf0f8;
            color: #caf0f8;
            }
            .css-1cpxqw2:focus {
            box-shadow: #caf0f83b 0px 0px 0px 0.2rem;
            outline: none;
            }
            .css-1cpxqw2:active {
            background-color: #385ba0ed;	
            }
            </style>
            ''', unsafe_allow_html=True)

# ---Label CSS---
st.markdown('''
            <style>
            .css-qrbaxs {
            font-weight: 505;
            }
            </style>
            ''', unsafe_allow_html=True)

# ---Centers the professor name---
st.markdown('''
            <style>
            h2 {
            font-family: "Source Sans Pro", sans-serif;
            font-weight: 600;
            color: rgb(49, 51, 63);
            letter-spacing: -0.005em;
            padding: 0.5rem 0px 0.5rem;
            text-align: center;
            line-height: 1.4;
            margin-bottom: 10px;
            margin-top: -60px;
            font-size: calc(1.3rem + .6vw);
            }
            </style>
            ''', unsafe_allow_html=True)

# ---DISPLAY THE LOGIN FORM---
name, authentication_status, username = authenticator.login('Login', 'main')

# ---EXECUTE IF LOGIN SUCCESSFUL
if authentication_status:

    # ---DISPLAY PROFESSORS NAME---
    st.header('Welcome *Prof.* *%s*' % name)

    # ---RETURNS THE OBJECT OF LOGGED IN PROFESSOR---
    professors = fbdb.child("Professors").child(name).get()

    c1, c2 = st.columns(2)

    with c1:
        subName = st.selectbox("SUBJECT : ", [professors.val()['Subject']])
    with c2:
        div = st.selectbox("CLASS : ", professors.val()['Class'].split(","))

    # ---TAKE DATE INPUT---
    today = date.today()
    d = st.date_input('SELECT DATE : ', today)

    # ---TAKE ABSENT ROLLS INPUT---
    absentRoll = st.text_input("ENTER ABSENT ROLL NO : ")
    absentRollList = absentRoll.strip().split(" ")

    # ---Info Box---
    placeholder = st.empty()
    placeholder.info("Verify the class and rollnos before proceeding.")

    # ---EMPTY LIST AND OBJECT TO STORE DATA---
    studDetails = None
    dflist = []

    # ---LOGIC TO FETCH GIVEN ROLLNO DATA---
    students = fbdb.child("Students2").child(div).get()

    # Iterates over each node and checks if rollno matches or not
    for s in students.each():
        for i in range(len(absentRollList)):
            # Checks if given rollno and division matches
            if str(s.val()['RollNo']).endswith(absentRollList[i]):
                # If rollno matches then fetch the details and store it in an object
                studDetails = fbdb.child("Students2").child(div).child(s.key()).get()
                # ---CONVERT DICT TO DATAFRAME---
                # The object returned is converted to dictionary and then to list
                toAppend = list(studDetails.val().values())
                # The list is appended to main list
                dflist.append(toAppend)

    # Nested list converted to dataframe
    studentsdf = pd.DataFrame(dflist, columns=['Class', 'Contact', 'Name', 'RollNo', 'Subjects'])
    del studentsdf['Subjects']
    del studentsdf['Contact']
    del studentsdf['Class']

    # ---DISPLAY THE ABSENT STUDENT DETAILS---
    if st.button("GET DETAILS"):
        if absentRoll.strip() == str(0):
            placeholder.info("No absent students ! ")
        else:
            box = placeholder.expander("SEE ABSENT STUDENTS : ")
            with box:
                st.dataframe(studentsdf)

    # ---MARKS THE ATTENDANCE OF THE STUDENTS---
    if st.button("MARK ATTENDANCE"):
        placeholder.success("Marking attendance ! You can exit the webapp")
        for s in students.each():
            for i in range(len(absentRollList)):
                # If student is absent mark Absent else mark absent
                if absentRoll.strip() == str(0):
                    fbdb.child("Students2").child(div).child(s.key()).child("Subjects").child(subName).child(d).set("P")
                else:
                    if not str(s.val()['RollNo']).endswith(absentRollList[i]):
                        if str(fbdb.child("Students2").child(div).child(s.key()).child("Subjects").child(subName).child(
                                d).get().val()) == "A":
                            continue
                        else:
                            fbdb.child("Students2").child(div).child(s.key()).child("Subjects").child(subName).child(
                                d).set("P")
                    else:
                        fbdb.child("Students2").child(div).child(s.key()).child("Subjects").child(subName).child(d).set(
                            "A")
        placeholder.success("Attendance marked successfully ! ")

    # ---SHOWS THE ATTENDANCE OF WHOLE CLASS---
    if st.button("SHOW ATTENDANCE"):
        placeholder.info("Please wait fetching attendance ! ")
        dfdict = collections.defaultdict(list)
        for s in students.each():
            studnames = fbdb.child("Students2").child(div).child(s.key()).child('Name').get().val()
            attendanceDate = list(
                fbdb.child("Students2").child(div).child(s.key()).child('Subjects').child(subName).get().val().keys())
            attendancestatus = list(
                fbdb.child("Students2").child(div).child(s.key()).child('Subjects').child(subName).get().val().values())
            attended = 0
            dfdict['Name'].append(studnames)
            for i in range(len(attendanceDate)):
                if attendancestatus[i] == 'P':
                    attended += 1
                dfdict[attendanceDate[i]].append(attendancestatus[i])
            dfdict['Conducted'].append(len(attendanceDate))
            dfdict['Attended'].append(attended)
            dfdict['Percentage'].append(round(100 - ((len(attendanceDate) - attended) / len(attendanceDate) * 100), 2))
        attendancedataframe = (pd.DataFrame(dfdict)).astype(str)
        attendancedataframe.index = np.arange(1, len(attendancedataframe) + 1)
        placeholder.info("Attendance fetched successfully !")
        with st.expander("ATTENDANCE TILL DATE : "):
            st.dataframe(attendancedataframe)

    # ---BUTTON TO LOGOUT---
    authenticator.logout('LOGOUT', 'main')

# ---IF LOGIN FAILS
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

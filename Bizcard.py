# IMPORTING THE REQUIRED LIBRARIES
import re
import cv2
import pickle
import base64
import numpy as np
import pandas as pd
from PIL import Image
import easyocr as ocr
import streamlit as st
from pathlib import Path
import psycopg2 as pg2
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
from annotated_text import annotated_text
from streamlit_option_menu import option_menu

# INSTANTIATION
reader = ocr.Reader(['en'])

# CREATING TABLE

conn = pg2.connect(database ='Bizcard',user ='postgres',password = 'postgres',port=5432)
cur = conn.cursor()
create = '''CREATE TABLE IF NOT EXISTS card_details(
                          user_name TEXT primary key,
                          designation TEXT,
                          company TEXT,
                          website TEXT,
                          phone_number VARCHAR(50),
                          e_mail TEXT,
                          address TEXT,
                          city TEXT,
                          state TEXT,
                          pincode VARCHAR(50),
                          image BYTEA)'''
cur.execute(create)
conn.commit()

# Setting page congiuration

st.set_page_config(page_title = 'BizCardX',layout='wide') 

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg(r'C:\Users\Shaik_AbdulRazack\Bizcard\login2.png')

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #9899AA;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color:white;'>BizCardX: Extracting Business Card Data with OCR</h2>", unsafe_allow_html=True)


# USER LOGIN CREDENTIALS

file_path = Path(__file__).parent/'hash_pw.pkl'
with file_path.open('rb') as file:
        hashed_passwords = pickle.load(file)

credentials = {
        "usernames":{
                        'nilomubeen':{"name":'Nilofer',"password":hashed_passwords[0]},
                        'shaik':{"name":'Abdur Razack',"password":hashed_passwords[1]}
                     }
                }

# USER VALIDATION

a1,a2 = st.columns(2)

with a2:
                authenticator = stauth.Authenticate(credentials,'Bizcard_dashboard','abcdef',cookie_expiry_days = 30)
                name,authentication_status,username = authenticator.login("Login","main")

                if authentication_status == False:
                        st.error("Username/Password is Incorrect!")

                if authentication_status == None:
                        st.warning("Please Enter your UserName and Password")

if authentication_status:
        

        def get_base64_of_bin_file(bin_file):
                        with open(bin_file, 'rb') as f:
                                data = f.read()
                        return base64.b64encode(data).decode()

        def set_png_as_page_bg(png_file):
                                bin_str = get_base64_of_bin_file(png_file)
                                page_bg_img = '''
                                <style>
                                .stApp {
                                background-image: url("data:image/png;base64,%s");
                                background-size: cover;
                                }
                                </style>
                                ''' % bin_str
                                
                                st.markdown(page_bg_img, unsafe_allow_html=True)
                                return

        set_png_as_page_bg(r'C:\Users\Shaik_AbdulRazack\Bizcard\back.png')

        with st.sidebar:
                selected = option_menu("Main Menu", ['Home','Upload and Extract','Update','Delete'], 
                                    icons=['house','cloud-arrow-up-fill','repeat','trash'], menu_icon="menu-up", default_index=0,orientation ="vertical")
                authenticator.logout("logout","sidebar")
        
        if selected == 'Home':
                    st.subheader(f"Welcome {name}!")
                    annotated_text(("Thank You",""),"for choosing our",("App.","","#81F21E"),
                                   "Please select an",("OPTION"," ","#66FFFF"),"from the Main Menu" )

#  IMAGE UPLOAD AND DISPLAY 
                        
        if selected == 'Upload and Extract':
                st.subheader('Business Card Image Upload',divider = 'rainbow')
                uploaded_file = st.file_uploader("Choose a Business card Image file...",type=['jpg','png','jpeg'])
                               
                if uploaded_file is not None:
                            img = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
                            image_file = Image.open(uploaded_file) 
                            col1, col2 = st.columns(2) 
                            with col1:
                                st.markdown("<h5 style='text-align: center; color: #063F27;'>Image Uploaded </h5>", unsafe_allow_html=True)
                                st.image(image_file,width = 420)
                            
                            with col2:
                                st.markdown("<h5 style='text-align: center; color: #063F27;'>Results Drawn </h5>", unsafe_allow_html=True)                           

                # BOUNDARY BOX DISPLAY

                                
                                                                                          
                                spacer = 100
                                res = reader.readtext(np.array(image_file))
                                for detection in res:
                                                num = res[0][0][0][0]
                                                top_left = tuple(detection[0][0])
                                                bottom_right = tuple(detection[0][2])
                                                text = detection[1]
                                                font = cv2.FONT_HERSHEY_TRIPLEX
                                                img = cv2.rectangle(img,(int(top_left[0]), int(top_left[1])), (int(bottom_right[0]), int(bottom_right[1])),(3,255,255),1)
                                                img = cv2.putText(img,text,(abs(num-500),spacer),font, 1,(128,128,128),1,cv2.LINE_AA)
                                                spacer+=30
                                plt.figure(figsize=(10,10))
                                plt.imshow(img)
                                st.image(img,width = 420)
                               
                           
                 # READING IMAGES
                            
                            path = Path(__file__).parent/uploaded_file.name
                            with open(path, 'rb') as file:
                                        image = file.read()
                            
                            result = reader.readtext(image,detail=0)
                            result1 = reader.readtext(image,detail=0, paragraph = True)
                            
                            # IMAGE TO BINARY

                            def convertToBinaryData():
                                        with open(path, 'rb') as file:
                                                blobData = file.read()
                                        return blobData
                            data = convertToBinaryData()
                            
                # CARD DETAILS EXTRACTION

                            def card_details_extraction ():

                                    details = {"Name": [],
                                                "designation": [],
                                                "company": [],
                                                "website": [],
                                                "phone_number": [],
                                                "e_mail": [],
                                                "Address": [],
                                                "city": [],
                                                "state": [],
                                                "pin_code": [],
                                                "image":data}
                                    # USER Name , Designation

                                    details['Name'].append(result[0])
                                    details['designation'].append(result[1])

                                    for i in result:

                                            # WEBSITE

                                            if "www " in i.lower() or "www." in i.lower():
                                                        details['website'].append(i.lower())
                                            elif "WWW" in i:
                                                        web = result[4] + "." + result[5]
                                                        details['website'].append(web.lower())

                                            # PHONE

                                            if '-' in i:
                                                details['phone_number'].append(i)

                                            #E-MAIL

                                            if "@" in i:
                                                details['e_mail'].append(i)

                                            #PINCODE

                                            if 'TamilNadu' in i:
                                                    pinn = i.split()
                                                    if pinn[1].isdigit():
                                                        pin = pinn[1]
                                                        details['pin_code'].append(pin)
                                            elif i.isdigit() and len(i) >= 6:
                                                    pin = i
                                                    details['pin_code'].append(pin)

                                    for i,value in enumerate(result1):

                                            addr_pattern = r'([0-9][0-9][0-9] [a-zA-Z]+ St)'
                                            st_pattern = r"\bT\w*u\b"

                                            #CITY

                                            if 'St' in value:
                                                    a1 = list(value.partition('TamilNadu'))
                                                    a2 = a1[0].split(',')
                                                    a3 = a2[1]
                                                    if a3 != '':
                                                        city = a3.replace(';','')
                                                        details['city'].append(city)
                                                    else:
                                                        details['city'].append(a2[2])
                                            #STATE

                                            if re.search(st_pattern,value):
                                                    x = re.findall(st_pattern, value)
                                                    state = x[0]
                                                    details['state'].append(state)

                                            #ADDRESS

                                            if re.search(addr_pattern, value):
                                                head, street, tail = re.split(addr_pattern, value, 1)
                                                details['Address'].append(street)

                                            #COMPANY PHONE

                                            if '.com' in value and i== len(result1)-1:
                                                details['company'].append(result1[i-1])
                                            elif i == len(result1) - 1:
                                                    details['company'].append(value)

                                    return details
                            card = card_details_extraction()  
                                                    
                # INSERTION INTO SQL DATABASE

                            st.subheader("Database Insertion",divider = 'violet')
                            bn = st.button('Insert and Display Data')
                            if bn:           
                                insert = '''INSERT INTO card_details(user_name,designation,company,website,phone_number,e_mail,address,city,state,pincode,image)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

                                data_tuple = (card["Name"][0],
                                        card["designation"][0],
                                        card["company"][0],
                                        card["website"][0],
                                        card["phone_number"][0],
                                        card["e_mail"][0],
                                        card["Address"][0],
                                        card["city"][0],
                                        card["state"][0],
                                        card["pin_code"][0],
                                        card['image'])
                                try:
                                        cur.execute(insert,data_tuple)
                                        conn.commit()  
                                except:
                                        conn.rollback()
                
                            
                # DISPLAY            
                            
                                def data_display():
                                        cur.execute("SELECT * FROM card_details")
                                        tab = cur.fetchall()
                                        display = pd.DataFrame(tab,columns = ['user_name','designation','company','website','phone_number','e_mail','address','city','state','pincode','image'])
                                        st.dataframe(display,hide_index=True)
                                        return display
                                data_display()

# UPDATE CARD DETAILS

        if selected == 'Update': 
                st.subheader("Edit User Details")
                cur.execute("SELECT * FROM card_details")
                tab = cur.fetchall()
                df1 = pd.DataFrame(tab,columns = ['user_name','designation','company','website','phone_number','e_mail','address','city','state','pincode','image'])
                a1,a2 = st.columns(2)
                with a1:
                        cur.execute('select user_name from card_details')
                        users = [i[0] for i in cur]

                        user = st.selectbox("Select the Username",users,index=None,placeholder='Select option')  
                if user:
                        st.subheader(':violet[Edit the field/fields for Updating]')

                        c1,c2 = st.columns(2)
                        with c1:
                        
                                upd_name = st.text_input('Name' , df1.loc[df1['user_name']==user,'user_name'].squeeze())
                                upd_desg = st.text_input('Designation' , df1.loc[df1['user_name']==user,'designation'].squeeze())  
                                upd_comp = st.text_input('Company' , df1.loc[df1['user_name']==user,'company'].squeeze())
                                upd_web = st.text_input('Website' , df1.loc[df1['user_name']==user,'website'].squeeze()) 
                                upd_ph = st.text_input('Phone' , df1.loc[df1['user_name']==user,'phone_number'].squeeze())
                        
                        
                        with c2:
                                upd_mail = st.text_input('Mail' , df1.loc[df1['user_name']==user,'e_mail'].squeeze())  
                                upd_add = st.text_input('Address' , df1.loc[df1['user_name']==user,'address'].squeeze())
                                upd_city = st.text_input('City', df1.loc[df1['user_name']==user,'city'].squeeze()) 
                                upd_st = st.text_input('State' , df1.loc[df1['user_name']==user,'state'].squeeze())
                                upd_pin = st.text_input('Pincode', df1.loc[df1['user_name']==user,'pincode'].squeeze())  
                        
                                    
                        button1 = st.button('Update')
                        
                        if button1:
                                query = "UPDATE card_details SET user_name = %s, designation = %s,company = %s,website=%s,"\
                                                "phone_number = %s, e_mail = %s , address = %s, city = %s,state = %s,pincode =%s"\
                                                "WHERE user_name = %s RETURNING *"
                                values = (upd_name,upd_desg,upd_comp,upd_web,upd_ph,upd_mail,upd_add,upd_city,upd_st,upd_pin,user)
                                cur.execute(query,values)
                                conn.commit()
                                updated = cur.fetchall()
                                st.subheader('Updated User Details',divider='rainbow')
                                st.dataframe(pd.DataFrame(updated,columns=['user_name','designation','company','website','phone_number','e_mail','address','city','state','pincode','image']),hide_index=True)

# DELETING CARD DETAILS      
        
        if selected == 'Delete':  
                st.subheader("Delete card")
                cur.execute('select user_name from card_details')
                user= [i[0] for i in cur]
                user_name = st.selectbox("Select the Username",user,index=None,placeholder='Select option') 
                
                cur.execute("SELECT * FROM card_details")
                tab = cur.fetchall()
                df1 = pd.DataFrame(tab,columns = ['user_name','designation','company','website','phone_number','e_mail','address','city','state','pincode','image'])
                if user_name:
                        st.write(f'Card Details of {user_name}')
                        st.dataframe(df1[df1['user_name']== user_name],hide_index=True)
                        st.write("Are you sure you want to delete user details?")
                        agree = st.checkbox('I agree')
                        d = st.button("Delete")
                if user_name and agree and d:
                        delete_query = "delete from card_details where user_name = %s returning *"
                        cur.execute(delete_query,[user_name])
                        conn.commit()
                        st.warning(f'Card details of {user_name} DELETED!!')
                        st.subheader('Updated database after Deletion')
                        cur.execute('select * from card_details')
                        upd=cur.fetchall()
                        st.dataframe(pd.DataFrame(upd,columns= ['user_name','designation','company','website','phone_number','e_mail','address','city','state','pincode','image']),hide_index=True)
                        conn.close()
from flask import Flask, render_template, request, flash, redirect, url_for,send_file
import pandas as pd
import os
import re
# from teams import create_chatid, send_anouncement, get_msg
 
# func to send message
def announce(email: str, msg: str):
    c_id = create_chatid(email)
    send_anouncement(c_id, msg)

app = Flask(__name__)
app.secret_key = 'secret'  
 
 
@app.route('/')
def home():
    files = os.listdir('uploads')
    return render_template("upload.html", files=files)
 
 
@app.route('/upload', methods=['POST'])
def upload_file():
 
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
 
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = file.filename
        if filename.endswith('.xlsx') or filename.endswith('.csv'):
            file.save(os.path.join('uploads', filename))
            flash('File uploaded successfully')
            return redirect(url_for('home'))
        else:
            flash('Unsupported file format. Please upload a .xlsx or .csv file.')
            return redirect(request.url)
 
@app.route('/display_file/<filename>')
def display_file(filename):
    file_path = os.path.join('uploads', filename)
    if os.path.exists(file_path):
        if filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            flash('Unsupported file format.')
            return redirect(url_for('home'))
        html_table = df.to_html()
        return render_template('viewtable.html', html_table=html_table, filename=filename)
    else:
        flash('File not found.')
        return redirect(url_for('home'))
 
 
@app.route('/extract', methods=['GET','POST'])
def extract():
    if request.method == 'POST':
        if 'delete' in request.form:
            os.remove(os.path.join('uploads', request.form['delete']))
            flash('File deleted')
        if 'extract' in request.form:
            file = request.form.get("extract")
            message = request.form['message']
            filepath = os.path.join("uploads", file)

            print(filepath, "\n", message)
 
            if ".csv" in file:
                emaildf = pd.read_csv(filepath, header=None)
 
            if ".xlsx" in file:
                emaildf = pd.read_excel(filepath, header=None)
 
            def get_emails(df):
                emails = []
                pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
 
                for value in df.values.flatten():
                    email_matches = re.findall(pattern, str(value))
                    emails.extend(email_matches)
 
                return emails
 
 
            emails = get_emails(emaildf)
 


            for i in emails:
                announce(i, message)

# --------------------  Get response  ----------------

        if "get_res" in request.form:
            file = request.form.get("get_res")
            filepath = os.path.join("uploads", file)
 
            if ".csv" in file:
                emaildf = pd.read_csv(filepath, header=None)
 
            if ".xlsx" in file:
                emaildf = pd.read_excel(filepath, header=None)
 
            def get_emails(df):
                emails = []
                pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
 
                for value in df.values.flatten():
                    email_matches = re.findall(pattern, str(value))
                    emails.extend(email_matches)
 
                return emails
            
            emails = get_emails(emaildf)
            

            ## messages dict

            res_messages = {}
            for i in emails:
                res_messages[i] = get_msg(i, '#idea')

            # Convert Series to DataFrame
            df = pd.DataFrame.from_dict(res_messages, orient='index')

            df.to_excel('response.xlsx')
            return send_file('response.xlsx', as_attachment=True)

            

            
 
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

import pandas as pd

df = pd.read_csv('emails.csv', header=None)

def get_emails(df):
    emails = []


    for column in df.columns:
        # valid emails mattum 
        email_matches = df[column].str.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b').sum()
        emails.extend(email_matches)

    return emails

emails = get_emails(df)
print(len(emails))
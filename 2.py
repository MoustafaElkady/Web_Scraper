import requests
from bs4 import BeautifulSoup as bs
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry  # يتطلب تثبيت: pip install tkcalendar

def start_scraping():
    # Get inputs from the GUI
    user_date = cal.get_date().strftime('%m/%d/%Y')
    save_path = folder_path.get()
    file_name = file_name_entry.get()

    if not save_path or not file_name:
        messagebox.showwarning("Input Error", "Please select a folder and enter a filename.")
        return

    full_path = f"{save_path}/{file_name}.csv"

    # Scraping logic
    try:
        page = requests.get(f'https://www.yallakora.com/matches?date={user_date}')
        soup = bs(page.content, 'lxml')
        matches_details = []
        championships = soup.find_all('div', {'class': 'matchCard'})

        for champ in championships:
            championship_title = champ.contents[1].find('h2').text.strip()
            all_matches = champ.contents[3].find_all('div', {'class': 'item'})
            
            for match in all_matches:
                team_A = match.find('div', {'class': 'teamA'}).text.strip()
                team_B = match.find('div', {'class': 'teamB'}).text.strip()
                result_div = match.find('div', {'class': 'MResult'})
                scores = result_div.find_all('span', {'class': 'score'})
                score = f'{scores[0].text.strip()} - {scores[1].text.strip()}'
                match_time = result_div.find('span', {'class': 'time'}).text.strip()

                matches_details.append({
                    'نوع البطولة': championship_title, 
                    'الفريق الاول': team_A, 
                    'الفريق الثاني': team_B, 
                    'موعد المبارة': match_time, 
                    'النتيجة': score
                })

        # Save to CSV
        with open(full_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=matches_details[0].keys())
            writer.writeheader()
            writer.writerows(matches_details)
        
        messagebox.showinfo("Success", f"File saved successfully at: {full_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# GUI Setup
root = tk.Tk()
root.title("YallaKora Scraper")
root.geometry("400x300")

# Date Selection
tk.Label(root, text="Select Date:").pack(pady=5)
cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
cal.pack(pady=5)

# Folder Selection
folder_path = tk.StringVar()
tk.Button(root, text="Select Folder", command=lambda: folder_path.set(filedialog.askdirectory())).pack(pady=5)
tk.Entry(root, textvariable=folder_path, width=50).pack(pady=5)

# Filename Input
tk.Label(root, text="Enter File Name:").pack(pady=5)
file_name_entry = tk.Entry(root)
file_name_entry.pack(pady=5)

# Action Button
tk.Button(root, text="Start Scraping", command=start_scraping, bg="green", fg="white").pack(pady=20)

root.mainloop()
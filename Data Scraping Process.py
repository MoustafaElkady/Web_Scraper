import requests
from bs4 import BeautifulSoup as bs
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkcalendar import DateEntry
from datetime import datetime
from PIL import Image, ImageTk

# --- دالة الشاشة الترحيبية ---
def show_splash():
    splash = tk.Toplevel()
    splash.title("Welcome")
    splash.overrideredirect(True)
    
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    w, h = 600, 300
    x, y = (screen_width // 2) - (w // 2), (screen_height // 2) - (h // 2)
    splash.geometry(f"{w}x{h}+{x}+{y}")

    try:
        img = Image.open("Gemini_Generated_Image_ftux8yftux8yftux.png")
        img = img.resize((500, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(splash, image=photo, bg="white")
        lbl.image = photo
        lbl.pack(pady=50)
    except:
        tk.Label(splash, text="جاري تحميل البرنامج...", font=("Arial", 20)).pack(pady=100)

    splash.after(2000, splash.destroy)

# --- دالة عرض النتائج ---
def show_results_gui(matches_details):
    results_window = tk.Toplevel(root)
    results_window.title("نتائج المباريات")
    results_window.geometry("700x500")

    columns = ('بطولة', 'فريق1', 'فريق2', 'وقت', 'نتيجة')
    tree = ttk.Treeview(results_window, columns=columns, show='headings')
    
    tree.heading('بطولة', text='البطولة')
    tree.heading('فريق1', text='الفريق الأول')
    tree.heading('فريق2', text='الفريق الثاني')
    tree.heading('وقت', text='الوقت')
    tree.heading('نتيجة', text='النتيجة')
    
    tree.column('بطولة', width=150)
    tree.column('فريق1', width=100)
    tree.column('فريق2', width=100)
    tree.column('وقت', width=80)
    tree.column('نتيجة', width=80)
    
    for m in matches_details:
        tree.insert('', tk.END, values=(m['نوع البطولة'], m['الفريق الاول'], m['الفريق الثاني'], m['موعد المبارة'], m['النتيجة']))
    
    tree.pack(expand=True, fill='both', padx=10, pady=10)
    
    def another_search():
        results_window.destroy()
        root.deiconify()

    btn_frame = tk.Frame(results_window)
    btn_frame.pack(fill=tk.X, pady=10)
    
    tk.Button(btn_frame, text="نتيجة أخرى", command=another_search, bg="blue", fg="white", width=15).pack(side=tk.RIGHT, padx=20)
    tk.Button(btn_frame, text="خروج", command=root.quit, bg="red", fg="white", width=15).pack(side=tk.LEFT, padx=20)

# --- دالة السكراب ---
def start_scraping():
    user_date = cal.get_date().strftime('%m/%d/%Y')
    
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

        root.withdraw()

        if messagebox.askyesno("حفظ النتائج", "هل ترغب في حفظ النتائج في ملف؟"):
            save_path = filedialog.askdirectory()
            if save_path:
                default_name = f"مباريات_{datetime.now().strftime('%d-%m-%Y')}.csv"
                file_name = simpledialog.askstring("اسم الملف", "أدخل اسم الملف:", initialvalue=default_name)
                
                if file_name:
                    full_path = f"{save_path}/{file_name}.csv"
                    with open(full_path, 'w', encoding='utf-8-sig', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=matches_details[0].keys())
                        writer.writeheader()
                        writer.writerows(matches_details)
                    messagebox.showinfo("Success", "تم الحفظ بنجاح")
            root.deiconify() 
        else:
            show_results_gui(matches_details)

    except Exception as e:
        messagebox.showerror("Error", f"حدث خطأ أثناء جلب البيانات: {e}")

# --- إعداد النافذة الرئيسية ---
root = tk.Tk()
root.title("YallaKora Scraper")
root.geometry("300x200")
root.withdraw() 

# تشغيل الشاشة الترحيبية
show_splash()
root.after(2000, root.deiconify)

tk.Label(root, text="اختر التاريخ لجلب المباريات:", font=('Arial', 10, 'bold')).pack(pady=15)
cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
cal.pack(pady=5)

tk.Button(root, text="بدء جلب البيانات", command=start_scraping, bg="green", fg="white", width=20).pack(pady=20)

root.mainloop()

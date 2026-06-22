import requests
from bs4 import BeautifulSoup as bs
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkcalendar import DateEntry
from datetime import datetime


# ---------------- شاشة الترحيب ----------------

def show_splash():
    splash = tk.Toplevel()
    splash.title("Welcome")
    splash.overrideredirect(True)

    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()

    w, h = 600, 300
    x = (screen_width // 2) - (w // 2)
    y = (screen_height // 2) - (h // 2)

    splash.geometry(f"{w}x{h}+{x}+{y}")
    splash.configure(bg="white")

    tk.Label(
        splash,
        text="برنامج جلب مباريات يلا كورة",
        font=("Arial", 24, "bold"),
        bg="white",
        fg="darkblue"
    ).pack(pady=(60, 15))

    tk.Label(
        splash,
        text="YallaKora Scraper",
        font=("Arial", 16),
        bg="white",
        fg="black"
    ).pack()

    tk.Label(
        splash,
        text="تنفيذ",
        font=("Arial", 12, "bold"),
        bg="white",
        fg="gray"
    ).pack(pady=(25, 5))

    tk.Label(
        splash,
        text="Moustafa Elkady",
        font=("Arial", 18, "bold"),
        bg="white",
        fg="green"
    ).pack()

    splash.after(2500, splash.destroy)


# ---------------- عرض النتائج وحفظها ----------------

def show_results_gui(matches_details):
    # إخفاء النافذة الرئيسية عند عرض النتائج
    root.withdraw()

    results_window = tk.Toplevel(root)
    results_window.title("نتائج المباريات")
    results_window.geometry("1000x550")

    # التعامل مع إغلاق النافذة من زر X العلوي ليعيد إظهار النافذة الرئيسية
    def on_closing():
        results_window.destroy()
        root.deiconify()
    results_window.protocol("WM_DELETE_WINDOW", on_closing)

    columns = ('بطولة', 'فريق1', 'فريق2', 'تاريخ', 'وقت', 'نتيجة')

    tree = ttk.Treeview(
        results_window,
        columns=columns,
        show='headings'
    )

    tree.heading('بطولة', text='البطولة')
    tree.heading('فريق1', text='الفريق الأول')
    tree.heading('فريق2', text='الفريق الثاني')
    tree.heading('تاريخ', text='التاريخ')
    tree.heading('وقت', text='الوقت')
    tree.heading('نتيجة', text='النتيجة')

    tree.column('بطولة', width=250)
    tree.column('فريق1', width=180)
    tree.column('فريق2', width=180)
    tree.column('تاريخ', width=100)
    tree.column('وقت', width=100)
    tree.column('نتيجة', width=100)

    for match in matches_details:
        tree.insert(
            '',
            tk.END,
            values=(
                match['نوع البطولة'],
                match['الفريق الاول'],
                match['الفريق الثاني'],
                match['التاريخ'],
                match['موعد المبارة'],
                match['النتيجة']
            )
        )

    tree.pack(expand=True, fill='both', padx=10, pady=10)

    # دالة حفظ الملف التي تم نقلها إلى هنا
    def save_to_csv():
        save_path = filedialog.askdirectory()
        if save_path:
            default_name = f"مباريات_{datetime.now().strftime('%d-%m-%Y')}"
            file_name = simpledialog.askstring(
                "اسم الملف",
                "أدخل اسم الملف:",
                initialvalue=default_name,
                parent=results_window
            )

            if file_name:
                if not file_name.endswith(".csv"):
                    file_name += ".csv"

                full_path = f"{save_path}/{file_name}"

                try:
                    with open(full_path, "w", encoding="utf-8-sig", newline="") as file:
                        writer = csv.DictWriter(file, fieldnames=matches_details[0].keys())
                        writer.writeheader()
                        writer.writerows(matches_details)
                    messagebox.showinfo("نجاح", "تم حفظ النتائج بنجاح", parent=results_window)
                except Exception as e:
                    messagebox.showerror("خطأ", f"فشل حفظ الملف:\n{e}", parent=results_window)

    def another_search():
        results_window.destroy()
        root.deiconify()

    # إطار الأزرار السفلي
    btn_frame = tk.Frame(results_window)
    btn_frame.pack(fill=tk.X, pady=10)

    # زر نتيجة أخرى (يمين)
    tk.Button(
        btn_frame,
        text="نتيجة أخرى",
        command=another_search,
        bg="blue",
        fg="white",
        width=15
    ).pack(side=tk.RIGHT, padx=20)

    # زر حفظ كـ CSV (منتصف)
    tk.Button(
        btn_frame,
        text="حفظ النتائج كـ CSV",
        command=save_to_csv,
        bg="green",
        fg="white",
        width=18
    ).pack(side=tk.RIGHT, padx=10)

    # زر خروج (يسار)
    tk.Button(
        btn_frame,
        text="خروج",
        command=root.quit,
        bg="red",
        fg="white",
        width=15
    ).pack(side=tk.LEFT, padx=20)


# ---------------- جلب البيانات ----------------

def start_scraping():
    selected_date = cal.get_date()
    user_date = selected_date.strftime('%m/%d/%Y')
    formatted_date = selected_date.strftime('%Y-%m-%d')

    try:
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        }

        response = requests.get(
            f"https://www.yallakora.com/matches?date={user_date}",
            headers=headers,
            timeout=15
        )

        response.raise_for_status()
        soup = bs(response.content, "lxml")
        matches_details = []

        championships = soup.find_all("div", class_="matchCard")

        if not championships:
            messagebox.showwarning("تنبيه", "لم يتم العثور على مباريات أو تغير هيكل الموقع.")
            return

        for championship in championships:
            title_tag = championship.find("h2")
            championship_title = title_tag.text.strip() if title_tag else "بطولة غير معروفة"

            matches = championship.find_all("div", class_="item")

            for match in matches:
                try:
                    teamA = match.find("div", class_="teamA")
                    teamB = match.find("div", class_="teamB")

                    team_A = teamA.text.strip() if teamA else "غير معروف"
                    team_B = teamB.text.strip() if teamB else "غير معروف"

                    result_div = match.find("div", class_="MResult")
                    score = "-"
                    match_time = "-"

                    if result_div:
                        scores = result_div.find_all("span", class_="score")
                        if len(scores) >= 2:
                            score = f"{scores[0].text.strip()} \u2013 {scores[1].text.strip()}"

                        time_tag = result_div.find("span", class_="time")
                        if time_tag:
                            match_time = time_tag.text.strip()

                    matches_details.append({
                        "التاريخ": formatted_date,
                        "نوع البطولة": championship_title,
                        "الفريق الاول": team_A,
                        "الفريق الثاني": team_B,
                        "موعد المبارة": match_time,
                        "النتيجة": score
                    })

                except Exception as match_error:
                    print(f"خطأ في معالجة مباراة: {match_error}")
                    continue

        if not matches_details:
            messagebox.showwarning("تنبيه", "لا توجد مباريات في هذا التاريخ.")
            return

        # عند نجاح الجلب، يتم فتح صفحة النتائج مباشرة
        show_results_gui(matches_details)

    except requests.exceptions.ConnectionError:
        messagebox.showerror("خطأ اتصال", "تعذر الاتصال بالموقع.\nتحقق من الإنترنت.")
    except requests.exceptions.Timeout:
        messagebox.showerror("انتهاء المهلة", "استغرق الموقع وقتاً طويلاً في الاستجابة.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("خطأ HTTP", str(e))
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء جلب البيانات:\n{e}")


# ---------------- النافذة الرئيسية ----------------

root = tk.Tk()
root.title("YallaKora Scraper")
root.geometry("350x220")

root.withdraw()
show_splash()

root.after(2000, root.deiconify)

tk.Label(
    root,
    text="اختر التاريخ لجلب المباريات",
    font=("Arial", 11, "bold")
).pack(pady=15)

cal = DateEntry(
    root,
    width=15,
    background="darkblue",
    foreground="white",
    borderwidth=2,
    date_pattern="mm/dd/yyyy"
)
cal.pack(pady=10)

tk.Button(
    root,
    text="بدء جلب البيانات",
    command=start_scraping,
    bg="green",
    fg="white",
    width=20
).pack(pady=20)

root.mainloop()

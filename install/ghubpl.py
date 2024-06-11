import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk, Menu
import git
import subprocess
import os
import threading
import requests
import platform

# Funkcja do przeglądania katalogów
def przegladaj_katalog():
    katalog_domowy = os.path.expanduser('~')
    katalog = filedialog.askdirectory(initialdir=katalog_domowy)
    if katalog:
        katalog_label.config(text=katalog)
        odswiez_liste(katalog)

# Funkcja do tworzenia nowego katalogu
def stworz_nowy_katalog():
    katalog_domowy = os.path.expanduser('~')
    nowy_katalog = simpledialog.askstring("Nowy katalog", "Wprowadź nazwę nowego katalogu:")
    if nowy_katalog:
        sciezka_nowego_katalogu = os.path.join(katalog_domowy, nowy_katalog)
        try:
            os.makedirs(sciezka_nowego_katalogu)
            messagebox.showinfo("Sukces", f"Katalog '{nowy_katalog}' został utworzony.")
            katalog_label.config(text=sciezka_nowego_katalogu)
            odswiez_liste(sciezka_nowego_katalogu)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się utworzyć katalogu: {e}")

# Funkcja do klonowania repozytorium
def klonuj_repozytorium():
    url_repozytorium = url_entry.get()
    sciezka_pobrania = katalog_label.cget("text")
    if not url_repozytorium or not sciezka_pobrania:
        messagebox.showerror("Błąd", "Proszę podać adres URL repozytorium i ścieżkę katalogu.")
        return

    okno_postepu = tk.Toplevel(root)
    okno_postepu.title("Pobieranie Repozytorium")
    okno_postepu.configure(bg="#575656")
    
    etykieta_postepu = ttk.Label(okno_postepu, text="Pobieranie repozytorium, proszę czekać...")
    etykieta_postepu.pack(pady=10)
    
    pasek_postepu = ttk.Progressbar(okno_postepu, mode="indeterminate")
    pasek_postepu.pack(pady=10, padx=10)
    pasek_postepu.start()

    def klonuj_repo():
        try:
            git.Repo.clone_from(url_repozytorium, sciezka_pobrania)
            pasek_postepu.stop()
            okno_postepu.destroy()
            messagebox.showinfo("Sukces", "Repozytorium zostało pomyślnie pobrane.")
            odswiez_liste(sciezka_pobrania)
        except Exception as e:
            pasek_postepu.stop()
            okno_postepu.destroy()
            messagebox.showerror("Błąd", f"Nie udało się pobrać repozytorium: {e}")

    threading.Thread(target=klonuj_repo).start()

# Funkcja do odświeżania listy plików i katalogów
def odswiez_liste(katalog):
    lista_plikow.delete(0, tk.END)
    for item in os.listdir(katalog):
        item_path = os.path.join(katalog, item)
        lista_plikow.insert(tk.END, item_path)

# Funkcja do uruchamiania skryptu
def uruchom_skrypt():
    wybrany_plik = lista_plikow.get(tk.ACTIVE)
    if wybrany_plik and wybrany_plik.endswith('.sh'):
        wykonaj_skrypt_shell(wybrany_plik)
    else:
        messagebox.showwarning("Ostrzeżenie", "Proszę wybrać plik skryptu (.sh).")

def wykonaj_skrypt_shell(sciezka_skryptu):
    try:
        nazwa_systemu = platform.system()
        katalog_skryptu = os.path.dirname(sciezka_skryptu)
        nazwa_skryptu = os.path.basename(sciezka_skryptu)
        if nazwa_systemu == 'Windows':
            subprocess.run(['cmd', '/c', nazwa_skryptu], cwd=katalog_skryptu, shell=True)
        elif nazwa_systemu == 'Darwin':  # macOS
            subprocess.run(['open', '-a', 'Terminal', sciezka_skryptu], cwd=katalog_skryptu)
        elif nazwa_systemu == 'Linux':
            subprocess.run(['xfce4-terminal', '--hold', '--working-directory', katalog_skryptu, '--command', f"bash -c 'source ~/.profile; ./{nazwa_skryptu}; exec bash'"])
        else:
            messagebox.showerror("Błąd", f"Niewspierany system operacyjny: {nazwa_systemu}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas uruchamiania skryptu: {e}")

# Funkcja do tworzenia menu kontekstowego
def stworz_menu_kontekstowe(entry):
    menu = Menu(entry, tearoff=0)
    menu.add_command(label="Kopiuj", command=lambda: entry.event_generate("<<Copy>>"))
    menu.add_command(label="Wklej", command=lambda: entry.event_generate("<<Paste>>"))
    
    def pokaz_menu_kontekstowe(event):
        menu.tk_popup(event.x_root, event.y_root)
    
    entry.bind("<Button-3>", pokaz_menu_kontekstowe)

# Funkcja do wyszukiwania repozytoriów na GitHub
def wyszukaj_repozytoria():
    zapytanie = simpledialog.askstring("Wyszukaj Repozytorium", "Wprowadź nazwę repozytorium:")
    if zapytanie:
        try:
            odpowiedz = requests.get(f'https://api.github.com/search/repositories?q={zapytanie}')
            wyniki = odpowiedz.json().get('items', [])
            okno_wynikow = tk.Toplevel(root)
            okno_wynikow.title("Wyniki Wyszukiwania")
            okno_wynikow.configure(bg="#575656")

            lista = tk.Listbox(okno_wynikow, width=100, height=20, bg="#575656", fg="white", selectbackground="#4CAF50", selectforeground="white")
            lista.pack(pady=10, padx=10)

            for repo in wyniki:
                lista.insert(tk.END, repo['html_url'])

            def wybierz_repo(event):
                wybrane = lista.get(lista.curselection())
                url_entry.delete(0, tk.END)
                url_entry.insert(0, wybrane)
                okno_wynikow.destroy()

            def pokaz_menu_kontekstowe(event):
                menu.tk_popup(event.x_root, event.y_root)

            def kopiuj_url():
                wybrane = lista.get(lista.curselection())
                root.clipboard_clear()
                root.clipboard_append(wybrane)

            menu = tk.Menu(lista, tearoff=0)
            menu.add_command(label="Kopiuj", command=kopiuj_url)

            lista.bind('<Double-1>', wybierz_repo)
            lista.bind("<Button-3>", pokaz_menu_kontekstowe)

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyszukać repozytoriów: {e}")

# Funkcja do otwierania dodatkowego okna
def otworz_dodatkowe_funkcje():
    okno_dodatkowe = tk.Toplevel(root)
    okno_dodatkowe.title("Konfiguracja")
    okno_dodatkowe.configure(bg="#575656")

    def uruchom_skrypt(skrypt):
        try:
            subprocess.run(['xfce4-terminal', '--hold', '--working-directory', os.path.dirname(skrypt), '--command', f"bash -c '{skrypt}; exec bash'"])
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas uruchamiania skryptu: {e}")

    def klonuj_repo(repo_url, sciezka_pobrania):
        def pobierz_i_uruchom():
            okno_postepu = tk.Toplevel(root)
            okno_postepu.title("Pobieranie Repozytorium")
            okno_postepu.configure(bg="#575656")
            
            etykieta_postepu = ttk.Label(okno_postepu, text="Pobieranie repozytorium, proszę czekać...")
            etykieta_postepu.pack(pady=10)
            
            pasek_postepu = ttk.Progressbar(okno_postepu, mode="indeterminate")
            pasek_postepu.pack(pady=10, padx=10)
            pasek_postepu.start()

            def klonuj_i_uruchom():
                try:
                    git.Repo.clone_from(repo_url, sciezka_pobrania)
                    pasek_postepu.stop()
                    okno_postepu.destroy()
                    messagebox.showinfo("Sukces", "Repozytorium zostało pomyślnie pobrane.")
                    uruchom_skrypt(os.path.join(sciezka_pobrania, 'install.sh'))
                except Exception as e:
                    pasek_postepu.stop()
                    okno_postepu.destroy()
                    messagebox.showerror("Błąd", f"Nie udało się pobrać repozytorium: {e}")

            threading.Thread(target=klonuj_i_uruchom).start()

        odpowiedz = messagebox.askyesno("Potwierdzenie", "Czy chcesz kontynuować?")
        if odpowiedz:
            pobierz_i_uruchom()

    def pobierz_i_uruchom_konfiguracje():
        repo_url = "https://github.com/OpowiesciSkrypty/configuration.git"
        sciezka_pobrania = os.path.join(os.path.expanduser('~'), 'ghub', 'configuration')
        klonuj_repo(repo_url, sciezka_pobrania)

    def xfce_look():
        repo_url = "https://github.com/OpowiesciSkrypty/xfce-look.git"
        sciezka_pobrania = os.path.join(os.path.expanduser('~'), 'ghub', 'xfce_look')
        klonuj_repo(repo_url, sciezka_pobrania)

    def extras():
        repo_url = "https://github.com/OpowiesciSkrypty/extra.git"
        sciezka_pobrania = os.path.join(os.path.expanduser('~'), 'ghub', 'debian_extra')
        klonuj_repo(repo_url, sciezka_pobrania)

    etykieta_konfiguracji = ttk.Label(okno_dodatkowe, text="Konfiguracja", font=("TkDefaultFont", 15, "bold"), background="#575656", foreground='#ffffff')
    etykieta_konfiguracji.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)

    przycisk_konfiguracji = ttk.Button(okno_dodatkowe, text="Uruchom", command=pobierz_i_uruchom_konfiguracje)
    przycisk_konfiguracji.grid(column=1, row=1, padx=10, pady=10, sticky=tk.W)

    etykieta_konfiguracji_opis = ttk.Label(okno_dodatkowe, text="Sterowniki, eksport /sbin do zmiennej środowiskowej PATH\nWyłącz dźwięk przy wylogowywaniu\nDodaj repozytoria za pomocą komendy terminala\nKonfiguracja języka systemu", font=("TkDefaultFont", 12, "bold"), background="#575656", foreground='#000000')
    etykieta_konfiguracji_opis.grid(column=2, row=1, padx=10, pady=10, sticky=tk.W)

    etykieta_xfce_look = ttk.Label(okno_dodatkowe, text="xfce-look", font=("TkDefaultFont", 15, "bold"), background="#575656", foreground='#ffffff')
    etykieta_xfce_look.grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)

    przycisk_xfce_look = ttk.Button(okno_dodatkowe, text="Uruchom", command=xfce_look)
    przycisk_xfce_look.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)

    etykieta_xfce_look_opis = ttk.Label(okno_dodatkowe, text="Instalacja motywów, tapet,ikon", font=("TkDefaultFont", 12, "bold"), background="#575656", foreground='#000000')
    etykieta_xfce_look_opis.grid(column=2, row=2, padx=10, pady=10, sticky=tk.W)

    etykieta_debian_extra = ttk.Label(okno_dodatkowe, text="debian_extra", font=("TkDefaultFont", 15, "bold"), background="#575656", foreground='#ffffff')
    etykieta_debian_extra.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

    przycisk_debian_extra = ttk.Button(okno_dodatkowe, text="Uruchom", command=extras)
    przycisk_debian_extra.grid(column=1, row=3, padx=10, pady=10, sticky=tk.W)

    etykieta_debian_extra_opis = ttk.Label(okno_dodatkowe, text="Kodeki, multimedia\nvim, neofetch, etc...", font=("TkDefaultFont", 12, "bold"), background="#575656", foreground='#000000')
    etykieta_debian_extra_opis.grid(column=2, row=3, padx=10, pady=10, sticky=tk.W)

    okno_dodatkowe.mainloop()

root = tk.Tk()
root.title("GHUB")
root.configure(bg="#575656")

styl = ttk.Style()
styl.theme_use("clam")
styl.configure("TButton", background="#4CAF50", foreground="white", font=("TkDefaultFont", 12), padding=10, focuscolor="none")
styl.map("TButton", background=[("active", "#45a049")])
styl.configure("TLabel", background="#575656", foreground="white", font=("TkDefaultFont", 12))
styl.configure("TEntry", fieldbackground="#2E2E2E", foreground="white")
styl.configure("TListbox", background="#2E2E2E", foreground="white", selectbackground="#4CAF50", selectforeground="white")

etykieta = ttk.Label(root, text="GHUB", font=("TkDefaultFont", 20, "bold"), background="#575656", foreground="#ffffff")
etykieta.grid(column=0, row=0, columnspan=2, pady=10)

etykieta_katalogu = ttk.Label(root, text="Katalog Docelowy:")
etykieta_katalogu.grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)

katalog_label = ttk.Label(root, text="", relief="sunken", anchor="w", background="#2E2E2E", foreground="white", width=40)
katalog_label.grid(column=1, row=2, padx=10, pady=5, sticky=tk.W)

przycisk_przegladania = ttk.Button(root, text="Utwórz", command=stworz_nowy_katalog)
przycisk_przegladania.grid(column=2, row=2, padx=10, pady=5)

etykieta_url = ttk.Label(root, text="Adres URL Repozytorium:")
etykieta_url.grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)

url_entry = ttk.Entry(root, width=40)
url_entry.grid(column=1, row=1, padx=10, pady=5, sticky=tk.W)

stworz_menu_kontekstowe(url_entry)

przycisk_klonowania = ttk.Button(root, text="Pobierz Repozytorium", command=klonuj_repozytorium)
przycisk_klonowania.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

etykieta_listy_plikow = ttk.Label(root, text="Lista Plików:")
etykieta_listy_plikow.grid(column=0, row=4, padx=10, pady=5, sticky=tk.W)

lista_plikow = tk.Listbox(root, width=80, height=10, bg="#2E2E2E", fg="white", selectbackground="#4CAF50", selectforeground="white")
lista_plikow.grid(column=0, row=5, columnspan=2, padx=10, pady=5)

przycisk_uruchamiania = ttk.Button(root, text="Uruchom Skrypt", command=uruchom_skrypt)
przycisk_uruchamiania.grid(column=0, row=6, columnspan=2, padx=10, pady=10)

menu_bar = Menu(root)
root.config(menu=menu_bar)

menu_plik = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Plik", menu=menu_plik)
menu_plik.add_command(label="Przeglądaj Katalog", command=przegladaj_katalog)
menu_plik.add_separator()
menu_plik.add_command(label="Wyjdź", command=root.quit)

menu_szukaj = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Szukaj", menu=menu_szukaj)
menu_szukaj.add_command(label="Szukaj na GitHubie", command=wyszukaj_repozytoria)

menu_dodatkowe = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="EXTRA", menu=menu_dodatkowe)
menu_dodatkowe.add_command(label="Konfiguracja Debiana", command=otworz_dodatkowe_funkcje)

root.mainloop()

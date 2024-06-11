import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk, Menu
import git
import subprocess
import os
import threading
import requests
import platform

# Function to browse directories
def browse_directory():
    home_directory = os.path.expanduser('~')
    directory = filedialog.askdirectory(initialdir=home_directory)
    if directory:
        directory_entry.config(text=directory)
        refresh_list(directory)

# Function to create a new directory
def create_new_directory():
    home_directory = os.path.expanduser('~')
    new_directory = simpledialog.askstring("New Directory", "Enter the name of the new directory:")
    if new_directory:
        new_directory_path = os.path.join(home_directory, new_directory)
        try:
            os.makedirs(new_directory_path)
            messagebox.showinfo("Success", f"Directory '{new_directory}' has been created.")
            directory_entry.config(text=new_directory_path)
            refresh_list(new_directory_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directory: {e}")

# Function to clone a repository
def clone_repo():
    repo_url = url_entry.get()
    download_path = directory_entry.cget("text")
    if not repo_url or not download_path:
        messagebox.showerror("Error", "Please provide the repository URL and directory path.")
        return

    progress_window = tk.Toplevel(root)
    progress_window.title("Cloning Repository")
    progress_window.configure(bg="#575656")
    
    progress_label = ttk.Label(progress_window, text="Cloning repository, please wait...")
    progress_label.pack(pady=10)
    
    progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
    progress_bar.pack(pady=10, padx=10)
    progress_bar.start()

    def clone_repository():
        try:
            git.Repo.clone_from(repo_url, download_path)
            progress_bar.stop()
            progress_window.destroy()
            messagebox.showinfo("Success", "Repository cloned successfully.")
            refresh_list(download_path)
        except Exception as e:
            progress_bar.stop()
            progress_window.destroy()
            messagebox.showerror("Error", f"Failed to clone repository: {e}")

    threading.Thread(target=clone_repository).start()

# Function to refresh the file and directory list
def refresh_list(directory):
    file_list.delete(0, tk.END)
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        file_list.insert(tk.END, item_path)

# Function to run a script
def run_script():
    selected_file = file_list.get(tk.ACTIVE)
    if selected_file and selected_file.endswith('.sh'):
        execute_shell_script(selected_file)
    else:
        messagebox.showwarning("Warning", "Please select a script file (.sh).")

def execute_shell_script(script_path):
    try:
        system_name = platform.system()
        script_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)
        if system_name == 'Windows':
            subprocess.run(['cmd', '/c', script_name], cwd=script_dir, shell=True)
        elif system_name == 'Darwin':  # macOS
            subprocess.run(['open', '-a', 'Terminal', script_path], cwd=script_dir)
        elif system_name == 'Linux':
            subprocess.run(['xfce4-terminal', '--hold', '--working-directory', script_dir, '--command', f"bash -c 'source ~/.profile; ./{script_name}; exec bash'"])
        else:
            messagebox.showerror("Error", f"Unsupported operating system: {system_name}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while running the script: {e}")

# Function to create a context menu
def create_context_menu(entry):
    menu = Menu(entry, tearoff=0)
    menu.add_command(label="Copy", command=lambda: entry.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))
    
    def show_context_menu(event):
        menu.tk_popup(event.x_root, event.y_root)
    
    entry.bind("<Button-3>", show_context_menu)

# Function to search repositories on GitHub
def search_repositories():
    query = simpledialog.askstring("Search Repository", "Enter the repository name:")
    if query:
        try:
            response = requests.get(f'https://api.github.com/search/repositories?q={query}')
            results = response.json().get('items', [])
            result_window = tk.Toplevel(root)
            result_window.title("Search Results")
            result_window.configure(bg="#575656")

            listbox = tk.Listbox(result_window, width=100, height=20, bg="#575656", fg="white", selectbackground="#4CAF50", selectforeground="white")
            listbox.pack(pady=10, padx=10)

            for repo in results:
                listbox.insert(tk.END, repo['html_url'])

            def select_repo(event):
                selected = listbox.get(listbox.curselection())
                url_entry.delete(0, tk.END)
                url_entry.insert(0, selected)
                result_window.destroy()

            def show_context_menu(event):
                menu.tk_popup(event.x_root, event.y_root)

            def copy_url():
                selected = listbox.get(listbox.curselection())
                root.clipboard_clear()
                root.clipboard_append(selected)

            menu = tk.Menu(listbox, tearoff=0)
            menu.add_command(label="Copy", command=copy_url)

            listbox.bind('<Double-1>', select_repo)
            listbox.bind("<Button-3>", show_context_menu)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to search repositories: {e}")

# Function to open additional window
def open_additional_features():
    additional_window = tk.Toplevel(root)
    additional_window.title("Configuration")
    additional_window.configure(bg="#575656")

    def run_script(script_path):
        try:
            subprocess.run(['xfce4-terminal', '--hold', '--working-directory', os.path.dirname(script_path), '--command', f"bash -c '{script_path}; exec bash'"])
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred while running the script: {e}")


    def clone_repo(repo_url, download_path):
        def download_and_run():
            progress_window = tk.Toplevel(root)
            progress_window.title("Cloning Repository")
            progress_window.configure(bg="#575656")
            
            progress_label = ttk.Label(progress_window, text="Cloning repository, please wait...")
            progress_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
            progress_bar.pack(pady=10, padx=10)
            progress_bar.start()

            def clone_and_run():
                try:
                    git.Repo.clone_from(repo_url, download_path)
                    progress_bar.stop()
                    progress_window.destroy()
                    messagebox.showinfo("Success", "Repository cloned successfully.")
                    run_script(os.path.join(download_path, 'installen.sh'))
                except Exception as e:
                    progress_bar.stop()
                    progress_window.destroy()
                    messagebox.showerror("Error", f"Failed to clone repository: {e}")

            threading.Thread(target=clone_and_run).start()

        answer = messagebox.askyesno("Confirmation", "Do you want to continue?")
        if answer:
            download_and_run()

    def download_and_run_configuration():
        repo_url = "https://github.com/OpowiesciSkrypty/configuration.git"
        download_path = os.path.join(os.path.expanduser('~'), 'ghub', 'configuration')
        clone_repo(repo_url, download_path)

    def xfce_look():
        repo_url = "https://github.com/OpowiesciSkrypty/xfce-look.git"
        download_path = os.path.join(os.path.expanduser('~'), 'ghub', 'xfce_look')
        clone_repo(repo_url, download_path)

    def extras():
        repo_url = "https://github.com/OpowiesciSkrypty/extra.git"
        download_path = os.path.join(os.path.expanduser('~'), 'ghub', 'debian_extra')
        clone_repo(repo_url, download_path)

    button2_label = ttk.Label(additional_window, text="Configuration", font=("TkDefaultFont", 15, "bold"), background="#575656", foreground='#ffffff')
    button2_label.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)

    button2_button = ttk.Button(additional_window, text="Run", command=download_and_run_configuration)
    button2_button.grid(column=1, row=1, padx=10, pady=10, sticky=tk.W)

    button2_label = ttk.Label(additional_window, text="Drivers, export /sbin directory to PATH variable\nDisable sound on logout\nAdd repositories using terminal command\nLanguage configuration", font=("TkDefaultFont", 12, "bold"), background="#575656", foreground='#000000')
    button2_label.grid(column=2, row=1, padx=10, pady=10, sticky=tk.W)

    button3_label = ttk.Label(additional_window, text="xfce-look", font=("TkDefaultFont", 15, "bold"), background="#575656", foreground='#ffffff')
    button3_label.grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)

    button3_button = ttk.Button(additional_window, text="Run", command=xfce_look)
    button3_button.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)

    button3_label = ttk.Label(additional_window, text="Themes, wallpapers, icons", font=("TkDefaultFont", 12, "bold"), background="#575656", foreground='#000000')
    button3_label.grid(column=2, row=2, padx=10, pady=10, sticky=tk.W)

    button4_label = ttk.Label(additional_window, text="debian_extra", font=("TkDefaultFont", 15, "bold"), background="#575656", foreground='#ffffff')
    button4_label.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

    button4_button = ttk.Button(additional_window, text="Run", command=extras)
    button4_button.grid(column=1, row=3, padx=10, pady=10, sticky=tk.W)

    button4_label = ttk.Label(additional_window, text="Codecs, multimedia\nvim, neofetch, etc...", font=("TkDefaultFont", 12, "bold"), background="#575656", foreground='#000000')
    button4_label.grid(column=2, row=3, padx=10, pady=10, sticky=tk.W)

    additional_window.mainloop()

root = tk.Tk()
root.title("GHUB")
root.configure(bg="#575656")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", background="#4CAF50", foreground="white", font=("TkDefaultFont", 12), padding=10, focuscolor="none")
style.map("TButton", background=[("active", "#45a049")])
style.configure("TLabel", background="#575656", foreground="white", font=("TkDefaultFont", 12))
style.configure("TEntry", fieldbackground="#2E2E2E", foreground="white")
style.configure("TListbox", background="#2E2E2E", foreground="white", selectbackground="#4CAF50", selectforeground="white")

label = ttk.Label(root, text="GHUB", font=("TkDefaultFont", 20, "bold"), background="#575656", foreground="#ffffff")
label.grid(column=0, row=0, columnspan=2, pady=10)

directory_label = ttk.Label(root, text="Save Directory:")
directory_label.grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)

directory_entry = ttk.Label(root, text="", relief="sunken", anchor="w", background="#2E2E2E", foreground="white", width=40)
directory_entry.grid(column=1, row=2, padx=10, pady=5, sticky=tk.W)

browse_button = ttk.Button(root, text="Create", command=create_new_directory)
browse_button.grid(column=2, row=2, padx=10, pady=5)

url_label = ttk.Label(root, text="Repository URL:")
url_label.grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)

url_entry = ttk.Entry(root, width=40)
url_entry.grid(column=1, row=1, padx=10, pady=5, sticky=tk.W)

create_context_menu(url_entry)

clone_button = ttk.Button(root, text="Clone Repository", command=clone_repo)
clone_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

file_list_label = ttk.Label(root, text="File List:")
file_list_label.grid(column=0, row=4, padx=10, pady=5, sticky=tk.W)

file_list = tk.Listbox(root, width=80, height=10, bg="#2E2E2E", fg="white", selectbackground="#4CAF50", selectforeground="white")
file_list.grid(column=0, row=5, columnspan=2, padx=10, pady=5)

run_button = ttk.Button(root, text="Run Script", command=run_script)
run_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10)

menu_bar = Menu(root)
root.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="browse directory", command=browse_directory)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

search_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Search", menu=search_menu)
search_menu.add_command(label="Search GitHub", command=search_repositories)

extra_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Extra", menu=extra_menu)
extra_menu.add_command(label="Debian Configuration", command=open_additional_features)

root.mainloop()
              


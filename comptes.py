import mysql.connector
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
from datetime import datetime

class GestionComptes(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.title("Gestion des Comptes")
        ctk.set_appearance_mode('dark')
        self.geometry("800x600")

        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Nostale2004@",
            database="banque"
        )
        self.cursor = self.connection.cursor()

        self.images = [
            "th.jpg",
            "2.jpg",
            "3.jpg",
            "4.jpg",
            "5.jpg",
            "6.jpg"
        ]
        
        self.display_accounts()

    def mode(self):
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode('light' if current_mode == 'Dark' else 'dark')

    def display_accounts(self):
        for widget in self.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self, text="🏦 Vos Comptes", font=("Poppins", 24, "bold"))
        title.pack(pady=20)

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20)

        self.cursor.execute("SELECT id, nom, solde, image FROM compte WHERE user_id = %s", (self.user_id,))
        comptes = self.cursor.fetchall()

        self.account_buttons = {}
        row, col = 0, 0
        for compte in comptes:
            account_id, nom, solde, image = compte
            image_path = image if image else self.images[0]
            
            btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
            btn_frame.grid(row=row, column=col, padx=10, pady=10)
            
            img = Image.open(image_path)
            img = img.resize((80, 80))
            photo = ImageTk.PhotoImage(img)
                
            btn_frame.photo = photo
                
            img_label = ctk.CTkLabel(btn_frame, image=photo, text="")
            img_label.pack(pady=5)

            text_label = ctk.CTkLabel(btn_frame, text=f"{nom}\nSolde: {solde}", font=("Poppins", 16))
            text_label.pack(pady=5)
            
            select_btn = ctk.CTkButton(btn_frame, text="Gérer", font=("Poppins", 14), 
                                       fg_color="#9370db", width=120, height=30, 
                                       command=lambda c=account_id, r=row, co=col: self.open_account(c, r, co))
            select_btn.pack(pady=5)
            
            self.account_buttons[account_id] = btn_frame
            
            col += 1
            if col > 1:
                col = 0
                row += 1

        if len(comptes) < 4:
            add_button = ctk.CTkButton(self.frame, text="+", font=("Poppins", 24), width=150, height=150, 
                                       fg_color="#dda0dd", hover_color="#4682B4", command=self.create_account)
            add_button.grid(row=row, column=col, padx=10, pady=10)

        mode_button = ctk.CTkButton(self, text="🌙", font=("Poppins", 14), width=40, height=40, 
                                    fg_color="#000000", hover_color="#333333", command=self.mode)
        mode_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    def open_account(self, account_id, row, col):
        if hasattr(self, 'option_frame') and self.option_frame.winfo_exists():
            self.option_frame.destroy()
        
        self.option_frame = ctk.CTkFrame(self.frame, fg_color='#9370db')
        self.option_frame.grid(row=row, column=col, padx=15, pady=15)
        
        ctk.CTkButton(self.option_frame, text="✅ Sélectionner", width=100, 
                     command=lambda: self.select_account(account_id)).pack(pady=5)
        ctk.CTkButton(self.option_frame, text="✏️ Modifier", width=100, 
                     command=lambda: self.modify_account(account_id)).pack(pady=5)
        ctk.CTkButton(self.option_frame, text="♻️ Supprimer", width=100, 
                     command=lambda: self.delete_account(account_id)).pack(pady=5)
    
    def select_account(self, account_id):
        self.destroy()
    
        from Home import Home 
        home_window = Home(self.user_id, account_id)
        home_window.mainloop()

    def modify_account(self, account_id):
        new_name = ctk.CTkInputDialog(text="Nouveau nom du compte:", title="Modification").get_input()
        if new_name:
            self.cursor.execute("UPDATE compte SET nom = %s WHERE id = %s", (new_name, account_id))
            self.connection.commit()
            self.display_accounts()

    def delete_account(self, account_id):
        confirmation = messagebox.askyesno("Suppression", "Voulez-vous vraiment supprimer ce compte ?")
        if confirmation:
            self.cursor.execute("DELETE FROM compte WHERE id = %s", (account_id,))
            self.connection.commit()
            self.display_accounts()

    def create_account(self):
        create_window = ctk.CTkToplevel(self)
        create_window.title("Création de compte")
        create_window.geometry("400x600") 
        
        title = ctk.CTkLabel(create_window, text="Créer un nouveau compte", font=("Poppins", 18, "bold"))
        title.pack(pady=10)
        
        info_frame = ctk.CTkFrame(create_window)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text="Nom du compte:", font=("Poppins", 14)).pack(pady=5)
        name_entry = ctk.CTkEntry(info_frame, width=300, font=("Poppins", 14))
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(info_frame, text="Sélectionnez une image:", font=("Poppins", 14)).pack(pady=20)
        
        images_frame = ctk.CTkFrame(create_window)
        images_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        selected_image = ctk.StringVar(value=self.images[0])
        
        
        row, col = 0, 0
        for idx, img_path in enumerate(self.images):
                img = Image.open(img_path)
                img = img.resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                
                img_frame = ctk.CTkFrame(images_frame, fg_color="transparent")
                img_frame.grid(row=row, column=col, padx=10, pady=10)
                
                img_frame.photo = photo
                
                img_label = ctk.CTkLabel(img_frame, image=photo, text="")
                img_label.pack(pady=5)
                
                select_btn = ctk.CTkRadioButton(img_frame, text="", variable=selected_image, value=img_path)
                select_btn.pack(pady=5)
                
                col += 1
                if col > 2:
                    col = 0
                    row += 1
        
        buttons_frame = ctk.CTkFrame(create_window, fg_color="transparent")
        buttons_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(buttons_frame, text="Annuler", fg_color="#ff6b6b", hover_color="#ff5252", 
                     command=create_window.destroy).pack(side="left", padx=10)
        
        ctk.CTkButton(buttons_frame, text="Créer", fg_color="#4CAF50", hover_color="#388E3C", 
                     command=lambda: self.add(name_entry.get(), selected_image.get(), create_window)
                     ).pack(side="right", padx=10)
    

    def add(self, name, image_path, window):
        if not name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom pour le compte.")
            return
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        print(current_date)
        
        self.cursor.execute("INSERT INTO compte (nom, user_id, image,IBAN,date_create) VALUES (%s, %s, %s,%s,%s)", 
                         (name, self.user_id, image_path,self.generate_iban(),current_date))
        self.connection.commit()

        
        window.destroy()
        self.display_accounts()

    def generate_iban(self):
        iban = f"FR{random.randint(1000000, 9999999)}"
        return iban
    


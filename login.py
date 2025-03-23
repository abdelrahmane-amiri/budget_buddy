import mysql.connector
import customtkinter as ctk
from tkinter import messagebox
from comptes import GestionComptes
import bcrypt

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - Banque")
        ctk.set_appearance_mode("dark")
        self.font = ("Poppins",13)
        self.geometry("800x600")
        
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Nostale2004@", 
            database="banque"
        )
        self.cursor = self.connection.cursor()
        self.icone = "🌙"

        self.show_pass = False



    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mode(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == 'Dark':
            ctk.set_appearance_mode('light')
            self.icone = "🌞"
        else:
            ctk.set_appearance_mode('dark')
            self.icone = "🌙"
        self.mode_button.configure(text=self.icone)

    def menu(self):
        self.clear()

        title = ctk.CTkLabel(self, text="💰 Banque RashToz", font=("Poppins", 30, "bold"))
        title.pack(pady=40)

        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=50, padx=50)

        subtitle = ctk.CTkLabel(frame, text=" Bienvenue", font=("Poppins", 20))
        subtitle.pack(pady=20)

        login_button = ctk.CTkButton(
            frame, text="🔑 Se connecter", font=("Poppins", 18), height=50, width=300,
            fg_color="#32CD32", hover_color="#228B22", command=self.login_wid
        )
        login_button.pack(padx=20, pady=10)

        register_button = ctk.CTkButton(
            frame, text="📝 S'inscrire", font=("Poppins", 18), height=50, width=300,fg_color="#1E90FF", hover_color="#4682B4", command=self.register_wid)
        register_button.pack(padx=20, pady=10)

        description = ctk.CTkLabel(frame, text="Gérez vos finances comme Rachid 💵", font=("Poppins", 14))
        description.pack(pady=20)

        self.mode_button = ctk.CTkButton(
            self, text=self.icone, font=("Poppins", 14), width=40, height=40, fg_color="#000000",hover_color="#333333", command=self.mode)
        self.mode_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)


    def register_wid(self):
        self.clear()

        title = ctk.CTkLabel(self, text="📝 Inscription - Banque RashToz", font=("Poppins", 24, "bold"))
        title.pack(pady=20)

        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=20, padx=50)

        subtitle = ctk.CTkLabel(frame, text="Créez votre compte", font=("Poppins", 16))
        subtitle.pack(pady=10)

        self.user_name = ctk.CTkEntry(frame, placeholder_text="🧑 Nom", font=("Poppins", 14), width=300)
        self.user_name.pack(padx=10, pady=5)

        self.user_surname = ctk.CTkEntry(frame, placeholder_text="👤 Prénom", font=("Poppins", 14), width=300)
        self.user_surname.pack(padx=10, pady=5)

        self.user_mail = ctk.CTkEntry(frame, placeholder_text="📧 Email", font=("Poppins", 14), width=300)
        self.user_mail.pack(padx=10, pady=5)

        self.user_mdp = ctk.CTkEntry(frame, placeholder_text="🔒 Mot de passe", font=("Poppins", 14), width=300, show='*')
        self.user_mdp.pack(padx=10, pady=5)

        self.user_cmdp = ctk.CTkEntry(frame, placeholder_text="🔑 Confirmer le mot de passe", font=("Poppins", 14), width=300, show='*')
        self.user_cmdp.pack(padx=10, pady=5)

        self.text_cond = ctk.CTkLabel(frame,text="Doit contenirs au moins:",font=("Poppins", 12), text_color="red")
        self.cond_one = ctk.CTkLabel(frame,text="1 Majuscule",font=("Poppins", 12), text_color="red")
        self.cond_two = ctk.CTkLabel(frame,text="1 Chiffre",font=("Poppins", 12), text_color="red")
        self.cond_three = ctk.CTkLabel(frame,text="1 Caractère spécial",font=("Poppins", 12), text_color="red")
        self.cond_four = ctk.CTkLabel(frame,text="10 Caractères",font=("Poppins", 12), text_color="red")

        self.user_mdp.bind("<KeyRelease>", self.password_strength)

        self.psw_show = ctk.CTkButton(
            frame, text="👀", font = ("¨Poppins", 14),fg_color= "#000000", width= 15, height= 15, corner_radius= 100 , command = self.show_psw)
        self.psw_show.pack(padx = 10, pady = 5)

        register_button = ctk.CTkButton(frame, text="✅ S'inscrire", font=("Poppins", 16), height=40, width=200,fg_color="#1E90FF", hover_color="#4682B4", command=self.register_user)
        register_button.pack(padx=10, pady=2)

        login_label = ctk.CTkLabel(frame, text="Déjà un compte ? Connectez-vous", font=("Poppins", 13, "underline"), text_color="#1E90FF",
        cursor="hand2")
        login_label.pack(pady=5)

        login_label.bind("<Button-1>", lambda event: self.login_wid())

        self.mode_button = ctk.CTkButton(
            self, text=self.icone, font=("Poppins", 14), width=40, height=40, fg_color="#000000",hover_color="#333333", command=self.mode)
        self.mode_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)



    def login_wid(self):
        self.clear()

        title = ctk.CTkLabel(self, text="🔑 Connection - Banque RashToz", font=("Poppins", 24, "bold"))
        title.pack(pady=20)

        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=20, padx=50)
    
        subtitle = ctk.CTkLabel(frame, text="Connectez-vous à votre compte", font=("Poppins", 16))
        subtitle.pack(pady=10)

        self.user_mail = ctk.CTkEntry(frame, placeholder_text="📧 Email", font=("Poppins", 14), width=300)
        self.user_mail.pack(padx=10, pady=5)

        self.user_mdp = ctk.CTkEntry(frame, placeholder_text="🔒 Mot de passe", font=("Poppins", 14), width=300, show='*')
        self.user_mdp.pack(padx=10, pady=5)

        login_button = ctk.CTkButton(
            frame, text="✅ Se connecter", font=("Poppins", 16), height=40, width=200,fg_color="#32CD32", hover_color="#228B22", command=self.login_user)
        login_button.pack(padx=10, pady=15)

        register_label = ctk.CTkLabel(
            frame, text="Pas encore de compte ? Inscrivez-vous", font=("Poppins", 13, "underline"), text_color="#1E90FF",cursor="hand2")
        register_label.pack(pady=5)

        register_label.bind("<Button-1>", lambda event: self.register_wid())
        
        self.mode_button = ctk.CTkButton(
            self, text=self.icone, font=("Poppins", 14), width=40, height=40, fg_color="#000000",hover_color="#333333", command=self.mode)
        self.mode_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    def register_user(self):
        name = self.user_name.get()
        surname = self.user_surname.get()
        email = self.user_mail.get()
        password = self.user_mdp.get()
        confirm_password = self.user_cmdp.get()

        if password != confirm_password:
            self.show_notif("Les Mots de passe ne correspondent pas", "#FF0000")
            return
        
        if not any(i.isupper() for i in password) or len(password) <= 10 or not any(i.isdigit() for i in password):
            self.show_notif("Mot de passe pas sécurisé", "#FF0000")
            return 

        if not "@" in email:
            self.show_notif("L'email n'est pas valide", "#FF0000")
            return
        
        self.cursor.execute("SELECT * FROM utilisateur WHERE mail = %s", (email,))
        existing_user = self.cursor.fetchone()
        
        if existing_user:
            self.show_notif("L'email est déjà utilisée", "#FF0000")
            return
        
        try:
            # Générer le hash et le convertir en string pour stockage
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')  # Convertir bytes en string
            
            query = "INSERT INTO utilisateur (nom, prenom, mail, mot_de_passe) VALUES (%s, %s, %s, %s)"
            values = (name, surname, email, hashed_password_str)
            self.cursor.execute(query, values)
            self.connection.commit()
            self.show_notif("✅ Inscription réussie !", "#1E90FF")
        except Exception as e:
            print(f"Erreur d'inscription: {e}")
            self.show_notif("❌ Inscription échouée !", "#FF0000")


    def login_user(self):
        email = self.user_mail.get()
        password = self.user_mdp.get()

        if not email or not password:
            self.show_notif("Veuillez remplir tous les champs !", "#FF0000")
            return

        try:
            self.cursor.execute("SELECT * FROM utilisateur WHERE mail = %s", (email,))
            user = self.cursor.fetchone()

            if user:
                # Le mot de passe stocké est une chaîne, le convertir en bytes pour la vérification
                stored_hash = user[4].encode('utf-8')
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    self.destroy()
                    compte = GestionComptes(user_id=user[0])
                    compte.mainloop()
                else:
                    self.show_notif("Email ou Mot de passe incorrect", "#FF0000")
            else:
                self.show_notif("Email ou Mot de passe incorrect", "#FF0000")
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            self.show_notif(f"Erreur lors de la connexion", "#FF0000")

    def password_strength(self, event=None):
        password = self.user_mdp.get()
        conditions = [
            len(password) >= 10,
            any(char.isupper() for char in password),
            any(char.isdigit() for char in password),
            any(char in "!@#$%^&*()_+-=[]{};':\",./<>?`~" for char in password)
        ]

        if password:
            self.text_cond.pack(padx=10)
            self.cond_one.pack(padx=10)
            self.cond_two.pack(padx=10)
            self.cond_three.pack(padx=10)
            self.cond_four.pack(padx=10)
        else:
            self.text_cond.pack_forget()
            self.cond_one.pack_forget()
            self.cond_two.pack_forget()
            self.cond_three.pack_forget()
            self.cond_four.pack_forget()

        if conditions[1]:
            self.cond_one.configure(text="✅1 Majuscule", text_color="green")
        else:
            self.cond_one.configure(text="❌1 Majuscule", text_color="red")
        if conditions[2]:
            self.cond_two.configure(text="✅1 Chiffre", text_color="green")
        else:
            self.cond_two.configure(text="❌1 Chiffre", text_color="red")
        if conditions[3]:
            self.cond_three.configure(text="✅1 Caractère spécial", text_color="green")
        else:
            self.cond_three.configure(text="❌1 Caractère spécial", text_color="red")
        if conditions[0]:
            self.cond_four.configure(text="✅10 Caractères", text_color="green")
        else:
            self.cond_four.configure(text="❌10 Caractères", text_color="red")

        if all(conditions):
            self.text_cond.configure(text_color="green")

    def show_notif(self, message, couleur="#32CD32"):
        notification = ctk.CTkLabel(self, text=message, font=("Poppins", 14, "bold"), text_color="white", fg_color=couleur, corner_radius=10)
        notification.place(relx=0.5, rely=0.11, anchor="center")
        
        self.after(3000, notification.destroy)
        
    def show_psw(self):
        if self.show_pass == False:
            self.show_pass = True
            self.user_mdp.configure(show = "")
            self.user_cmdp.configure(show = "")
        else:
            self.show_pass = False
            self.user_mdp.configure(show = "*")
            self.user_cmdp.configure(show = "*")

import mysql.connector
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from login import Login

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class Home(ctk.CTk):
    def __init__(self,user_id,id):
        super().__init__()

        # fenêtre
        self.title("Banque RashToz")
        self.geometry("1000x600")
        self.configure(fg_color="#1A1A1A")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.id = id
        self.user_id = user_id

        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Nostale2004@", 
            database="banque"
        )
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT nom FROM compte WHERE id = %s", (id,))
        self.nom_compte = self.cursor.fetchone()
        self.cursor.execute("SELECT nom, prenom FROM utilisateur WHERE id = %s", (user_id,))
        self.nom_user = self.cursor.fetchall()
        self.cursor.execute("SELECT solde FROM compte WHERE id = %s", (id,))
        self.solde = self.cursor.fetchone()
        self.solde_value = 0 if self.solde[0] == None else self.solde[0]
        self.cursor.execute("SELECT IBAN FROM compte WHERE id = %s", (id,))
        self.iban = self.cursor.fetchone()
        self.cursor.execute("SELECT date_create FROM compte WHERE id = %s", (id,))
        self.date = self.cursor.fetchone()
        self.cursor.execute("SELECT SUM(solde) FROM compte WHERE user_id = %s", (user_id,))
        self.allsolde = self.cursor.fetchone()
        self.cursor.execute("SELECT * FROM transaction WHERE id_compte = %s ORDER BY ID DESC", (id,))
        self.transa = self.cursor.fetchall()

        self.active_menu = 0


        #Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, fg_color="#1A1A1A", corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Logo et titre
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="RASHTOZ", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.logo_label2 = ctk.CTkLabel(self.sidebar_frame, text="BANQUE", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00FF7F")
        self.logo_label2.grid(row=1, column=0, padx=20, pady=(0, 20))

        #Utilisateur
        self.avatar_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#1A1A1A", corner_radius=10)
        self.avatar_frame.grid(row=2, column=0, padx=20, pady=10)
        
        self.avatar_circle = ctk.CTkButton(self.avatar_frame, text="", fg_color="#00FF7F", width=40, height=40, 
                                           corner_radius=20, hover=False, border_width=0)
        self.avatar_circle.grid(row=0, column=0, padx=10, pady=10)
        
        self.user_info = ctk.CTkFrame(self.avatar_frame, fg_color="#1A1A1A")
        self.user_info.grid(row=0, column=1, padx=5, pady=5)
        
        self.username_label = ctk.CTkLabel(self.user_info, text=self.nom_user[0], font=ctk.CTkFont(size=14, weight="bold"))
        self.username_label.grid(row=0, column=0, sticky="w")
        
        self.wallet_label = ctk.CTkLabel(self.user_info, text="Porte-Monnaie", font=ctk.CTkFont(size=12))
        self.wallet_label.grid(row=1, column=0, sticky="w")
        
        self.balance_label = ctk.CTkLabel(self.avatar_frame, text= f"{self.allsolde[0]} €", font=ctk.CTkFont(size=14, weight="bold"))
        self.balance_label.grid(row=0, column=2, padx=10)

        #Menu
        self.menu_items = [
            {"icon": "🏠", "text": "Accueil"},
            {"icon": "📊", "text": "Compte"},
            {"icon": "💸", "text": "Transaction"},
            {"icon": "⚙️", "text": "Paramètres"}
        ]
        
        for i, item in enumerate(self.menu_items):
            command = None
            if item['text'] == "Accueil":
                command = self.reset_main_frame
            elif item['text'] == "Compte":
                command = self.show_accounts
            elif item['text'] == "Transaction":
                command = self.transfer_money
            elif item['text'] == "Paramètres":
                command = self.show_settings

            menu_button = ctk.CTkButton(
                self.sidebar_frame,
                text=f"{item['icon']}  {item['text']}",
                fg_color="#1A1A1A", 
                hover_color="#00CC66", 
                anchor="w",
                height=40,
                corner_radius=10,
                border_spacing=10,
                font=ctk.CTkFont(size=14),
                command=command
            )
            menu_button.grid(row=i+4, column=0, sticky="ew", pady=5, padx=20)

        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="↩️  Déconnexion",
            fg_color="#1A1A1A",
            hover_color="#FF5555", 
            anchor="w",
            height=40,
            corner_radius=10,
            border_spacing=10,
            font=ctk.CTkFont(size=14),
            command= self.deconn
        )
        self.logout_button.grid(row=11, column=0, sticky="ew", pady=20, padx=20)

        #Contenu principale
        self.main_frame = ctk.CTkFrame(self, fg_color="#292929", corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.reset_main_frame()



    # Frame Principale (Acceuil)
    def reset_main_frame(self):
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid_rowconfigure(1, weight=1)

            self.geometry("1000x600")

            #Titre du compte
            self.account_header = ctk.CTkFrame(self.main_frame, fg_color="#292929", corner_radius=0)
            self.account_header.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
            
            account_title = ctk.CTkLabel(self.account_header, text=f"Compte de {self.nom_compte[0]}", font=ctk.CTkFont(size=24, weight="bold"))
            account_title.grid(row=0, column=0, sticky="w")
            
            account_balance = ctk.CTkLabel(self.account_header, text="Ton Solde", font=ctk.CTkFont(size=12))
            account_balance.grid(row=0, column=1, padx=100, sticky="e")
            
            analyse_btn = ctk.CTkButton(self.account_header, text="Analyse", fg_color="#292929", hover_color="#3A3A3A", 
                          corner_radius=5, border_width=0, command=self.show_analysis)
            analyse_btn.grid(row=0, column=2, padx=20, sticky="e")

            # Contenu du compte - cadre interne
            self.account_content = ctk.CTkFrame(self.main_frame, fg_color="#292929")
            self.account_content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
            self.account_content.grid_columnconfigure((0, 1), weight=1)
            
            # Carte et info
            self.left_column = ctk.CTkFrame(self.account_content, fg_color="#292929")
            self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            # Carte ou mettre image si trop moche
            self.card_frame = ctk.CTkFrame(self.left_column, fg_color="#00CC66", corner_radius=10, height=200)
            self.card_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
            self.card_frame.grid_propagate(False)
            
            visa_name = ctk.CTkLabel(self.card_frame, text="Dév", font=ctk.CTkFont(size=16), text_color="white")
            visa_name.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
            
            visa_chip = ctk.CTkFrame(self.card_frame, width=40, height=30, fg_color="#FFD700", corner_radius=5)
            visa_chip.grid(row=1, column=0, padx=20, pady=10, sticky="w")
            visa_chip.grid_propagate(False)
            
            visa_logo = ctk.CTkLabel(self.card_frame, text="VISA", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
            visa_logo.grid(row=2, column=0, padx=20, pady=(50, 20), sticky="e")
            
            # Info du compte
            self.info_frame = ctk.CTkFrame(self.left_column, fg_color="#292929")
            self.info_frame.grid(row=1, column=0, sticky="nsew")
            
            info_title = ctk.CTkLabel(self.info_frame, text="Informations", font=ctk.CTkFont(size=16, weight="bold"))
            info_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
            
            view_all_btn = ctk.CTkButton(self.info_frame, text="Tout voir", fg_color="#00CC66", hover_color="#00AA55", 
                                        corner_radius=5, width=80, height=25)
            view_all_btn.grid(row=0, column=1, padx=20, pady=(0, 10))
            
            # liste des info
            info_items = [
                {"label": "Solde", "value": f"{self.solde_value} €"},
                {"label": "IBAN", "value": self.iban},
                {"label": "Propriétaire", "value": "Toi"},
                {"label": "Permission", "value": "Tout"},
                {"label": "Date de création", "value": self.date}
            ] 
            
            for i, item in enumerate(info_items):
                info_label = ctk.CTkLabel(self.info_frame, text=item["label"], font=ctk.CTkFont(size=14))
                info_label.grid(row=i+1, column=0, sticky="w", pady=5)
                
                info_value = ctk.CTkLabel(self.info_frame, text=item["value"], font=ctk.CTkFont(size=14, weight="bold"))
                info_value.grid(row=i+1, column=1, sticky="e", pady=5)
                
            
            # Boutons du bas
            self.action_frame = ctk.CTkFrame(self.left_column, fg_color="#292929")
            self.action_frame.grid(row=2, column=0, sticky="ew", pady=5)
            
            self.add_button = ctk.CTkButton(self.action_frame, text="+", fg_color="#00CC66", hover_color="#00AA55", 
                                        corner_radius=5, width=40, height=30)
            self.add_button.grid(row=0, column=0, padx=(0, 10))
            
            self.transaction_button = ctk.CTkButton(self.action_frame, text="+ Ajouter Argent", fg_color="#00CC66", 
                                                hover_color="#00AA55", corner_radius=5, width=150, height=30,command=self.add_money)
            self.transaction_button.grid(row=0, column=1)
            
            # Graphique et historique
            self.right_column = ctk.CTkFrame(self.account_content, fg_color="#292929")
            self.right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            
            # Espace pour le graphique
            self.chart_frame = ctk.CTkFrame(self.right_column, fg_color="#333333", height=200)
            self.chart_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
            
            # Graphique
            # Appel de la méthode pour créer le graphique
            self.create_transaction_chart()
            
            # Transactions
            self.history_frame = ctk.CTkFrame(self.right_column, fg_color="#292929")
            self.history_frame.grid(row=1, column=0, sticky="nsew")
            
            history_title = ctk.CTkLabel(self.history_frame, text="Historique", font=ctk.CTkFont(size=16, weight="bold"))
            history_title.grid(row=0, column=0, sticky="w", pady=(0, 10))

            view_all2_btn = ctk.CTkButton(self.history_frame, text="Tout voir", fg_color="#00CC66", hover_color="#00AA55", 
                                        corner_radius=5, width=80, height=25,command=self.show_history_frame)
            view_all2_btn.grid(row=0, column=2, padx=20, pady=(0, 10))

            bottom_image = ctk.CTkImage(light_image=Image.open("bottom.png"), size=(40,20 ))
            up_image = ctk.CTkImage(light_image=Image.open("up.png"), size=(40,20 ))

            self.transactions = []
            num_transactions = min(4, len(self.transa))

            for i in range(num_transactions):
                self.transactions.append({
                    "price": f"{self.transa[i][7]} €", 
                    "type": self.transa[i][4]
                })

            for i in range(num_transactions, 4):
                self.transactions.append({
                    "price": "0.00 €",
                    "type": "Aucune transaction"
                })

            for i, price in enumerate(self.transactions):
                price_label = ctk.CTkLabel(self.history_frame, text=price["price"], font=ctk.CTkFont(size=14, weight="bold"))
                price_label.grid(row=i+1, column=1, sticky="w", pady=5)
                
                if price["type"] == "Aucune transaction":
                    icon_label = ctk.CTkLabel(self.history_frame, image=None, text="")
                else:
                    icon_label = ctk.CTkLabel(self.history_frame, image=bottom_image if float(price["price"].replace("€", "").strip()) < 0 else up_image, text="")
                icon_label.grid(row=i+1, column=0, sticky="w", pady=5)

                if price["type"] == "Aucune transaction":
                    text_color = "gray"
                else:
                    text_color = "red" if float(price["price"].replace("€", "").strip()) < 0 else "green"
                
                type_label = ctk.CTkLabel(self.history_frame, text=price["type"], font=ctk.CTkFont(size=14, weight="bold"), text_color=text_color)
                type_label.grid(row=i+1, column=2, sticky="w", pady=5, padx=30)



    #Frame history
    def show_history_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.geometry("1400x775")

        self.main_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(self.main_frame, text="Historique des transactions", 
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Section des filtres
        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="#333333", corner_radius=10)
        filter_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Première ligne de filtres
        filter_label = ctk.CTkLabel(filter_frame, text="Filtres:", font=ctk.CTkFont(size=16, weight="bold"))
        filter_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Filtre par date
        date_label = ctk.CTkLabel(filter_frame, text="Date:", font=ctk.CTkFont(size=14))
        date_label.grid(row=0, column=1, padx=(20, 5), pady=10, sticky="w")
        
        self.date_from_entry = ctk.CTkEntry(filter_frame, width=100, placeholder_text="AAAA-MM-JJ")
        self.date_from_entry.grid(row=0, column=2, padx=5, pady=10, sticky="w")
        
        date_to_label = ctk.CTkLabel(filter_frame, text="à", font=ctk.CTkFont(size=14))
        date_to_label.grid(row=0, column=3, padx=5, pady=10)
        
        self.date_to_entry = ctk.CTkEntry(filter_frame, width=100, placeholder_text="AAAA-MM-JJ")
        self.date_to_entry.grid(row=0, column=4, padx=5, pady=10, sticky="w")
        
        # Filtre par catégorie
        category_label = ctk.CTkLabel(filter_frame, text="Catégorie:", font=ctk.CTkFont(size=14))
        category_label.grid(row=0, column=5, padx=(20, 5), pady=10, sticky="w")
        
        # Récupérer les catégories uniques de la base de données
        self.cursor.execute("SELECT DISTINCT categorie FROM transaction WHERE id_compte = %s", (self.id,))
        categories = [cat[0] for cat in self.cursor.fetchall()]
        categories.insert(0, "Toutes")
        
        self.category_var = ctk.StringVar(value="Toutes")
        self.category_dropdown = ctk.CTkOptionMenu(filter_frame, values=categories, variable=self.category_var, width=150)
        self.category_dropdown.grid(row=0, column=6, padx=5, pady=10, sticky="w")
        
        # Deuxième ligne de filtres
        # Filtre par type
        type_label = ctk.CTkLabel(filter_frame, text="Type:", font=ctk.CTkFont(size=14))
        type_label.grid(row=1, column=1, padx=(20, 5), pady=10, sticky="w")
        
        self.cursor.execute("SELECT DISTINCT type FROM transaction WHERE id_compte = %s", (self.id,))
        types = [t[0] for t in self.cursor.fetchall()]
        types.insert(0, "Tous")
        
        self.type_var = ctk.StringVar(value="Tous")
        self.type_dropdown = ctk.CTkOptionMenu(filter_frame, values=types, variable=self.type_var, width=150)
        self.type_dropdown.grid(row=1, column=2, padx=5, pady=10, sticky="w")
        
        # Tri par montant
        sort_label = ctk.CTkLabel(filter_frame, text="Tri par montant:", font=ctk.CTkFont(size=14))
        sort_label.grid(row=1, column=3, padx=(20, 5), pady=10, sticky="w")
        
        sort_options = ["Aucun", "Croissant", "Décroissant"]
        self.sort_var = ctk.StringVar(value="Aucun")
        self.sort_dropdown = ctk.CTkOptionMenu(filter_frame, values=sort_options, variable=self.sort_var, width=120)
        self.sort_dropdown.grid(row=1, column=4, padx=5, pady=10, sticky="w")
        
        # Boutons de recherche et réinitialisation
        buttons_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=6, padx=10, pady=10, sticky="e")
        
        reset_filters_btn = ctk.CTkButton(buttons_frame, text="Réinitialiser", fg_color="#555555", 
                                        hover_color="#444444", corner_radius=5, width=120, 
                                        command=self.reset_filters)
        reset_filters_btn.grid(row=0, column=0, padx=(0, 10))
        
        search_btn = ctk.CTkButton(buttons_frame, text="Rechercher", fg_color="#00CC66", 
                                hover_color="#00AA55", corner_radius=5, width=120,
                                command=self.apply_filters)
        search_btn.grid(row=0, column=1)
        
        # Frame pour les transactions
        self.container_frame = ctk.CTkFrame(self.main_frame, fg_color="#292929")
        self.container_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        # Définir les largeurs des colonnes
        self.col_widths = [60, 150, 150, 350, 120, 120]
        
        header_frame = ctk.CTkFrame(self.container_frame, fg_color="#1F1F1F")
        header_frame.grid(row=0, column=0, sticky="ew")
        
        headers = ["", "Type", "Catégorie", "Description", "Montant", "Date"]
        
        for col, (text, width) in enumerate(zip(headers, self.col_widths)):
            header_label = ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(size=16, weight="bold"), width=width)
            header_label.grid(row=0, column=col, padx=5, pady=8, sticky="w")
        
        # Afficher les transactions (en utilisant les données non filtrées par défaut)
        self.display_transactions(self.transa)


    #Show transaction on history_frame
    def display_transactions(self, transactions):
        for widget in self.container_frame.winfo_children():
            if widget.winfo_class() == "CTkScrollableFrame":
                widget.destroy()
        
        scroll_frame = ctk.CTkScrollableFrame(self.container_frame, fg_color="#292929", 
                                            width=sum(self.col_widths)+30, height=400)
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.container_frame.grid_rowconfigure(1, weight=1)
        
        bottom_image = ctk.CTkImage(light_image=Image.open("bottom.png"), size=(40, 20))
        up_image = ctk.CTkImage(light_image=Image.open("up.png"), size=(40, 20))
        
        if not transactions:
            no_data_label = ctk.CTkLabel(scroll_frame, text="Aucune transaction ne correspond aux critères de recherche", 
                                        font=ctk.CTkFont(size=14, weight="bold"))
            no_data_label.grid(row=0, column=0, padx=20, pady=50, sticky="ew")
            return
        
        for i, transac in enumerate(transactions):
            bg_color = "#333333" if i % 2 == 0 else "#2A2A2A"
            transaction_row = ctk.CTkFrame(scroll_frame, fg_color=bg_color)
            transaction_row.grid(row=i, column=0, sticky="ew", pady=2)
            
            transac_type = transac[4]
            transac_category = transac[5]
            transac_description = transac[2]
            transac_amount = f"{transac[7]} €"
            transac_date = transac[3]
            
            icon = bottom_image if transac_type == "Paiement CB" else up_image
            text_color = "red" if float(transac[7]) < 0 else "green"
            
            icon_label = ctk.CTkLabel(transaction_row, image=icon, text="", width=self.col_widths[0])
            icon_label.grid(row=0, column=0, padx=5, pady=8, sticky="w")
            
            type_label = ctk.CTkLabel(transaction_row, text=transac_type, 
                                    font=ctk.CTkFont(size=14, weight="bold"), 
                                    text_color=text_color, width=self.col_widths[1])
            type_label.grid(row=0, column=1, padx=5, pady=8, sticky="w")
            
            category_label = ctk.CTkLabel(transaction_row, text=transac_category, 
                                        font=ctk.CTkFont(size=14, weight="bold"), 
                                        text_color="white", width=self.col_widths[2])
            category_label.grid(row=0, column=2, padx=5, pady=8, sticky="w")
            
            description_label = ctk.CTkLabel(transaction_row, text=transac_description, 
                                            font=ctk.CTkFont(size=14), 
                                            text_color="gray", width=self.col_widths[3])
            description_label.grid(row=0, column=3, padx=5, pady=8, sticky="w")
            
            amount_label = ctk.CTkLabel(transaction_row, text=transac_amount, 
                                        font=ctk.CTkFont(size=14, weight="bold"), 
                                        width=self.col_widths[4])
            amount_label.grid(row=0, column=4, padx=5, pady=8, sticky="e")
            
            date_label = ctk.CTkLabel(transaction_row, text=transac_date, 
                                    font=ctk.CTkFont(size=12), 
                                    width=self.col_widths[5])
            date_label.grid(row=0, column=5, padx=5, pady=8, sticky="e")

    #Reset Filters
    def reset_filters(self):
        self.date_from_entry.delete(0, 'end')
        self.date_to_entry.delete(0, 'end')
        self.category_var.set("Toutes")
        self.type_var.set("Tous")
        self.sort_var.set("Aucun")
        
        self.display_transactions(self.transa)

    #Apply filters on transaction
    def apply_filters(self):
        date_from = self.date_from_entry.get()
        date_to = self.date_to_entry.get()
        category = self.category_var.get()
        transaction_type = self.type_var.get()
        sort_order = self.sort_var.get()
        
        query = "SELECT * FROM transaction WHERE id_compte = %s"
        params = [self.id]
        
        if date_from:
            query += " AND date >= %s"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= %s"
            params.append(date_to)
        
        if category != "Toutes":
            query += " AND categorie = %s"
            params.append(category)
        
        if transaction_type != "Tous":
            query += " AND type = %s"
            params.append(transaction_type)
        
        if sort_order == "Croissant":
            query += " ORDER BY montant ASC"
        elif sort_order == "Décroissant":
            query += " ORDER BY montant DESC"
        else:
            query += " ORDER BY ID DESC"
        
        self.cursor.execute(query, tuple(params))
        filtered_transactions = self.cursor.fetchall()
        
        self.display_transactions(filtered_transactions)


    #Frame for add money
    def add_money(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(self.main_frame, text="Ajouter de l'argent", 
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")
        
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#333333", corner_radius=10)
        form_frame.grid(row=1, column=0, columnspan=2, padx=50, pady=20, sticky="new")
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=2)
        
        subtitle_label = ctk.CTkLabel(form_frame, text="Dépôt sur votre compte", 
                                    font=ctk.CTkFont(size=18, weight="bold"))
        subtitle_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 30), sticky="w")
        
        amount_label = ctk.CTkLabel(form_frame, text="Montant (€):", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        amount_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.amount_entry = ctk.CTkEntry(form_frame, width=200, placeholder_text="0.00")
        self.amount_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        source_label = ctk.CTkLabel(form_frame, text="Source:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        source_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        sources = ["Virement bancaire", "Espèces", "Chèque", "Autre"]
        source_var = ctk.StringVar(value=sources[0])
        self.source_dropdown = ctk.CTkOptionMenu(form_frame, values=sources, variable=source_var)
        self.source_dropdown.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        category_label = ctk.CTkLabel(form_frame, text="Catégorie:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        category_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        categories = ["Salaire", "Remboursement", "Cadeau", "Économies", "Investissement", "Autre"]
        category_var = ctk.StringVar(value=categories[0])
        self.category_dropdown = ctk.CTkOptionMenu(form_frame, values=categories, variable=category_var)
        self.category_dropdown.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        
        description_label = ctk.CTkLabel(form_frame, text="Description:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        description_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        self.description_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Description de la transaction")
        self.description_entry.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        
        date_label = ctk.CTkLabel(form_frame, text="Date:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        date_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.grid(row=5, column=1, padx=20, pady=10, sticky="w")
        
        from datetime import datetime
        current_date = datetime.now()
        
        self.day_entry = ctk.CTkEntry(date_frame, width=50, placeholder_text="JJ")
        self.day_entry.grid(row=0, column=0, padx=(0, 5))
        self.day_entry.insert(0, current_date.day)
        
        self.month_entry = ctk.CTkEntry(date_frame, width=50, placeholder_text="MM")
        self.month_entry.grid(row=0, column=1, padx=5)
        self.month_entry.insert(0, current_date.month)
        
        self.year_entry = ctk.CTkEntry(date_frame, width=70, placeholder_text="AAAA")
        self.year_entry.grid(row=0, column=2, padx=(5, 0))
        self.year_entry.insert(0, current_date.year)
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=(30, 20), sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text="Annuler", fg_color="#555555", 
                                    hover_color="#444444", corner_radius=5, width=120, 
                                    command=self.main_frame)
        cancel_button.grid(row=0, column=0, padx=(0, 10))

        validate_button = ctk.CTkButton(button_frame, text="Valider", fg_color="#00CC66", 
                                    hover_color="#00AA55", corner_radius=5, width=120,command=self.add_transac)
        validate_button.grid(row=0, column=1)


    #For validate add money 
    def add_transac(self):
        description = self.description_entry.get()
        day = self.day_entry.get()
        month = self.month_entry.get()
        year = self.year_entry.get()
        date = f"{year}-{month}-{day}"
        source = self.source_dropdown.get()
        category = self.category_dropdown.get()
        amount = float(self.amount_entry.get())

        self.cursor.execute("INSERT INTO transaction(description,date,type,categorie,id_compte,montant) VALUES (%s,%s,%s,%s,%s,%s)", (description,date,source,category,self.id,amount))
        self.connection.commit()

        self.cursor.execute("UPDATE compte SET solde = solde + %s WHERE id = %s", (amount, self.id))
        self.connection.commit()
        
        self.cursor.execute("SELECT solde FROM compte WHERE id = %s", (self.id,))
        self.solde = self.cursor.fetchone()
        self.solde_value = 0 if self.solde[0] == None else self.solde[0]
        
        self.cursor.execute("SELECT * FROM transaction WHERE id_compte = %s ORDER BY ID DESC", (self.id,))
        self.transa = self.cursor.fetchall()
        self.show_notif("Transaction effectué", "#00CC66")

    def show_accounts(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        self.geometry("1000x600")
        
        title_label = ctk.CTkLabel(self.main_frame, text="Mes Comptes", 
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="w")
        
        self.cursor.execute("SELECT * FROM compte WHERE user_id = %s", (self.user_id,))
        accounts = self.cursor.fetchall()
        
        accounts_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#292929")
        accounts_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        add_account_btn = ctk.CTkButton(self.main_frame, text="+ Ajouter un compte", 
                                    fg_color="#00CC66", hover_color="#00AA55", 
                                    corner_radius=5, height=35,command=self.add_account)
        add_account_btn.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="e")
        
        if not accounts:
            no_accounts_label = ctk.CTkLabel(accounts_frame, text="Vous n'avez pas encore de compte", 
                                        font=ctk.CTkFont(size=16))
            no_accounts_label.grid(row=0, column=0, padx=20, pady=40)
            return
        
        # Créer une carte pour chaque compte
        for i, account in enumerate(accounts):
            account_id = account[0]
            account_name = account[1]
            account_balance = account[3] if account[3] is not None else 0
            account_iban = account[5] if account[5] is not None else "N/A"
            account_date = account[6] if account[6] is not None else "N/A"
            
            account_card = ctk.CTkFrame(accounts_frame, fg_color="#333333", corner_radius=10)
            account_card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            accounts_frame.grid_columnconfigure(0, weight=1)
            
            card_left = ctk.CTkFrame(account_card, fg_color="transparent")
            card_left.grid(row=0, column=0, padx=20, pady=20, sticky="w")
            
            header_frame = ctk.CTkFrame(card_left, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew")
            
            name_label = ctk.CTkLabel(header_frame, text=account_name, 
                                    font=ctk.CTkFont(size=18, weight="bold"))
            name_label.grid(row=0, column=0, sticky="w")
            
            info_frame = ctk.CTkFrame(card_left, fg_color="transparent")
            info_frame.grid(row=1, column=0, pady=(10, 0), sticky="w")
            
            iban_label = ctk.CTkLabel(info_frame, text=f"IBAN: {account_iban}", 
                                    font=ctk.CTkFont(size=14))
            iban_label.grid(row=0, column=0, sticky="w", pady=2)
            
            date_label = ctk.CTkLabel(info_frame, text=f"Créé le: {account_date}", 
                                    font=ctk.CTkFont(size=14))
            date_label.grid(row=1, column=0, sticky="w", pady=2)
            
            card_right = ctk.CTkFrame(account_card, fg_color="transparent")
            card_right.grid(row=0, column=1, padx=20, pady=20, sticky="e")
            account_card.grid_columnconfigure(1, weight=1)
            
            balance_frame = ctk.CTkFrame(card_right, fg_color="#00CC66", corner_radius=5)
            balance_frame.grid(row=0, column=0, sticky="e")
            
            balance_label = ctk.CTkLabel(balance_frame, text=f"{account_balance} €", 
                                    font=ctk.CTkFont(size=18, weight="bold"),
                                    text_color="white")
            balance_label.grid(row=0, column=0, padx=15, pady=10)
            
            buttons_frame = ctk.CTkFrame(card_right, fg_color="transparent")
            buttons_frame.grid(row=1, column=0, pady=(15, 0), sticky="e")
            
            view_btn = ctk.CTkButton(buttons_frame, text="Voir", fg_color="#444444", 
                                hover_color="#333333", corner_radius=5, width=80,
                                command=lambda acc_id=account_id: self.view_account(acc_id))
            view_btn.grid(row=0, column=0, padx=(0, 10))
            
            delete_btn = ctk.CTkButton(buttons_frame, text="Supprimer", fg_color="#FF3333", 
                        hover_color="#CC0000", corner_radius=5, width=80,
                        command=lambda acc_id=account_id: self.delete_account(acc_id))
            delete_btn.grid(row=0, column=1)


    #Function for account view(sql)
    def view_account(self, account_id):
        self.id = account_id
        
        self.cursor.execute("SELECT nom FROM compte WHERE id = %s", (self.id,))
        self.nom_compte = self.cursor.fetchone()
        self.cursor.execute("SELECT solde FROM compte WHERE id = %s", (self.id,))
        self.solde = self.cursor.fetchone()
        self.solde_value = 0 if self.solde[0] is None else self.solde[0]
        self.cursor.execute("SELECT IBAN FROM compte WHERE id = %s", (self.id,))
        self.iban = self.cursor.fetchone()
        self.cursor.execute("SELECT date_create FROM compte WHERE id = %s", (self.id,))
        self.date = self.cursor.fetchone()
        self.cursor.execute("SELECT * FROM transaction WHERE id_compte = %s ORDER BY ID DESC", (self.id,))
        self.transa = self.cursor.fetchall()
        
        self.reset_main_frame()

    #Added account in frame(graphic) 
    def add_account(self):
        self.cursor.execute("SELECT COUNT(*) FROM compte WHERE user_id = %s", (self.user_id,))
        account_count = self.cursor.fetchone()[0]

        if account_count >= 4:
            self.show_notif("Vous avez déjà 4 comptes. Impossible d'en créer plus.", "#FF5555")
            return

        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        title_label = ctk.CTkLabel(self.main_frame, text="Créer un nouveau compte", 
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="w")
        
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#333333", corner_radius=10)
        form_frame.grid(row=1, column=0, padx=50, pady=20, sticky="new")
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=2)
        
        name_label = ctk.CTkLabel(form_frame, text="Nom du compte:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        name_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.account_name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="ex: Compte courant")
        self.account_name_entry.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        
        balance_label = ctk.CTkLabel(form_frame, text="Solde initial (€):", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        balance_label.grid(row=1, column=0, padx=20, pady=20, sticky="w")
        
        self.initial_balance_entry = ctk.CTkEntry(form_frame, width=200, placeholder_text="0.00")
        self.initial_balance_entry.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        
        iban_label = ctk.CTkLabel(form_frame, text="IBAN:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        iban_label.grid(row=3, column=0, padx=20, pady=20, sticky="w")
        
        iban_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        iban_frame.grid(row=3, column=1, padx=20, pady=20, sticky="w")
        
        self.generate_iban_btn = ctk.CTkButton(iban_frame, text="Générer un IBAN", 
                                            fg_color="#555555", hover_color="#444444", 
                                            corner_radius=5, width=150, command=self.generate_iban)
        self.generate_iban_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.iban_display = ctk.CTkLabel(iban_frame, text="", font=ctk.CTkFont(size=14))
        self.iban_display.grid(row=0, column=1)
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(40, 20), sticky="e")
        
        cancel_button = ctk.CTkButton(button_frame, text="Annuler", fg_color="#555555", 
                                    hover_color="#444444", corner_radius=5, width=120, 
                                    command=self.show_accounts)
        cancel_button.grid(row=0, column=0, padx=(0, 10))
        
        create_button = ctk.CTkButton(button_frame, text="Créer", fg_color="#00CC66", 
                                    hover_color="#00AA55", corner_radius=5, width=120,
                                    command=self.create_account)
        create_button.grid(row=0, column=1)

    def generate_iban(self):
        import random
        self.iban = f"FR{random.randint(1000000, 9999999)}"
        self.iban_display.configure(text=self.iban)
        self.generated_iban = True

    #For create new account
    def create_account(self):
        account_name = self.account_name_entry.get()
        
        try:
            initial_balance = float(self.initial_balance_entry.get()) if self.initial_balance_entry.get() else 0
        except ValueError:
            self.show_notif("Le solde initial ne peut pas être négatif", "#FF5555")
            return
        
        # Vérifier si un IBAN a été généré
        if not hasattr(self, 'generated_iban'):
            self.show_notif("Veuillez génerer un IBAN", "#FF5555")
            return
        
        # Vérifier si le nom du compte est renseigné
        if not account_name:
            self.show_notif("Le nom du compte est requis", "#FF5555")
            return
        
        # Insérer le nouveau compte dans la base de données
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        self.cursor.execute(
            "INSERT INTO compte (nom, solde, user_id, IBAN, date_create) VALUES (%s, %s, %s, %s, %s)",
            (account_name, initial_balance, self.user_id, self.iban, current_date)
        )
        self.connection.commit()
            
        if initial_balance > 0:
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            new_account_id = self.cursor.fetchone()[0]
                
            self.cursor.execute(
                "INSERT INTO transaction (description, date, type, categorie, id_compte, montant) VALUES (%s, %s, %s, %s, %s, %s)",
                ("Dépôt initial", current_date, "Dépôt", "Autre", new_account_id, initial_balance)
            )
            self.connection.commit()
            
        self.show_notif("Compte crée avec succés", "#32CD32")
        self.show_accounts()

    #For create a notif
    def show_notif(self, message, couleur="#32CD32"):
        notification = ctk.CTkLabel(self.main_frame, text=message, font=("Poppins", 14, "bold"), text_color="white", fg_color=couleur, corner_radius=10)
        notification.place(relx=0.5, rely=0.13, anchor="center")
        self.after(3000, notification.destroy)

    #Show settings
    def show_settings(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
                
        self.geometry("1000x600")
            
        title_label = ctk.CTkLabel(self.main_frame, text="Paramètres", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#292929")
        scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        profile_frame = ctk.CTkFrame(scrollable_frame, fg_color="#333333", corner_radius=10)
        profile_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        profile_title = ctk.CTkLabel(profile_frame, text="Profil utilisateur", font=ctk.CTkFont(size=16, weight="bold"))
        profile_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        profile_info_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        profile_info_frame.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        avatar_circle = ctk.CTkButton(profile_info_frame, text="", fg_color="#00FF7F", width=80, height=80, 
                                    corner_radius=40, hover=False, border_width=0)
        avatar_circle.grid(row=0, column=0, padx=20, pady=10, rowspan=4)
        
        name_label = ctk.CTkLabel(profile_info_frame, text="Nom:", font=ctk.CTkFont(size=14))
        name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        name_value = ctk.CTkLabel(profile_info_frame, text=f"{self.nom_user[0][0]}", font=ctk.CTkFont(size=14, weight="bold"))
        name_value.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        firstname_label = ctk.CTkLabel(profile_info_frame, text="Prénom:", font=ctk.CTkFont(size=14))
        firstname_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        firstname_value = ctk.CTkLabel(profile_info_frame, text=f"{self.nom_user[0][1]}", font=ctk.CTkFont(size=14, weight="bold"))
        firstname_value.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        self.cursor.execute("SELECT mail FROM utilisateur WHERE id = %s", (self.user_id,))
        email = self.cursor.fetchone()
        
        email_label = ctk.CTkLabel(profile_info_frame, text="Email:", font=ctk.CTkFont(size=14))
        email_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        email_value = ctk.CTkLabel(profile_info_frame, text=email[0] if email else "Non défini", font=ctk.CTkFont(size=14, weight="bold"))
        email_value.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        edit_profile_btn = ctk.CTkButton(profile_frame, text="Modifier mon profil", fg_color="#00CC66", 
                                        hover_color="#00AA55", corner_radius=5, 
                                        command=self.edit_profile)
        edit_profile_btn.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        security_frame = ctk.CTkFrame(scrollable_frame, fg_color="#333333", corner_radius=10)
        security_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        security_title = ctk.CTkLabel(security_frame, text="Sécurité", font=ctk.CTkFont(size=16, weight="bold"))
        security_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        change_password_btn = ctk.CTkButton(security_frame, text="Changer mon mot de passe", fg_color="#00CC66", 
                                        hover_color="#00AA55", corner_radius=5,
                                        command=self.change_password)
        change_password_btn.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        two_factor_frame = ctk.CTkFrame(security_frame, fg_color="transparent")
        two_factor_frame.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        two_factor_label = ctk.CTkLabel(two_factor_frame, text="Authentification à deux facteurs:", font=ctk.CTkFont(size=14))
        two_factor_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.two_factor_var = ctk.BooleanVar(value=False)
        two_factor_switch = ctk.CTkSwitch(two_factor_frame, text="", variable=self.two_factor_var, 
                                        switch_width=50, switch_height=25, 
                                        fg_color="#555555", progress_color="#00CC66",
                                        command=self.toggle_two_factor)
        two_factor_switch.grid(row=0, column=1, padx=10, pady=5)
        
        notification_frame = ctk.CTkFrame(scrollable_frame, fg_color="#333333", corner_radius=10)
        notification_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        notification_title = ctk.CTkLabel(notification_frame, text="Notifications", font=ctk.CTkFont(size=16, weight="bold"))
        notification_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        notification_options = [
            {"text": "Alertes de transactions", "default": True},
            {"text": "Alertes de solde bas", "default": True},
            {"text": "Offres promotionnelles", "default": False}
        ]
        
        for i, option in enumerate(notification_options):
            option_frame = ctk.CTkFrame(notification_frame, fg_color="transparent")
            option_frame.grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
            
            option_label = ctk.CTkLabel(option_frame, text=option["text"], font=ctk.CTkFont(size=14))
            option_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            option_var = ctk.BooleanVar(value=option["default"])
            option_switch = ctk.CTkSwitch(option_frame, text="", variable=option_var, 
                                        switch_width=50, switch_height=25, 
                                        fg_color="#555555", progress_color="#00CC66")
            option_switch.grid(row=0, column=1, padx=10, pady=5)
        
        appearance_frame = ctk.CTkFrame(scrollable_frame, fg_color="#333333", corner_radius=10)
        appearance_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        appearance_title = ctk.CTkLabel(appearance_frame, text="Apparence", font=ctk.CTkFont(size=16, weight="bold"))
        appearance_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_frame.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        theme_label = ctk.CTkLabel(theme_frame, text="Thème:", font=ctk.CTkFont(size=14))
        theme_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.theme_var = ctk.StringVar(value="Sombre")
        theme_options = ["Sombre", "Clair"]
        theme_dropdown = ctk.CTkOptionMenu(theme_frame, values=theme_options, variable=self.theme_var, width=150,
                                        command=self.change_theme)
        theme_dropdown.grid(row=0, column=1, padx=10, pady=5)
        
        buttons_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, padx=20, pady=20, sticky="e")
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", fg_color="#555555", 
                                hover_color="#444444", corner_radius=5, width=120,
                                command=self.reset_main_frame)
        cancel_btn.grid(row=0, column=0, padx=(0, 10))
        
        save_btn = ctk.CTkButton(buttons_frame, text="Enregistrer", fg_color="#00CC66", 
                                hover_color="#00AA55", corner_radius=5, width=120,
                                command=self.save_settings)
        save_btn.grid(row=0, column=1)

    #For edit profil
    def edit_profile(self):
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Modifier mon profil")
        edit_window.geometry("400x300")
        edit_window.focus_set()
        
        title_label = ctk.CTkLabel(edit_window, text="Modifier mon profil", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        form_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        self.cursor.execute("SELECT nom, prenom, mail FROM utilisateur WHERE id = %s", (self.user_id,))
        user_data = self.cursor.fetchone()
        
        name_label = ctk.CTkLabel(form_frame, text="Nom:", anchor="w")
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ctk.CTkEntry(form_frame, width=200)
        name_entry.insert(0, user_data[0])
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        firstname_label = ctk.CTkLabel(form_frame, text="Prénom:", anchor="w")
        firstname_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        firstname_entry = ctk.CTkEntry(form_frame, width=200)
        firstname_entry.insert(0, user_data[1])
        firstname_entry.grid(row=1, column=1, padx=10, pady=5)
        
        email_label = ctk.CTkLabel(form_frame, text="Email:", anchor="w")
        email_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        email_entry = ctk.CTkEntry(form_frame, width=200)
        email_entry.insert(0, user_data[2] if user_data[2] else "")
        email_entry.grid(row=2, column=1, padx=10, pady=5)
        
        buttons_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", fg_color="#555555", 
                                hover_color="#444444", corner_radius=5, width=100,
                                command=edit_window.destroy)
        cancel_btn.grid(row=0, column=0, padx=10)
        
        #Save changes
        def save_profile():
            self.cursor.execute("UPDATE utilisateur SET nom = %s, prenom = %s, mail = %s WHERE id = %s", 
                            (name_entry.get(), firstname_entry.get(), email_entry.get(), self.user_id))
            self.connection.commit()
            self.show_notif("Profil mis à jour avec succès")
            edit_window.destroy()
            self.show_settings()

        
        save_btn = ctk.CTkButton(buttons_frame, text="Enregistrer", fg_color="#00CC66", 
                                hover_color="#00AA55", corner_radius=5, width=100,
                                command=save_profile)
        save_btn.grid(row=0, column=1, padx=10)

    #Change password
    def change_password(self):
        password_window = ctk.CTkToplevel(self)
        password_window.title("Changer mon mot de passe")
        password_window.geometry("400x300")
        password_window.focus_set()
        
        password_window.update_idletasks()
        password_window.geometry("500x300")
        
        title_label = ctk.CTkLabel(password_window, text="Changer mon mot de passe", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        form_frame = ctk.CTkFrame(password_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        current_pwd_label = ctk.CTkLabel(form_frame, text="Mot de passe actuel:", anchor="w")
        current_pwd_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        current_pwd_entry = ctk.CTkEntry(form_frame, width=200, show="*")
        current_pwd_entry.grid(row=0, column=1, padx=10, pady=5)
        
        new_pwd_label = ctk.CTkLabel(form_frame, text="Nouveau mot de passe:", anchor="w")
        new_pwd_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        new_pwd_entry = ctk.CTkEntry(form_frame, width=200, show="*")
        new_pwd_entry.grid(row=1, column=1, padx=10, pady=5)
        
        confirm_pwd_label = ctk.CTkLabel(form_frame, text="Confirmer mot de passe:", anchor="w")
        confirm_pwd_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        confirm_pwd_entry = ctk.CTkEntry(form_frame, width=200, show="*")
        confirm_pwd_entry.grid(row=2, column=1, padx=10, pady=5)
        
        buttons_frame = ctk.CTkFrame(password_window, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Annuler", fg_color="#555555", 
                                hover_color="#444444", corner_radius=5, width=100,
                                command=password_window.destroy)
        cancel_btn.grid(row=0, column=0, padx=10)
        
    
        #Save password
        def save_password():
            current = current_pwd_entry.get()
            new = new_pwd_entry.get()
            confirm = confirm_pwd_entry.get()
            
            if not current or not new or not confirm:
                self.show_notif("Tous les champs sont obligatoires", "#FF5252")
                return
                
            if new != confirm:
                self.show_notif("Les mots de passe ne correspondent pas", "#FF5252")
                return
                
            self.cursor.execute("SELECT mot_de_passe FROM utilisateur WHERE id = %s", (self.user_id,))
            stored_password = self.cursor.fetchone()[0]
            
            if stored_password != current:
                self.show_notif("Mot de passe actuel incorrect", "#FF5252")
                return
                
            try:
                self.cursor.execute("UPDATE utilisateur SET mot_de_passe = %s WHERE id = %s", (new, self.user_id))
                self.connection.commit()
                self.show_notif("Mot de passe modifié avec succès")
                password_window.destroy()
            except Exception as e:
                self.show_notif(f"Erreur lors de la modification du mot de passe: {str(e)}", "#FF5252")
        
        save_btn = ctk.CTkButton(buttons_frame, text="Enregistrer", fg_color="#00CC66", 
                                hover_color="#00AA55", corner_radius=5, width=100,
                                command=save_password)
        save_btn.grid(row=0, column=1, padx=10)

    def toggle_two_factor(self):
        state = "activée" if self.two_factor_var.get() else "désactivée"
        self.show_notif(f"Authentification à deux facteurs {state}")

    def change_theme(self, choice):
        if choice == "Sombre":
            ctk.set_appearance_mode("dark")
        elif choice == "Clair":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        self.show_notif(f"Thème changé pour: {choice}")

    def save_settings(self):
        self.show_notif("Paramètres enregistrés avec succès")
        self.reset_main_frame()

    def delete_account(self, account_id):
        confirm = messagebox.askyesno("Confirmation", 
                                    "Êtes-vous sûr de vouloir supprimer ce compte ?",
                                    parent=self)
        
        if confirm:
            self.cursor.execute("DELETE FROM transaction WHERE id_compte = %s", (account_id,))
                
            self.cursor.execute("DELETE FROM compte WHERE id = %s", (account_id,))
                
            self.connection.commit()
                
            messagebox.showinfo("Succès", "Le compte a été supprimé avec succès.", parent=self)
                
            self.show_accounts()
                
    #Graphics of transaction
    def create_transaction_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        try:
            data = []
            for trans in self.transa:
                try:
                    date = datetime.strptime(str(trans[3]), '%Y-%m-%d')
                    amount = float(trans[7])
                    data.append({'date': date, 'amount': amount})
                except:
                    continue
            
            if data:
                df = pd.DataFrame(data)
                df = df.sort_values('date')
                
                df = df.groupby('date').sum().reset_index()
                
                initial_balance = float(self.solde_value)
                df['cumulative_balance'] = df['amount'].cumsum()
                last_transactions = min(len(df), 10) 
                df = df.tail(last_transactions).set_index('date')
            else:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=9)
                dates = [start_date + timedelta(days=i) for i in range(10)]
                
                initial_balance = float(self.solde_value)
                np.random.seed(42)
                daily_changes = np.random.normal(50, 200, len(dates))
                
                df = pd.DataFrame({
                    'date': dates,
                    'amount': daily_changes
                })
                
                df['cumulative_balance'] = df['amount'].cumsum()
                df = df.set_index('date')
        except Exception as e:
            error_label = ctk.CTkLabel(self.chart_frame, text=f"Impossible d'afficher le graphique", font=ctk.CTkFont(size=16))
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        fig, ax = plt.subplots(figsize=(5, 2.5))
        fig.patch.set_facecolor('#333333')
        ax.set_facecolor('#333333')
        

        ax.spines['bottom'].set_color('#AAAAAA')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#AAAAAA')
        ax.tick_params(axis='x', colors='#DDDDDD')
        ax.tick_params(axis='y', colors='#DDDDDD')
        ax.yaxis.label.set_color('#DDDDDD')
        ax.xaxis.label.set_color('#DDDDDD')
        ax.title.set_color('#DDDDDD')
        
        ax.plot(df.index, df['cumulative_balance'], color='#00FF7F', linewidth=2, marker='o', markersize=4)
        
        if len(df) > 1:
            min_val = df['cumulative_balance'].min()
            max_val = df['cumulative_balance'].max()

            if min_val != max_val:
                gradient = np.atleast_2d(np.linspace(0, 1, 256)).T
                ax.fill_between(df.index, df['cumulative_balance'], min_val, alpha=0.2, color='#00CC66')
        
        ax.set_title('Évolution du solde', fontsize=12, pad=10)
        ax.set_ylabel('Solde (€)', fontsize=10)
        
        if len(df) > 4:
            step = len(df) // 4
            ax.set_xticks(df.index[::step])
        plt.xticks(rotation=45)
        
        ax.grid(True, linestyle='--', alpha=0.3, color='#AAAAAA')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_analysis(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        self.geometry("1200x700")
        
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="#292929")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        title_label = ctk.CTkLabel(title_frame, text=f"Analyse de compte - {self.nom_compte[0]}", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        back_button = ctk.CTkButton(title_frame, text="Retour", fg_color="#555555", 
                                hover_color="#444444", width=100, command=self.reset_main_frame)
        back_button.grid(row=0, column=1, padx=20, sticky="e")
        
        analysis_container = ctk.CTkFrame(self.main_frame, fg_color="#292929")
        analysis_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        analysis_container.grid_columnconfigure(0, weight=1)
        analysis_container.grid_columnconfigure(1, weight=1)
        
        self.cursor.execute("""
            SELECT date, montant, categorie, type 
            FROM transaction 
            WHERE id_compte = %s 
            ORDER BY date
        """, (self.id,))
        
        transactions = self.cursor.fetchall()
        
        if transactions:
            df = pd.DataFrame(transactions, columns=['date', 'montant', 'categorie', 'type'])
            df['date'] = pd.to_datetime(df['date'])
            
            df['mois'] = df['date'].dt.strftime('%Y-%m')
            monthly_data = df.groupby('mois')['montant'].agg(['sum', 'mean', 'count']).reset_index()
            monthly_data = monthly_data.rename(columns={'sum': 'total', 'mean': 'moyenne', 'count': 'nombre'})
            
            category_data = df.groupby('categorie')['montant'].sum().reset_index()
            category_data = category_data.sort_values('montant')
            
            depenses = df[df['montant'] < 0]
            revenus = df[df['montant'] > 0]
            
            summary_frame = ctk.CTkFrame(analysis_container, fg_color="#333333", corner_radius=10)
            summary_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
            
            summary_title = ctk.CTkLabel(summary_frame, text="Résumé Financier", 
                                    font=ctk.CTkFont(size=18, weight="bold"))
            summary_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            total_depenses = depenses['montant'].sum() if not depenses.empty else 0
            total_revenus = revenus['montant'].sum() if not revenus.empty else 0
            solde_actuel = self.solde_value
            
            summary_items = [
                {"label": "Solde actuel", "value": f"{solde_actuel} €"},
                {"label": "Total des revenus", "value": f"{total_revenus:.2f} €"},
                {"label": "Total des dépenses", "value": f"{total_depenses:.2f} €"},
                {"label": "Nombre de transactions", "value": f"{len(df)}"},
                {"label": "Moyenne des dépenses", "value": f"{depenses['montant'].mean():.2f} €" if not depenses.empty else "0.00 €"},
                {"label": "Montant max (entrée)", "value": f"{revenus['montant'].max():.2f} €" if not revenus.empty else "0.00 €"},
                {"label": "Montant max (sortie)", "value": f"{depenses['montant'].min():.2f} €" if not depenses.empty else "0.00 €"}
            ]
            
            for i, item in enumerate(summary_items):
                label = ctk.CTkLabel(summary_frame, text=item["label"], font=ctk.CTkFont(size=14))
                label.grid(row=i+1, column=0, padx=15, pady=5, sticky="w")
                
                value = ctk.CTkLabel(summary_frame, text=item["value"], font=ctk.CTkFont(size=14, weight="bold"))
                value.grid(row=i+1, column=1, padx=15, pady=5, sticky="e")
            
            monthly_frame = ctk.CTkFrame(analysis_container, fg_color="#333333", corner_radius=10)
            monthly_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
            
            monthly_title = ctk.CTkLabel(monthly_frame, text="Évolution Mensuelle", 
                                    font=ctk.CTkFont(size=18, weight="bold"))
            monthly_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            if not monthly_data.empty and len(monthly_data) > 1:
                fig, ax = plt.subplots(figsize=(5, 3), facecolor='#333333')
                ax.plot(monthly_data['mois'], monthly_data['total'], marker='o', color='#00CC66', linewidth=2)
                ax.set_facecolor('#333333')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.set_title('Montant total par mois', color='white')
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=monthly_frame)
                canvas.draw()
                canvas.get_tk_widget().grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
            else:
                no_data_label = ctk.CTkLabel(monthly_frame, text="Données insuffisantes pour l'analyse mensuelle", 
                                        font=ctk.CTkFont(size=14))
                no_data_label.grid(row=1, column=0, padx=15, pady=40, sticky="nsew")
            
            category_frame = ctk.CTkFrame(analysis_container, fg_color="#333333", corner_radius=10)
            category_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))
            
            category_title = ctk.CTkLabel(category_frame, text="Répartition par Catégorie", 
                                    font=ctk.CTkFont(size=18, weight="bold"))
            category_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            # Créer un graphique circulaire des catégories
            if not category_data.empty:
                fig2, ax2 = plt.subplots(figsize=(5, 4), facecolor='#333333')
                
                expense_cat = category_data[category_data['montant'] < 0].copy()
                if not expense_cat.empty:
                    expense_cat['montant'] = expense_cat['montant'].abs() 
                    
                    if len(expense_cat) > 5:
                        top_cats = expense_cat.nlargest(5, 'montant')
                        others_sum = expense_cat[~expense_cat['categorie'].isin(top_cats['categorie'])]['montant'].sum()
                        
                        others_row = pd.DataFrame({'categorie': ['Autres'], 'montant': [others_sum]})
                        expense_cat = pd.concat([top_cats, others_row])
                    
                    colors = ['#00CC66', '#33CCFF', '#FF6666', '#FFCC33', '#9966FF', '#FF99CC']
                    
                    ax2.pie(expense_cat['montant'], labels=expense_cat['categorie'], autopct='%1.1f%%', 
                        startangle=90, colors=colors)
                    ax2.set_facecolor('#333333')
                    ax2.set_title('Répartition des dépenses par catégorie', color='white')
                    fig2.tight_layout()
                    
                    canvas2 = FigureCanvasTkAgg(fig2, master=category_frame)
                    canvas2.draw()
                    canvas2.get_tk_widget().grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
                else:
                    no_expense_label = ctk.CTkLabel(category_frame, text="Aucune dépense trouvée pour l'analyse par catégorie", 
                                                font=ctk.CTkFont(size=14))
                    no_expense_label.grid(row=1, column=0, padx=15, pady=40, sticky="nsew")
            else:
                no_cat_label = ctk.CTkLabel(category_frame, text="Aucune donnée de catégorie disponible", 
                                        font=ctk.CTkFont(size=14))
                no_cat_label.grid(row=1, column=0, padx=15, pady=40, sticky="nsew")
            
            forecast_frame = ctk.CTkFrame(analysis_container, fg_color="#333333", corner_radius=10)
            forecast_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))
            
            forecast_title = ctk.CTkLabel(forecast_frame, text="Prévisions et Conseils", 
                                        font=ctk.CTkFont(size=18, weight="bold"))
            forecast_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            # Calculer la moyenne des dépenses mensuelles
            if not df.empty:
                forecast_text = ""
                
                if not monthly_data.empty and len(monthly_data) >= 2:
                    last_month = monthly_data.iloc[-1]
                    previous_month = monthly_data.iloc[-2]
                    
                    # Comparer avec le mois précédent
                    if last_month['total'] < previous_month['total']:
                        diff_percent = ((last_month['total'] - previous_month['total']) / previous_month['total']) * 100
                        forecast_text += f"📉 Vos dépenses ont diminué de {abs(diff_percent):.1f}% par rapport au mois précédent.\n\n"
                    else:
                        diff_percent = ((last_month['total'] - previous_month['total']) / previous_month['total']) * 100
                        forecast_text += f"📈 Vos dépenses ont augmenté de {diff_percent:.1f}% par rapport au mois précédent.\n\n"
                
                if not category_data.empty:
                    expense_categories = category_data[category_data['montant'] < 0].copy()
                    if not expense_categories.empty:
                        expense_categories['montant'] = expense_categories['montant'].abs()
                        top_expense = expense_categories.loc[expense_categories['montant'].idxmax()]
                        forecast_text += f"💰 Votre catégorie de dépense principale est '{top_expense['categorie']}' "
                        forecast_text += f"({top_expense['montant']:.2f} €).\n\n"
                        
                        if top_expense['montant'] > abs(total_depenses) * 0.4:  # Si plus de 40% des dépenses
                            forecast_text += f"⚠️ Attention! Cette catégorie représente une grande partie de vos dépenses. "
                
                if forecast_text == "":
                    forecast_text = "Pas assez de données pour générer des prévisions et conseils personnalisés. "
                    forecast_text += "Continuez à utiliser votre compte pour obtenir des analyses plus précises."
                
                forecast_textbox = ctk.CTkTextbox(forecast_frame, width=400, height=200, fg_color="#333333", text_color="white")
                forecast_textbox.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
                forecast_textbox.insert("1.0", forecast_text)
                forecast_textbox.configure(state="disabled")
            else:
                no_forecast_label = ctk.CTkLabel(forecast_frame, text="Données insuffisantes pour générer des prévisions", 
                                            font=ctk.CTkFont(size=14))
                no_forecast_label.grid(row=1, column=0, padx=15, pady=40, sticky="nsew")
        else:
            no_data_frame = ctk.CTkFrame(analysis_container, fg_color="#333333", corner_radius=10)
            no_data_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
            
            no_data_label = ctk.CTkLabel(no_data_frame, 
                                    text="Aucune transaction trouvée.\nEffectuez des transactions pour générer des analyses.", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
            no_data_label.grid(row=0, column=0, padx=20, pady=40)

    #Transfer money with IBAN
    def transfer_money(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(self.main_frame, text="Transfert d'argent via IBAN", 
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")
        
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#333333", corner_radius=10)
        form_frame.grid(row=1, column=0, columnspan=2, padx=50, pady=20, sticky="new")
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=2)
        
        subtitle_label = ctk.CTkLabel(form_frame, text="Effectuer un virement", 
                                    font=ctk.CTkFont(size=18, weight="bold"))
        subtitle_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 30), sticky="w")
        
        # IBAN du destinataire
        iban_label = ctk.CTkLabel(form_frame, text="IBAN Destinataire:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        iban_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.iban_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="FRXX XXXX X")
        self.iban_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        # Nom du destinataire
        recipient_label = ctk.CTkLabel(form_frame, text="Nom:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        recipient_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.recipient_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nom")
        self.recipient_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Montant du transfert
        amount_label = ctk.CTkLabel(form_frame, text="Montant (€):", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        amount_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.transfer_amount_entry = ctk.CTkEntry(form_frame, width=200, placeholder_text="0.00")
        self.transfer_amount_entry.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        
        # Catégorie
        category_label = ctk.CTkLabel(form_frame, text="Catégorie:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        category_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        categories = ["Virement", "Paiement", "Loyer", "Facture", "Remboursement", "Autre"]
        category_var = ctk.StringVar(value=categories[0])
        self.transfer_category_dropdown = ctk.CTkOptionMenu(form_frame, values=categories, variable=category_var)
        self.transfer_category_dropdown.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        
        # Description/motif
        description_label = ctk.CTkLabel(form_frame, text="Motif du virement:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        description_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        
        self.transfer_description_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Motif du virement")
        self.transfer_description_entry.grid(row=5, column=1, padx=20, pady=10, sticky="w")
        
        # Date
        date_label = ctk.CTkLabel(form_frame, text="Date:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        date_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")
        
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.grid(row=6, column=1, padx=20, pady=10, sticky="w")
        
        from datetime import datetime
        current_date = datetime.now()
        
        self.transfer_day_entry = ctk.CTkEntry(date_frame, width=50, placeholder_text="JJ")
        self.transfer_day_entry.grid(row=0, column=0, padx=(0, 5))
        self.transfer_day_entry.insert(0, current_date.day)
        
        self.transfer_month_entry = ctk.CTkEntry(date_frame, width=50, placeholder_text="MM")
        self.transfer_month_entry.grid(row=0, column=1, padx=5)
        self.transfer_month_entry.insert(0, current_date.month)
        
        self.transfer_year_entry = ctk.CTkEntry(date_frame, width=70, placeholder_text="AAAA")
        self.transfer_year_entry.grid(row=0, column=2, padx=(5, 0))
        self.transfer_year_entry.insert(0, current_date.year)
        
        # Boutons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(30, 20), sticky="e")
        
        cancel_button = ctk.CTkButton(button_frame, text="Annuler", fg_color="#555555", 
                                    hover_color="#444444", corner_radius=5, width=120, 
                                    command=self.reset_main_frame)
        cancel_button.grid(row=0, column=0, padx=(0, 10))
        
        validate_button = ctk.CTkButton(button_frame, text="Effectuer le virement", fg_color="#00CC66", 
                                    hover_color="#00AA55", corner_radius=5, width=120, 
                                    command=self.process_transfer)
        validate_button.grid(row=0, column=1)

    #Validate transfert
    def process_transfer(self):
        recipient_iban = self.iban_entry.get()
        recipient_name = self.recipient_entry.get()
        amount = float(self.transfer_amount_entry.get())
        category = self.transfer_category_dropdown.get()
        description = self.transfer_description_entry.get()
        day = self.transfer_day_entry.get()
        month = self.transfer_month_entry.get()
        year = self.transfer_year_entry.get()
        date = f"{year}-{month}-{day}"
        
        # Vérification du solde disponible
        if amount <= 0:
            messagebox.showerror("Erreur", "Le montant doit être supérieur à 0.")
            return
        
        if amount > self.solde_value:
            messagebox.showerror("Erreur", "Solde insuffisant pour effectuer ce virement.")
            return
        
        self.cursor.execute("SELECT id FROM compte WHERE IBAN = %s", (recipient_iban,))
        dest_account = self.cursor.fetchone()
        
        try:
            self.cursor.execute("UPDATE compte SET solde = solde - %s WHERE id = %s", (amount, self.id))
            
            if dest_account:
                self.cursor.execute("UPDATE compte SET solde = solde + %s WHERE IBAN = %s", (amount, recipient_iban))
                
                self.cursor.execute(
                    "INSERT INTO transaction(description, date, type, categorie, id_compte, montant) VALUES (%s, %s, %s, %s, %s, %s)",
                    (f"Virement reçu de {self.nom_user[0][0]} {self.nom_user[0][1]}", date, "Virement reçu", category, dest_account[0], amount)
                )
            
            self.cursor.execute(
                "INSERT INTO transaction(description, date, type, categorie, id_compte, montant) VALUES (%s, %s, %s, %s, %s, %s)",
                (f"{description} - Destinataire: {recipient_name}", date, "Virement émis", category, self.id, -amount)
            )
            
            # Valider les transactions
            self.connection.commit()
            
            # Mettre à jour les soldes en mémoire
            self.cursor.execute("SELECT solde FROM compte WHERE id = %s", (self.id,))
            self.solde = self.cursor.fetchone()
            self.solde_value = 0 if self.solde[0] is None else self.solde[0]
            
            self.cursor.execute("SELECT * FROM transaction WHERE id_compte = %s ORDER BY ID DESC", (self.id,))
            self.transa = self.cursor.fetchall()
            
            self.cursor.execute("SELECT SUM(solde) FROM compte WHERE user_id = %s", (self.user_id,))
            self.allsolde = self.cursor.fetchone()
            
            self.show_notif(f"Virement de {amount}€ effectué avec succès", "#00CC66")
            
            self.reset_main_frame()
            
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Erreur de transaction", f"Une erreur s'est produite: {str(e)}")

    def deconn(self):
        self.destroy()
        menu = Login()
        menu.menu()
        menu.mainloop()

if __name__ == "__main__":
    app = Home(15,53)
    app.mainloop()

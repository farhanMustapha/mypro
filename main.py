import flet as ft
import json

# Charger le fichier JSON des exemples
def load_json():
    with open('exemples.json', encoding='utf-8') as f:
        return json.load(f)

# Page 1 : Liste des comptes
def show_comptes(page):
    data = load_json()

    def search_comptes(e):
        query = search_field.value.lower()
        filtered_items.controls = [
            ft.ListTile(
                title=ft.Text(f" {compte['numero']} : {compte['titre']}"),
                on_click=lambda e, c=compte: show_details(page, c)
            )
            for compte in data
            if query in compte["numero"].lower() or query in compte["titre"].lower()
        ]
        page.update()

    search_field = ft.TextField(label="Chercher par numéro ou titre de compte", 
                                width=390, icon=ft.icons.SEARCH,
                                border_color="amber", on_change=search_comptes)

    filtered_items = ft.Column(
        [
            ft.ListTile(
                title=ft.Text(f" {compte['numero']} : {compte['titre']}"),
                on_click=lambda e, c=compte: show_details(page, c), bgcolor=ft.colors.AMBER, width=390,
                text_color=ft.colors.WHITE
            )
            for compte in data
        ],
        spacing=10,
    )

    page.controls.clear()
    page.controls.append(ft.Column([search_field, filtered_items]))
    page.update()

# Page 2 : Détails du compte sélectionné
def show_details(page, compte):
    if isinstance(compte, dict):
        def go_to_exemples(e):
            show_exemples(page, compte)

        page.controls.clear()

        page.controls.append(ft.Container(
            content=ft.Text(f"{compte['numero']} - {compte['titre']}", color=ft.colors.WHITE, size=20),
            width=450, bgcolor=ft.colors.AMBER, padding=10
        ))
        page.controls.append(ft.Container(
            content=ft.Text(f"{compte['explication']}", color=ft.colors.WHITE, size=15),
            bgcolor=ft.colors.AMBER, padding=10
        ))

        btn_exemples = ft.ElevatedButton("Voir les exemples", bgcolor=ft.colors.BLUE, color=ft.colors.WHITE, on_click=go_to_exemples)
        btn_back_home = ft.ElevatedButton("Retour à l'accueil", bgcolor=ft.colors.BLUE, color=ft.colors.WHITE, on_click=lambda e: show_comptes(page))
        page.controls.append(ft.Row([btn_exemples, btn_back_home]))
        page.update()
    else:
        page.controls.clear()
        page.controls.append(ft.Text("Erreur : Données du compte non valides"))
        page.update()

#=======================================================================================



# Page 3 : Exemples et Validation
def show_exemples(page, compte):
    data = load_json()

    # Récupérer les exemples associés au compte sélectionné
    examples = next((acc['exemples'] for acc in data if acc['numero'] == compte["numero"]), None)

    if not examples:
        page.controls.clear()
        page.controls.append(ft.Text("Aucun exemple trouvé pour ce compte"))
        page.update()
        return

    current_index = 0
    user_journal = ft.Ref[ft.Dropdown]()
    user_date = ft.Ref[ft.TextField]()
    user_description = ft.Ref[ft.TextField]()
    user_message = ft.Ref[ft.Text]()

    user_comptes = []
    user_debit = []
    user_credit = []

    def create_question(example):
        user_comptes.clear()
        user_debit.clear()
        user_credit.clear()
        compte_rows = []

        # Récupérer les informations de l'exemple actuel
        comptes = example['reponse']['comptes_debit'] + example['reponse']['comptes_credit']
        max_len = max(len(comptes), len(example['reponse']['montants_debit']), len(example['reponse']['montants_credit']))

        for i in range(max_len):
            compte_field = ft.TextField(label=f"Compte {i+1}", value="", border_color=ft.colors.AMBER)
            debit_field = ft.TextField(label=f"Débit {i+1}", value="", border_color=ft.colors.AMBER)
            credit_field = ft.TextField(label=f"Crédit {i+1}", value="", border_color=ft.colors.AMBER)

            user_comptes.append(compte_field)
            user_debit.append(debit_field)
            user_credit.append(credit_field)

            compte_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Container(content=compte_field, padding=ft.padding.all(0))),
                    ft.DataCell(ft.Container(content=debit_field, padding=ft.padding.all(0))),
                    ft.DataCell(ft.Container(content=credit_field, padding=ft.padding.all(0)))
                ])
            )

        page.controls.clear()
        page.add(ft.Container(content=ft.Text(f"Exemple :\n {example['qst']}", size=15, color=ft.colors.WHITE), bgcolor=ft.colors.AMBER, width=400, padding=10))

        # Ligne avec le dropdown pour le journal et la date
        page.add(
            ft.Row([
                ft.Dropdown(ref=user_journal, label="Journal", width=200, options=[
                    ft.dropdown.Option("Achat"),
                    ft.dropdown.Option("Vente"),
                    ft.dropdown.Option("Caisse"),
                    ft.dropdown.Option("Banque"),
                    ft.dropdown.Option("OD")
                ]),
                ft.TextField(ref=user_date, label="Date", width=190)
            ])
        )

        # Description (facultatif)
        page.add(ft.TextField(ref=user_description, label="Description (facultatif)", width=400))

        # Tableau pour saisir les comptes et montants de débit et crédit
        page.add(
            ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Compte")), ft.DataColumn(ft.Text("Débit")), ft.DataColumn(ft.Text("Crédit"))],
                rows=compte_rows,
                heading_row_color=ft.colors.AMBER,
                border=ft.border.all(1, ft.colors.GREY),
                width=600
            )
        )

        page.add(ft.Text(ref=user_message))  # Message pour la validation

        # Boutons "Valider", "Next", "Retour"
        page.add(ft.Row([
            ft.ElevatedButton("Valider", on_click=lambda e: validate(example), color=ft.colors.WHITE, bgcolor=ft.colors.BLUE, width=200),
            ft.ElevatedButton("Next", on_click=next_question, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE, width=200),
            ft.ElevatedButton("Retour", on_click=lambda e: show_details(page, compte), color=ft.colors.WHITE, bgcolor=ft.colors.BLUE, width=200)
        ]))

        page.update()

    def validate(example):
        correct_answer = example['reponse']

        user_input = {
            "journal": user_journal.current.value,
            "date": user_date.current.value,
            "comptes": [compte.value for compte in user_comptes],
            "montants_debit": [debit.value for debit in user_debit],
            "montants_credit": [credit.value for credit in user_credit]
        }

        valid = True
        user_message.current.value = ""  # Réinitialiser le message d'erreur

        # Vérification du journal et de la date
        if user_input['journal'] != correct_answer['journal']:
            user_journal.current.border_color = ft.colors.RED
            user_message.current.value += f"Erreur : Le journal est incorrect, valeur attendue : {correct_answer['journal']}.\n"
            valid = False
        else:
            user_journal.current.border_color = ft.colors.GREEN

        if user_input['date'] != correct_answer['date']:
            user_date.current.border_color = ft.colors.RED
            user_message.current.value += f"Erreur : La date est incorrecte, valeur attendue : {correct_answer['date']}.\n"
            valid = False
        else:
            user_date.current.border_color = ft.colors.GREEN

        # Vérification des comptes et montants
        for i, (compte_field, debit_field, credit_field) in enumerate(zip(user_comptes, user_debit, user_credit)):
            compte = compte_field.value
            debit_value = debit_field.value
            credit_value = credit_field.value

            # Vérifier si le compte est associé à un montant correspondant
            if compte in correct_answer['comptes_debit'] and debit_value and not credit_value:
                debit_field.border_color = ft.colors.GREEN
                compte_field.border_color = ft.colors.GREEN
            elif compte in correct_answer['comptes_credit'] and credit_value and not debit_value:
                credit_field.border_color = ft.colors.GREEN
                compte_field.border_color = ft.colors.GREEN
            else:
                debit_field.border_color = ft.colors.RED
                credit_field.border_color = ft.colors.RED
                compte_field.border_color = ft.colors.RED
                user_message.current.value += f"Erreur : Compte {compte} mal associé. Vérifiez le montant correspondant.\n"
                valid = False

        if not valid:
            page.update()
            return

        # Calcul des totaux
        total_debit = sum(float(debit) for debit in user_input['montants_debit'] if debit)
        total_credit = sum(float(credit) for credit in user_input['montants_credit'] if credit)

        # Vérifier si le total débit = total crédit
        if total_debit != total_credit:
            user_message.current.value += f"Déséquilibre : Total Débit = {total_debit}, Total Crédit = {total_credit}.\n"
            page.update()
            return

        user_message.current.value = "Bonne réponse !"
        page.update()

    def next_question(e):
        nonlocal current_index
        if current_index < len(examples) - 1:
            current_index += 1
            create_question(examples[current_index])
        else:
            page.controls.clear()
            page.add(ft.Text("Fin des exercices"))
            page.update()

    create_question(examples[current_index])



#========================================================================================



# Fonction principale (Page d'accueil)
def main(page):
    page.title = "Comptabilité - Plan Comptable"
    #page.window.width = 450
    page.window.height = 700
    page.window.left = 800
    page.scroll = True
    show_comptes(page)

# Configuration WSGI
#pr anywhere
def application(environ, start_response):
    return ft.wsgi(target=main)(environ, start_response)

"""
pr runer localemet l'app
 if __name__=="__main__":
    ft.app(target=main, view=ft.WEB_BROWSER) """
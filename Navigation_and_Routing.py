# app.py
import datetime
import flet as ft


def main(page: ft.Page):
    page.title = "Navigation and Routing"
    page.window_width = 700
    page.window_height = 700
    page.vertical_alignment = ft.MainAxisAlignment.START

    # --------------- Shared state ---------------
    app_data = {
        "email": None,
        "name": "",
        "dob": None,   # datetime.date
        "gender": None,
        "address": "",
        "country": None,
    }

    # --------------- Login controls ---------------
    login_email = ft.TextField(label="Email", width=400)
    login_password = ft.TextField(
        label="Password", password=True, can_reveal_password=True, width=400)
    login_error = ft.Text("", visible=False, color="red")

    def do_login(e):
        login_email.error_text = None
        login_password.error_text = None
        login_error.visible = False

        email = (login_email.value or "").strip()
        pwd = (login_password.value or "").strip()

        missing = False
        if not email:
            login_email.error_text = "Email is required"
            missing = True
        if not pwd:
            login_password.error_text = "Password is required"
            missing = True

        if missing:
            login_error.value = "Please enter email and password."
            login_error.visible = True
            login_email.update()
            login_password.update()
            login_error.update()
            return

        app_data["email"] = email
        page.go("/form")  # Go directly to form page after login

    # --------------- Form controls ---------------
    form_name = ft.TextField(label="Full name", width=500)
    form_dob_text = ft.TextField(
        label="Date of birth", width=300, read_only=True)

    def on_date_change(e: ft.ControlEvent):
        val = None
        try:
            val = e.control.value
        except Exception:
            pass
        if val:
            try:
                form_dob_text.value = val.strftime("%Y-%m-%d")
            except Exception:
                form_dob_text.value = str(val)
        else:
            form_dob_text.value = ""
        form_dob_text.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime.date(1900, 1, 1),
        last_date=datetime.date(2050, 12, 31),
        help_text="Select your date of birth",
        confirm_text="OK",
        cancel_text="Cancel",
    )
    page.overlay.append(date_picker)

    def open_datepicker(e):
        try:
            date_picker.open = True
            date_picker.update()
        except Exception:
            form_error.value = "Could not open calendar dialog (upgrade flet?)."
            form_error.visible = True
            form_error.update()

    open_datepicker_btn = ft.ElevatedButton(
        text="Open calendar", icon=ft.Icons.CALENDAR_MONTH, on_click=open_datepicker)

    form_gender = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="Male", label="Male"),
                ft.Radio(value="Female", label="Female"),
                ft.Radio(value="Other", label="Other"),
            ],
            spacing=20,
        )
    )

    form_address = ft.TextField(
        label="Address", multiline=True, min_lines=3, width=500)

    form_country = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="Finland", label="Finland"),
                ft.Radio(value="Bangladesh", label="Bangladesh"),
                ft.Radio(value="India", label="India"),
                ft.Radio(value="Other", label="Other"),
            ],
            tight=True,
        )
    )

    form_error = ft.Text("", visible=False, color="red")

    def submit_form(e):
        errors = []
        if not (form_name.value or "").strip():
            errors.append("Name is required.")
        if not form_gender.value:
            errors.append("Gender is required.")
        if not form_country.value:
            errors.append("Country is required.")
        if not (form_dob_text.value or "").strip():
            errors.append("Date of birth is required (use the calendar).")

        dob_value = None
        if form_dob_text.value:
            try:
                dob_value = datetime.datetime.strptime(
                    form_dob_text.value, "%Y-%m-%d").date()
            except Exception:
                errors.append(
                    "Selected date format invalid. Use the calendar to re-select.")

        if errors:
            form_error.value = "\n".join(errors)
            form_error.visible = True
            form_error.update()
            return

        app_data["name"] = form_name.value.strip()
        app_data["dob"] = dob_value
        app_data["gender"] = form_gender.value
        app_data["address"] = form_address.value.strip(
        ) if form_address.value else ""
        app_data["country"] = form_country.value
        page.go("/details")

    def do_logout(e):
        app_data["email"] = None
        login_email.value = ""
        login_password.value = ""
        login_error.visible = False
        login_email.update()
        login_password.update()
        login_error.update()
        page.go("/")

    # --------------- Views ---------------
    def make_appbar(title: str, back_route: str | None = None):
        if back_route:
            return ft.AppBar(
                title=ft.Text(title),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK, tooltip="Back", on_click=lambda e: page.go(back_route)),
            )
        else:
            return ft.AppBar(title=ft.Text(title))

    def login_view():
        return ft.View(
            "/",
            controls=[
                ft.AppBar(title=ft.Text("Login")),
                ft.Column(
                    [
                        ft.Container(height=30),
                        ft.Text("Please login", size=20),
                        ft.Container(height=12),
                        login_email,
                        login_password,
                        ft.ElevatedButton("Login", on_click=do_login),
                        login_error,
                        ft.Container(height=20),
                        ft.Text(
                            "Demo: enter any non-empty email and password to proceed.", size=12),
                    ],
                    tight=True,
                    horizontal_alignment=ft.alignment.center,
                ),
            ],
        )

    def form_view():
        # prefill
        form_name.value = app_data.get("name", "")
        if app_data.get("dob"):
            try:
                form_dob_text.value = app_data["dob"].isoformat()
            except Exception:
                form_dob_text.value = str(app_data["dob"])
        form_gender.value = app_data.get("gender", None)
        form_address.value = app_data.get("address", "")
        form_country.value = app_data.get("country", None)

        controls = [
            ft.Text("Please fill your details", size=18),
            form_name,
            ft.Row([form_dob_text, open_datepicker_btn], spacing=8),
            ft.Text("Gender"),
            form_gender,
            ft.Text("Address"),
            form_address,
            ft.Text("Country"),
            form_country,
            form_error,
            ft.Row(
                [ft.ElevatedButton("Submit", on_click=submit_form)],
                spacing=12,
            ),
        ]

        return ft.View(
            "/form",
            controls=[
                make_appbar("Form"),
                ft.Container(
                    content=ft.ListView(
                        controls=controls,
                        spacing=8,
                        padding=ft.padding.symmetric(12, 12),
                        expand=True,
                    ),
                    expand=True,
                ),
            ],
        )

    def details_view():
        dob_str = app_data["dob"].isoformat() if isinstance(
            app_data["dob"], datetime.date) else (str(app_data["dob"]) if app_data["dob"] else "-")
        card_content = ft.Column(
            [
                ft.Text(f"Name: {app_data.get('name', '-')}", size=14),
                ft.Text(f"Date of birth: {dob_str}", size=14),
                ft.Text(f"Gender: {app_data.get('gender', '-')}", size=14),
                ft.Text(f"Address: {app_data.get('address', '-')}", size=14),
                ft.Text(f"Country: {app_data.get('country', '-')}", size=14),
                ft.Container(height=8),
                ft.Row([
                    # ✅ Only Go back
                    ft.ElevatedButton(
                        "Go back", on_click=lambda e: page.go("/")),
                ], spacing=12),
            ],
            tight=True,
            spacing=8,
        )

        return ft.View(
            "/details",
            controls=[
                make_appbar("Details"),
                ft.Column(
                    [
                        ft.Container(height=20),
                        ft.Card(
                            content=card_content,
                            elevation=4,
                            margin=ft.padding.symmetric(12, 12),
                        ),
                    ],
                    horizontal_alignment=ft.alignment.center,
                ),
            ],
        )

    # --------------- Routing ---------------
    def route_change(route):
        r = page.route
        page.views.clear()
        if r == "/" or r == "":
            page.views.append(login_view())
        elif r == "/form":
            page.views.append(form_view())
        elif r == "/details":
            page.views.append(details_view())
        else:
            page.views.append(ft.View("/404", controls=[
                make_appbar("Not found", back_route="/"),
                ft.Column([ft.Text(f"Route {r} not found")]),
            ]))
        page.update()

    page.on_route_change = lambda e: route_change(e)
    page.go("/")


if __name__ == "__main__":
    ft.app(target=main)

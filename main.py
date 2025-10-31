from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from datetime import datetime, timedelta
import json
import os
import hashlib

# تنظیمات رنگ‌های مدرن
COLORS = {
    'primary': get_color_from_hex('#4361ee'),
    'secondary': get_color_from_hex('#3a0ca3'),
    'success': get_color_from_hex('#4cc9f0'),
    'danger': get_color_from_hex('#f72585'),
    'warning': get_color_from_hex('#f8961e'),
    'light': get_color_from_hex('#f8f9fa'),
    'dark': get_color_from_hex('#212529'),
    'background': get_color_from_hex('#ffffff')
}

Window.clearcolor = COLORS['background']

class NotificationManager:
    def __init__(self):
        self.notifications = []
        self.load_notifications()
    
    def add_notification(self, title, message, notification_type="info"):
        notification = {
            'id': len(self.notifications) + 1,
            'title': title,
            'message': message,
            'type': notification_type,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'read': False
        }
        self.notifications.append(notification)
        self.save_notifications()
    
    def get_unread_count(self):
        return sum(1 for n in self.notifications if not n['read'])
    
    def mark_as_read(self, notification_id):
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
        self.save_notifications()
    
    def mark_all_as_read(self):
        for notification in self.notifications:
            notification['read'] = True
        self.save_notifications()
    
    def get_recent_notifications(self, count=5):
        return sorted(self.notifications, key=lambda x: x['time'], reverse=True)[:count]
    
    def save_notifications(self):
        with open('notifications.json', 'w', encoding='utf-8') as f:
            json.dump(self.notifications, f, ensure_ascii=False)
    
    def load_notifications(self):
        try:
            with open('notifications.json', 'r', encoding='utf-8') as f:
                self.notifications = json.load(f)
        except FileNotFoundError:
            self.notifications = []

class UserManager:
    def __init__(self):
        self.current_user = None
        self.users = {}
        self.load_users()
    
    def register_user(self, username, password, email):
        if username in self.users:
            return False, "این نام کاربری قبلا ثبت شده است"
        
        user_id = hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()[:8]
        user_data = {
            'user_id': user_id,
            'username': username,
            'password': hashlib.md5(password.encode()).hexdigest(),
            'email': email,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.users[username] = user_data
        self.save_users()
        return True, "ثبت‌نام با موفقیت انجام شد"
    
    def login_user(self, username, password):
        if username not in self.users:
            return False, "نام کاربری یا رمز عبور اشتباه است"
        
        user = self.users[username]
        if user['password'] == hashlib.md5(password.encode()).hexdigest():
            user['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.current_user = username
            self.save_users()
            return True, "ورود موفقیت‌آمیز بود"
        
        return False, "نام کاربری یا رمز عبور اشتباه است"
    
    def logout_user(self):
        self.current_user = None
        return True
    
    def get_current_user_data(self):
        if self.current_user:
            return self.users[self.current_user]
        return None
    
    def save_users(self):
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False)
    
    def load_users(self):
        try:
            with open('users.json', 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = COLORS['light']
        self.font_size = '18sp'
        self.bold = True
        
        with self.canvas.before:
            Color(*COLORS['primary'])
            self.rect = RoundedRectangle(radius=[25])
            self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernCard(BoxLayout):
    def __init__(self, title, value, color, icon, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 120
        self.padding = 15
        self.spacing = 10
        
        with self.canvas.before:
            Color(*color)
            self.rect = RoundedRectangle(radius=[20])
            self.bind(pos=self.update_rect, size=self.update_rect)
        
        title_layout = BoxLayout(size_hint_y=0.4)
        title_icon = Label(text=icon, font_size='20sp', color=COLORS['light'])
        title_label = Label(text=title, font_size='16sp', color=COLORS['light'], bold=True)
        title_layout.add_widget(title_icon)
        title_layout.add_widget(title_label)
        
        value_label = Label(text=str(value), font_size='24sp', color=COLORS['light'], bold=True)
        
        self.add_widget(title_layout)
        self.add_widget(value_label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FinancialManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transactions = []
        self.categories = ['🍔 خوراک', '🚗 حمل‌ونقل', '🏠 مسکن', '🎮 تفریح', '🏥 سلامت', '📦 دیگر']
        self.budget = {category: 0 for category in self.categories}
        self.load_data()
    
    def add_income(self, amount, description, source):
        transaction = {
            'type': 'income',
            'amount': amount,
            'description': description,
            'source': source,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions.append(transaction)
        self.save_data()
        return True
    
    def add_expense(self, amount, description, category):
        transaction = {
            'type': 'expense',
            'amount': amount,
            'description': description,
            'category': category,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions.append(transaction)
        self.save_data()
        return True
    
    def get_balance(self):
        total_income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        return total_income - total_expense
    
    def get_category_expenses(self):
        expenses = {}
        for category in self.categories:
            total = sum(t['amount'] for t in self.transactions 
                       if t['type'] == 'expense' and t['category'] == category)
            expenses[category] = total
        return expenses
    
    def get_total_income(self):
        return sum(t['amount'] for t in self.transactions if t['type'] == 'income')
    
    def get_total_expense(self):
        return sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
    
    def check_budget_alerts(self):
        alerts = []
        expenses = self.get_category_expenses()
        
        for category, budget in self.budget.items():
            if budget > 0:
                current_expense = expenses.get(category, 0)
                if current_expense >= budget * 0.9:
                    alerts.append(f"هشدار: بودجه {category} در حال اتمام است!")
                elif current_expense >= budget:
                    alerts.append(f"هشدار: بودجه {category} превышен است!")
        
        return alerts
    
    def get_weekly_report(self):
        one_week_ago = datetime.now() - timedelta(days=7)
        weekly_income = sum(t['amount'] for t in self.transactions 
                           if t['type'] == 'income' and datetime.strptime(t['date'], "%Y-%m-%d %H:%M:%S") >= one_week_ago)
        weekly_expense = sum(t['amount'] for t in self.transactions 
                            if t['type'] == 'expense' and datetime.strptime(t['date'], "%Y-%m-%d %H:%M:%S") >= one_week_ago)
        
        return weekly_income, weekly_expense
    
    def save_data(self):
        data = {
            'transactions': self.transactions,
            'budget': self.budget
        }
        filename = f'financial_data_{self.user_id}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    
    def load_data(self):
        filename = f'financial_data_{self.user_id}.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.transactions = data.get('transactions', [])
                self.budget = data.get('budget', {})
        except FileNotFoundError:
            self.transactions = []
            self.budget = {category: 0 for category in self.categories}

class LoginScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [30, 40, 30, 40]
        self.spacing = 20
        
        header = BoxLayout(size_hint_y=0.2)
        title = Label(
            text='💰 هوش مالی',
            font_size='32sp',
            bold=True,
            color=COLORS['primary']
        )
        header.add_widget(title)
        self.add_widget(header)
        
        form_layout = BoxLayout(orientation='vertical', spacing=15)
        
        self.username_input = TextInput(
            hint_text='نام کاربری',
            font_size='18sp',
            size_hint_y=0.15,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        self.password_input = TextInput(
            hint_text='رمز عبور',
            font_size='18sp',
            size_hint_y=0.15,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark'],
            password=True
        )
        
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.password_input)
        self.add_widget(form_layout)
        
        btn_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        
        btn_login = RoundedButton(text='🚀 ورود به برنامه')
        btn_login.canvas.before.children[0].rgba = COLORS['success']
        btn_login.bind(on_press=self.login)
        
        btn_register = RoundedButton(text='📝 ثبت‌نام کاربر جدید')
        btn_register.canvas.before.children[0].rgba = COLORS['primary']
        btn_register.bind(on_press=self.show_register)
        
        btn_layout.add_widget(btn_login)
        btn_layout.add_widget(btn_register)
        self.add_widget(btn_layout)
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_message('خطا', 'لطفا نام کاربری و رمز عبور را وارد کنید')
            return
        
        success, message = self.app.user_manager.login_user(username, password)
        if success:
            self.app.fm = FinancialManager(self.app.user_manager.get_current_user_data()['user_id'])
            self.app.show_main_screen()
            self.app.notification_manager.add_notification(
                "خوش آمدید! 👋",
                f"به هوش مالی خوش آمدید {username}!\nموجودی فعلی شما: {self.app.fm.get_balance():,} تومان",
                "success"
            )
        else:
            self.show_message('خطا', message)
    
    def show_register(self, instance):
        self.app.show_register_screen()
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size='18sp'))
        
        btn_ok = Button(text='باشه', size_hint_y=0.4, background_color=COLORS['primary'])
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        
        popup.open()

class RegisterScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [30, 40, 30, 40]
        self.spacing = 20
        
        header = BoxLayout(size_hint_y=0.15)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.go_back)
        title = Label(text='ثبت‌نام کاربر جدید', font_size='24sp', bold=True, color=COLORS['primary'])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))
        self.add_widget(header)
        
        form_layout = BoxLayout(orientation='vertical', spacing=15)
        
        self.username_input = TextInput(
            hint_text='نام کاربری',
            font_size='18sp',
            size_hint_y=0.12,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        self.email_input = TextInput(
            hint_text='ایمیل',
            font_size='18sp',
            size_hint_y=0.12,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        self.password_input = TextInput(
            hint_text='رمز عبور',
            font_size='18sp',
            size_hint_y=0.12,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark'],
            password=True
        )
        
        self.confirm_password_input = TextInput(
            hint_text='تکرار رمز عبور',
            font_size='18sp',
            size_hint_y=0.12,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark'],
            password=True
        )
        
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.email_input)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(self.confirm_password_input)
        self.add_widget(form_layout)
        
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        btn_register = RoundedButton(text='✅ ثبت‌نام')
        btn_register.canvas.before.children[0].rgba = COLORS['success']
        btn_register.bind(on_press=self.register)
        
        btn_cancel = RoundedButton(text='❌ انصراف')
        btn_cancel.canvas.before.children[0].rgba = COLORS['danger']
        btn_cancel.bind(on_press=self.go_back)
        
        btn_layout.add_widget(btn_register)
        btn_layout.add_widget(btn_cancel)
        self.add_widget(btn_layout)
    
    def register(self, instance):
        username = self.username_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        
        if not username or not email or not password:
            self.show_message('خطا', 'لطفا تمام فیلدها را پر کنید')
            return
        
        if password != confirm_password:
            self.show_message('خطا', 'رمز عبور و تکرار آن مطابقت ندارند')
            return
        
        if len(password) < 4:
            self.show_message('خطا', 'رمز عبور باید حداقل ۴ کاراکتر باشد')
            return
        
        success, message = self.app.user_manager.register_user(username, password, email)
        if success:
            self.show_message('موفق', message)
            self.app.show_login_screen()
        else:
            self.show_message('خطا', message)
    
    def go_back(self, instance):
        self.app.show_login_screen()
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size='18sp'))
        
        btn_ok = Button(text='باشه', size_hint_y=0.4, background_color=COLORS['primary'])
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        
        popup.open()

class MainScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [20, 10, 20, 10]
        self.spacing = 15
        self.create_main_menu()
    
    def create_main_menu(self):
        header = BoxLayout(size_hint_y=0.15)
        title = Label(
            text='💰 هوش مالی',
            font_size='28sp',
            bold=True,
            color=COLORS['primary']
        )
        
        notification_btn = Button(
            text='🔔',
            size_hint_x=0.2,
            background_color=(0,0,0,0),
            font_size='20sp'
        )
        notification_btn.bind(on_press=self.app.show_notification_screen)
        
        profile_btn = Button(
            text='👤',
            size_hint_x=0.2,
            background_color=(0,0,0,0),
            font_size='20sp'
        )
        profile_btn.bind(on_press=self.app.show_profile_screen)
        
        header.add_widget(profile_btn)
        header.add_widget(title)
        header.add_widget(notification_btn)
        self.add_widget(header)
        
        cards_layout = BoxLayout(size_hint_y=0.4, spacing=15)
        
        balance_card = ModernCard(
            title='موجودی', 
            value=f'{self.app.fm.get_balance():,} تومان',
            color=COLORS['primary'],
            icon='💰'
        )
        
        income_card = ModernCard(
            title='کل درآمد', 
            value=f'{self.app.fm.get_total_income():,}',
            color=COLORS['success'],
            icon='📈'
        )
        
        expense_card = ModernCard(
            title='کل هزینه', 
            value=f'{self.app.fm.get_total_expense():,}',
            color=COLORS['danger'],
            icon='📉'
        )
        
        cards_layout.add_widget(balance_card)
        cards_layout.add_widget(income_card)
        cards_layout.add_widget(expense_card)
        self.add_widget(cards_layout)
        
        buttons_layout = GridLayout(cols=2, spacing=15, size_hint_y=0.4)
        
        buttons = [
            ('➕ درآمد', COLORS['success'], self.app.show_income_screen),
            ('➖ هزینه', COLORS['danger'], self.app.show_expense_screen),
            ('📊 گزارش', COLORS['primary'], self.app.show_report_screen),
            ('📋 تاریخچه', COLORS['warning'], self.app.show_history_screen),
        ]
        
        for text, color, callback in buttons:
            btn = RoundedButton(text=text)
            btn.canvas.before.children[0].rgba = color
            btn.bind(on_press=callback)
            buttons_layout.add_widget(btn)
        
        self.add_widget(buttons_layout)

class IncomeScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [25, 20, 25, 20]
        self.spacing = 20
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.go_back)
        title = Label(text='ثبت درآمد جدید', font_size='24sp', bold=True, color=COLORS['primary'])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))
        self.add_widget(header)
        
        input_layout = BoxLayout(orientation='vertical', spacing=15)
        
        self.amount_input = TextInput(
            hint_text='مبلغ درآمد (تومان)',
            input_filter='float',
            font_size='18sp',
            size_hint_y=0.2,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        self.desc_input = TextInput(
            hint_text='توضیحات',
            font_size='18sp',
            size_hint_y=0.2,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        self.source_input = TextInput(
            hint_text='منبع درآمد',
            font_size='18sp', 
            size_hint_y=0.2,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        input_layout.add_widget(self.amount_input)
        input_layout.add_widget(self.desc_input)
        input_layout.add_widget(self.source_input)
        self.add_widget(input_layout)
        
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=15)
        btn_save = RoundedButton(text='ذخیره درآمد')
        btn_save.canvas.before.children[0].rgba = COLORS['success']
        btn_save.bind(on_press=self.save_income)
        
        btn_clear = RoundedButton(text='پاک کردن')
        btn_clear.canvas.before.children[0].rgba = COLORS['warning']
        btn_clear.bind(on_press=self.clear_inputs)
        
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_clear)
        self.add_widget(btn_layout)
    
    def save_income(self, instance):
        try:
            amount = float(self.amount_input.text)
            description = self.desc_input.text
            source = self.source_input.text
            
            if amount > 0 and description and source:
                self.app.fm.add_income(amount, description, source)
                self.show_message('موفق', 'درآمد با موفقیت ثبت شد!')
                self.clear_inputs()
                self.app.notification_manager.add_notification(
                    "درآمد جدید 💰",
                    f"مبلغ {amount:,} تومان از {source} ثبت شد",
                    "success"
                )
                self.app.show_main_screen()
            else:
                self.show_message('خطا', 'لطفا همه فیلدها را پر کنید')
        except ValueError:
            self.show_message('خطا', 'مبلغ باید عددی باشد')
    
    def clear_inputs(self, instance=None):
        self.amount_input.text = ''
        self.desc_input.text = '' 
        self.source_input.text = ''
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size='18sp'))
        
        btn_ok = Button(text='باشه', size_hint_y=0.4, background_color=COLORS['primary'])
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        
        popup.open()
    
    def go_back(self, instance):
        self.app.show_main_screen()

class ExpenseScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [25, 20, 25, 20]
        self.spacing = 20
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.go_back)
        title = Label(text='ثبت هزینه جدید', font_size='24sp', bold=True, color=COLORS['primary'])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))
        self.add_widget(header)
        
        input_layout = BoxLayout(orientation='vertical', spacing=15)
        
        self.amount_input = TextInput(
            hint_text='مبلغ هزینه (تومان)',
            input_filter='float',
            font_size='18sp',
            size_hint_y=0.2,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        self.desc_input = TextInput(
            hint_text='توضیحات',
            font_size='18sp',
            size_hint_y=0.2,
            background_color=COLORS['light'],
            foreground_color=COLORS['dark']
        )
        
        category_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        category_layout.add_widget(Label(text='دسته‌بندی:', size_hint_x=0.4, font_size='18sp'))
        self.category_spinner = Spinner(
            text=self.app.fm.categories[0],
            values=self.app.fm.categories,
            size_hint_x=0.6,
            background_color=COLORS['light']
        )
        category_layout.add_widget(self.category_spinner)
        input_layout.add_widget(category_layout)
        
        input_layout.add_widget(self.amount_input)
        input_layout.add_widget(self.desc_input)
        self.add_widget(input_layout)
        
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=15)
        btn_save = RoundedButton(text='ذخیره هزینه')
        btn_save.canvas.before.children[0].rgba = COLORS['danger']
        btn_save.bind(on_press=self.save_expense)
        
        btn_clear = RoundedButton(text='پاک کردن')
        btn_clear.canvas.before.children[0].rgba = COLORS['warning']
        btn_clear.bind(on_press=self.clear_inputs)
        
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_clear)
        self.add_widget(btn_layout)
    
    def save_expense(self, instance):
        try:
            amount = float(self.amount_input.text)
            description = self.desc_input.text
            category = self.category_spinner.text
            
            if amount > 0 and description:
                self.app.fm.add_expense(amount, description, category)
                self.show_message('موفق', 'هزینه با موفقیت ثبت شد!')
                self.clear_inputs()
                self.app.notification_manager.add_notification(
                    "هزینه جدید 💸",
                    f"مبلغ {amount:,} تومان برای {category} ثبت شد",
                    "info"
                )
                self.app.show_main_screen()
            else:
                self.show_message('خطا', 'لطفا همه فیلدها را پر کنید')
        except ValueError:
            self.show_message('خطا', 'مبلغ باید عددی باشد')
    
    def clear_inputs(self, instance=None):
        self.amount_input.text = ''
        self.desc_input.text = ''
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size='18sp'))
        
        btn_ok = Button(text='باشه', size_hint_y=0.4, background_color=COLORS['primary'])
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        
        popup.open()
    
    def go_back(self, instance):
        self.app.show_main_screen()

class NotificationScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [25, 20, 25, 20]
        self.spacing = 15
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.go_back)
        title = Label(text='🔔 اعلان‌ها', font_size='24sp', bold=True, color=COLORS['primary'])
        notification_count = self.app.notification_manager.get_unread_count()
        count_label = Label(text=f'({notification_count} جدید)', font_size='16sp', color=COLORS['danger'])
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(count_label)
        self.add_widget(header)
        
        if notification_count > 0:
            btn_mark_all = Button(
                text='📭 علامت‌گذاری همه как خوانده شده',
                size_hint_y=0.08,
                background_color=COLORS['success']
            )
            btn_mark_all.bind(on_press=self.mark_all_read)
            self.add_widget(btn_mark_all)
        
        content = ScrollView()
        notifications_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        notifications_layout.bind(minimum_height=notifications_layout.setter('height'))
        
        notifications = self.app.notification_manager.get_recent_notifications(20)
        
        if not notifications:
            empty_label = Label(
                text='📭 هیچ اعلانی وجود ندارد',
                font_size='18sp',
                color=COLORS['dark'],
                size_hint_y=None,
                height=100
            )
            notifications_layout.add_widget(empty_label)
        else:
            for notification in notifications:
                notification_card = self.create_notification_card(notification)
                notifications_layout.add_widget(notification_card)
        
        content.add_widget(notifications_layout)
        self.add_widget(content)
    
    def create_notification_card(self, notification):
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=15,
            spacing=5
        )
        
        if notification['type'] == 'success':
            bg_color = COLORS['success']
        elif notification['type'] == 'warning':
            bg_color = COLORS['warning']
        elif notification['type'] == 'danger':
            bg_color = COLORS['danger']
        else:
            bg_color = COLORS['primary']
        
        with card.canvas.before:
            Color(*bg_color)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        
        title_layout = BoxLayout(size_hint_y=0.4)
        title_label = Label(
            text=notification['title'],
            font_size='16sp',
            color=COLORS['light'],
            bold=True
        )
        time_label = Label(
            text=notification['time'][11:16],
            font_size='12sp',
            color=COLORS['light']
        )
        title_layout.add_widget(title_label)
        title_layout.add_widget(time_label)
        
        message_label = Label(
            text=notification['message'],
            font_size='14sp',
            color=COLORS['light'],
            text_size=(Window.width - 80, None)
        )
        
        if not notification['read']:
            unread_indicator = Label(
                text='●',
                font_size='20sp',
                color=get_color_from_hex('#ffeb3b')
            )
            title_layout.add_widget(unread_indicator)
        
        card.add_widget(title_layout)
        card.add_widget(message_label)
        
        card.bind(on_touch_down=lambda instance, touch: self.mark_as_read(notification['id']) 
                 if instance.collide_point(*touch.pos) else False)
        
        return card
    
    def mark_as_read(self, notification_id):
        self.app.notification_manager.mark_as_read(notification_id)
        self.app.show_notification_screen()
    
    def mark_all_read(self, instance):
        self.app.notification_manager.mark_all_as_read()
        self.app.show_notification_screen()
    
    def go_back(self, instance):
        self.app.show_main_screen()

class ProfileScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = [25, 20, 25, 20]
        self.spacing = 20
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.go_back)
        title = Label(text='👤 پروفایل کاربری', font_size='24sp', bold=True, color=COLORS['primary'])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))
        self.add_widget(header)
        
        user_data = self.app.user_manager.get_current_user_data()
        
        info_card = BoxLayout(orientation='vertical', size_hint_y=None, height=180, padding=15)
        with info_card.canvas.before:
            Color(*COLORS['primary'])
            RoundedRectangle(pos=info_card.pos, size=info_card.size, radius=[15])
        
        username_label = Label(text=f'👤 نام کاربری: {user_data["username"]}', 
                              font_size='18sp', color=COLORS['light'])
        email_label = Label(text=f'📧 ایمیل: {user_data["email"]}', 
                           font_size='16sp', color=COLORS['light'])
        join_date = Label(text=f'📅 عضو since: {user_data["created_at"][:10]}', 
                         font_size='14sp', color=COLORS['light'])
        
        info_card.add_widget(username_label)
        info_card.add_widget(email_label)
        info_card.add_widget(join_date)
        self.add_widget(info_card)
        
        stats_card = BoxLayout(orientation='vertical', size_hint_y=None, height=150, padding=15)
        with stats_card.canvas.before:
            Color(*COLORS['secondary'])
            RoundedRectangle(pos=stats_card.pos, size=stats_card.size, radius=[15])
        
        balance_label = Label(text=f'💰 موجودی: {self.app.fm.get_balance():,} تومان', 
                            font_size='16sp', color=COLORS['light'])
        trans_count = Label(text=f'📊 تعداد تراکنش‌ها: {len(self.app.fm.transactions)}', 
                          font_size='16sp', color=COLORS['light'])
        
        stats_card.add_widget(balance_label)
        stats_card.add_widget(trans_count)
        self.add_widget(stats_card)
        
        btn_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.4)
        
        btn_logout = RoundedButton(text='🚪 خروج از حساب')
        btn_logout.canvas.before.children[0].rgba = COLORS['danger']
        btn_logout.bind(on_press=self.logout)
        
        btn_layout.add_widget(btn_logout)
        self.add_widget(btn_layout)
    
    def logout(self, instance):
        self.app.user_manager.logout_user()
        self.app.show_login_screen()
        self.app.notification_manager.add_notification(
            "خروج موفق ✅",
            "شما با موفقیت از حساب کاربری خود خارج شدید",
            "info"
        )
    
    def go_back(self, instance):
        self.app.show_main_screen()

class FinancialIntelligenceApp(App):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.notification_manager = NotificationManager()
        self.fm = None
        
        self.setup_notification_checker()
    
    def setup_notification_checker(self):
        Clock.schedule_interval(self.check_auto_notifications, 30)
    
    def check_auto_notifications(self, dt):
        if self.fm and self.user_manager.current_user:
            budget_alerts = self.fm.check_budget_alerts()
            for alert in budget_alerts:
                self.notification_manager.add_notification("هشدار بودجه ⚠️", alert, "warning")
            
            weekly_income, weekly_expense = self.fm.get_weekly_report()
            if weekly_income > 0 or weekly_expense > 0:
                self.notification_manager.add_notification(
                    "گزارش هفتگی 📈",
                    f"درآمد هفته: {weekly_income:,} تومان\nهزینه هفته: {weekly_expense:,} تومان",
                    "info"
                )
    
    def build(self):
        self.title = "هوش مالی"
        if self.user_manager.current_user:
            self.fm = FinancialManager(self.user_manager.get_current_user_data()['user_id'])
            return MainScreen(self)
        else:
            return LoginScreen(self)
    
    def show_login_screen(self):
        self.root.clear_widgets()
        self.root.add_widget(LoginScreen(self))
    
    def show_register_screen(self):
        self.root.clear_widgets()
        self.root.add_widget(RegisterScreen(self))
    
    def show_main_screen(self):
        self.root.clear_widgets()
        self.main_screen = MainScreen(self)
        self.root.add_widget(self.main_screen)
    
    def show_income_screen(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(IncomeScreen(self))
    
    def show_expense_screen(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(ExpenseScreen(self))
    
    def show_notification_screen(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(NotificationScreen(self))
    
    def show_profile_screen(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(ProfileScreen(self))
    
    def show_report_screen(self, instance=None):
        layout = BoxLayout(orientation='vertical', padding=[25, 20, 25, 20])
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.show_main_screen)
        title = Label(text='گزارش مالی', font_size='24sp', bold=True, color=COLORS['primary'])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))
        layout.add_widget(header)
        
        content = ScrollView()
        report_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        report_layout.bind(minimum_height=report_layout.setter('height'))
        
        balance = self.fm.get_balance()
        balance_color = COLORS['success'] if balance >= 0 else COLORS['danger']
        
        balance_card = ModernCard(
            title='موجودی فعلی', 
            value=f'{balance:,} تومان',
            color=balance_color,
            icon='💰'
        )
        report_layout.add_widget(balance_card)
        
        expenses = self.fm.get_category_expenses()
        for category, amount in expenses.items():
            if amount > 0:
                expense_card = ModernCard(
                    title=category, 
                    value=f'{amount:,} تومان',
                    color=COLORS['warning'],
                    icon='📋'
                )
                report_layout.add_widget(expense_card)
        
        content.add_widget(report_layout)
        layout.add_widget(content)
        
        self.root.clear_widgets()
        self.root.add_widget(layout)
    
    def show_history_screen(self, instance=None):
        layout = BoxLayout(orientation='vertical', padding=[25, 20, 25, 20])
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(text='🔙', size_hint_x=0.2, background_color=(0,0,0,0))
        back_btn.bind(on_press=self.show_main_screen)
        title = Label(text='تاریخچه تراکنش‌ها', font_size='24sp', bold=True, color=COLORS['primary'])
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label(size_hint_x=0.2))
        layout.add_widget(header)
        
        content = ScrollView()
        history_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        history_layout.bind(minimum_height=history_layout.setter('height'))
        
        recent_transactions = self.fm.transactions[-15:]
        
        if not recent_transactions:
            empty_label = Label(
                text='هیچ تراکنشی ثبت نشده است',
                font_size='18sp',
                color=COLORS['dark'],
                size_hint_y=None,
                height=100
            )
            history_layout.add_widget(empty_label)
        else:
            for transaction in reversed(recent_transactions):
                if transaction['type'] == 'income':
                    text = f"درآمد: {transaction['amount']:,} تومان\n{transaction['description']}"
                    bg_color = COLORS['success']
                else:
                    text = f"هزینه: {transaction['amount']:,} تومان\n{transaction['description']}\n{transaction['category']}"
                    bg_color = COLORS['danger']
                
                transaction_card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=120,
                    padding=15,
                    spacing=5
                )
                
                with transaction_card.canvas.before:
                    Color(*bg_color)
                    RoundedRectangle(pos=transaction_card.pos, size=transaction_card.size, radius=[15])
                
                amount_label = Label(
                    text=text,
                    font_size='16sp',
                    color=COLORS['light'],
                    text_size=(Window.width - 80, None)
                )
                
                date_label = Label(
                    text=transaction['date'][:16],
                    font_size='12sp',
                    color=COLORS['light']
                )
                
                transaction_card.add_widget(amount_label)
                transaction_card.add_widget(date_label)
                history_layout.add_widget(transaction_card)
        
        content.add_widget(history_layout)
        layout.add_widget(content)
        
        self.root.clear_widgets()
        self.root.add_widget(layout)

if __name__ == '__main__':
    FinancialIntelligenceApp().run()
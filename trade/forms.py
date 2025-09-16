from django import forms
from trade.models.trade import Trade
from trade.models.transactions import Transaction
from trade.models.customers import Customer
from trade.models.accounts import Account


class BankTransferForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["sender_account", "recipient_account", "amount", "description"]

    sender_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(status="ACTIVE"),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    recipient_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(status="ACTIVE"),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01"}),
    )
    description = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )


class MobileMoneyForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["sender_account", "recipient_number", "network", "amount", "description"]

    sender_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(status="ACTIVE"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    recipient_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    network = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01"}),
    )
    description = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )


class DepositForm(forms.Form):
    to_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(status="ACTIVE"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01"}),
    )
    description = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )


class WithdrawalForm(forms.Form):
    from_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(status="ACTIVE"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01"}),
    )
    description = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )


class BillPaymentForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["sender_account", "bill_type", "recipient_account_number", "amount", "description"]

    sender_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(status="ACTIVE"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    bill_type = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    recipient_account_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0.01"}),
    )
    description = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "currency", "wallet_address"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "1000"}
            ),
            "currency": forms.Select(attrs={"class": "form-control"}),
            "wallet_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter or paste your crypto wallet",
                }
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= 0:
            raise forms.ValidationError("Please enter a valid amount greater than 0.")
        return amount


class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "amount",
            "currency",
        ]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "1000"}
            ),
            "currency": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= 0:
            raise forms.ValidationError("Please enter a valid amount greater than 0.")
        return amount


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ["is_active", "referial_code"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your full name"}
            ),
            "country_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Country code (e.g. +1)"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone number"}
            ),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "agent": forms.Select(attrs={"class": "form-control"}),
            "user": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "full_name": "Full Name",
            "country_code": "Country Code",
            "phone_number": "Phone Number",
            "image": "Profile Image",
            "agent": "Assigned Agent",
            "user": "Linked User Account",
        }


class EditTradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            "trade_type",
            "symbol",
            "amount",
            "leverage",
            "stop_loss",
            "take_profit",
            "profit_loss",
            "allow_close_trade",
        ]
        widgets = {
            "trade_type": forms.RadioSelect(
                choices=Trade.TRADE_TYPE_CHOICES, attrs={"class": "trade-type-btn"}
            ),
            "symbol": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "1000"}
            ),
            "leverage": forms.Select(attrs={"class": "form-control"}),
            "stop_loss": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "46000"}
            ),
            "take_profit": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "48000"}
            ),
            "profit_loss": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "48000"}
            ),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["balance"]
        widgets = {
            "balance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            )
        }
